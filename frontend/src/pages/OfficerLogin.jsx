import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { FiShield } from 'react-icons/fi';

const OfficerLogin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const user = await login(email, password);
      if (user) {
        if (user.role === 'officer' || user.role === 'admin') {
          navigate('/inspector-dashboard');
        } else {
          // Log them out because they logged into the wrong portal
          logout();
          setError('Access Denied. You do not have Food Inspector privileges.');
        }
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      if (!err.response) {
        setError('Database is temporarily unavailable. Please try again.');
      } else {
        setError(err.response?.data?.message || 'Login failed');
      }
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: '400px', borderTop: '4px solid var(--accent-color)' }}>
        <div style={{ textAlign: 'center', marginBottom: '16px' }}>
            <FiShield size={48} color="var(--accent-color)" />
        </div>
        <h2 className="text-center mb-4" style={{ color: 'var(--accent-color)' }}>Food Inspector Login</h2>
        <p className="text-center mb-6" style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>Authorized personnel only</p>
        
        {error && <div className="text-error mb-4 text-center">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Official Officer ID / Email</label>
            <input 
              type="text" 
              className="input-field" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              required 
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              className="input-field" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
            />
          </div>
          <button type="submit" className="btn btn-secondary w-full mt-4" style={{ borderColor: 'var(--accent-color)', color: 'var(--accent-color)' }}>Access Secure Portal</button>
        </form>
        <p className="text-center mt-6 text-sm">
          <Link to="/login" style={{ color: '#cbd5e1' }}>&larr; Return to User Login</Link>
        </p>
      </div>
    </div>
  );
};

export default OfficerLogin;
