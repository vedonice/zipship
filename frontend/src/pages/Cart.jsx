import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { cartAPI } from '../services/api';
import { setCart, removeFromCart, updateQuantity } from '../store/cartSlice';
import '../styles/Cart.css';

function Cart() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const cart = useSelector((state) => state.cart);
  const [loading, setLoading] = useState(true);
  const [showAddItem, setShowAddItem] = useState(false);
  const [newItem, setNewItem] = useState({
    product_id: '',
    product_name: '',
    quantity: 1,
    unit_price: ''
  });

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      setLoading(true);
      const response = await cartAPI.listCarts();
      if (response.data && response.data.length > 0) {
        const cartData = response.data[0];
        dispatch(setCart(cartData));
      }
    } catch (error) {
      console.error('Failed to load cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCart = async () => {
    try {
      setLoading(true);
      const response = await cartAPI.createCart();
      if (response.data) {
        const cartData = response.data;
        dispatch(setCart(cartData));
        alert('✅ Cart created successfully!');
      }
    } catch (error) {
      console.error('Failed to create cart:', error);
      alert('❌ Failed to create cart');
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!cart?.cartId) {
      alert('❌ Please create a cart first');
      return;
    }
    if (!newItem.product_id || !newItem.product_name || !newItem.unit_price) {
      alert('❌ Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      await cartAPI.addItem(cart.cartId, {
        product_id: newItem.product_id,
        product_name: newItem.product_name,
        quantity: parseInt(newItem.quantity),
        unit_price: parseFloat(newItem.unit_price)
      });

      await loadCart();
      setNewItem({
        product_id: '',
        product_name: '',
        quantity: 1,
        unit_price: ''
      });
      setShowAddItem(false);
      alert('✅ Item added successfully!');
    } catch (error) {
      console.error('Failed to add item:', error);
      alert('❌ Failed to add item');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveItem = async (itemId) => {
    try {
      await cartAPI.removeItem(cart.cartId, itemId);
      dispatch(removeFromCart(itemId));
    } catch (error) {
      console.error('Failed to remove item:', error);
    }
  };

  const handleUpdateQuantity = async (itemId, quantity) => {
    try {
      await cartAPI.updateItem(cart.cartId, itemId, quantity);
      dispatch(updateQuantity({ itemId, quantity }));
    } catch (error) {
      console.error('Failed to update quantity:', error);
    }
  };

  const handleCheckout = () => {
    if (!cart?.items || cart.items.length === 0) {
      alert('Your cart is empty');
      return;
    }
    navigate('/checkout');
  };

  return (
    <div className="cart-container">
      <h1>🛒 Shopping Cart</h1>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : !cart?.cartId ? (
        <div className="no-cart-section">
          <p className="empty-message">No cart created yet</p>
          <button
            className="create-cart-btn"
            onClick={handleCreateCart}
            disabled={loading}
          >
            ➕ Create New Cart
          </button>
        </div>
      ) : !cart.items || cart.items.length === 0 ? (
        <div className="empty-section">
          <p className="empty-message">Your cart is empty</p>
          <button
            className="add-item-btn"
            onClick={() => setShowAddItem(!showAddItem)}
          >
            ➕ Add Item
          </button>

          {showAddItem && (
            <form className="add-item-form" onSubmit={handleAddItem}>
              <div className="form-group">
                <label>Product ID</label>
                <input
                  type="text"
                  placeholder="e.g., PROD-001"
                  value={newItem.product_id}
                  onChange={(e) => setNewItem({...newItem, product_id: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Product Name</label>
                <input
                  type="text"
                  placeholder="e.g., MacBook Pro"
                  value={newItem.product_name}
                  onChange={(e) => setNewItem({...newItem, product_name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input
                  type="number"
                  min="1"
                  max="999"
                  value={newItem.quantity}
                  onChange={(e) => setNewItem({...newItem, quantity: parseInt(e.target.value)})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Unit Price</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="e.g., 99.99"
                  value={newItem.unit_price}
                  onChange={(e) => setNewItem({...newItem, unit_price: e.target.value})}
                  required
                />
              </div>
              <div className="form-buttons">
                <button type="submit" className="submit-btn">✓ Add Item</button>
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setShowAddItem(false)}
                >
                  ✕ Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      ) : (
        <>
          <div className="cart-items-header">
            <h2>Items in Cart ({cart.items.length})</h2>
            <button
              className="add-item-btn-small"
              onClick={() => setShowAddItem(!showAddItem)}
            >
              {showAddItem ? '➖ Hide Form' : '➕ Add More Items'}
            </button>
          </div>

          {showAddItem && (
            <form className="add-item-form" onSubmit={handleAddItem}>
              <div className="form-group">
                <label>Product ID</label>
                <input
                  type="text"
                  placeholder="e.g., PROD-001"
                  value={newItem.product_id}
                  onChange={(e) => setNewItem({...newItem, product_id: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Product Name</label>
                <input
                  type="text"
                  placeholder="e.g., MacBook Pro"
                  value={newItem.product_name}
                  onChange={(e) => setNewItem({...newItem, product_name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input
                  type="number"
                  min="1"
                  max="999"
                  value={newItem.quantity}
                  onChange={(e) => setNewItem({...newItem, quantity: parseInt(e.target.value)})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Unit Price</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="e.g., 99.99"
                  value={newItem.unit_price}
                  onChange={(e) => setNewItem({...newItem, unit_price: e.target.value})}
                  required
                />
              </div>
              <div className="form-buttons">
                <button type="submit" className="submit-btn">✓ Add Item</button>
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setShowAddItem(false)}
                >
                  ✕ Cancel
                </button>
              </div>
            </form>
          )}

          <div className="cart-items">
            {cart.items.map((item) => (
              <div key={item.cart_item_id} className="cart-item">
                <div className="item-details">
                  <h3>{item.product_name}</h3>
                  <p>Unit Price: ${parseFloat(item.unit_price).toFixed(2)}</p>
                </div>
                <div className="item-actions">
                  <input
                    type="number"
                    min="1"
                    max="999"
                    value={item.quantity}
                    onChange={(e) =>
                      handleUpdateQuantity(item.cart_item_id, parseInt(e.target.value))
                    }
                  />
                  <p className="item-subtotal">Subtotal: ${parseFloat(item.subtotal).toFixed(2)}</p>
                  <button
                    className="remove-btn"
                    onClick={() => handleRemoveItem(item.cart_item_id)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="cart-summary">
            <h2>Order Summary</h2>
            <p>Items: {cart.itemCount || 0}</p>
            <p>Subtotal: ${parseFloat(cart.totalAmount || 0).toFixed(2)}</p>
            <button className="checkout-btn" onClick={handleCheckout}>
              Proceed to Checkout
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default Cart;
