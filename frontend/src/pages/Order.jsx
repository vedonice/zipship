import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { billAPI } from '../services/api';
import '../styles/Order.css';

function Order() {
  const location = useLocation();
  const navigate = useNavigate();
  const { orderId, paymentId } = location.state || {};
  const [bill, setBill] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadBill();
  }, []);

  const loadBill = async () => {
    try {
      const response = await billAPI.getBillForOrder(orderId);
      if (response.data.success) {
        setBill(response.data.data);
      } else if (response.status === 404) {
        // Bill not generated yet, show order confirmation anyway
        console.warn('Bill not found yet for order:', orderId);
        setBill(null);
      }
    } catch (error) {
      if (error.response?.status === 404) {
        // Bill not found - that's OK, show order confirmation anyway
        console.warn('Bill not found for order:', orderId);
        setBill(null);
      } else {
        setError('Failed to load bill: ' + error.message);
        console.error('Error loading bill:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadBill = async () => {
    if (bill) {
      try {
        const response = await fetch(
          `/api/v1/bills/orders/${orderId}/download`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token') || 'test-token-12345'}`
            }
          }
        );

        if (!response.ok) {
          throw new Error('Failed to download bill');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${bill.bill_number}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error downloading bill:', error);
        alert('Failed to download invoice. Please try again.');
      }
    }
  };

  const handleBackToCart = () => {
    navigate('/');
  };

  if (loading) return <div className="loading">Loading order details...</div>;

  return (
    <div className="order-container">
      <div className="success-message">
        ✓ Order Confirmed Successfully!
      </div>

      <h1>Order Confirmation</h1>

      {error && <div className="warning-message">⚠️ {error}</div>}

      {bill ? (
        <div className="bill-container">
          <div className="bill-header">
            <h2>Invoice #{bill.bill_number}</h2>
            <p className="bill-date">Date: {new Date(bill.created_at).toLocaleDateString()}</p>
          </div>

          <div className="bill-items">
            <h3>Items Ordered</h3>
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Qty</th>
                  <th>Unit Price</th>
                  <th>Subtotal</th>
                </tr>
              </thead>
              <tbody>
                {bill.items && bill.items.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.product_name}</td>
                    <td>{item.quantity}</td>
                    <td>${parseFloat(item.unit_price).toFixed(2)}</td>
                    <td>${parseFloat(item.subtotal).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="bill-summary">
            <div className="summary-row">
              <span>Subtotal:</span>
              <span>${parseFloat(bill.subtotal).toFixed(2)}</span>
            </div>
            <div className="summary-row">
              <span>Shipping:</span>
              <span>${parseFloat(bill.shipping_fee).toFixed(2)}</span>
            </div>
            <div className="summary-row">
              <span>Tax:</span>
              <span>${parseFloat(bill.tax_amount).toFixed(2)}</span>
            </div>
            <div className="summary-row total">
              <span>Total:</span>
              <span>${parseFloat(bill.total).toFixed(2)}</span>
            </div>
          </div>

          <div className="bill-actions">
            <button className="download-btn" onClick={handleDownloadBill}>
              Download Invoice
            </button>
          </div>
        </div>
      ) : (
        <div className="bill-placeholder">
          <p>📄 Your invoice will be generated shortly.</p>
          <p>Check your email for the invoice confirmation.</p>
        </div>
      )}

      <div className="order-actions">
        <button className="back-btn" onClick={handleBackToCart}>
          🛒 Back to Shopping
        </button>
      </div>
    </div>
  );
}

export default Order;
