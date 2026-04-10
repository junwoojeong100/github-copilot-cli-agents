const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const config = require('../config');

// In-memory stores
const users = new Map();          // userId → { id, email, passwordHash }
const emailIndex = new Map();     // email → userId  (O(1) lookup)
// token → { userId, expiresAt }
const refreshTokens = new Map();

const PASSWORD_REGEX = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]).{8,}$/;

function generateTokens(user) {
  const accessToken = jwt.sign(
    { sub: user.id, email: user.email },
    config.ACCESS_TOKEN_SECRET,
    { expiresIn: config.ACCESS_TOKEN_EXPIRY },
  );

  const refreshToken = jwt.sign(
    { sub: user.id, email: user.email },
    config.REFRESH_TOKEN_SECRET,
    { expiresIn: config.REFRESH_TOKEN_EXPIRY },
  );

  const decoded = jwt.decode(refreshToken);
  refreshTokens.set(refreshToken, {
    userId: user.id,
    expiresAt: new Date(decoded.exp * 1000),
  });

  return { accessToken, refreshToken };
}

function validatePassword(password) {
  if (typeof password !== 'string' || !PASSWORD_REGEX.test(password)) {
    return 'Password must be at least 8 characters with 1 uppercase, 1 number, and 1 special character';
  }
  return null;
}

async function register(email, password) {
  if (!email || !password) {
    return { error: 'Email and password are required', status: 400 };
  }

  if (typeof email !== 'string' || !email.includes('@')) {
    return { error: 'Invalid email format', status: 400 };
  }

  const pwError = validatePassword(password);
  if (pwError) {
    return { error: pwError, status: 400 };
  }

  if (emailIndex.has(email)) {
    return { error: 'Email already registered', status: 409 };
  }

  const passwordHash = await bcrypt.hash(password, config.SALT_ROUNDS);
  const id = uuidv4();
  const user = { id, email, passwordHash };

  users.set(id, user);
  emailIndex.set(email, id);

  const tokens = generateTokens(user);

  return {
    status: 201,
    data: {
      message: 'User registered successfully',
      user: { id, email },
      ...tokens,
    },
  };
}

async function login(email, password) {
  if (!email || !password) {
    return { error: 'Email and password are required', status: 400 };
  }

  const userId = emailIndex.get(email);
  const user = userId ? users.get(userId) : undefined;

  if (!user) {
    return { error: 'Invalid email or password', status: 401 };
  }

  const valid = await bcrypt.compare(password, user.passwordHash);
  if (!valid) {
    return { error: 'Invalid email or password', status: 401 };
  }

  const tokens = generateTokens(user);

  return {
    status: 200,
    data: {
      message: 'Login successful',
      user: { id: user.id, email: user.email },
      ...tokens,
    },
  };
}

function refresh(token) {
  if (!token) {
    return { error: 'Refresh token is required', status: 400 };
  }

  if (!refreshTokens.has(token)) {
    return { error: 'Refresh token is revoked or invalid', status: 403 };
  }

  let payload;
  try {
    payload = jwt.verify(token, config.REFRESH_TOKEN_SECRET);
  } catch (err) {
    refreshTokens.delete(token);
    if (err.name === 'TokenExpiredError') {
      return { error: 'Refresh token expired', status: 401 };
    }
    return { error: 'Invalid refresh token', status: 403 };
  }

  const user = users.get(payload.sub);
  if (!user) {
    refreshTokens.delete(token);
    return { error: 'User no longer exists', status: 401 };
  }

  // Rotate: revoke old, issue new pair
  refreshTokens.delete(token);
  const tokens = generateTokens(user);

  return {
    status: 200,
    data: { message: 'Tokens refreshed successfully', ...tokens },
  };
}

function logout(token) {
  if (!token) {
    return { error: 'Refresh token is required', status: 400 };
  }

  refreshTokens.delete(token);
  return { status: 200, data: { message: 'Logged out successfully' } };
}

function logoutAll(userId) {
  if (!userId) {
    return { error: 'User ID is required', status: 400 };
  }

  let revoked = 0;
  for (const [token, meta] of refreshTokens) {
    if (meta.userId === userId) {
      refreshTokens.delete(token);
      revoked++;
    }
  }

  return {
    status: 200,
    data: { message: `All sessions revoked (${revoked} tokens invalidated)` },
  };
}

// Expose stores for testing only
module.exports = {
  register,
  login,
  refresh,
  logout,
  logoutAll,
  _stores: { users, emailIndex, refreshTokens },
};
