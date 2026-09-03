import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';

const ComplaintForm = () => {
  const [searchParams] = useSearchParams();
  const restaurantId = searchParams.get('restaurantId');
  const restaurantName = searchParams.get('restaurantName');
  
  const [issueCategory, setIssueCategory] = useState('Poor Hygiene');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!restaurantId) return setError("No restaurant selected.");
    
    setLoading(true);
    setError('');
    
    try {
      const res = await api.post('/complaints', { restaurantId, issueCategory, description });
      if (res.data.success) {
        setSuccessMsg(`Complaint submitted successfully. ID: ${res.data.data.complaintId}`);
        setTimeout(() => {
          navigate(-1);
        }, 3000);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to submit complaint.');
    }
    setLoading(false);
  };

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '700px', margin: '0 auto' }}>
      <div className="glass-card">
        <h2 className="text-center mb-2" style={{ color: 'var(--warning-color)' }}>Report Food Safety Concern</h2>
        <p className="text-center mb-6" style={{ color: '#cbd5e1' }}>
          For: <strong>{restaurantName || 'Selected Restaurant'}</strong>
        </p>

        {error && <div className="text-error text-center mb-4 p-3" style={{ background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>{error}</div>}
        {successMsg && <div className="text-center mb-4 p-3" style={{ color: 'var(--score-excellent)', background: 'rgba(34, 197, 94, 0.1)', borderRadius: '8px', fontWeight: 'bold' }}>{successMsg}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Issue Category</label>
            <select className="input-field" value={issueCategory} onChange={(e) => setIssueCategory(e.target.value)}>
              <option value="Poor Hygiene">Poor Hygiene</option>
              <option value="Suspected Spoiled Food">Suspected Spoiled Food</option>
              <option value="Suspected Adulteration">Suspected Adulteration</option>
              <option value="Insects/Pests">Insects/Pests</option>
              <option value="Poor Storage">Poor Storage</option>
              <option value="Unsafe Kitchen">Unsafe Kitchen</option>
              <option value="Other">Other</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Description of Issue</label>
            <textarea 
              className="input-field" 
              rows="5" 
              value={description} 
              onChange={(e) => setDescription(e.target.value)} 
              required 
              placeholder="Please describe the food safety issue in detail..."
            ></textarea>
          </div>

          <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '16px' }}>
            Note: This complaint is submitted through this platform for internal review. It is not an official submission to FSSAI. If this is a severe public health emergency, please contact local authorities directly.
          </p>

          <button type="submit" className="btn btn-primary w-full" disabled={loading} style={{ background: 'var(--warning-color)', color: '#000' }}>
            {loading ? 'Submitting...' : 'Submit Official Concern'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ComplaintForm;
