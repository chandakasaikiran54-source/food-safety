import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiAlertTriangle, FiCheckCircle, FiInfo } from 'react-icons/fi';
import api from '../utils/api';

const RawFoodResult = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [imageSize, setImageSize] = useState({ width: 1, height: 1 });
  
  // Customer Rating State
  const [foodQualityRating, setFoodQualityRating] = useState(0);
  const [tasteRating, setTasteRating] = useState(0);
  const [qualityComment, setQualityComment] = useState('');
  const [tasteComment, setTasteComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [finalAssessment, setFinalAssessment] = useState(null);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const res = await api.get(`/raw-food/${id}`);
        if (res.data.success) {
          setResult(res.data.data);
        } else {
          setError('Failed to fetch assessment results.');
        }
      } catch (err) {
        setError(err.response?.data?.message || 'Error fetching assessment details.');
      } finally {
        setLoading(false);
      }
    };

    fetchResult();
  }, [id]);

  if (loading) {
    return <div className="text-center" style={{ marginTop: '100px' }}>Loading assessment results...</div>;
  }

  if (error || !result) {
    return (
      <div className="text-center text-error" style={{ marginTop: '100px' }}>
        <p>{error || 'Assessment not found.'}</p>
        <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={() => navigate('/raw-food-scan')}>Go Back</button>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'FRESH':
        return '#10b981'; // Green
      case 'ACCEPTABLE':
        return '#f59e0b'; // Yellow
      case 'POOR':
      case 'SPOILED / VISIBLY SPOILED':
        return '#ef4444'; // Red
      default:
        return '#64748b'; // Gray
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'FRESH':
      case 'ACCEPTABLE':
        return <FiCheckCircle size={24} color={getStatusColor(status)} />;
      case 'POOR':
      case 'SPOILED / VISIBLY SPOILED':
        return <FiAlertTriangle size={24} color={getStatusColor(status)} />;
      default:
        return <FiInfo size={24} color={getStatusColor(status)} />;
    }
  };

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '800px', margin: '0 auto' }}>
      <button className="btn btn-secondary mb-4" onClick={() => navigate('/raw-food-scan')} style={{ padding: '8px 16px' }}>
        <FiArrowLeft style={{ marginRight: '8px' }} /> Check Another Food
      </button>

      <h2 className="mb-6">Raw Food Quality Assessment</h2>

      <div className="glass-card mb-6" style={{ overflow: 'hidden' }}>
        <div style={{ position: 'relative', width: '100%' }}>
          <img 
            src={`http://localhost:5000${result.imageUrl}`} 
            alt="Scanned Food" 
            style={{ width: '100%', maxHeight: '500px', objectFit: 'contain', borderBottom: '1px solid var(--glass-border)', display: 'block' }} 
            onLoad={(e) => {
              setImageSize({ width: e.target.naturalWidth, height: e.target.naturalHeight });
            }}
          />
          {result.defectBoxes && result.defectBoxes.map((box, idx) => (
            <div 
              key={idx}
              style={{
                position: 'absolute',
                border: '2px solid #ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.2)',
                left: `${(box.x / imageSize.width) * 100}%`,
                top: `${(box.y / imageSize.height) * 100}%`,
                width: `${(box.w / imageSize.width) * 100}%`,
                height: `${(box.h / imageSize.height) * 100}%`,
                pointerEvents: 'none'
              }}
            >
              <span style={{ backgroundColor: '#ef4444', color: '#fff', fontSize: '10px', padding: '2px 4px', position: 'absolute', top: '-18px', left: '-2px', whiteSpace: 'nowrap' }}>
                Defect
              </span>
            </div>
          ))}
        </div>
        
        <div style={{ padding: '24px' }}>
          {/* Food Identification */}
          <div className="mb-6">
            <h3 style={{ color: 'var(--primary-color)', marginBottom: '12px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px' }}>Food Identification</h3>
            <div className="flex" style={{ justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: '#cbd5e1' }}>Food Name:</span>
              <span style={{ fontWeight: 'bold' }}>{result.foodName}</span>
            </div>
            <div className="flex" style={{ justifyContent: 'space-between' }}>
              <span style={{ color: '#cbd5e1' }}>Identification Confidence:</span>
              <span>{(result.foodConfidence * 100).toFixed(1)}%</span>
            </div>
          </div>

          {/* Quality Assessment */}
          <div className="mb-6">
            <h3 style={{ color: 'var(--primary-color)', marginBottom: '12px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px' }}>Quality Assessment</h3>
            <div className="flex" style={{ justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span style={{ color: '#cbd5e1' }}>Visual Quality:</span>
              <div className="flex" style={{ alignItems: 'center', gap: '8px' }}>
                {getStatusIcon(result.qualityStatus)}
                <span style={{ fontWeight: 'bold', color: getStatusColor(result.qualityStatus) }}>{result.qualityStatus}</span>
              </div>
            </div>
            <div className="flex" style={{ justifyContent: 'space-between' }}>
              <span style={{ color: '#cbd5e1' }}>Quality Confidence:</span>
              <span>{(result.qualityConfidence * 100).toFixed(1)}%</span>
            </div>
          </div>

          {/* Detected Visual Indicators */}
          <div className="mb-6">
            <h3 style={{ color: 'var(--primary-color)', marginBottom: '12px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px' }}>Detected Visual Indicators</h3>
            {result.detectedVisualIndicators && result.detectedVisualIndicators.length > 0 ? (
              <ul style={{ listStyleType: 'disc', paddingLeft: '20px', color: '#f87171' }}>
                {result.detectedVisualIndicators.map((issue, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{issue}</li>
                ))}
              </ul>
            ) : (
              <p style={{ color: '#10b981' }}>No significant visual indicators detected.</p>
            )}
          </div>

          {/* Microbial Assessment */}
          <div className="mb-6">
            <h3 style={{ color: 'var(--primary-color)', marginBottom: '12px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px' }}>Microbial Assessment</h3>
            <div className="flex" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#cbd5e1' }}>Indicator Status:</span>
              <span style={{ fontWeight: 'bold', color: result.microbialAssessment?.status === 'NOT_DETERMINABLE_FROM_RGB' ? '#64748b' : '#ef4444' }}>
                {result.microbialAssessment?.status || 'NOT_DETERMINABLE_FROM_RGB'}
              </span>
            </div>
            {result.microbialAssessment?.confidence && (
              <div className="flex" style={{ justifyContent: 'space-between', marginTop: '8px' }}>
                <span style={{ color: '#cbd5e1' }}>Confidence:</span>
                <span>{(result.microbialAssessment.confidence * 100).toFixed(1)}%</span>
              </div>
            )}
          </div>

          {/* AI Explanation */}
          <div className="mb-6">
            <h3 style={{ color: 'var(--primary-color)', marginBottom: '12px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '8px' }}>AI Explanation</h3>
            <p style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '16px', borderRadius: '8px', fontStyle: 'italic' }}>
              "{result.explanation}"
            </p>
          </div>

          {/* Limitations */}
          <div style={{ marginTop: '32px', padding: '16px', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderLeft: '4px solid #ef4444', borderRadius: '4px' }}>
            <h4 style={{ color: '#ef4444', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FiAlertTriangle /> Assessment Limitations
            </h4>
            <p style={{ fontSize: '0.9rem', color: '#cbd5e1', lineHeight: '1.5' }}>
              {result.limitations || "This is a computer-vision based visual assessment. It cannot confirm pathogens, invisible chemical contamination, pesticides, or complete food purity. This system is not a laboratory test and should be used for visual guidance only."}
            </p>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '8px' }}>
              Model Version: {result.modelVersion} | Assessment Type: {result.assessmentType}
            </p>
          </div>

        </div>
      </div>

      {/* Final Assessment Result view */}
      {finalAssessment ? (
        <div className="glass-card" style={{ padding: '24px', borderLeft: '4px solid #3b82f6', marginTop: '24px' }}>
          <h2 style={{ color: '#3b82f6', marginBottom: '16px' }}>⭐ Final Food Quality Result</h2>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--glass-border)', marginBottom: '16px' }}>
            <div>
              <span style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Customer Quality:</span>
              <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{finalAssessment.customerQualityScore} / 5</span>
            </div>
            <div>
              <span style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Website AI Quality:</span>
              <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{finalAssessment.aiQualityScore} / 5</span>
            </div>
            <div>
              <span style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Defect Impact:</span>
              <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: result.defectSeverity === 'None' ? '#10b981' : '#ef4444' }}>
                {result.defectSeverity || 'None'}
              </span>
            </div>
          </div>

          <div style={{ marginBottom: '24px', padding: '16px', backgroundColor: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px' }}>
            <h3 style={{ margin: '0 0 8px 0', fontSize: '1.1rem' }}>⚖️ Comparison</h3>
            <p style={{ margin: 0, fontStyle: 'italic', color: '#e2e8f0' }}>{finalAssessment.comparisonText}</p>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', margin: '32px 0' }}>
            <div style={{ textAlign: 'center' }}>
              <span style={{ display: 'block', color: '#94a3b8', fontSize: '1rem', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>Final Food Quality Score</span>
              <span style={{ display: 'block', fontSize: '3.5rem', fontWeight: 'bold', color: '#10b981', lineHeight: '1' }}>
                {finalAssessment.finalQualityScore.toFixed(1)} <span style={{ fontSize: '1.5rem', color: '#64748b' }}>/ 5</span>
              </span>
            </div>
          </div>

          <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px dashed var(--glass-border)' }}>
            <h3 style={{ color: '#f59e0b', marginBottom: '12px' }}>😋 Customer Taste Rating</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <span style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>{finalAssessment.tasteRating} / 5</span>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', margin: 0 }}>
                Taste is based strictly on customer feedback. Visual AI cannot determine actual taste.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-card" style={{ padding: '24px', marginTop: '24px' }}>
          <h2 className="mb-4">Your Assessment</h2>
          <p style={{ color: '#94a3b8', marginBottom: '24px' }}>
            Please provide your own rating of the food quality and taste to generate the final evidence-based score.
          </p>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#cbd5e1' }}>Food Quality Rating (1-5 Stars)</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={`quality-${star}`}
                  onClick={() => setFoodQualityRating(star)}
                  style={{
                    background: 'none', border: 'none', cursor: 'pointer',
                    fontSize: '2rem', color: star <= foodQualityRating ? '#f59e0b' : '#334155',
                    transition: 'color 0.2s'
                  }}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#cbd5e1' }}>Taste Rating (1-5 Stars)</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={`taste-${star}`}
                  onClick={() => setTasteRating(star)}
                  style={{
                    background: 'none', border: 'none', cursor: 'pointer',
                    fontSize: '2rem', color: star <= tasteRating ? '#f59e0b' : '#334155',
                    transition: 'color 0.2s'
                  }}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          <button 
            className="btn btn-primary" 
            style={{ width: '100%', marginTop: '16px' }}
            disabled={foodQualityRating === 0 || tasteRating === 0 || isSubmitting}
            onClick={async () => {
              setIsSubmitting(true);
              try {
                const res = await api.post(`/raw-food/${id}/customer-assessment`, {
                  foodQualityRating,
                  tasteRating,
                  qualityComment,
                  tasteComment
                });
                if (res.data.success) {
                  setFinalAssessment(res.data.data.finalAssessment);
                } else {
                  alert(res.data.message || 'Error submitting assessment');
                }
              } catch (err) {
                alert(err.response?.data?.message || 'Failed to submit assessment.');
              } finally {
                setIsSubmitting(false);
              }
            }}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Assessment & View Final Score'}
          </button>
        </div>
      )}

    </div>
  );
};

export default RawFoodResult;
