const express = require('express');
const rateLimit = require('express-rate-limit');
const authService = require('../services/auth');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many login attempts, please try again after 15 minutes' },
});

const registerLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many registration attempts, please try again after 15 minutes' },
});

// POST /auth/register
router.post('/register', registerLimiter, async (req, res, next) => {
  try {
    const { email, password } = req.body;
    const result = await authService.register(email, password);
    if (result.error) {
      return res.status(result.status).json({ error: result.error });
    }
    req.log.info({ email }, 'User registered');
    res.status(result.status).json(result.data);
  } catch (err) {
    next(err);
  }
});

// POST /auth/login
router.post('/login', loginLimiter, async (req, res, next) => {
  try {
    const { email, password } = req.body;
    const result = await authService.login(email, password);
    if (result.error) {
      return res.status(result.status).json({ error: result.error });
    }
    req.log.info({ email }, 'User logged in');
    res.status(result.status).json(result.data);
  } catch (err) {
    next(err);
  }
});

// POST /auth/refresh
router.post('/refresh', (req, res, next) => {
  try {
    const { refreshToken } = req.body;
    const result = authService.refresh(refreshToken);
    if (result.error) {
      return res.status(result.status).json({ error: result.error });
    }
    res.status(result.status).json(result.data);
  } catch (err) {
    next(err);
  }
});

// POST /auth/logout
router.post('/logout', (req, res, next) => {
  try {
    const { refreshToken } = req.body;
    const result = authService.logout(refreshToken);
    if (result.error) {
      return res.status(result.status).json({ error: result.error });
    }
    res.status(result.status).json(result.data);
  } catch (err) {
    next(err);
  }
});

// POST /auth/logout-all — revokes all refresh tokens for the authenticated user
router.post('/logout-all', authenticateToken, (req, res, next) => {
  try {
    const result = authService.logoutAll(req.user.id);
    if (result.error) {
      return res.status(result.status).json({ error: result.error });
    }
    req.log.info({ userId: req.user.id }, 'All sessions revoked');
    res.status(result.status).json(result.data);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
