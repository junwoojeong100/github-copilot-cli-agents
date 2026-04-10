const config = require('./config');
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const pino = require('pino');
const pinoHttp = require('pino-http');
const authRoutes = require('./routes/auth');
const { authenticateToken, errorHandler } = require('./middleware/auth');

const logger = pino({ level: config.LOG_LEVEL });
const app = express();

app.use(helmet());
app.use(cors({ origin: config.CORS_ORIGIN }));
app.use(express.json());
app.use(pinoHttp({ logger, quietReqLogger: true }));

// Auth routes (public)
app.use('/auth', authRoutes);

// Example protected route
app.get('/me', authenticateToken, (req, res) => {
  res.json({ user: req.user });
});

// Health check
app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

// Global error handler (must be registered last)
app.use(errorHandler);

const server = app.listen(config.PORT, () => {
  logger.info({ port: config.PORT }, 'Auth API started');
});

// Graceful shutdown
function shutdown(signal) {
  logger.info({ signal }, 'Shutdown signal received, closing server…');
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
  // Force exit after 10 s if connections don't drain
  setTimeout(() => {
    logger.warn('Forcing shutdown after timeout');
    process.exit(1);
  }, 10_000).unref();
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

module.exports = app;
