import React, { useContext, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { FiCamera } from 'react-icons/fi';
import api from '../utils/api';

const Dashboard = () => {
  const { user } = useContext(AuthContext);
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchScans = async () => {
      try {
        const res = await api.get('/scans');
        setScans(res.data.data);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };
    fetchScans();
  }, []);

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--score-excellent)';
    if (score >= 60) return 'var(--score-good)';
    if (score >= 40) return 'var(--score-poor)';
    return 'var(--score-high-concern)';
  };

  const totalScans = scans.length;
  const avgScore = totalScans > 0 ? (scans.reduce((acc, curr) => acc + curr.score, 0) / totalScans).toFixed(0) : 0;
  const highConcern = scans.filter(s => s.score < 40).length;

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%' }}>
      <h2 style={{ fontSize: '2rem', marginBottom: '24px' }}>Welcome, {user?.name}</h2>

      <div className="glass-card mb-8 text-center" style={{ padding: '40px' }}>
        <h3 style={{ fontSize: '1.5rem', marginBottom: '16px' }}>Scan Your Food</h3>
        <p style={{ color: '#cbd5e1', marginBottom: '24px' }}>Get an AI visual food safety assessment instantly.</p>
        <Link to="/scan" className="btn btn-primary" style={{ padding: '16px 32px', fontSize: '1.2rem' }}>
          <FiCamera style={{ marginRight: '8px' }} /> Scan Food
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        <div className="glass-card text-center">
          <h4 style={{ color: '#cbd5e1' }}>Total Scans</h4>
          <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{totalScans}</p>
        </div>
        <div className="glass-card text-center">
          <h4 style={{ color: '#cbd5e1' }}>Avg Safety Score</h4>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: getScoreColor(avgScore) }}>{avgScore}</p>
        </div>
        <div className="glass-card text-center">
          <h4 style={{ color: '#cbd5e1' }}>High Concern</h4>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--score-high-concern)' }}>{highConcern}</p>
        </div>
      </div>

      <div className="glass-card">
        <div className="flex justify-between items-center mb-4">
          <h3 style={{ fontSize: '1.5rem' }}>Recent Scans</h3>
          <Link to="/history" style={{ color: 'var(--primary-color)' }}>View All</Link>
        </div>
        
        {loading ? (
          <p>Loading...</p>
        ) : scans.length === 0 ? (
          <p style={{ color: '#cbd5e1', textAlign: 'center', padding: '20px 0' }}>No scans yet. Start by scanning your food!</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--glass-border)', textAlign: 'left' }}>
                  <th style={{ padding: '12px 8px' }}>Food</th>
                  <th style={{ padding: '12px 8px' }}>Category</th>
                  <th style={{ padding: '12px 8px' }}>Score</th>
                  <th style={{ padding: '12px 8px' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {scans.slice(0, 5).map(scan => (
                  <tr key={scan._id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '12px 8px' }}>{scan.detectedFood}</td>
                    <td style={{ padding: '12px 8px' }}>{scan.category}</td>
                    <td style={{ padding: '12px 8px', color: getScoreColor(scan.score), fontWeight: 'bold' }}>
                      {scan.score}/100
                    </td>
                    <td style={{ padding: '12px 8px' }}>
                      <Link to={`/result/${scan._id}`} style={{ color: 'var(--primary-color)' }}>View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
