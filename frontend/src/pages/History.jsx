import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiTrash2, FiSearch } from 'react-icons/fi';
import api from '../utils/api';

const History = () => {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('All');

  useEffect(() => {
    fetchScans();
  }, []);

  const fetchScans = async () => {
    try {
      const res = await api.get('/scans');
      setScans(res.data.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this scan?')) {
      try {
        await api.delete(`/scans/${id}`);
        setScans(scans.filter(scan => scan._id !== id));
      } catch (err) {
        console.error(err);
      }
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--score-excellent)';
    if (score >= 60) return 'var(--score-good)';
    if (score >= 40) return 'var(--score-poor)';
    return 'var(--score-high-concern)';
  };

  const filteredScans = scans.filter(scan => {
    const matchesSearch = scan.detectedFood.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'All' || scan.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '1000px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '24px' }}>Scan History</h2>

      <div className="glass-card mb-8" style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
        <div style={{ flex: '1', minWidth: '250px', position: 'relative' }}>
          <FiSearch style={{ position: 'absolute', top: '14px', left: '16px', color: '#cbd5e1' }} />
          <input 
            type="text" 
            placeholder="Search by food name..." 
            className="input-field" 
            style={{ paddingLeft: '40px', margin: 0 }}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div style={{ minWidth: '200px' }}>
          <select 
            className="input-field" 
            style={{ margin: 0 }}
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
          >
            <option value="All">All Categories</option>
            <option value="Cooked Food">Cooked Food</option>
            <option value="Fried Food">Fried Food</option>
            <option value="Raw / Not Cooked Food">Raw / Not Cooked Food</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p className="text-center">Loading history...</p>
      ) : filteredScans.length === 0 ? (
        <div className="glass-card text-center">
          <p style={{ color: '#cbd5e1', marginBottom: '16px' }}>No scans found.</p>
          <Link to="/scan" className="btn btn-primary">Scan Food Now</Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {filteredScans.map(scan => (
            <div key={scan._id} className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', padding: '16px 24px' }}>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1, minWidth: '250px' }}>
                <div style={{ width: '60px', height: '60px', borderRadius: '8px', overflow: 'hidden', flexShrink: 0 }}>
                  <img src={`http://localhost:5000${scan.image}`} alt={scan.detectedFood} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                </div>
                <div>
                  <h4 style={{ fontSize: '1.1rem', marginBottom: '4px' }}>{scan.detectedFood}</h4>
                  <p style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{new Date(scan.createdAt).toLocaleDateString()}</p>
                </div>
              </div>

              <div style={{ flex: 1, minWidth: '150px' }}>
                <span style={{ padding: '4px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '20px', fontSize: '0.85rem' }}>
                  {scan.isFood === false ? 'Not Food' : scan.category}
                </span>
              </div>

              <div style={{ flex: 1, minWidth: '100px', textAlign: 'center' }}>
                <div style={{ display: 'inline-flex', flexDirection: 'column' }}>
                  {scan.isFood !== false ? (
                    <>
                      <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: getScoreColor(scan.score) }}>{scan.score}/100</span>
                      <span style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>{scan.status}</span>
                    </>
                  ) : (
                    <span style={{ fontSize: '1rem', color: 'var(--error-color)', fontWeight: 'bold' }}>N/A</span>
                  )}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px' }}>
                <Link to={`/result/${scan._id}`} className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '0.9rem' }}>Details</Link>
                <button 
                  onClick={() => handleDelete(scan._id)}
                  style={{ background: 'none', border: 'none', color: 'var(--error-color)', cursor: 'pointer', padding: '8px' }}
                >
                  <FiTrash2 size={20} />
                </button>
              </div>

            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
