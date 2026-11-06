import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { checkoutAPI } from '../services/api';
import '../styles/Checkout.css';

function Checkout() {
  const navigate = useNavigate();
  const cart = useSelector((state) => state.cart);
  const [loading, setLoading] = useState(false);
  const [address, setAddress] = useState({
    street: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'USA',
  });
  const [orderData, setOrderData] = useState(null);

  const handleAddressChange = (e) => {
    const { name, value } = e.target;
    setAddress((prev) => ({ ...prev, [name]: value }));
  };

  const handleCheckout = async (e) => {
    e.preventDefault();
    
    if (!address.street || !address.city || !address.state || !address.postal_code) {
      alert('Please fill in all address fields');
      return;
    }

    try {
      setLoading(true);
      const response = await checkoutAPI.initiateCheckout(cart.cartId, address);
      if (response.data.success) {
        setOrderData(response.data.data);
        // Navigate to payment after a brief delay
        setTimeout(() => {
          navigate('/payment', { state: { orderId: response.data.data.order_id, total: response.data.data.total_amount } });
        }, 1500);
      }
    } catch (error) {
      alert('Checkout failed: ' + error.message);
      console.error('Checkout error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!cart.cartId) {
    return <div className="error-message">No cart found. Please add items first.</div>;
  }

  return (
    <div className="checkout-container">
      <h1>Checkout</h1>
      
      <div className="checkout-content">
        <form onSubmit={handleCheckout} className="checkout-form">
          <h2>Shipping Address</h2>
          
          <div className="form-group">
            <label>Street Address *</label>
            <input
              type="text"
              name="street"
              value={address.street}
              onChange={handleAddressChange}
              placeholder="123 Main Street"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>City *</label>
              <input
                type="text"
                name="city"
                value={address.city}
                onChange={handleAddressChange}
                placeholder="Chicago"
                required
              />
            </div>

            <div className="form-group">
              <label>State *</label>
              <input
                type="text"
                name="state"
                value={address.state}
                onChange={handleAddressChange}
                placeholder="IL"
                maxLength="2"
                required
              />
            </div>

            <div className="form-group">
              <label>Postal Code *</label>
              <input
                type="text"
                name="postal_code"
                value={address.postal_code}
                onChange={handleAddressChange}
                placeholder="60601"
                required
              />
            </div>
          </div>

          <button type="submit" className="checkout-btn" disabled={loading}>
            {loading ? 'Processing...' : 'Continue to Payment'}
          </button>
        </form>

        {orderData && (
          <div className="order-summary">
            <h2>Order Summary</h2>
            <p>Subtotal: ${parseFloat(orderData.items_subtotal).toFixed(2)}</p>
            <p>Shipping: ${parseFloat(orderData.shipping_fee).toFixed(2)}</p>
            <p>Tax: ${parseFloat(orderData.tax_amount).toFixed(2)}</p>
            <h3>Total: ${parseFloat(orderData.total_amount).toFixed(2)}</h3>
          </div>
        )}
      </div>
    </div>
  );
}

export default Checkout;
