import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiCamera, FiUpload, FiRefreshCw, FiAlertCircle, FiInfo } from 'react-icons/fi';
import api from '../utils/api';

const MicrobialAnalysis = () => {
    const [imageFile, setImageFile] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    
    const navigate = useNavigate();
    const inputRef = useRef(null);

    const handleUpload = (e) => {
        const file = e.target.files[0];
        if (validateFile(file)) {
            setImageFile(file);
            setImagePreview(URL.createObjectURL(file));
        }
    };

    const validateFile = (file) => {
        if (!file) return false;
        if (!file.type.startsWith('image/')) {
            setError('Invalid file type. Please upload a valid image file.');
            return false;
        }
        if (file.size > 10 * 1024 * 1024) {
            setError('Image is too large. Please upload an image smaller than 10MB.');
            return false;
        }
        setError('');
        return true;
    };

    const handleAnalyze = async () => {
        if (!imageFile) {
            setError('A microscopic image is required for this analysis.');
            return;
        }

        setLoading(true);
        setError('');

        const formData = new FormData();
        formData.append('microscopicImage', imageFile);

        try {
            const res = await api.post('/microbial/analyze', formData);
            if (res.data.success) {
                navigate(`/microbial-result/${res.data.data._id}`);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Error analyzing microscopic image. Please try again.');
            setLoading(false);
        }
    };

    return (
        <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '900px', margin: '0 auto' }}>
            <div className="text-center mb-8">
                <h2>MICROBIAL ANALYSIS</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Advanced microscopic bacterial detection pipeline.</p>
            </div>

            <div className="glass-card mb-8" style={{ padding: '24px', borderLeft: '6px solid var(--warning-color)' }}>
                <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                    <FiInfo size={32} color="var(--warning-color)" style={{ flexShrink: 0 }} />
                    <div>
                        <h3 style={{ margin: '0 0 8px 0', color: 'var(--warning-color)' }}>MICROSCOPIC IMAGE REQUIRED</h3>
                        <p style={{ margin: 0, lineHeight: '1.5' }}>
                            For microbial analysis, capture a clear microscopic image of the tomato sample using a microscope or compatible smartphone microscope attachment. 
                            <strong> Ordinary smartphone RGB photographs cannot be used to detect invisible bacteria.</strong>
                        </p>
                    </div>
                </div>
            </div>

            {error && (
                <div className="text-error mb-4 text-center glass-card" style={{ padding: '16px', borderColor: 'var(--error-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <FiAlertCircle /> {error}
                </div>
            )}

            {loading ? (
                <div className="glass-card flex flex-col items-center justify-center" style={{ minHeight: '400px' }}>
                    <FiRefreshCw size={48} color="var(--primary-color)" style={{ animation: 'spin 2s linear infinite', marginBottom: '16px' }} />
                    <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
                    <h3>Validating Image Quality...</h3>
                    <p style={{ color: '#cbd5e1', marginTop: '8px' }}>Checking resolution, blur, and magnification before inference.</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    <div className="glass-card" style={{ padding: '24px' }}>
                        <h3 style={{ marginBottom: '16px' }}>UPLOAD MICROSCOPIC IMAGE</h3>
                        
                        {imagePreview ? (
                            <div style={{ textAlign: 'center' }}>
                                <img src={imagePreview} alt="Microscopic Sample" style={{ maxWidth: '100%', maxHeight: '400px', borderRadius: '8px', marginBottom: '16px', border: '1px solid var(--glass-border)' }} />
                                <div>
                                    <button className="btn btn-secondary" onClick={() => { setImageFile(null); setImagePreview(null); }}>Change Image</button>
                                </div>
                            </div>
                        ) : (
                            <div>
                                <input type="file" accept="image/*" ref={inputRef} style={{ display: 'none' }} onChange={handleUpload} />
                                <button className="btn btn-secondary w-full flex items-center justify-center gap-2" style={{ padding: '32px', fontSize: '18px' }} onClick={() => inputRef.current.click()}>
                                    <FiUpload size={24} /> Upload Microscopic Image
                                </button>
                            </div>
                        )}
                    </div>

                    <button 
                        className="btn btn-primary w-full" 
                        style={{ padding: '20px', fontSize: '18px', fontWeight: 'bold', marginTop: '16px' }}
                        onClick={handleAnalyze}
                    >
                        🔬 RUN MICROBIAL ANALYSIS
                    </button>
                </div>
            )}
        </div>
    );
};

export default MicrobialAnalysis;
