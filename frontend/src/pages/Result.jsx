import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { FiAlertTriangle, FiCheckCircle, FiInfo, FiActivity } from 'react-icons/fi';
import api from '../utils/api';

const Result = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Customer Rating State
  const [quality, setQuality] = useState('');
  const [taste, setTaste] = useState('');
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const res = await api.get(`/scans/${id}`);
        setResult(res.data.data);
        if (res.data.data.customerAssessment?.quality) {
          setQuality(res.data.data.customerAssessment.quality);
          setTaste(res.data.data.customerAssessment.taste);
          setComment(res.data.data.customerAssessment.comment);
        }
      } catch (err) {
        setError('Result not found or error loading result.');
      }
      setLoading(false);
    };
    fetchResult();
  }, [id]);

  const handleSubmitAssessment = async () => {
    if (!quality || !taste) {
      alert("Please select both Quality and Taste");
      return;
    }
    setIsSubmitting(true);
    try {
      const res = await api.post(`/scans/${id}/customer-assessment`, { quality, taste, comment });
      setResult(res.data.data);
    } catch (err) {
      alert(err.response?.data?.message || 'Error submitting assessment');
    }
    setIsSubmitting(false);
  };

  const getVisualScoreColor = (score) => {
    if (score >= 80) return 'var(--score-excellent)'; // Green
    if (score >= 60) return 'var(--score-good)';      // Yellow
    if (score >= 40) return 'var(--score-poor)';      // Orange
    return 'var(--score-high-concern)';               // Red
  };

  const getMicrobialRiskColor = (riskText) => {
    if (!riskText) return '#94a3b8'; // Gray
    if (riskText.includes('High Risk')) return 'var(--score-high-concern)'; // Red
    if (riskText.includes('Moderate Risk')) return 'var(--score-poor)';     // Orange
    if (riskText.includes('Low Risk')) return 'var(--score-excellent)';     // Green (never used by AI)
    return '#94a3b8'; // Gray (Unknown)
  };

  if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading result...</div>;
  if (error) return <div className="text-error text-center mt-4">{error}</div>;
  if (!result) return null;

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '900px', margin: '0 auto' }}>
      
      {/* ⚠️ FOOD SAFETY WARNING */}
      {result.isFood !== false && (
        <div style={{ marginBottom: '24px', padding: '16px', background: 'rgba(239, 68, 68, 0.15)', borderLeft: '6px solid var(--error-color)', borderRadius: '0 8px 8px 0', display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
          <FiAlertTriangle size={32} color="var(--error-color)" style={{ flexShrink: 0, marginTop: '4px' }} />
          <div>
            <h3 style={{ color: 'var(--error-color)', margin: '0 0 8px 0', fontSize: '1.2rem' }}>FOOD SAFETY WARNING</h3>
            <p style={{ margin: 0, color: '#f8fafc', lineHeight: '1.5' }}>
              This system provides a <strong>VISUAL QUALITY ANALYSIS</strong> only. A good appearance does <strong>NOT</strong> guarantee that the food is microbiologically safe. The camera cannot detect bacteria, viruses, pesticides, or toxins.
            </p>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center mb-6">
        <h2>Visual Analysis Result</h2>
        <span style={{ padding: '4px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '20px', fontSize: '0.9rem' }}>
          {new Date(result.createdAt).toLocaleDateString()}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '32px' }}>
        
        {/* Left Column - Image & Visual Quality */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
            <img src={`http://localhost:5000${result.image}`} alt="Food Scan" style={{ width: '100%', height: '300px', objectFit: 'cover' }} />
          </div>

          {result.isFood === false ? (
             <div className="glass-card text-center" style={{ border: '1px solid var(--error-color)', background: 'rgba(239, 68, 68, 0.1)' }}>
               <h3 style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', color: 'var(--error-color)', marginBottom: '16px' }}>
                 <FiAlertTriangle /> Food Not Detected
               </h3>
               <p style={{ fontSize: '1.1rem', lineHeight: '1.5', color: '#cbd5e1' }}>
                 {result.message || "Tomato not detected. Please upload a clear tomato image."}
               </p>
             </div>
          ) : (
            <>
              {/* VISUAL QUALITY SECTION */}
              <div className="glass-card" style={{ borderLeft: `4px solid ${getVisualScoreColor(result.qualityScore || 0)}` }}>
                <h3 style={{ marginBottom: '16px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px', color: 'var(--primary-color)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  📸 VISUAL QUALITY
                </h3>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
                  <div>
                    <span style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Food Name:</span>
                    <span style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>{result.detectedFood}</span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Visual Score:</span>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px', justifyContent: 'flex-end' }}>
                      <span style={{ fontSize: '2.5rem', fontWeight: 'bold', color: getVisualScoreColor(result.qualityScore || 0), lineHeight: '1' }}>
                        {result.qualityScore || 0}
                      </span>
                      <span style={{ color: '#94a3b8' }}>/100</span>
                    </div>
                  </div>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <span style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Visual Assessment:</span>
                  <span style={{ 
                    fontWeight: 'bold', 
                    fontSize: '1.1rem',
                    color: getVisualScoreColor(result.qualityScore || 0)
                  }}>
                    {result.visualAssessmentStatus || 'INSUFFICIENT EVIDENCE'}
                  </span>
                </div>
              </div>

              {/* VISIBLE SPOILAGE SECTION */}
              <div className="glass-card" style={{ borderLeft: '4px solid #f59e0b' }}>
                <h3 style={{ marginBottom: '16px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px', color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  🔎 VISIBLE SPOILAGE / RISK INDICATORS
                </h3>
                
                <div style={{ marginBottom: '16px' }}>
                  <span style={{ color: '#cbd5e1', display: 'block', marginBottom: '8px' }}>Defect Penalty Score:</span>
                  <span style={{ fontWeight: 'bold', fontSize: '1.2rem', color: result.defectScore > 0 ? 'var(--score-poor)' : 'var(--score-excellent)' }}>
                    -{result.defectScore || 0} pts
                  </span>
                </div>

                <div>
                  <span style={{ color: '#cbd5e1', display: 'block', marginBottom: '8px' }}>Detected Visible Issues:</span>
                  {result.visibleIssues && result.visibleIssues.length > 0 ? (
                    <ul style={{ paddingLeft: '20px', margin: 0, color: result.defectScore > 0 ? 'var(--score-high-concern)' : 'var(--score-excellent)' }}>
                      {result.visibleIssues.map((issue, idx) => (
                        <li key={idx} style={{ marginBottom: '6px' }}>{issue}</li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ color: 'var(--score-excellent)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <FiCheckCircle /> No obvious visible defect detected
                    </p>
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Right Column - Microbial Risk, Customer Input & Final Quality */}
        {result.isFood !== false && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            {/* MICROBIAL CONTAMINATION RISK SECTION */}
            <div className="glass-card" style={{ borderLeft: `4px solid ${getMicrobialRiskColor(result.microbialSafetyRisk)}`, background: 'rgba(0,0,0,0.3)' }}>
              <h3 style={{ marginBottom: '16px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px', color: '#e2e8f0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                🦠 MICROBIAL SAFETY RISK <span style={{ fontSize: '0.8rem', padding: '2px 8px', background: '#334155', borderRadius: '12px', marginLeft: 'auto' }}>ESTIMATED</span>
              </h3>
              
              <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '16px' }}>
                <FiActivity size={28} color={getMicrobialRiskColor(result.microbialSafetyRisk)} />
                <span style={{ 
                  fontWeight: 'bold', 
                  fontSize: '1.3rem',
                  color: getMicrobialRiskColor(result.microbialSafetyRisk)
                }}>
                  {result.microbialSafetyRisk || 'Unknown / Cannot Determine'}
                </span>
              </div>
              
              {result.microbialSafetyRisk?.includes('Unknown') && (
                <p style={{ color: '#cbd5e1', fontSize: '0.9rem', margin: 0, fontStyle: 'italic', background: 'rgba(255,255,255,0.05)', padding: '12px', borderRadius: '8px' }}>
                  Microbial contamination cannot be determined from an ordinary image. While the food appears visually fine, invisible pathogens could still be present.
                </p>
              )}
            </div>
            
            {/* FUTURE TECHNOLOGY SECTION */}
            <div className="glass-card" style={{ borderLeft: '4px solid #8b5cf6', background: 'rgba(139, 92, 246, 0.05)' }}>
              <h3 style={{ marginBottom: '12px', color: '#8b5cf6', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                🔬 FUTURE TECHNOLOGY INTEGRATION
              </h3>
              <p style={{ fontSize: '0.9rem', color: '#cbd5e1', margin: '0 0 12px 0', lineHeight: '1.5' }}>
                Actual bacterial detection requires specialized hardware. This architecture is prepared to integrate with future APIs for:
              </p>
              <ul style={{ fontSize: '0.85rem', color: '#94a3b8', margin: 0, paddingLeft: '20px', lineHeight: '1.6' }}>
                <li>Portable IoT Biosensors</li>
                <li>Hyperspectral / Multispectral Imaging</li>
                <li>Microbiological Laboratory Testing APIs</li>
                <li>Specialized Food Spectroscopy</li>
              </ul>
              {result.sensorData && (
                 <div style={{ marginTop: '12px', padding: '8px', background: 'rgba(139, 92, 246, 0.2)', borderRadius: '4px', fontSize: '0.85rem' }}>
                    Sensor Data Connected: {JSON.stringify(result.sensorData)}
                 </div>
              )}
            </div>

            {/* CUSTOMER ASSESSMENT SECTION */}
            <div className="glass-card">
              <h3 style={{ marginBottom: '16px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px', color: '#38bdf8' }}>
                Customer Assessment
              </h3>
              
              {!result.finalQualityScore ? (
                <>
                  <div style={{ marginBottom: '16px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', color: '#cbd5e1' }}>Overall Experience / Quality:</label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {['Excellent', 'Good', 'Average', 'Poor', 'Very Poor'].map(opt => (
                        <button 
                          key={opt}
                          className={`btn ${quality === opt ? 'btn-primary' : 'btn-secondary'}`}
                          onClick={() => setQuality(opt)}
                          style={{ padding: '6px 12px', fontSize: '0.9rem' }}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div style={{ marginBottom: '16px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', color: '#cbd5e1' }}>Taste (If eaten):</label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {['Excellent', 'Good', 'Average', 'Poor', 'Very Poor'].map(opt => (
                        <button 
                          key={opt}
                          className={`btn ${taste === opt ? 'btn-primary' : 'btn-secondary'}`}
                          onClick={() => setTaste(opt)}
                          style={{ padding: '6px 12px', fontSize: '0.9rem' }}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div style={{ marginBottom: '16px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', color: '#cbd5e1' }}>Comment:</label>
                    <textarea 
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Optional customer comment..."
                      style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', color: 'white', minHeight: '80px' }}
                    />
                  </div>
                  
                  <button 
                    className="btn btn-primary" 
                    style={{ width: '100%' }}
                    onClick={handleSubmitAssessment}
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Assessment'}
                  </button>
                </>
              ) : (
                <div style={{ display: 'grid', gap: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                    <span style={{ color: '#cbd5e1' }}>Experience Quality:</span>
                    <span style={{ fontWeight: 'bold' }}>{result.customerAssessment?.quality}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                    <span style={{ color: '#cbd5e1' }}>Taste:</span>
                    <span style={{ fontWeight: 'bold' }}>{result.customerAssessment?.taste}</span>
                  </div>
                  {result.customerAssessment?.comment && (
                    <div style={{ padding: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                      <span style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Comment:</span>
                      <span style={{ fontStyle: 'italic' }}>"{result.customerAssessment.comment}"</span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* FINAL SCORE SECTION */}
            <div className="glass-card" style={{ borderLeft: '4px solid #3b82f6' }}>
              <h3 style={{ marginBottom: '16px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px', color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '8px' }}>
                🏆 COMPOSITE QUALITY SCORE
              </h3>
              
              <div style={{ display: 'grid', gap: '8px', marginBottom: '16px', fontSize: '0.9rem', color: '#cbd5e1', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Visual Score Weight:</span> <span>40%</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Defect Impact Weight:</span> <span>30%</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Customer Input Weight:</span> <span>30%</span>
                </div>
              </div>
              
              <div style={{ margin: '24px 0', textAlign: 'center' }}>
                <span style={{ color: '#94a3b8', display: 'block', marginBottom: '8px', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  NOT A MICROBIOLOGICAL SAFETY SCORE
                </span>
                {result.finalQualityScore ? (
                  <span style={{ fontSize: '4rem', fontWeight: 'bold', color: getVisualScoreColor(result.finalQualityScore), textShadow: '0 2px 10px rgba(0,0,0,0.3)' }}>
                    {result.finalQualityScore.toFixed(1)} <span style={{ fontSize: '1.5rem', color: '#64748b' }}>/100</span>
                  </span>
                ) : (
                  <span style={{ color: '#fbbf24', fontStyle: 'italic' }}>Waiting for customer assessment</span>
                )}
              </div>
              
              {result.assessmentDifference && (
                <div style={{ marginTop: '16px', padding: '16px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px' }}>
                  <p style={{ margin: 0, fontStyle: 'italic', color: '#e2e8f0', lineHeight: '1.5' }}>
                    {result.assessmentDifference}
                  </p>
                </div>
              )}
            </div>

            {/* HOW TO EAT (CONDITIONAL) */}
            {result.howToEat && result.howToEat.length > 0 && (
              <div className="glass-card" style={{ borderLeft: '4px solid #10b981' }}>
                <h3 style={{ marginBottom: '16px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px', color: '#10b981' }}>
                  🍴 Culinary Suggestions
                </h3>
                <ul style={{ paddingLeft: '20px', margin: 0, color: '#e2e8f0' }}>
                  {result.howToEat.map((guide, idx) => (
                    <li key={idx} style={{ marginBottom: '8px' }}>{guide}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* LIMITATIONS / DISCLAIMER */}
            <div className="glass-card" style={{ border: '1px solid var(--glass-border)', background: 'rgba(255, 255, 255, 0.02)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#94a3b8', marginBottom: '12px', fontSize: '0.9rem', textTransform: 'uppercase' }}>
                <FiInfo /> System Limitations
              </h4>
              <p style={{ fontSize: '0.85rem', lineHeight: '1.6', margin: 0, color: '#94a3b8' }}>
                {result.limitations || "This AI performs visual food-quality analysis. It cannot directly detect bacteria, viruses, toxins, pesticides, or other microscopic/chemical contaminants. Visual appearance does not guarantee microbiological safety."}
              </p>
            </div>

          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '40px', flexWrap: 'wrap' }}>
        <Link to="/scan" className="btn btn-primary">Scan Another Tomato</Link>
        <Link to="/history" className="btn btn-secondary">View Scan History</Link>
        <Link to="/dashboard" className="btn btn-secondary" style={{ border: 'none', textDecoration: 'underline' }}>Back to Dashboard</Link>
      </div>

    </div>
  );
};

export default Result;
