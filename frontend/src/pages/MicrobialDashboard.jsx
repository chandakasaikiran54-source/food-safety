import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import { FiDatabase, FiAlertTriangle, FiCheck, FiX, FiActivity } from 'react-icons/fi';

const MicrobialDashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await api.get('/microbial/stats');
                if (res.data.success) {
                    setStats(res.data.data);
                }
            } catch (err) {
                setError('Failed to load dashboard statistics.');
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    if (loading) return <div className="text-center" style={{ marginTop: '100px' }}>Loading dashboard...</div>;
    if (error) return <div className="text-error text-center" style={{ marginTop: '100px' }}>{error}</div>;
    if (!stats) return null;

    return (
        <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '1200px', margin: '0 auto' }}>
            <div className="text-center mb-8">
                <h2>AI vs LAB DASHBOARD</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Microscopic Bacterial Detection Validation</p>
            </div>

            {/* Validation Banner */}
            <div className="glass-card mb-8" style={{ padding: '24px', borderLeft: '6px solid var(--warning-color)', display: 'flex', gap: '16px', alignItems: 'center' }}>
                <FiAlertTriangle size={32} color="var(--warning-color)" />
                <div>
                    <h3 style={{ margin: '0 0 4px 0', color: 'var(--warning-color)' }}>Microbial AI model is not currently validated.</h3>
                    <p style={{ margin: 0, color: 'var(--text-secondary)' }}>Metrics below are placeholders until sufficient laboratory ground-truth data is collected to train the microscopic AI.</p>
                </div>
            </div>

            {/* Global Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px', marginBottom: '32px' }}>
                <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
                    <FiDatabase size={32} color="var(--primary-color)" style={{ margin: '0 auto 16px auto' }} />
                    <h4 style={{ color: 'var(--text-secondary)' }}>TOTAL SAMPLES</h4>
                    <div style={{ fontSize: '36px', fontWeight: 'bold' }}>{stats.totalSamples}</div>
                </div>
                <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
                    <FiActivity size={32} color="#8b5cf6" style={{ margin: '0 auto 16px auto' }} />
                    <h4 style={{ color: 'var(--text-secondary)' }}>LAB VERIFIED</h4>
                    <div style={{ fontSize: '36px', fontWeight: 'bold' }}>{stats.labVerifiedCount}</div>
                </div>
                <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
                    <FiAlertTriangle size={32} color="var(--warning-color)" style={{ margin: '0 auto 16px auto' }} />
                    <h4 style={{ color: 'var(--text-secondary)' }}>INCONCLUSIVE / NO MODEL</h4>
                    <div style={{ fontSize: '36px', fontWeight: 'bold' }}>{stats.aiInconclusive}</div>
                </div>
            </div>

            {/* AI vs LAB Comparison */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px', marginBottom: '32px' }}>
                <div className="glass-card" style={{ padding: '24px' }}>
                    <h3 style={{ marginBottom: '24px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '12px' }}>AI PREDICTIONS</h3>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><FiX color="var(--error-color)"/> Positive (Bacteria Detected)</span>
                        <strong>{stats.aiPositive}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><FiCheck color="var(--success-color)"/> Negative (No Bacteria)</span>
                        <strong>{stats.aiNegative}</strong>
                    </div>
                </div>

                <div className="glass-card" style={{ padding: '24px' }}>
                    <h3 style={{ marginBottom: '24px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '12px' }}>LABORATORY GROUND TRUTH</h3>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><FiX color="var(--error-color)"/> Lab Positive</span>
                        <strong>{stats.labPositive}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><FiCheck color="var(--success-color)"/> Lab Negative</span>
                        <strong>{stats.labNegative}</strong>
                    </div>
                </div>
            </div>

            {/* Metrics Placeholder */}
            <div className="glass-card" style={{ padding: '32px' }}>
                <h3 style={{ marginBottom: '24px' }}>VALIDATION METRICS</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px', filter: 'blur(2px)', opacity: 0.7 }}>
                    {['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Sensitivity', 'Specificity'].map(metric => (
                        <div key={metric} style={{ background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                            <div style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>{metric}</div>
                            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>--%</div>
                        </div>
                    ))}
                </div>
                <p style={{ textAlign: 'center', marginTop: '24px', color: 'var(--warning-color)', fontWeight: 'bold' }}>
                    Metrics will be displayed here once laboratory-validated test data exists.
                </p>
            </div>
        </div>
    );
};

export default MicrobialDashboard;
