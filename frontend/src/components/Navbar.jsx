import React, { useContext, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { FiMenu, FiX, FiShield } from 'react-icons/fi';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setMobileMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        <FiShield style={{ color: 'var(--primary-color)' }} />
        FoodSafe AI
      </Link>
      
      <button className="mobile-menu-btn" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
        {mobileMenuOpen ? <FiX /> : <FiMenu />}
      </button>

      <div className={`nav-links ${mobileMenuOpen ? 'mobile-active' : ''}`}>
        {user ? (
          <>
            <Link to="/dashboard" className="nav-link" onClick={() => setMobileMenuOpen(false)}>Dashboard</Link>
            <Link to="/scan" className="nav-link" onClick={() => setMobileMenuOpen(false)}>Scan Food</Link>
            <Link to="/history" className="nav-link" onClick={() => setMobileMenuOpen(false)}>History</Link>
            <button className="btn btn-secondary" onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" className="nav-link" onClick={() => setMobileMenuOpen(false)}>Login</Link>
            <Link to="/register" className="btn btn-primary" onClick={() => setMobileMenuOpen(false)}>Register</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
