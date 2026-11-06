import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add Bearer token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken') || 'test_user_token_12345678';
  config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Cart APIs
export const cartAPI = {
  createCart: () => api.post('/carts'),
  getCart: (cartId) => api.get(`/carts/${cartId}`),
  listCarts: () => api.get('/carts'),
  addItem: (cartId, item) => api.post(`/carts/${cartId}/items`, item),
  updateItem: (cartId, itemId, quantity) =>
    api.put(`/carts/${cartId}/items/${itemId}`, { quantity }),
  removeItem: (cartId, itemId) =>
    api.delete(`/carts/${cartId}/items/${itemId}`),
};

// Checkout APIs
export const checkoutAPI = {
  initiateCheckout: (cartId, shippingAddress) =>
    api.post('/checkout', { cart_id: cartId, shipping_address: shippingAddress }),
};

// Payment APIs
export const paymentAPI = {
  processPayment: (orderId, amount, idempotencyKey, processorTxnId) =>
    api.post(`/checkout/${orderId}/payment`, {
      amount,
      idempotency_key: idempotencyKey,
      processor_transaction_id: processorTxnId,
    }),
};

// Bill APIs
export const billAPI = {
  getBillForOrder: (orderId) => api.get(`/bills/orders/${orderId}`),
  getBill: (billId) => api.get(`/bills/${billId}`),
};

export default api;
