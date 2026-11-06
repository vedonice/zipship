import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  cartId: null,
  items: [],
  totalAmount: 0,
  itemCount: 0,
  loading: false,
  error: null,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    setCart: (state, action) => {
      const { cart_id, items, summary } = action.payload;
      state.cartId = cart_id;
      state.items = items || [];
      state.totalAmount = summary?.total || '0.00';
      state.itemCount = summary?.item_count || 0;
    },
    addToCart: (state, action) => {
      state.items.push(action.payload);
      state.itemCount += action.payload.quantity;
    },
    removeFromCart: (state, action) => {
      const index = state.items.findIndex((item) => item.cart_item_id === action.payload);
      if (index > -1) {
        state.itemCount -= state.items[index].quantity;
        state.items.splice(index, 1);
      }
    },
    updateQuantity: (state, action) => {
      const { itemId, quantity } = action.payload;
      const item = state.items.find((item) => item.cart_item_id === itemId);
      if (item) {
        state.itemCount += quantity - item.quantity;
        item.quantity = quantity;
      }
    },
    clearCart: (state) => {
      state.cartId = null;
      state.items = [];
      state.totalAmount = 0;
      state.itemCount = 0;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const {
  setCart,
  addToCart,
  removeFromCart,
  updateQuantity,
  clearCart,
  setLoading,
  setError,
} = cartSlice.actions;

export default cartSlice.reducer;
