import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../utils/api';
import { FiCheckCircle, FiXCircle, FiAlertTriangle, FiInfo } from 'react-icons/fi';

const TomatoResult = () => {
    const { id } = useParams();
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchResult = async () => {
            try {
                const res = await api.get(`/tomato/${id}`);
                if (res.data.success) {
                    setResult(res.data.data);
                }
            } catch (err) {
                setError('Failed to fetch tomato analysis results.');
            } finally {
                setLoading(false);
            }
        };
        fetchResult();
    }, [id]);

    if (loading) return <div className="text-center" style={{ marginTop: '100px' }}>Loading results...</div>;
    if (error) return <div className="text-error text-center" style={{ marginTop: '100px' }}>{error}</div>;
    if (!result) return null;

    const isHygienic = result.finalHygieneStatus === 'HYGIENIC';
    const isInsufficient = result.finalHygieneStatus === 'INSUFFICIENT EVIDENCE';

    return (
        <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '1000px', margin: '0 auto' }}>
            <h2 className="text-center mb-8" style={{ textTransform: 'uppercase' }}>TOMATO ANALYSIS RESULT</h2>
            
            <div style={{ display: 'flex', gap: '24px', marginBottom: '32px' }}>
                <div className="glass-card" style={{ flex: 1, padding: '16px', textAlign: 'center' }}>
                    <h4 style={{ marginBottom: '12px' }}>WHOLE TOMATO</h4>
                    <img src={`http://localhost:5000${result.wholeImage}`} alt="Whole" style={{ maxWidth: '100%', maxHeight: '250px', borderRadius: '8px' }} />
                </div>
                <div className="glass-card" style={{ flex: 1, padding: '16px', textAlign: 'center' }}>
                    <h4 style={{ marginBottom: '12px' }}>CUT TOMATO</h4>
                    {result.cutImage ? (
                        <img src={`http://localhost:5000${result.cutImage}`} alt="Cut" style={{ maxWidth: '100%', maxHeight: '250px', borderRadius: '8px' }} />
                    ) : (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '250px', background: 'rgba(0,0,0,0.1)', borderRadius: '8px', color: 'var(--text-secondary)' }}>
                            [ Not Provided ]
                        </div>
                    )}
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '32px' }}>
                
                {/* OUTPUT 1: AI Tomato Analysis */}
                <div className="glass-card" style={{ padding: '24px', borderTop: '4px solid var(--primary-color)' }}>
                    <h3 style={{ marginBottom: '16px', color: 'var(--primary-color)' }}>AI TOMATO ANALYSIS</h3>
                    
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                        <div className="flex justify-between items-center">
                            <span style={{ color: 'var(--text-secondary)' }}>Food:</span>
                            <span style={{ fontWeight: 'bold' }}>{result.foodName}</span>
                        </div>
                        <div className="flex justify-between items-center pt-3" style={{ borderTop: '1px solid var(--glass-border)' }}>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '18px' }}>AI Score:</span>
                            <span style={{ fontWeight: 'bold', fontSize: '24px', color: '#fff' }}>{result.aiScore}/100</span>
                        </div>
                    </div>

                    <div>
                        <div style={{ marginBottom: '16px' }}>
                            <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Whole Tomato Findings:</span>
                            {(!result.wholeIssues || result.wholeIssues.length === 0 || (result.wholeIssues.length === 1 && result.wholeIssues[0].includes("No obvious visible defect"))) ? (
                                <div style={{ color: 'var(--success-color)', fontSize: '14px' }}><FiCheckCircle style={{ verticalAlign: 'middle', marginRight: '4px' }} /> No major visible issues detected.</div>
                            ) : (
                                <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '14px' }}>
                                    {result.wholeIssues.map((issue, idx) => (
                                        <li key={idx} style={{ color: 'var(--error-color)', marginBottom: '4px', lineHeight: '1.4' }}><FiXCircle style={{ verticalAlign: 'middle', marginRight: '4px' }} /> {issue}</li>
                                    ))}
                                </ul>
                            )}
                        </div>

                        <div style={{ marginBottom: '16px' }}>
                            <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Cut Tomato Findings:</span>
                            {!result.cutImage ? (
                                <div style={{ color: 'var(--warning-color)', fontSize: '14px', fontStyle: 'italic' }}>
                                    <FiAlertTriangle style={{ verticalAlign: 'middle', marginRight: '4px' }} /> Internal analysis unavailable because a cut-tomato image was not provided.
                                </div>
                            ) : (!result.cutIssues || result.cutIssues.length === 0 || (result.cutIssues.length === 1 && result.cutIssues[0].includes("No obvious visible defect"))) ? (
                                <div style={{ color: 'var(--success-color)', fontSize: '14px' }}><FiCheckCircle style={{ verticalAlign: 'middle', marginRight: '4px' }} /> No major visible issues detected.</div>
                            ) : (
                                <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '14px' }}>
                                    {result.cutIssues.map((issue, idx) => (
                                        <li key={idx} style={{ color: 'var(--error-color)', marginBottom: '4px', lineHeight: '1.4' }}><FiXCircle style={{ verticalAlign: 'middle', marginRight: '4px' }} /> {issue}</li>
                                    ))}
                                </ul>
                            )}
                        </div>

                        <div style={{ marginBottom: '16px' }}>
                            <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Detected Colour:</span>
                            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{result.aiDetectedColour || 'Unknown'}</div>
                        </div>

                        <div>
                            <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Visible Abnormalities:</span>
                            {(!result.detectedIssues || result.detectedIssues.length === 0 || (result.detectedIssues.length === 1 && result.detectedIssues[0].includes("No obvious visible defect"))) ? (
                                <div style={{ color: 'var(--success-color)', fontSize: '14px' }}><FiCheckCircle style={{ verticalAlign: 'middle', marginRight: '4px' }} /> None</div>
                            ) : (
                                <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '14px' }}>
                                    {result.detectedIssues.map((issue, idx) => (
                                        <li key={idx} style={{ color: 'var(--warning-color)', marginBottom: '4px', lineHeight: '1.4' }}><FiAlertTriangle style={{ verticalAlign: 'middle', marginRight: '4px' }} /> {issue}</li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>
                </div>

                {/* OUTPUT 2: Customer Assessment */}
                <div className="glass-card" style={{ padding: '24px', borderTop: '4px solid var(--secondary-color)' }}>
                    <h3 style={{ marginBottom: '16px', color: 'var(--secondary-color)' }}>CUSTOMER ASSESSMENT</h3>
                    
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                        <div className="flex justify-between items-center pt-3" style={{ borderTop: '1px solid var(--glass-border)', paddingBottom: '12px' }}>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '18px' }}>Customer Score:</span>
                            <span style={{ fontWeight: 'bold', fontSize: '24px', color: '#fff' }}>{result.customerScore}/100</span>
                        </div>
                    </div>

                    <div>
                        <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>Customer observations:</span>
                        <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <li>
                                <span style={{ color: 'var(--text-secondary)' }}>Food Quality:</span> <span style={{ fontWeight: 'bold' }}>{result.customerFoodQuality || 'N/A'}</span>
                            </li>
                            <li>
                                <span style={{ color: 'var(--text-secondary)' }}>Taste:</span> <span style={{ fontWeight: 'bold' }}>{result.customerTaste || 'N/A'}</span>
                            </li>
                            <li>
                                <span style={{ color: 'var(--text-secondary)' }}>Colour:</span> <span style={{ fontWeight: 'bold' }}>{result.customerColour}</span>
                            </li>
                            <li>
                                <span style={{ color: 'var(--text-secondary)' }}>Texture:</span> <span style={{ fontWeight: 'bold' }}>{result.customerTexture}</span>
                            </li>
                            {result.customerComment && (
                                <li className="mt-2 pt-2" style={{ borderTop: '1px dashed var(--glass-border)' }}>
                                    <span style={{ color: 'var(--text-secondary)' }}>Comment:</span> 
                                    <br />
                                    <span style={{ fontStyle: 'italic' }}>"{result.customerComment}"</span>
                                </li>
                            )}
                        </ul>
                    </div>
                </div>
            </div>

            {/* FINAL TOMATO ASSESSMENT */}
            <div className="glass-card" style={{ padding: '32px', marginBottom: '32px', textAlign: 'center', background: 'rgba(255, 255, 255, 0.03)' }}>
                <h2 style={{ marginBottom: '24px' }}>FINAL TOMATO ASSESSMENT</h2>
                
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '24px', margin: '24px 0' }}>
                    <div style={{ textAlign: 'center', padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', minWidth: '150px' }}>
                        <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>AI Score</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--primary-color)' }}>{result.aiScore}/100</div>
                    </div>
                    <div style={{ fontSize: '24px', color: 'var(--text-secondary)' }}>+</div>
                    <div style={{ textAlign: 'center', padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', minWidth: '150px' }}>
                        <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Customer Score</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--secondary-color)' }}>{result.customerScore}/100</div>
                    </div>
                </div>

                <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid var(--glass-border)' }}>
                    <div style={{ fontSize: '18px', color: 'var(--text-secondary)', marginBottom: '8px' }}>AVERAGE</div>
                    <div style={{ fontSize: '64px', fontWeight: 'bold', lineHeight: '1', color: '#fff' }}>
                        {result.finalScore} <span style={{ fontSize: '24px', color: 'var(--text-secondary)' }}>/ 100</span>
                    </div>
                </div>
            </div>

            {/* Hygiene & Microbial Safety */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
                <div className="glass-card" style={{ padding: '24px', borderLeft: `6px solid ${isHygienic ? 'var(--success-color)' : (isInsufficient ? 'var(--warning-color)' : 'var(--error-color)')}` }}>
                    <h3 style={{ marginBottom: '16px' }}>Hygiene Status</h3>
                    
                    <div style={{ 
                        display: 'inline-flex', 
                        alignItems: 'center', 
                        gap: '12px', 
                        color: isHygienic ? 'var(--success-color)' : (isInsufficient ? 'var(--warning-color)' : 'var(--error-color)'),
                        fontWeight: 'bold',
                        fontSize: '24px',
                        marginBottom: '16px'
                    }}>
                        {isHygienic ? <FiCheckCircle size={28} /> : (isInsufficient ? <FiAlertTriangle size={28} /> : <FiXCircle size={28} />)}
                        {result.finalHygieneStatus}
                    </div>

                    <div>
                        <span style={{ color: 'var(--text-secondary)', fontWeight: 'bold' }}>Based on Visual Evidence: </span>
                        <span style={{ color: '#cbd5e1' }}>
                            {isHygienic 
                                ? "No obvious visible mold, severe spoilage indicators, or visible foreign material detected in either image."
                                : (isInsufficient 
                                    ? "Available images do not provide sufficient visual evidence for a reliable hygiene assessment."
                                    : "Visible contamination risks (such as mold or severe decay) were detected by the AI.")
                            }
                        </span>
                    </div>
                </div>

                <div className="glass-card" style={{ padding: '24px', borderLeft: '6px solid var(--warning-color)' }}>
                    <h3 style={{ marginBottom: '16px' }}>Microbial Safety</h3>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                        <FiInfo size={28} color="var(--warning-color)" style={{ flexShrink: 0 }} />
                        <div style={{ fontSize: '16px', lineHeight: '1.5' }}>
                            <strong>Cannot be determined from ordinary image.</strong>
                            <p style={{ marginTop: '8px', color: 'var(--text-secondary)', fontSize: '14px' }}>
                                A normal camera can assess visible characteristics, but invisible microbial contamination (bacteria, pathogens) or chemical adulteration cannot be confirmed from the photograph alone.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* PLANT DISEASE RECOGNITION */}
            <div className="glass-card" style={{ padding: '24px', marginTop: '24px', borderTop: '4px solid #10b981' }}>
                <h3 style={{ marginBottom: '16px', color: '#10b981', textTransform: 'uppercase' }}>PLANT DISEASE RECOGNITION</h3>
                
                {result.diseaseAssessment && result.diseaseAssessment.isCompatible ? (
                    <div>
                        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', marginBottom: '16px' }}>
                            <div style={{ flex: 1, minWidth: '200px', background: 'rgba(16, 185, 129, 0.1)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                                <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '4px' }}>ResNet18:</div>
                                <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>
                                    Disease: {result.diseaseAssessment.resnet18?.predicted_class || 'Unknown'}
                                </div>
                                <div style={{ fontSize: '14px' }}>
                                    Confidence: {result.diseaseAssessment.resnet18 ? Math.round(result.diseaseAssessment.resnet18.confidence * 100) : 0}%
                                </div>
                            </div>
                            <div style={{ flex: 1, minWidth: '200px', background: 'rgba(16, 185, 129, 0.1)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                                <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '4px' }}>MobileNetV3:</div>
                                <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>
                                    Disease: {result.diseaseAssessment.mobilenetv3?.predicted_class || 'Unknown'}
                                </div>
                                <div style={{ fontSize: '14px' }}>
                                    Confidence: {result.diseaseAssessment.mobilenetv3 ? Math.round(result.diseaseAssessment.mobilenetv3.confidence * 100) : 0}%
                                </div>
                            </div>
                        </div>
                        <div style={{ fontSize: '13px', color: 'var(--text-secondary)', fontStyle: 'italic', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                            <FiInfo size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                            <span>This is an image-based plant disease classification result based on the PlantVillage dataset. It is not a laboratory microbiological test for food safety.</span>
                        </div>
                    </div>
                ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                        <FiInfo size={24} color="var(--warning-color)" />
                        <span style={{ color: 'var(--text-secondary)' }}>
                            {result.diseaseAssessment?.message || "Plant disease model requires a compatible plant/leaf image."}
                        </span>
                    </div>
                )}
            </div>

            {/* FUTURE SENSOR / LAB INTEGRATION */}
            <div className="glass-card" style={{ padding: '24px', marginTop: '24px', borderTop: '4px solid #8b5cf6' }}>
                <h3 style={{ marginBottom: '16px', color: '#8b5cf6', textTransform: 'uppercase' }}>FUTURE SENSOR / LAB INTEGRATION</h3>
                
                <div style={{ marginBottom: '12px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Available:</span> <span style={{ fontWeight: 'bold' }}>{result.hasLabData ? 'Yes' : 'No'}</span>
                </div>
                
                {result.hasLabData && result.labData ? (
                    <div style={{ background: 'rgba(139, 92, 246, 0.1)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(139, 92, 246, 0.3)' }}>
                        <div style={{ marginBottom: '8px' }}><span style={{ color: 'var(--text-secondary)' }}>Test:</span> {result.labData.testName}</div>
                        <div style={{ marginBottom: '8px' }}><span style={{ color: 'var(--text-secondary)' }}>Result:</span> <strong>{result.labData.result}</strong></div>
                        <div style={{ marginBottom: '8px' }}><span style={{ color: 'var(--text-secondary)' }}>Source:</span> {result.labData.source}</div>
                        <div><span style={{ color: 'var(--text-secondary)' }}>Date:</span> {new Date(result.labData.date).toLocaleDateString()}</div>
                    </div>
                ) : (
                    <div style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                        Sensor/laboratory data not available.
                    </div>
                )}
            </div>
            
            <div style={{ marginTop: '32px', textAlign: 'center' }}>
                <Link to="/tomato-analysis" className="btn btn-primary" style={{ display: 'inline-block' }}>Analyze Another Tomato</Link>
            </div>
        </div>
    );
};

export default TomatoResult;
