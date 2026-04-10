const { v4: uuidv4 } = require('uuid');

// userId → Map<todoId, todo>
const todosByUser = new Map();

function getUserTodos(userId) {
  if (!todosByUser.has(userId)) {
    todosByUser.set(userId, new Map());
  }
  return todosByUser.get(userId);
}

function list(userId, { completed, sort = 'createdAt', order = 'asc' } = {}) {
  const todos = getUserTodos(userId);
  let items = Array.from(todos.values());

  if (completed !== undefined) {
    const flag = completed === 'true' || completed === true;
    items = items.filter((t) => t.completed === flag);
  }

  const dir = order === 'desc' ? -1 : 1;
  if (sort === 'createdAt') {
    items.sort((a, b) => dir * (new Date(a.createdAt) - new Date(b.createdAt)));
  }

  return { status: 200, data: items };
}

function getById(userId, todoId) {
  const todos = getUserTodos(userId);
  const todo = todos.get(todoId);
  if (!todo) {
    return { error: 'Todo not found', status: 404 };
  }
  return { status: 200, data: todo };
}

function create(userId, { title, description = '' }) {
  if (!title || typeof title !== 'string' || !title.trim()) {
    return { error: 'Title is required', status: 400 };
  }

  const now = new Date().toISOString();
  const todo = {
    id: uuidv4(),
    title: title.trim(),
    description,
    completed: false,
    createdAt: now,
    updatedAt: now,
  };

  const todos = getUserTodos(userId);
  todos.set(todo.id, todo);

  return { status: 201, data: todo };
}

function update(userId, todoId, fields) {
  const todos = getUserTodos(userId);
  const todo = todos.get(todoId);
  if (!todo) {
    return { error: 'Todo not found', status: 404 };
  }

  if (fields.title !== undefined) {
    if (typeof fields.title !== 'string' || !fields.title.trim()) {
      return { error: 'Title must be a non-empty string', status: 400 };
    }
    todo.title = fields.title.trim();
  }

  if (fields.description !== undefined) {
    todo.description = fields.description;
  }

  if (fields.completed !== undefined) {
    if (typeof fields.completed !== 'boolean') {
      return { error: 'Completed must be a boolean', status: 400 };
    }
    todo.completed = fields.completed;
  }

  todo.updatedAt = new Date().toISOString();

  return { status: 200, data: todo };
}

function remove(userId, todoId) {
  const todos = getUserTodos(userId);
  if (!todos.has(todoId)) {
    return { error: 'Todo not found', status: 404 };
  }

  todos.delete(todoId);
  return { status: 200, data: { message: 'Todo deleted successfully' } };
}

module.exports = {
  list,
  getById,
  create,
  update,
  remove,
  _store: todosByUser,
};
