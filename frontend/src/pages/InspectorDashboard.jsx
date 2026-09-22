import React, { useContext, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { FiClipboard, FiSearch, FiList, FiAlertCircle } from 'react-icons/fi';
import api from '../utils/api';

const InspectorDashboard = () => {
  const { user } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/officers/dashboard-stats');
        setStats(res.data.data);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };
    fetchStats();
  }, []);

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
            <h2 style={{ fontSize: '2.5rem', color: 'var(--accent-color)', marginBottom: '8px' }}>Inspector Dashboard</h2>
            <p style={{ color: '#cbd5e1' }}>Welcome, Officer {user?.name}</p>
            {user?.officerId && <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Officer ID: {user.officerId}</p>}
        </div>
        <div style={{ padding: '12px 24px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', borderLeft: '4px solid var(--warning-color)' }}>
            <p style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>Status: <strong style={{ color: 'var(--warning-color)' }}>DEMO / TEST DATA</strong></p>
        </div>
      </div>

      {loading ? (
        <p className="text-center">Loading dashboard...</p>
      ) : (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px', marginBottom: '32px' }}>
            <div className="glass-card text-center" style={{ padding: '24px' }}>
              <h4 style={{ color: '#cbd5e1' }}>Total Inspections</h4>
              <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats?.totalInspections || 0}</p>
            </div>
            <div className="glass-card text-center" style={{ padding: '24px' }}>
              <h4 style={{ color: '#cbd5e1' }}>Upcoming Inspections</h4>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--score-good)' }}>{stats?.upcoming || 0}</p>
            </div>
            <div className="glass-card text-center" style={{ padding: '24px' }}>
              <h4 style={{ color: '#cbd5e1' }}>Due Today</h4>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--warning-color)' }}>{stats?.dueToday || 0}</p>
            </div>
            <div className="glass-card text-center" style={{ padding: '24px' }}>
              <h4 style={{ color: '#cbd5e1' }}>Overdue Inspections</h4>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--score-high-concern)' }}>{stats?.overdue || 0}</p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginBottom: '32px' }}>
            <div className="glass-card text-center" style={{ padding: '32px', borderTop: '3px solid var(--primary-color)' }}>
              <FiClipboard size={48} color="var(--primary-color)" style={{ margin: '0 auto 16px' }} />
              <h3 style={{ fontSize: '1.5rem', marginBottom: '12px' }}>New Inspection</h3>
              <p style={{ color: '#cbd5e1', marginBottom: '24px', fontSize: '0.95rem' }}>Submit a comprehensive inspection report for a restaurant.</p>
              <Link to="/inspect" className="btn btn-primary" style={{ padding: '12px 24px', display: 'block' }}>
                Start Inspection
              </Link>
            </div>
            <div className="glass-card text-center" style={{ padding: '32px', borderTop: '3px solid var(--secondary-color)' }}>
              <FiSearch size={48} color="var(--secondary-color)" style={{ margin: '0 auto 16px' }} />
              <h3 style={{ fontSize: '1.5rem', marginBottom: '12px' }}>Restaurant Search</h3>
              <p style={{ color: '#cbd5e1', marginBottom: '24px', fontSize: '0.95rem' }}>Look up previous inspection records for any restaurant.</p>
              <Link to="/restaurants/search" className="btn btn-secondary" style={{ padding: '12px 24px', display: 'block' }}>
                Search Database
              </Link>
            </div>
          </div>
          
          <div className="glass-card">
            <h3 style={{ fontSize: '1.5rem', marginBottom: '16px' }}>Recent Inspections</h3>
            {(!stats?.recentInspections || stats.recentInspections.length === 0) ? (
              <p style={{ color: '#cbd5e1', textAlign: 'center', padding: '20px 0' }}>No inspection records found.</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--glass-border)', textAlign: 'left' }}>
                      <th style={{ padding: '12px 8px' }}>Date</th>
                      <th style={{ padding: '12px 8px' }}>Food Status</th>
                      <th style={{ padding: '12px 8px' }}>Hygiene Rating</th>
                      <th style={{ padding: '12px 8px' }}>Next Due</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.recentInspections.map(insp => (
                      <tr key={insp._id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '12px 8px' }}>{new Date(insp.date).toLocaleDateString()}</td>
                        <td style={{ padding: '12px 8px' }}>{insp.foodStatus}</td>
                        <td style={{ padding: '12px 8px', fontWeight: 'bold' }}>{insp.hygieneRating}/5</td>
                        <td style={{ padding: '12px 8px' }}>{insp.nextInspectionDate ? new Date(insp.nextInspectionDate).toLocaleDateString() : 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default InspectorDashboard;
