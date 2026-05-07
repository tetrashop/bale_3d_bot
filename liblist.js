// lib/state.js
export const pendingModels = new Map(); // token -> { path, filename, createdAt, imageBuffer? }
export const paidTokens = new Map();    // token -> transactionId
