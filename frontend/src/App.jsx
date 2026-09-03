import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ScanFood from './pages/ScanFood';
import Result from './pages/Result';
import History from './pages/History';
import RestaurantSearch from './pages/RestaurantSearch';
import RestaurantHistory from './pages/RestaurantHistory';
import InspectionForm from './pages/InspectionForm';
import OfficerVerification from './pages/OfficerVerification';
import ComplaintForm from './pages/ComplaintForm';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) return <div style={{textAlign: 'center', marginTop: '50px'}}>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  return children;
};

const AppContent = () => {
  return (
    <>
      <Navbar />
      <div style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/scan" element={<ProtectedRoute><ScanFood /></ProtectedRoute>} />
          <Route path="/result/:id" element={<ProtectedRoute><Result /></ProtectedRoute>} />
          <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
          <Route path="/restaurants/search" element={<ProtectedRoute><RestaurantSearch /></ProtectedRoute>} />
          <Route path="/restaurants/history" element={<ProtectedRoute><RestaurantHistory /></ProtectedRoute>} />
          <Route path="/inspect" element={<ProtectedRoute><InspectionForm /></ProtectedRoute>} />
          <Route path="/officer-verification" element={<ProtectedRoute><OfficerVerification /></ProtectedRoute>} />
          <Route path="/complaints/new" element={<ProtectedRoute><ComplaintForm /></ProtectedRoute>} />
        </Routes>
      </div>
    </>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
};

export default App;
