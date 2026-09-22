import React from 'react';
import { Link } from 'react-router-dom';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px 5%', textAlign: 'center', minHeight: '60vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
          <h2 style={{ color: 'var(--error-color)', marginBottom: '16px' }}>Oops! Something went wrong.</h2>
          <p style={{ color: '#cbd5e1', marginBottom: '24px', maxWidth: '500px' }}>
            We encountered an unexpected error while loading this page. 
            {this.state.error && <span style={{ display: 'block', marginTop: '8px', fontSize: '0.85rem', color: '#94a3b8' }}>{this.state.error.message}</span>}
          </p>
          <div style={{ display: 'flex', gap: '16px' }}>
            <button className="btn btn-primary" onClick={() => window.location.reload()}>Try Again</button>
            <Link to="/dashboard" className="btn btn-secondary" onClick={() => this.setState({ hasError: false })}>Return to Dashboard</Link>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
