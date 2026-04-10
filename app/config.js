require('dotenv').config();
const pino = require('pino');

const bootLogger = pino({ level: 'fatal' });

const REQUIRED_ENV = ['ACCESS_TOKEN_SECRET', 'REFRESH_TOKEN_SECRET'];
const missing = REQUIRED_ENV.filter((key) => !process.env[key]);

if (missing.length > 0) {
  bootLogger.fatal(
    { missing },
    `Missing required environment variables: ${missing.join(', ')}`,
  );
  process.exit(1);
}

module.exports = {
  ACCESS_TOKEN_SECRET: process.env.ACCESS_TOKEN_SECRET,
  REFRESH_TOKEN_SECRET: process.env.REFRESH_TOKEN_SECRET,
  PORT: parseInt(process.env.PORT, 10) || 3000,
  CORS_ORIGIN: process.env.CORS_ORIGIN || '*',
  ACCESS_TOKEN_EXPIRY: process.env.ACCESS_TOKEN_EXPIRY || '15m',
  REFRESH_TOKEN_EXPIRY: process.env.REFRESH_TOKEN_EXPIRY || '7d',
  SALT_ROUNDS: parseInt(process.env.SALT_ROUNDS, 10) || 10,
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
};
