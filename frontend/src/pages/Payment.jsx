import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import { paymentAPI } from '../services/api';
import '../styles/Payment.css';

function Payment() {
  const navigate = useNavigate();
  const location = useLocation();
  const { orderId, total } = location.state || {};
  const [loading, setLoading] = useState(false);
  const [cardData, setCardData] = useState({
    cardNumber: '',
    cardHolder: '',
    expiryDate: '',
    cvv: '',
  });

  const handleCardChange = (e) => {
    const { name, value } = e.target;
    setCardData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePayment = async (e) => {
    e.preventDefault();

    if (!cardData.cardNumber || !cardData.cardHolder || !cardData.expiryDate || !cardData.cvv) {
      alert('Please fill in all card details');
      return;
    }

    try {
      setLoading(true);
      const idempotencyKey = uuidv4();
      
      // In production, this would use Stripe tokenization
      // For MVP, send to backend with test token
      const response = await paymentAPI.processPayment(
        orderId,
        parseFloat(total),
        idempotencyKey,
        `txn_${Date.now()}`
      );

      if (response.data.success) {
        // Redirect to order confirmation
        navigate('/order', { state: { orderId, paymentId: response.data.data.payment_id } });
      }
    } catch (error) {
      alert('Payment failed: ' + error.message);
      console.error('Payment error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!orderId) {
    return <div className="error-message">No order found. Please complete checkout first.</div>;
  }

  return (
    <div className="payment-container">
      <h1>Payment</h1>
      
      <form onSubmit={handlePayment} className="payment-form">
        <h2>Card Details</h2>

        <div className="form-group">
          <label>Card Holder Name *</label>
          <input
            type="text"
            name="cardHolder"
            value={cardData.cardHolder}
            onChange={handleCardChange}
            placeholder="John Doe"
            required
          />
        </div>

        <div className="form-group">
          <label>Card Number *</label>
          <input
            type="text"
            name="cardNumber"
            value={cardData.cardNumber}
            onChange={handleCardChange}
            placeholder="4242 4242 4242 4242"
            maxLength="19"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Expiry Date (MM/YY) *</label>
            <input
              type="text"
              name="expiryDate"
              value={cardData.expiryDate}
              onChange={handleCardChange}
              placeholder="12/25"
              maxLength="5"
              required
            />
          </div>

          <div className="form-group">
            <label>CVV *</label>
            <input
              type="text"
              name="cvv"
              value={cardData.cvv}
              onChange={handleCardChange}
              placeholder="123"
              maxLength="4"
              required
            />
          </div>
        </div>

        <div className="payment-total">
          <h3>Amount to Pay: ${parseFloat(total).toFixed(2)}</h3>
        </div>

        <button type="submit" className="payment-btn" disabled={loading}>
          {loading ? 'Processing Payment...' : 'Complete Payment'}
        </button>
      </form>

      <div className="security-notice">
        <p>🔒 Your payment is secure and encrypted</p>
      </div>
    </div>
  );
}

export default Payment;
