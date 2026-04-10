const express = require('express');
const todoService = require('../services/todo');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// All todo routes require authentication
router.use(authenticateToken);

// GET /todos
router.get('/', (req, res, next) => {
  try {
    const { completed, sort, order } = req.query;
    const result = todoService.list(req.user.id, { completed, sort, order });
    res.status(result.status).json(result.data);
  } catch (err) {
    next(err);
  }
});

// GET /todos/:id
router.get('/:id', (req, res, next) => {
  try {
    const result = todoService.getById(req.user.id, req.params.id);
    if (result.error) {
      return res.status(result.status).json({ error: result.error });
    }
    res.status(result.status).json(result.data);
  } catch (err) {
    next(err);
  }
});

// POST /todos
router.post('/', (req, res, next) => {
  try {
    const { title, description } = req.body;
    const result = todoService.create(req.user.id, { title, description });
    if (result.error) {
      return res.status(result.status).json({ error: result.error });
    }
    req.log.info({ todoId: result.data.id }, 'Todo created');
    res.status(result.status).json(result.data);
  } catch (err) {
    next(err);
  }
});

// PUT /todos/:id
router.put('/:id', (req, res, next) => {
  try {
    const { title, description, completed } = req.body;
    const result = todoService.update(req.user.id, req.params.id, { title, description, completed });
    if (result.error) {
      return res.status(result.status).json({ error: result.error });
    }
    req.log.info({ todoId: req.params.id }, 'Todo updated');
    res.status(result.status).json(result.data);
  } catch (err) {
    next(err);
  }
});

// DELETE /todos/:id
router.delete('/:id', (req, res, next) => {
  try {
    const result = todoService.remove(req.user.id, req.params.id);
    if (result.error) {
      return res.status(result.status).json({ error: result.error });
    }
    req.log.info({ todoId: req.params.id }, 'Todo deleted');
    res.status(result.status).json(result.data);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
