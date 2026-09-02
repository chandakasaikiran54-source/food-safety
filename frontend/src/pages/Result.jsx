import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { FiCheckCircle, FiAlertTriangle, FiInfo } from 'react-icons/fi';
import api from '../utils/api';

const Result = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const res = await api.get(`/scans/${id}`);
        setResult(res.data.data);
      } catch (err) {
        setError('Result not found or error loading result.');
      }
      setLoading(false);
    };
    fetchResult();
  }, [id]);

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--score-excellent)';
    if (score >= 60) return 'var(--score-good)';
    if (score >= 40) return 'var(--score-poor)';
    return 'var(--score-high-concern)';
  };

  if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading result...</div>;
  if (error) return <div className="text-error text-center mt-4">{error}</div>;
  if (!result) return null;

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '900px', margin: '0 auto' }}>
      <div className="flex justify-between items-center mb-6">
        <h2>Analysis Result</h2>
        <span style={{ padding: '4px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '20px', fontSize: '0.9rem' }}>
          {new Date(result.createdAt).toLocaleDateString()}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '32px' }}>
        
        {/* Left Column - Image & Score */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
            <img src={`http://localhost:5000${result.image}`} alt="Food Scan" style={{ width: '100%', height: '300px', objectFit: 'cover' }} />
            {result.isFood !== false && (
              <div style={{ padding: '20px' }}>
                <p style={{ color: '#cbd5e1', fontSize: '0.9rem', marginBottom: '4px' }}>Detected Food</p>
                <h3 style={{ fontSize: '1.5rem', marginBottom: '8px' }}>{result.detectedFood}</h3>
                <span style={{ display: 'inline-block', padding: '4px 12px', background: 'var(--primary-color)', borderRadius: '20px', fontSize: '0.9rem', fontWeight: 'bold' }}>
                  {result.category}
                </span>
                <span style={{ marginLeft: '12px', fontSize: '0.9rem', color: '#cbd5e1' }}>
                  Confidence: {Math.round(result.confidence * 100)}%
                </span>
              </div>
            )}
          </div>

          {result.isFood !== false && (
            <div className="glass-card text-center text-white" style={{ background: `linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, ${getScoreColor(result.score)}40 100%)`, borderLeft: `6px solid ${getScoreColor(result.score)}` }}>
              <p style={{ fontSize: '1.1rem', marginBottom: '8px' }}>AI Visual Food Safety Score</p>
              <h1 style={{ fontSize: '4rem', margin: '0', color: getScoreColor(result.score), textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>
                {result.score}<span style={{ fontSize: '1.5rem', color: '#cbd5e1' }}>/100</span>
              </h1>
              <p style={{ fontSize: '1.2rem', fontWeight: 'bold', marginTop: '8px', letterSpacing: '1px' }}>{result.status.toUpperCase()}</p>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '12px', fontStyle: 'italic' }}>Visual assessment only — not a laboratory test.</p>
            </div>
          )}
        </div>

        {/* Right Column - Analysis */}
        {result.isFood === false ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="glass-card text-center" style={{ border: '1px solid var(--error-color)', background: 'rgba(239, 68, 68, 0.1)' }}>
              <h3 style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', color: 'var(--error-color)', marginBottom: '16px' }}>
                <FiAlertTriangle /> Food Not Detected
              </h3>
              <p style={{ fontSize: '1.1rem', lineHeight: '1.5', color: '#cbd5e1' }}>
                {result.message || "The uploaded image does not appear to contain food."}
              </p>
              <p style={{ marginTop: '16px', color: '#94a3b8' }}>
                Please upload a clear image of food.
              </p>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            <div className="glass-card">
              <h3 style={{ marginBottom: '16px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px' }}>
                Visual Assessment
              </h3>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {result.visualIndicators.map((indicator, idx) => {
                  const isConcern = indicator.toLowerCase().includes('concern') || indicator.toLowerCase().includes('attention') || indicator.toLowerCase().includes('excessive');
                  return (
                    <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px', padding: '12px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                      {isConcern ? <FiAlertTriangle color="var(--warning-color)" size={20} /> : <FiCheckCircle color="var(--score-excellent)" size={20} />}
                      <span>{indicator}</span>
                    </li>
                  );
                })}
              </ul>
            </div>

            <div className="glass-card">
              <h3 style={{ marginBottom: '16px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px' }}>
                Safety Recommendation
              </h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', marginBottom: '8px' }}>
                    <span style={{ color: 'var(--primary-color)' }}>•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="glass-card" style={{ border: '1px solid var(--error-color)', background: 'rgba(239, 68, 68, 0.1)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--error-color)', marginBottom: '16px', fontSize: '1.1rem' }}>
                <FiAlertTriangle /> IMPORTANT NOTICE
              </h4>
              <p style={{ fontSize: '0.9rem', lineHeight: '1.5', marginBottom: '12px' }}>
                FoodSafe AI provides an AI-based visual assessment of food images. The assessment is limited to characteristics that may be observable in the image and is not a laboratory test.
              </p>
              <p style={{ fontSize: '0.9rem', lineHeight: '1.5', marginBottom: '12px' }}>
                Invisible or microscopic hazards — including bacteria, viruses, pesticide residues, chemical contaminants, veterinary drug residues, toxins, and other substances that cannot be reliably identified from appearance alone — cannot be confirmed through ordinary image analysis.
              </p>
              <p style={{ fontSize: '0.9rem', lineHeight: '1.5', marginBottom: '12px' }}>
                A food image that appears normal does not prove that the food is free from contamination. Where food safety is in doubt, appropriate food-safety procedures and laboratory testing should be used for confirmation.
              </p>
              <p style={{ fontSize: '0.9rem', lineHeight: '1.5', marginBottom: '16px' }}>
                The FoodSafe AI score is a visual assessment and must not be interpreted as a certified food-safety result.
              </p>
              
              <hr style={{ borderColor: 'rgba(255,255,255,0.1)', margin: '16px 0' }} />
              
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '0.85rem', marginBottom: '16px' }}>
                <div style={{ flex: '1 1 45%' }}>
                  <strong style={{ color: '#cbd5e1', display: 'block', marginBottom: '8px' }}>What the AI can assess:</strong>
                  <ul style={{ listStyleType: 'disc', paddingLeft: '20px', margin: 0, color: '#94a3b8' }}>
                    <li>Visible characteristics</li>
                    <li>Visual appearance</li>
                    <li>Possible visible concerns</li>
                  </ul>
                </div>
                <div style={{ flex: '1 1 45%' }}>
                  <strong style={{ color: '#cbd5e1', display: 'block', marginBottom: '8px' }}>What it cannot confirm:</strong>
                  <ul style={{ listStyleType: 'disc', paddingLeft: '20px', margin: 0, color: '#94a3b8' }}>
                    <li>Bacteria/viruses</li>
                    <li>Pesticide residues</li>
                    <li>Chemical contaminants/adulterants</li>
                    <li>Toxins and other invisible hazards</li>
                  </ul>
                </div>
              </div>

              <hr style={{ borderColor: 'rgba(255,255,255,0.1)', margin: '16px 0' }} />
              
              <div style={{ fontSize: '0.85rem' }}>
                <strong style={{ color: '#cbd5e1', display: 'block', marginBottom: '8px' }}>Sources:</strong>
                <a href="https://www.fssai.gov.in/" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary-color)', textDecoration: 'underline', marginRight: '16px' }}>
                  FSSAI — Food Safety and Standards Authority of India
                </a>
                <a href="https://www.fda.gov/" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary-color)', textDecoration: 'underline', display: 'inline-block' }}>
                  FDA — U.S. Food and Drug Administration
                </a>
              </div>
            </div>

          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '40px', flexWrap: 'wrap' }}>
        <Link to="/scan" className="btn btn-primary">Scan Another Food</Link>
        <Link to="/history" className="btn btn-secondary">View Scan History</Link>
        <Link to="/dashboard" className="btn btn-secondary" style={{ border: 'none', textDecoration: 'underline' }}>Back to Dashboard</Link>
      </div>

    </div>
  );
};

export default Result;
