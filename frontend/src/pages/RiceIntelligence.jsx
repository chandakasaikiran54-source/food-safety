import React, { useState, useRef } from 'react';
import {
  FiUpload, FiCamera, FiRefreshCw, FiCheckCircle, FiAlertCircle,
  FiInfo, FiSliders, FiActivity, FiShield, FiChevronDown, FiChevronUp, FiCode
} from 'react-icons/fi';
import api from '../utils/api';

const RiceIntelligence = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [weight, setWeight] = useState(0.20);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [showJson, setShowJson] = useState(false);
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

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select or upload a rice image first.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('weight', weight);

    try {
      const response = await api.post('/rice/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (err) {
      console.error('Rice Intelligence Error:', err);
      if (err.response && err.response.data && err.response.data.message) {
        setError(err.response.data.message);
      } else {
        setError('Rice Intelligence service is unavailable. Please verify backend and AI services are running.');
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

  const getSuitabilityColor = (rating) => {
    switch (rating?.toLowerCase()) {
      case 'high': return 'var(--score-excellent, #10b981)';
      case 'moderate': return 'var(--score-good, #fbbf24)';
      case 'low': return 'var(--score-poor, #f97316)';
      default: return '#94a3b8';
    }
  };

  const getQualityColor = (indicator) => {
    switch (indicator?.toLowerCase()) {
      case 'high': return 'var(--score-excellent, #10b981)';
      case 'medium': return 'var(--score-good, #fbbf24)';
      case 'low': return 'var(--score-high-concern, #ef4444)';
      default: return '#94a3b8';
    }
  };

  const riceData = result?.rice;

  return (
    <div className="container" style={{ maxWidth: '1100px', margin: '30px auto', padding: '0 20px' }}>
      {/* Header Banner */}
      <div className="glass-card mb-8 text-center" style={{ padding: '32px 24px', position: 'relative', overflow: 'hidden' }}>
        <div style={{ display: 'inline-block', padding: '6px 14px', borderRadius: '20px', background: 'rgba(59, 130, 246, 0.15)', border: '1px solid rgba(59, 130, 246, 0.3)', marginBottom: '12px', fontSize: '0.85rem', fontWeight: '600', color: '#60a5fa' }}>
          🌾 BIRYANI AI CORE MODULE
        </div>
        <h1 style={{ fontSize: '2.4rem', fontWeight: '800', marginBottom: '8px', letterSpacing: '-0.5px' }}>
          RICE INTELLIGENCE
        </h1>
        <p style={{ color: '#cbd5e1', fontSize: '1.05rem', maxWidth: '750px', margin: '0 auto 16px', lineHeight: '1.5' }}>
          Comprehensive computer vision grain morphology & verified food science nutrition knowledge for Biryani rice assessment.
        </p>

        {/* Scientific Safety Badge */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 16px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '8px', fontSize: '0.82rem', color: '#34d399' }}>
          <FiShield /> Combined Image AI & Verified ICMR-NIN / USDA Knowledge Layer
        </div>
      </div>

      {/* Upload and Configuration Form */}
      <div className="glass-card mb-8" style={{ padding: '28px' }}>
        <form onSubmit={handleAnalyze}>
          <div style={{ display: 'grid', gridTemplateColumns: imagePreview ? '1fr 1fr' : '1fr', gap: '24px', alignItems: 'center' }}>
            <div
              style={{
                border: '2px dashed var(--glass-border)',
                borderRadius: '12px',
                padding: '30px',
                textAlign: 'center',
                background: 'rgba(255, 255, 255, 0.02)',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
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
              <FiUpload size={36} color="var(--primary-color)" style={{ marginBottom: '10px' }} />
              <p style={{ fontWeight: '600', fontSize: '1rem', marginBottom: '6px' }}>
                Select or Drop a Rice Image
              </p>
              <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                Raw grain spread or cooked Biryani rice (JPG, PNG, WEBP up to 10MB)
              </p>
            </div>

            {imagePreview && (
              <div style={{ textAlign: 'center' }}>
                <img
                  src={imagePreview}
                  alt="Preview"
                  style={{ maxHeight: '220px', maxWidth: '100%', borderRadius: '10px', objectFit: 'contain', border: '1px solid var(--glass-border)' }}
                />
                <div style={{ marginTop: '8px' }}>
                  <button
                    type="button"
                    onClick={handleReset}
                    className="btn btn-secondary"
                    style={{ fontSize: '0.85rem', padding: '6px 14px' }}
                  >
                    Change Image
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Configurable Weight Slider (Phase 17) */}
          <div style={{ marginTop: '24px', padding: '16px 20px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--glass-border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
              <label style={{ fontWeight: '600', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FiSliders color="#60a5fa" /> Rice Contribution Weight in Biryani Assessment:
              </label>
              <span style={{ fontWeight: '700', color: 'var(--primary-color)', fontSize: '1rem' }}>
                {(weight * 100).toFixed(0)}%
              </span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.50"
              step="0.05"
              value={weight}
              onChange={(e) => setWeight(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer' }}
            />
            <p style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: '6px' }}>
              Project Design Hypothesis: 20% default weight is a configurable conceptual model, not an immutable physical constant or institutional mandate.
            </p>
          </div>

          {error && (
            <div style={{ marginTop: '16px', padding: '12px 16px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--error-color)', color: '#fca5a5', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' }}>
              <FiAlertCircle /> {error}
            </div>
          )}

          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <button
              type="submit"
              disabled={loading || !selectedFile}
              className="btn btn-primary"
              style={{ padding: '12px 36px', fontSize: '1.05rem', minWidth: '220px' }}
            >
              {loading ? (
                <>
                  <FiRefreshCw className="spin" style={{ marginRight: '8px', animation: 'spin 1s linear infinite' }} />
                  Analyzing Rice Grains...
                </>
              ) : (
                '🔍 Run Rice Intelligence'
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Analysis Results Display */}
      {result && riceData && (
        <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

          {/* Primary Variety & Assessment Summary */}
          <div className="glass-card" style={{ padding: '28px', borderLeft: `6px solid ${getSuitabilityColor(riceData.biryani_suitability?.rating)}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1px', color: '#94a3b8' }}>
                  IDENTIFIED RICE VARIETY
                </span>
                <h2 style={{ fontSize: '2.2rem', fontWeight: '800', margin: '4px 0 6px 0', textTransform: 'capitalize' }}>
                  {riceData.type?.replace('_', ' ')}
                </h2>
                {riceData.scientific_label && (
                  <p style={{ fontStyle: 'italic', color: '#94a3b8', fontSize: '0.9rem', marginBottom: '8px' }}>
                    {riceData.scientific_label}
                  </p>
                )}
                {riceData.variety_notice && (
                  <div style={{ padding: '8px 12px', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '6px', fontSize: '0.85rem', color: '#fcd34d', maxWidth: '650px' }}>
                    <FiInfo style={{ verticalAlign: 'middle', marginRight: '6px' }} />
                    {riceData.variety_notice}
                  </div>
                )}
              </div>

              <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block' }}>Identification Confidence</span>
                  <span style={{ fontSize: '1.6rem', fontWeight: '800', color: 'var(--primary-color)' }}>
                    {(riceData.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <span style={{ padding: '4px 10px', borderRadius: '6px', background: 'rgba(255, 255, 255, 0.05)', fontSize: '0.8rem' }}>
                    Quality: <strong style={{ color: getQualityColor(riceData.quality?.indicator) }}>{riceData.quality?.indicator?.toUpperCase()}</strong>
                  </span>
                  <span style={{ padding: '4px 10px', borderRadius: '6px', background: 'rgba(255, 255, 255, 0.05)', fontSize: '0.8rem' }}>
                    Biryani Fit: <strong style={{ color: getSuitabilityColor(riceData.biryani_suitability?.rating) }}>{riceData.biryani_suitability?.rating?.toUpperCase()}</strong>
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Grid Layout: Visual Morphology & Quality */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
            
            {/* Card 1: Grain Morphology */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', color: '#60a5fa', display: 'flex', alignItems: 'center', gap: '8px' }}>
                📐 Grain Morphology & Optics
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid var(--glass-border)' }}>
                  <span style={{ color: '#cbd5e1' }}>Aspect Ratio (L/W):</span>
                  <strong>{riceData.visual_characteristics?.aspect_ratio ? `${riceData.visual_characteristics.aspect_ratio} : 1` : 'N/A'}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid var(--glass-border)' }}>
                  <span style={{ color: '#cbd5e1' }}>Median Grain Length:</span>
                  <span>{riceData.visual_characteristics?.grain_length_px ? `${riceData.visual_characteristics.grain_length_px} px` : 'Bulk Cluster'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid var(--glass-border)' }}>
                  <span style={{ color: '#cbd5e1' }}>Median Grain Width:</span>
                  <span>{riceData.visual_characteristics?.grain_width_px ? `${riceData.visual_characteristics.grain_width_px} px` : 'Bulk Cluster'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid var(--glass-border)' }}>
                  <span style={{ color: '#cbd5e1' }}>Size Uniformity:</span>
                  <span style={{ textTransform: 'capitalize' }}>{riceData.visual_characteristics?.uniformity}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid var(--glass-border)' }}>
                  <span style={{ color: '#cbd5e1' }}>Dominant Color:</span>
                  <span>{riceData.visual_characteristics?.colour}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid var(--glass-border)' }}>
                  <span style={{ color: '#cbd5e1' }}>Visible Discoloration:</span>
                  <span style={{ color: riceData.visual_characteristics?.visible_discoloration ? 'var(--warning-color)' : '#34d399' }}>
                    {riceData.visual_characteristics?.visible_discoloration ? 'Detected' : 'None Observed'}
                  </span>
                </div>
              </div>
              <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '12px', fontStyle: 'italic' }}>
                * {riceData.visual_characteristics?.calibration_note}
              </p>
            </div>

            {/* Card 2: Visual Rice Quality */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', color: '#34d399', display: 'flex', alignItems: 'center', gap: '8px' }}>
                ✨ Rice Quality Grading
              </h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '16px' }}>
                <div style={{ fontSize: '2rem', fontWeight: '800', color: getQualityColor(riceData.quality?.indicator) }}>
                  {riceData.quality?.indicator?.toUpperCase()}
                </div>
                <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                  {riceData.quality?.reason}
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '6px', borderBottom: '1px solid var(--glass-border)' }}>
                  <span style={{ color: '#cbd5e1' }}>Broken Grains:</span>
                  <span>{riceData.quality?.broken_grains !== null && riceData.quality?.broken_grains !== undefined ? `${riceData.quality.broken_grains}%` : 'Cluster assessment'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '6px', borderBottom: '1px solid var(--glass-border)' }}>
                  <span style={{ color: '#cbd5e1' }}>Foreign Matter:</span>
                  <span>{riceData.quality?.foreign_material ? '⚠️ Concerns Observed' : 'None Detected'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '6px', borderBottom: '1px solid var(--glass-border)' }}>
                  <span style={{ color: '#cbd5e1' }}>Abnormal Grains:</span>
                  <span>{riceData.quality?.abnormal_grains ? 'Observed' : 'None Detected'}</span>
                </div>
              </div>
            </div>

          </div>

          {/* Grid Layout: Biryani Suitability & Culinary Profile */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>

            {/* Card 3: Biryani Suitability */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                🍛 Biryani Suitability Prediction
              </h3>
              <div style={{ padding: '12px 16px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--glass-border)', marginBottom: '16px' }}>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block' }}>CULINARY RATING</span>
                <span style={{ fontSize: '1.4rem', fontWeight: '800', color: getSuitabilityColor(riceData.biryani_suitability?.rating) }}>
                  {riceData.biryani_suitability?.rating?.toUpperCase()}
                </span>
                <p style={{ marginTop: '8px', fontSize: '0.9rem', lineHeight: '1.5', color: '#cbd5e1' }}>
                  {riceData.biryani_suitability?.reason}
                </p>
              </div>
              <div>
                <h4 style={{ fontSize: '0.9rem', color: '#94a3b8', marginBottom: '6px' }}>Expected Cooking Characteristics:</h4>
                <p style={{ fontSize: '0.88rem', color: '#cbd5e1', lineHeight: '1.4' }}>
                  {riceData.culinary_profile?.cooking_characteristics}
                </p>
              </div>
            </div>

            {/* Card 4: Expected Culinary & Texture Profile */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', color: '#ec4899', display: 'flex', alignItems: 'center', gap: '8px' }}>
                🍲 Expected Texture & Culinary Profile
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Expected Texture:</span>
                  <p style={{ fontSize: '0.92rem', fontWeight: '500', color: '#f8fafc' }}>{riceData.culinary_profile?.expected_texture}</p>
                </div>
                <div>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Grain Separation Tendency:</span>
                  <p style={{ fontSize: '0.92rem', fontWeight: '500', color: '#f8fafc', textTransform: 'capitalize' }}>{riceData.culinary_profile?.grain_separation}</p>
                </div>
                <div>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Natural Aroma Potential:</span>
                  <p style={{ fontSize: '0.92rem', fontWeight: '500', color: '#f8fafc' }}>{riceData.culinary_profile?.aroma_potential}</p>
                </div>
                <div style={{ padding: '10px 14px', borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--glass-border)', fontSize: '0.78rem', color: '#94a3b8' }}>
                  <strong>Culinary Notice:</strong> {riceData.culinary_profile?.taste_prediction}
                </div>
              </div>
            </div>

          </div>

          {/* Grid Layout: Verified Nutrition & Glycemic Information */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>

            {/* Card 5: Verified Nutrition Profile */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <h3 style={{ fontSize: '1.2rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  🥗 Verified Nutrition Profile
                </h3>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', background: 'rgba(255, 255, 255, 0.05)', padding: '2px 8px', borderRadius: '4px' }}>
                  ICMR-NIN IFCT / USDA
                </span>
              </div>
              <p style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '14px' }}>
                {riceData.nutrition?.basis} ({riceData.nutrition?.variety_referenced})
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', marginBottom: '16px' }}>
                <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', textAlign: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Calories</span>
                  <div style={{ fontSize: '1.2rem', fontWeight: '700' }}>{riceData.nutrition?.calories_kcal ?? 'N/A'} kcal</div>
                </div>
                <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', textAlign: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Protein</span>
                  <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#60a5fa' }}>{riceData.nutrition?.protein_g ? `${riceData.nutrition.protein_g} g` : 'N/A'}</div>
                </div>
                <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', textAlign: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Carbohydrates</span>
                  <div style={{ fontSize: '1.2rem', fontWeight: '700' }}>{riceData.nutrition?.carbohydrates_g ? `${riceData.nutrition.carbohydrates_g} g` : 'N/A'}</div>
                </div>
                <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', textAlign: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Dietary Fiber</span>
                  <div style={{ fontSize: '1.2rem', fontWeight: '700' }}>{riceData.nutrition?.fiber_g ? `${riceData.nutrition.fiber_g} g` : 'N/A'}</div>
                </div>
              </div>

              {riceData.nutrition?.minerals_mg && Object.keys(riceData.nutrition.minerals_mg).length > 0 && (
                <div>
                  <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '8px' }}>Essential Minerals (per 100g raw):</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px', fontSize: '0.8rem' }}>
                    {Object.entries(riceData.nutrition.minerals_mg).map(([min, val]) => (
                      <div key={min} style={{ padding: '4px 8px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                        <span style={{ textTransform: 'capitalize', color: '#cbd5e1' }}>{min}:</span> <strong>{val} mg</strong>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <p style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '12px' }}>
                * {riceData.nutrition?.reference_note}
              </p>
            </div>

            {/* Card 6: Carbohydrate & Glycemic Information */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '14px', color: '#a78bfa', display: 'flex', alignItems: 'center', gap: '8px' }}>
                ⚡ Glycemic & Carbohydrate Insights
              </h3>
              
              <div style={{ display: 'flex', gap: '14px', alignItems: 'center', marginBottom: '14px', padding: '12px', background: 'rgba(167, 139, 250, 0.08)', borderRadius: '8px', border: '1px solid rgba(167, 139, 250, 0.2)' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: '#c4b5fd' }}>REFERENCE GLYCEMIC INDEX (GI)</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: '800', color: '#a78bfa' }}>
                    {riceData.glycemic_information?.gi ?? 'N/A'}
                  </div>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.4' }}>
                  <strong>{riceData.glycemic_information?.gi_category}</strong>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>
                    Est. Glycemic Load: {riceData.glycemic_information?.glycemic_load}
                  </p>
                </div>
              </div>

              <div style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '12px' }}>
                <strong>Amylose Content:</strong> {riceData.glycemic_information?.amylose_context}
              </div>

              <div style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: '1.5', background: 'rgba(255, 255, 255, 0.02)', padding: '12px', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                <strong style={{ color: '#a78bfa', display: 'block', marginBottom: '4px' }}>Scientific Cooking & Meal Matrix Factors:</strong>
                <p style={{ margin: 0, whiteSpace: 'pre-line', fontSize: '0.78rem', color: '#94a3b8' }}>
                  {riceData.glycemic_information?.cooking_factors}
                </p>
              </div>

              <p style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '10px' }}>
                * {riceData.glycemic_information?.limitations}
              </p>
            </div>

          </div>

          {/* Card 7: Rice-based Visual Hygiene Indicator & Scientific Safety */}
          <div className="glass-card" style={{ padding: '24px', borderLeft: '4px solid #38bdf8' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '12px', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🛡️ Rice-Based Visual Hygiene Indicator
            </h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <span style={{ fontSize: '1.1rem', fontWeight: '700' }}>
                Status: {riceData.hygiene_indicator?.rating}
              </span>
            </div>
            {riceData.hygiene_indicator?.visible_concerns?.length > 0 ? (
              <ul style={{ paddingLeft: '20px', fontSize: '0.85rem', color: '#fca5a5', marginBottom: '12px' }}>
                {riceData.hygiene_indicator.visible_concerns.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: '0.85rem', color: '#34d399', marginBottom: '12px' }}>
                ✓ No visible foreign matter, severe discoloration, or obvious physical anomalies detected.
              </p>
            )}
            <div style={{ padding: '12px 16px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '8px', border: '1px solid var(--glass-border)', fontSize: '0.78rem', color: '#94a3b8', lineHeight: '1.5' }}>
              <strong>Scientific Safety Disclosure:</strong> {riceData.hygiene_indicator?.limitations}
            </div>
          </div>

          {/* Raw JSON Transparency Viewer */}
          <div className="glass-card" style={{ padding: '16px 24px' }}>
            <button
              onClick={() => setShowJson(!showJson)}
              className="btn btn-secondary"
              style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '100%', justifyContent: 'space-between', padding: '10px 16px', fontSize: '0.9rem' }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FiCode /> View Structured JSON Response (Phase 19 Standard)
              </span>
              {showJson ? <FiChevronUp /> : <FiChevronDown />}
            </button>
            {showJson && (
              <pre style={{ marginTop: '16px', padding: '16px', background: '#0b1120', borderRadius: '8px', overflowX: 'auto', fontSize: '0.8rem', color: '#38bdf8' }}>
                {JSON.stringify(result, null, 2)}
              </pre>
            )}
          </div>

        </div>
      )}
    </div>
  );
};

export default RiceIntelligence;
