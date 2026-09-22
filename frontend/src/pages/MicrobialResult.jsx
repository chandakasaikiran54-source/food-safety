import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../utils/api';
import { FiCheckCircle, FiXCircle, FiAlertTriangle, FiInfo } from 'react-icons/fi';

const MicrobialResult = () => {
    const { id } = useParams();
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchResult = async () => {
            try {
                const res = await api.get(`/microbial/${id}`);
                if (res.data.success) {
                    setResult(res.data.data);
                }
            } catch (err) {
                setError('Failed to fetch microbial analysis results.');
            } finally {
                setLoading(false);
            }
        };
        fetchResult();
    }, [id]);

    if (loading) return <div className="text-center" style={{ marginTop: '100px' }}>Loading results...</div>;
    if (error) return <div className="text-error text-center" style={{ marginTop: '100px' }}>{error}</div>;
    if (!result) return null;

    let resultColor = 'var(--warning-color)';
    let ResultIcon = FiAlertTriangle;
    let resultText = 'Inconclusive';

    if (result.bacterialResult === 'bacteria_detected') {
        resultColor = 'var(--error-color)';
        ResultIcon = FiXCircle;
        resultText = 'Bacteria Detected';
    } else if (result.bacterialResult === 'no_bacteria_detected') {
        resultColor = 'var(--success-color)';
        ResultIcon = FiCheckCircle;
        resultText = 'No Bacteria Detected';
    } else if (result.bacterialResult === 'image_quality_insufficient') {
        resultText = 'Image Quality Insufficient';
    } else if (result.bacterialResult === 'model_not_available') {
        resultText = 'Model Not Validated';
    }

    return (
        <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '800px', margin: '0 auto' }}>
            <h2 className="text-center mb-8" style={{ textTransform: 'uppercase' }}>MICROBIAL ANALYSIS RESULT</h2>
            
            <div className="glass-card" style={{ padding: '32px', marginBottom: '32px', borderTop: `6px solid ${resultColor}` }}>
                
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '32px' }}>
                    <div style={{ 
                        color: resultColor,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        fontSize: '32px',
                        fontWeight: 'bold',
                        marginBottom: '16px'
                    }}>
                        <ResultIcon size={40} /> {resultText}
                    </div>
                    
                    {result.bacterialResult === 'model_not_available' && (
                        <div style={{ background: 'rgba(234, 179, 8, 0.1)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(234, 179, 8, 0.3)', maxWidth: '600px', textAlign: 'center' }}>
                            <strong style={{ color: 'var(--warning-color)' }}>Microbial AI model is not yet validated.</strong>
                            <p style={{ marginTop: '8px', fontSize: '14px', color: 'var(--text-secondary)' }}>
                                A dedicated microscopic bacterial dataset is required to train and validate this model against laboratory ground truth before production deployment.
                            </p>
                        </div>
                    )}

                    {result.bacterialResult === 'image_quality_insufficient' && (
                        <div style={{ background: 'rgba(234, 179, 8, 0.1)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(234, 179, 8, 0.3)', maxWidth: '600px', textAlign: 'center' }}>
                            <strong style={{ color: 'var(--warning-color)' }}>Insufficient image quality.</strong>
                            <p style={{ marginTop: '8px', fontSize: '14px', color: 'var(--text-secondary)' }}>
                                Please capture a clearer microscopic image. The current image failed resolution, blur, or magnification checks.
                            </p>
                        </div>
                    )}
                </div>

                <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap' }}>
                    <div style={{ flex: '1 1 300px' }}>
                        <h4 style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}>MICROSCOPIC IMAGE</h4>
                        <img src={`http://localhost:5000${result.microscopicImage}`} alt="Microscopic View" style={{ width: '100%', borderRadius: '8px', border: '1px solid var(--glass-border)' }} />
                    </div>
                    
                    <div style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <h4 style={{ marginBottom: '8px', color: 'var(--text-secondary)' }}>ANALYSIS DETAILS</h4>
                        
                        <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                            <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Sample:</span>
                            <span style={{ fontWeight: 'bold', fontSize: '18px' }}>{result.foodName}</span>
                        </div>
                        
                        <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                            <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Model Confidence:</span>
                            <span style={{ fontWeight: 'bold', fontSize: '18px' }}>{(result.confidence * 100).toFixed(1)}%</span>
                        </div>

                        <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                            <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Model Version:</span>
                            <span style={{ fontWeight: 'bold', fontSize: '18px' }}>{result.modelVersion}</span>
                        </div>
                        
                        {result.detectionRegions && result.detectionRegions.length > 0 && (
                            <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                                <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Detection Visualization:</span>
                                <span style={{ fontWeight: 'bold', fontSize: '18px' }}>Bounding boxes generated</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* IMPORTANT LIMITATION */}
            <div className="glass-card" style={{ padding: '24px', borderLeft: '6px solid var(--primary-color)' }}>
                <h3 style={{ marginBottom: '16px', color: 'var(--primary-color)' }}>IMPORTANT LIMITATION</h3>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                    <FiInfo size={28} color="var(--primary-color)" style={{ flexShrink: 0 }} />
                    <div style={{ fontSize: '16px', lineHeight: '1.5' }}>
                        <p style={{ margin: '0 0 8px 0', color: '#cbd5e1' }}>
                            This microbial result is based strictly on the validated microscopic analysis pipeline.
                        </p>
                        <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '14px' }}>
                            A normal smartphone RGB image alone must NOT be treated as direct evidence of invisible bacterial contamination.
                        </p>
                    </div>
                </div>
            </div>
            
            <div style={{ marginTop: '32px', textAlign: 'center' }}>
                <Link to="/microbial-analysis" className="btn btn-primary" style={{ display: 'inline-block' }}>Analyze Another Sample</Link>
            </div>
        </div>
    );
};

export default MicrobialResult;
