import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

const OfficerVerification = () => {
  const [officerId, setOfficerId] = useState('');
  const [state, setState] = useState('');
  const [district, setDistrict] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const res = await api.post('/officers/verify', { officerId, state, district });
      if (res.data.success) {
        setMessage(res.data.message);
        setTimeout(() => {
          window.location.href = '/dashboard'; 
        }, 2000);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Verification failed. Service unavailable.');
    }
    setLoading(false);
  };

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '600px', margin: '0 auto' }}>
      <div className="glass-card">
        <h2 className="text-center mb-4">Official Identity Verification</h2>
        <p className="text-center mb-6" style={{ color: '#cbd5e1', fontSize: '0.9rem' }}>
          Please enter your official credentials. These will be verified against the latest available official government data.
        </p>

        {error && <div className="text-error text-center mb-4 p-3" style={{ background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>{error}</div>}
        {message && <div className="text-center mb-4 p-3" style={{ color: 'var(--score-excellent)', background: 'rgba(34, 197, 94, 0.1)', borderRadius: '8px', fontWeight: 'bold' }}>{message}</div>}

        <form onSubmit={handleVerify}>
          <div className="form-group">
            <label>Official Officer ID</label>
            <input type="text" className="input-field" value={officerId} onChange={(e) => setOfficerId(e.target.value)} required placeholder="e.g. FDA-HYD-001" />
          </div>
          <div className="form-group">
            <label>State / Union Territory</label>
            <input type="text" className="input-field" value={state} onChange={(e) => setState(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>District</label>
            <input type="text" className="input-field" value={district} onChange={(e) => setDistrict(e.target.value)} required />
          </div>
          
          <button type="submit" className="btn btn-primary w-full mt-4" disabled={loading}>
            {loading ? 'Verifying with Official Source...' : 'Verify Identity'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default OfficerVerification;
