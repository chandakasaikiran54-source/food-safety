import React from 'react';
import { Link } from 'react-router-dom';
import { FiCamera, FiShield, FiAlertTriangle } from 'react-icons/fi';

const LandingPage = () => {
  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%' }}>
      <header className="text-center mb-8">
        <h1 style={{ fontSize: '3rem', marginBottom: '16px', fontWeight: '800' }}>
          Check Your Food. Understand Its Safety.
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#cbd5e1', maxWidth: '600px', margin: '0 auto 32px' }}>
          AI-powered visual food safety assessment for everyday food awareness.
        </p>
        
        <div style={{ padding: '24px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', display: 'inline-block', marginBottom: '24px' }}>
            <h3 style={{ marginBottom: '16px', color: '#cbd5e1' }}>Select Access Level</h3>
            <div className="flex justify-center gap-4 flex-wrap">
              <Link to="/login" className="btn btn-primary" style={{ padding: '16px 32px', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FiCamera /> User Mode
              </Link>
              <Link to="/officer-login" className="btn btn-secondary" style={{ padding: '16px 32px', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px', borderColor: 'var(--accent-color)' }}>
                <FiShield /> Food Inspector Mode
              </Link>
            </div>
        </div>
      </header>

      <section className="glass-card mb-8" style={{ marginTop: '60px' }}>
        <h2 className="text-center mb-4" style={{ fontSize: '2rem' }}>How It Works</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', textAlign: 'center' }}>
          <div>
            <FiCamera size={48} color="var(--primary-color)" />
            <h3 className="mt-4 mb-2">1. Snap a Photo</h3>
            <p style={{ color: '#cbd5e1' }}>Use your device camera or upload an image of your food.</p>
          </div>
          <div>
            <FiShield size={48} color="var(--secondary-color)" />
            <h3 className="mt-4 mb-2">2. AI Analysis</h3>
            <p style={{ color: '#cbd5e1' }}>Our visual AI detects the food type and checks for visible hygiene concerns.</p>
          </div>
          <div>
            <FiAlertTriangle size={48} color="var(--warning-color)" />
            <h3 className="mt-4 mb-2">3. Get Safety Score</h3>
            <p style={{ color: '#cbd5e1' }}>Receive a visual safety score and recommendations instantly.</p>
          </div>
        </div>
      </section>

      <section className="glass-card mb-8" style={{ borderLeft: '4px solid var(--error-color)' }}>
        <h3 className="flex items-center" style={{ color: 'var(--error-color)', gap: '8px', marginBottom: '12px' }}>
          <FiAlertTriangle /> Important AI Limitation
        </h3>
        <p style={{ lineHeight: '1.6' }}>
          <strong>Visual analysis cannot confirm chemical or microbial contamination.</strong>
          <br/>
          This system provides an "AI Visual Food Safety Assessment" based solely on visible indicators (e.g., charring, unusual discoloration, handling signs). It does not definitively detect chemical ingredients, pesticides, bacteria, viruses, detergents, adulterants, or laboratory-level food contamination. Laboratory testing is required for confirmation of food safety.
        </p>
      </section>
    </div>
  );
};

export default LandingPage;
