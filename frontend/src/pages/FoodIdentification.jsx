import React, { useState, useRef } from 'react';
import { FiCamera, FiUpload, FiRefreshCw, FiCheckCircle, FiAlertCircle, FiHelpCircle } from 'react-icons/fi';
import api from '../utils/api';

const FoodIdentification = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        setError('Image size exceeds 10MB limit.');
        return;
      }
      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
      setResult(null);
      setError('');
    }
  };

  const handleIdentify = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select or upload an image first.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      // Direct call to Biryani regional classification endpoint
      const response = await api.post('/biryani/classify', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (err) {
      console.warn('Direct /biryani/classify failed, trying fallback:', err);
      try {
        const fallbackRes = await api.post('/food-identification/biryani', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setResult(fallbackRes.data);
      } catch (fallbackErr) {
        console.error('Identification error:', fallbackErr);
        if (fallbackErr.response && fallbackErr.response.data && fallbackErr.response.data.message) {
          setError(fallbackErr.response.data.message);
        } else {
          setError('Biryani identification service failed or is unavailable.');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setImagePreview(null);
    setResult(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="container" style={{ maxWidth: '850px', margin: '40px auto', padding: '0 20px' }}>
      <div className="card" style={{ padding: '30px', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
        <div style={{ textAlign: 'center', marginBottom: '25px' }}>
          <h2 style={{ fontSize: '1.8rem', fontWeight: '700', color: 'var(--text-color, #1a202c)', marginBottom: '8px' }}>
            Food Identification
          </h2>
          <p style={{ color: 'var(--text-muted, #718096)', fontSize: '0.95rem' }}>
            AI-powered food identification system. Currently featuring dedicated classification for <strong>Biryani</strong>.
          </p>
        </div>

        {error && (
          <div style={{ backgroundColor: '#fff5f5', color: '#c53030', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #feb2b2', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FiAlertCircle />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleIdentify}>
          <div
            style={{
              border: '2px dashed #cbd5e0',
              borderRadius: '10px',
              padding: '30px',
              textAlign: 'center',
              backgroundColor: '#f7fafc',
              cursor: 'pointer',
              marginBottom: '20px'
            }}
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/jpeg,image/png,image/webp"
              style={{ display: 'none' }}
            />
            {imagePreview ? (
              <div>
                <img
                  src={imagePreview}
                  alt="Preview"
                  style={{ maxHeight: '280px', maxWidth: '100%', borderRadius: '8px', objectFit: 'contain' }}
                />
                <p style={{ marginTop: '10px', fontSize: '0.85rem', color: '#718096' }}>Click to choose a different photo</p>
              </div>
            ) : (
              <div>
                <FiUpload style={{ fontSize: '2.5rem', color: '#4a5568', marginBottom: '10px' }} />
                <p style={{ fontWeight: '600', color: '#2d3748', marginBottom: '4px' }}>Click or drop a food image here</p>
                <p style={{ fontSize: '0.85rem', color: '#a0aec0' }}>JPG, PNG, or WEBP up to 10MB</p>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !selectedFile}
              style={{ minWidth: '160px', padding: '10px 20px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            >
              {loading ? (
                <>
                  <FiRefreshCw className="spin" /> Identifying...
                </>
              ) : (
                'Identify Food'
              )}
            </button>
            {selectedFile && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleReset}
                disabled={loading}
                style={{ padding: '10px 20px' }}
              >
                Reset
              </button>
            )}
          </div>
        </form>

        {result && (
          <div
            style={{
              marginTop: '30px',
              padding: '24px',
              borderRadius: '12px',
              backgroundColor: '#fff',
              border: '1px solid #e2e8f0',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)'
            }}
          >
            {/* Header / Primary Identification */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {result.biryani_type && result.biryani_type !== 'Unknown' ? (
                  <FiCheckCircle style={{ color: '#38a169', fontSize: '1.8rem' }} />
                ) : (
                  <FiAlertCircle style={{ color: '#dd6b20', fontSize: '1.8rem' }} />
                )}
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.4rem', fontWeight: '800', color: '#1a202c' }}>
                    {result.biryani_type && result.biryani_type !== 'Unknown'
                      ? `${result.biryani_type} Biryani`
                      : result.food === 'biryani'
                      ? 'Biryani Detected'
                      : 'Dish Identified'}
                  </h3>
                  <span style={{ fontSize: '0.85rem', color: '#718096' }}>
                    Status: {result.status || 'Analysis Available'}
                  </span>
                </div>
              </div>

              {result.evidence_quality && (
                <div
                  style={{
                    padding: '6px 14px',
                    borderRadius: '20px',
                    fontSize: '0.85rem',
                    fontWeight: '700',
                    textTransform: 'uppercase',
                    backgroundColor:
                      result.evidence_quality === 'high' || result.evidence_quality === 'good'
                        ? '#def7ec'
                        : result.evidence_quality === 'moderate'
                        ? '#fef08a'
                        : '#fee2e2',
                    color:
                      result.evidence_quality === 'high' || result.evidence_quality === 'good'
                        ? '#03543f'
                        : result.evidence_quality === 'moderate'
                        ? '#713f12'
                        : '#991b1b'
                  }}
                >
                  Evidence: {result.evidence_quality}
                </div>
              )}
            </div>

            {/* Core Metrics Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '15px', marginBottom: '20px' }}>
              <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <span style={{ fontSize: '0.78rem', color: '#64748b', display: 'block', fontWeight: '600', textTransform: 'uppercase' }}>
                  Regional Style
                </span>
                <strong style={{ fontSize: '1.2rem', color: '#0f172a' }}>
                  {result.biryani_type || result.food || 'Unknown'}
                </strong>
              </div>

              <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <span style={{ fontSize: '0.78rem', color: '#64748b', display: 'block', fontWeight: '600', textTransform: 'uppercase' }}>
                  Calibrated Confidence
                </span>
                <strong style={{ fontSize: '1.2rem', color: '#0f172a' }}>
                  {Math.round((result.confidence || 0) * 100)}%
                </strong>
              </div>

              {result.regional_profile?.traditional_rice && (
                <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <span style={{ fontSize: '0.78rem', color: '#64748b', display: 'block', fontWeight: '600', textTransform: 'uppercase' }}>
                    Authentic Rice
                  </span>
                  <strong style={{ fontSize: '1rem', color: '#0f172a' }}>
                    {result.regional_profile.traditional_rice}
                  </strong>
                </div>
              )}
            </div>

            {/* Top Regional Candidates if present */}
            {result.top_candidates && result.top_candidates.length > 1 && (
              <div style={{ marginBottom: '20px', padding: '16px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h4 style={{ margin: '0 0 10px 0', fontSize: '0.95rem', fontWeight: '700', color: '#334155' }}>
                  Regional Candidate Probabilities
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {result.top_candidates.map((cand, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                      <span style={{ fontWeight: idx === 0 ? '700' : '500', color: idx === 0 ? '#0f172a' : '#64748b' }}>
                        {cand.style} Biryani
                      </span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '50%' }}>
                        <div style={{ flex: 1, height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                          <div
                            style={{
                              width: `${Math.round(cand.confidence * 100)}%`,
                              height: '100%',
                              background: idx === 0 ? '#3182ce' : '#94a3b8',
                              borderRadius: '4px'
                            }}
                          />
                        </div>
                        <span style={{ minWidth: '40px', textAlign: 'right', fontWeight: '600', color: '#475569' }}>
                          {Math.round(cand.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Regional Profile Knowledge Card */}
            {result.regional_profile && (
              <div style={{ marginBottom: '20px', padding: '16px', background: '#fffbeb', borderRadius: '8px', border: '1px solid #fef3c7' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '1rem', fontWeight: '700', color: '#92400e' }}>
                  Regional Culinary Profile: {result.biryani_type}
                </h4>
                <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.9rem', color: '#78350f', lineHeight: '1.6' }}>
                  {result.regional_profile.origin && <li><strong>Culinary Origin:</strong> {result.regional_profile.origin}</li>}
                  {result.regional_profile.cooking_method && <li><strong>Cooking Technique:</strong> {result.regional_profile.cooking_method}</li>}
                  {result.regional_profile.key_visual_cues && <li><strong>Visual Indicators:</strong> {result.regional_profile.key_visual_cues}</li>}
                  {result.regional_profile.traditional_accompaniments && <li><strong>Accompaniments:</strong> {result.regional_profile.traditional_accompaniments}</li>}
                </ul>
              </div>
            )}

            {/* Explainability / Visual Evidence */}
            {result.explainability && (
              <div style={{ marginBottom: '16px', padding: '14px', background: '#f0fdf4', borderRadius: '8px', border: '1px solid #bbf7d0', fontSize: '0.88rem', color: '#166534' }}>
                <strong>Visual Evidence (Grad-CAM):</strong> {result.explainability.visual_evidence}
              </div>
            )}

            {/* Scientific Disclaimer (Phase 26) */}
            <div style={{ padding: '12px', background: '#f1f5f9', borderRadius: '6px', fontSize: '0.82rem', color: '#475569', lineHeight: '1.5' }}>
              <strong>Important Note:</strong> {result.disclaimer || 'Regional style prediction is based on visual evidence and may vary with recipe, restaurant, and presentation. Optical photography cannot determine internal microbial safety.'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FoodIdentification;
