import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiCamera, FiUpload, FiRefreshCw, FiAlertCircle } from 'react-icons/fi';
import api from '../utils/api';

const TomatoAnalysis = () => {
    const [wholeImageFile, setWholeImageFile] = useState(null);
    const [wholeImagePreview, setWholeImagePreview] = useState(null);

    const [cutImageFile, setCutImageFile] = useState(null);
    const [cutImagePreview, setCutImagePreview] = useState(null);

    const [customerFoodQuality, setCustomerFoodQuality] = useState('');
    const [customerTaste, setCustomerTaste] = useState('');
    const [customerColour, setCustomerColour] = useState('');
    const [customerTexture, setCustomerTexture] = useState('');
    const [customerComment, setCustomerComment] = useState('');

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const navigate = useNavigate();
    const wholeInputRef = useRef(null);
    const cutInputRef = useRef(null);

    const handleWholeUpload = (e) => {
        const file = e.target.files[0];
        if (validateFile(file)) {
            setWholeImageFile(file);
            setWholeImagePreview(URL.createObjectURL(file));
        }
    };

    const handleCutUpload = (e) => {
        const file = e.target.files[0];
        if (validateFile(file)) {
            setCutImageFile(file);
            setCutImagePreview(URL.createObjectURL(file));
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
        if (!wholeImageFile) {
            setError('Whole Tomato image is required.');
            return;
        }
        if (!customerColour || !customerTexture || !customerFoodQuality || !customerTaste) {
            setError('Please provide colour, texture, food quality, and taste observations.');
            return;
        }

        setLoading(true);
        setError('');

        const formData = new FormData();
        formData.append('wholeImage', wholeImageFile);
        if (cutImageFile) {
            formData.append('cutImage', cutImageFile);
        }
        formData.append('customerColour', customerColour);
        formData.append('customerTexture', customerTexture);
        formData.append('customerFoodQuality', customerFoodQuality);
        formData.append('customerTaste', customerTaste);
        formData.append('customerComment', customerComment);

        try {
            const res = await api.post('/tomato/analyze', formData);
            if (res.data.success) {
                navigate(`/tomato-result/${res.data.data._id}`);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Error analyzing images. Please try again.');
            setLoading(false);
        }
    };

    return (
        <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '900px', margin: '0 auto' }}>
            <div className="text-center mb-8">
                <h2>TOMATO ANALYSIS</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Upload two images and share a few details to analyze your tomato.</p>
                <div style={{ marginTop: '10px', fontSize: '14px', fontWeight: 'bold', color: 'var(--primary-color)' }}>
                    AI Analysis 70% • Customer Review 30%
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
                    <h3>Analyzing Tomato...</h3>
                    <p style={{ color: '#cbd5e1', marginTop: '8px' }}>Processing visual evidence and combining your observations.</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {/* Card 1: Whole Tomato */}
                    <div className="glass-card" style={{ padding: '24px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                            <div style={{ background: 'var(--primary-color)', color: '#fff', width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>1</div>
                            <h3 style={{ margin: 0 }}>UPLOAD WHOLE TOMATO IMAGE</h3>
                        </div>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>Capture or upload a clear photo of the whole tomato.</p>
                        
                        {wholeImagePreview ? (
                            <div style={{ textAlign: 'center' }}>
                                <img src={wholeImagePreview} alt="Whole Tomato" style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '8px', marginBottom: '16px' }} />
                                <div>
                                    <button className="btn btn-secondary" onClick={() => { setWholeImageFile(null); setWholeImagePreview(null); }}>Change Image</button>
                                </div>
                            </div>
                        ) : (
                            <div>
                                <input type="file" accept="image/*" ref={wholeInputRef} style={{ display: 'none' }} onChange={handleWholeUpload} />
                                <button className="btn btn-secondary w-full flex items-center justify-center gap-2" onClick={() => wholeInputRef.current.click()}>
                                    <FiUpload /> Upload Image
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Card 2: Cut Tomato */}
                    <div className="glass-card" style={{ padding: '24px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                            <div style={{ background: 'var(--primary-color)', color: '#fff', width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>2</div>
                            <h3 style={{ margin: 0 }}>UPLOAD CUT TOMATO IMAGE</h3>
                        </div>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>Cut the tomato in the middle and upload a clear photo of the inside.</p>
                        
                        {cutImagePreview ? (
                            <div style={{ textAlign: 'center' }}>
                                <img src={cutImagePreview} alt="Cut Tomato" style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '8px', marginBottom: '16px' }} />
                                <div>
                                    <button className="btn btn-secondary" onClick={() => { setCutImageFile(null); setCutImagePreview(null); }}>Change Image</button>
                                </div>
                            </div>
                        ) : (
                            <div>
                                <input type="file" accept="image/*" ref={cutInputRef} style={{ display: 'none' }} onChange={handleCutUpload} />
                                <button className="btn btn-secondary w-full flex items-center justify-center gap-2" onClick={() => cutInputRef.current.click()}>
                                    <FiUpload /> Upload Image
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Card 3: Observations */}
                    <div className="glass-card" style={{ padding: '24px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                            <div style={{ background: 'var(--primary-color)', color: '#fff', width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>3</div>
                            <h3 style={{ margin: 0 }}>YOUR OBSERVATIONS</h3>
                        </div>
                        
                        <div style={{ marginBottom: '20px' }}>
                            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Food Quality:</label>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                {['Excellent', 'Good', 'Average', 'Poor', 'Very Poor'].map(opt => (
                                    <label key={opt} style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                                        <input type="radio" name="foodQuality" value={opt} checked={customerFoodQuality === opt} onChange={(e) => setCustomerFoodQuality(e.target.value)} />
                                        {opt}
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div style={{ marginBottom: '20px' }}>
                            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Taste:</label>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                {['Excellent', 'Good', 'Average', 'Poor', 'Very Poor'].map(opt => (
                                    <label key={opt} style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                                        <input type="radio" name="taste" value={opt} checked={customerTaste === opt} onChange={(e) => setCustomerTaste(e.target.value)} />
                                        {opt}
                                    </label>
                                ))}
                            </div>
                        </div>
                        
                        <div style={{ marginBottom: '20px' }}>
                            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Tomato Colour:</label>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                {['Bright Red', 'Light Red', 'Orange', 'Yellowish', 'Greenish', 'Mixed / Other'].map(opt => (
                                    <label key={opt} style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                                        <input type="radio" name="colour" value={opt} checked={customerColour === opt} onChange={(e) => setCustomerColour(e.target.value)} />
                                        {opt}
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div style={{ marginBottom: '20px' }}>
                            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>How does the tomato feel? (Texture)</label>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                {['Hard', 'Firm', 'Normal', 'Soft', 'Very Soft'].map(opt => (
                                    <label key={opt} style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                                        <input type="radio" name="texture" value={opt} checked={customerTexture === opt} onChange={(e) => setCustomerTexture(e.target.value)} />
                                        {opt}
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Optional comment:</label>
                            <textarea 
                                className="input-field" 
                                rows="3" 
                                placeholder="Enter your observation (e.g., Tomato feels firm and smells normal)"
                                value={customerComment}
                                onChange={(e) => setCustomerComment(e.target.value)}
                                style={{ width: '100%', resize: 'vertical' }}
                            ></textarea>
                        </div>
                    </div>

                    <button 
                        className="btn btn-primary w-full" 
                        style={{ padding: '20px', fontSize: '18px', fontWeight: 'bold', marginTop: '16px' }}
                        onClick={handleAnalyze}
                    >
                        🔍 ANALYZE TOMATO
                    </button>
                </div>
            )}
        </div>
    );
};

export default TomatoAnalysis;
