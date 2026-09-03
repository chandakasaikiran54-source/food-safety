import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

const InspectionForm = () => {
  const [formData, setFormData] = useState({
    restaurantName: '',
    restaurantLocation: '',
    foodStatus: 'Safe',
    hygieneRating: 5,
    rawMaterialStatus: 'Good',
    kitchenCleanliness: 'Clean',
    overallRating: 5,
    remarks: '',
    date: new Date().toISOString().split('T')[0],
    nextInspectionDate: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await api.post('/restaurants/inspect', formData);
      if (res.data.success) {
        navigate(`/restaurants/history?name=${encodeURIComponent(formData.restaurantName)}&location=${encodeURIComponent(formData.restaurantLocation)}`);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Error submitting inspection');
    }
    setLoading(false);
  };

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '800px', margin: '0 auto' }}>
      <div className="glass-card">
        <h2 className="text-center mb-6">Submit Inspection Report</h2>
        {error && <div className="text-error text-center mb-4">{error}</div>}
        
        <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          
          <div className="form-group" style={{ gridColumn: '1 / -1' }}>
            <label>Restaurant Name</label>
            <input type="text" name="restaurantName" className="input-field" value={formData.restaurantName} onChange={handleChange} required />
          </div>

          <div className="form-group" style={{ gridColumn: '1 / -1' }}>
            <label>Location</label>
            <input type="text" name="restaurantLocation" className="input-field" value={formData.restaurantLocation} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label>Inspection Date</label>
            <input type="date" name="date" className="input-field" value={formData.date} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label>Next Inspection Due (Optional)</label>
            <input type="date" name="nextInspectionDate" className="input-field" value={formData.nextInspectionDate} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label>Food Status</label>
            <select name="foodStatus" className="input-field" value={formData.foodStatus} onChange={handleChange}>
              <option value="Safe">Safe</option>
              <option value="Needs Further Verification">Needs Further Verification</option>
              <option value="Unsafe">Unsafe</option>
            </select>
          </div>

          <div className="form-group">
            <label>Hygiene Rating (1-5)</label>
            <input type="number" name="hygieneRating" className="input-field" min="1" max="5" value={formData.hygieneRating} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label>Raw Materials Status</label>
            <select name="rawMaterialStatus" className="input-field" value={formData.rawMaterialStatus} onChange={handleChange}>
              <option value="Good">Good</option>
              <option value="Acceptable">Acceptable</option>
              <option value="Poor">Poor</option>
            </select>
          </div>

          <div className="form-group">
            <label>Kitchen Cleanliness</label>
            <select name="kitchenCleanliness" className="input-field" value={formData.kitchenCleanliness} onChange={handleChange}>
              <option value="Clean">Clean</option>
              <option value="Not Clean">Not Clean</option>
            </select>
          </div>

          <div className="form-group" style={{ gridColumn: '1 / -1' }}>
            <label>Overall Rating (1-5)</label>
            <input type="number" name="overallRating" className="input-field" min="1" max="5" step="0.1" value={formData.overallRating} onChange={handleChange} required />
          </div>

          <div className="form-group" style={{ gridColumn: '1 / -1' }}>
            <label>Remarks</label>
            <textarea name="remarks" className="input-field" rows="4" value={formData.remarks} onChange={handleChange} placeholder="Any additional comments..."></textarea>
          </div>

          <button type="submit" className="btn btn-primary" style={{ gridColumn: '1 / -1' }} disabled={loading}>
            {loading ? 'Submitting...' : 'Submit Inspection'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default InspectionForm;
