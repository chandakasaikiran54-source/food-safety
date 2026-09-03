import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const RestaurantSearch = () => {
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(`/restaurants/history?name=${encodeURIComponent(name)}&location=${encodeURIComponent(location)}`);
  };

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '600px', margin: '0 auto' }}>
      <div className="glass-card">
        <h2 className="text-center mb-6">Check Restaurant</h2>
        <p className="text-center mb-6" style={{ color: '#cbd5e1' }}>Search by name and location to view inspection history.</p>
        
        <form onSubmit={handleSearch}>
          <div className="form-group">
            <label>Restaurant Name</label>
            <input 
              type="text" 
              className="input-field" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              required 
              placeholder="e.g. ABC Restaurant"
            />
          </div>
          <div className="form-group">
            <label>Location</label>
            <input 
              type="text" 
              className="input-field" 
              value={location} 
              onChange={(e) => setLocation(e.target.value)} 
              required 
              placeholder="e.g. Hyderabad"
            />
          </div>
          <button type="submit" className="btn btn-primary w-full mt-4">
            Search
          </button>
        </form>
      </div>
    </div>
  );
};

export default RestaurantSearch;
