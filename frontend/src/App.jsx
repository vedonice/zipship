import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from './store';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Payment from './pages/Payment';
import Order from './pages/Order';
import './App.css';

function App() {
  useEffect(() => {
    console.log('✅ App component mounted successfully');
  }, []);

  return (
    <Provider store={store}>
      <Router>
        <div className="app">
          <nav className="navbar">
            <div className="nav-container">
              <Link to="/" className="nav-logo">
                🛒 ZipShip
              </Link>
              <ul className="nav-menu">
                <li>
                  <Link to="/" className="nav-link">
                    Cart
                  </Link>
                </li>
              </ul>
            </div>
          </nav>

          <main className="main-content">
            <Routes>
              <Route path="/" element={<Cart />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="/payment" element={<Payment />} />
              <Route path="/order" element={<Order />} />
            </Routes>
          </main>

          <footer className="footer">
            <p>&copy; 2026 ZipShip - Express Shopping Cart. All rights reserved.</p>
          </footer>
        </div>
      </Router>
    </Provider>
  );
}

export default App;
