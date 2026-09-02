import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiCamera, FiUpload, FiRefreshCw } from 'react-icons/fi';
import api from '../utils/api';

const ScanFood = () => {
  const [stream, setStream] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [cameraLoading, setCameraLoading] = useState(false);
  const [videoReady, setVideoReady] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const navigate = useNavigate();

  const startCamera = async () => {
    if (!window.isSecureContext && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      setError('Camera access requires HTTPS or localhost. Please open the application using a secure connection.');
      return;
    }

    setCameraLoading(true);
    setError('');
    
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: { ideal: 'environment' } },
        audio: false
      }).catch(async (e) => {
        // Fallback to any camera if environment facing fails or is unavailable
        return await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      });
      
      setStream(mediaStream);
      setImagePreview(null);
      setFile(null);
      setVideoReady(false);
    } catch (err) {
      console.error("Camera error:", err);
      setCameraLoading(false);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError' || err.name === 'SecurityError') {
        setError('Camera permission denied. Please allow camera access in your browser settings.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setError('No camera found on this device.');
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        setError('Camera is already in use by another application.');
      } else {
        setError('Camera access denied or unavailable. Please upload an image instead.');
      }
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setVideoReady(false);
    } else if (videoRef.current && videoRef.current.srcObject) {
      // Fallback cleanup
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    }
  };

  const captureImage = () => {
    if (videoRef.current && canvasRef.current && videoReady) {
      const videoWidth = videoRef.current.videoWidth;
      const videoHeight = videoRef.current.videoHeight;
      
      if (videoWidth === 0 || videoHeight === 0) {
        setError('Camera is not ready yet. Please try again.');
        return;
      }

      const context = canvasRef.current.getContext('2d');
      canvasRef.current.width = videoWidth;
      canvasRef.current.height = videoHeight;
      context.drawImage(videoRef.current, 0, 0, videoWidth, videoHeight);
      
      canvasRef.current.toBlob((blob) => {
        if (!blob) {
          setError('Failed to capture image. Please try again.');
          return;
        }
        const capturedFile = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
        setFile(capturedFile);
        setImagePreview(URL.createObjectURL(blob));
        stopCamera();
      }, 'image/jpeg', 0.9);
    }
  };

  const handleFileUpload = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setImagePreview(URL.createObjectURL(selectedFile));
      stopCamera();
      setError('');
    }
  };

  const handleRetake = () => {
    setImagePreview(null);
    setFile(null);
    startCamera();
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('image', file);

    try {
      const res = await api.post('/scans/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      if (res.data.success) {
        navigate(`/result/${res.data.data._id}`);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Error analyzing image. Please try again.');
      setLoading(false);
    }
  };

  // Attach stream when video element renders
  React.useEffect(() => {
    if (stream && videoRef.current && !videoRef.current.srcObject) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  // Cleanup camera on unmount
  React.useEffect(() => {
    return () => stopCamera();
  }, []);

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '800px', margin: '0 auto' }}>
      <h2 className="text-center mb-8">Scan Your Food</h2>
      
      {error && <div className="text-error mb-4 text-center glass-card" style={{ padding: '16px', borderColor: 'var(--error-color)' }}>{error}</div>}

      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: '400px', justifyContent: 'center' }}>
        
        {loading ? (
          <div className="text-center">
            <FiRefreshCw size={48} color="var(--primary-color)" style={{ animation: 'spin 2s linear infinite', marginBottom: '16px' }} />
            <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
            <h3>Analyzing your food...</h3>
            <p style={{ color: '#cbd5e1', marginTop: '8px' }}>Please wait while our AI visual assessment runs.</p>
          </div>
        ) : imagePreview ? (
          <div style={{ width: '100%', textAlign: 'center' }}>
            <img src={imagePreview} alt="Captured food" style={{ maxWidth: '100%', maxHeight: '400px', borderRadius: '8px', marginBottom: '24px' }} />
            <div className="flex justify-center gap-4">
              <button className="btn btn-secondary" onClick={handleRetake}>Retake</button>
              <button className="btn btn-primary" onClick={handleAnalyze}>Analyze Food</button>
            </div>
          </div>
        ) : stream ? (
          <div style={{ width: '100%', textAlign: 'center' }}>
            {cameraLoading && !videoReady && <p style={{ color: '#cbd5e1', marginBottom: '16px' }}>Starting camera...</p>}
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted
              onLoadedMetadata={() => {
                if (videoRef.current) {
                  videoRef.current.play().catch(e => console.error("Video play error:", e));
                  if (videoRef.current.videoWidth > 0 && videoRef.current.videoHeight > 0) {
                    setVideoReady(true);
                    setCameraLoading(false);
                  }
                }
              }}
              onCanPlay={() => {
                if (videoRef.current && videoRef.current.videoWidth > 0 && videoRef.current.videoHeight > 0) {
                  setVideoReady(true);
                  setCameraLoading(false);
                }
              }}
              style={{ width: '100%', height: '100%', objectFit: 'cover', maxWidth: '100%', maxHeight: '400px', borderRadius: '8px', marginBottom: '24px', backgroundColor: '#000' }}
            ></video>
            <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
            <div className="flex justify-center gap-4">
              <button className="btn btn-secondary" onClick={stopCamera}>Cancel</button>
              <button 
                className={`btn ${videoReady && !cameraLoading ? 'btn-primary' : 'btn-secondary'}`} 
                onClick={captureImage} 
                disabled={!videoReady || cameraLoading}
              >
                {videoReady ? 'Capture Photo' : 'Waiting for camera...'}
              </button>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', width: '100%', maxWidth: '300px' }}>
            <button className="btn btn-primary w-full" onClick={startCamera} style={{ padding: '16px' }}>
              <FiCamera style={{ marginRight: '8px' }} /> Open Camera
            </button>
            <div style={{ position: 'relative', textAlign: 'center' }}>
              <hr style={{ borderColor: 'var(--glass-border)' }} />
              <span style={{ position: 'absolute', top: '-10px', left: '50%', transform: 'translateX(-50%)', background: 'var(--card-bg)', padding: '0 10px', color: '#cbd5e1' }}>OR</span>
            </div>
            <label className="btn btn-secondary w-full" style={{ padding: '16px', cursor: 'pointer' }}>
              <FiUpload style={{ marginRight: '8px' }} /> Upload Image
              <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFileUpload} />
            </label>
          </div>
        )}

      </div>
    </div>
  );
};

export default ScanFood;
