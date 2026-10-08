import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Navbar from './components/Navbar';
import ErrorBoundary from './components/ErrorBoundary';
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
import OfficerLogin from './pages/OfficerLogin';
import InspectorDashboard from './pages/InspectorDashboard';
import RawFoodScan from './pages/RawFoodScan';
import RawFoodResult from './pages/RawFoodResult';
import MicrobialAnalysis from './pages/MicrobialAnalysis';
import MicrobialResult from './pages/MicrobialResult';
import MicrobialDashboard from './pages/MicrobialDashboard';
import FoodIdentification from './pages/FoodIdentification';
import RiceIntelligence from './pages/RiceIntelligence';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) return <div style={{textAlign: 'center', marginTop: '50px'}}>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" />;
  }
  
  return children;
};

const AppContent = () => {
  return (
    <>
      <Navbar />
      <div style={{ flex: 1 }}>
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/officer-login" element={<OfficerLogin />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/inspector-dashboard" element={<ProtectedRoute allowedRoles={['officer', 'admin']}><InspectorDashboard /></ProtectedRoute>} />
            <Route path="/scan" element={<ProtectedRoute><ScanFood /></ProtectedRoute>} />
            <Route path="/result/:id" element={<ProtectedRoute><Result /></ProtectedRoute>} />
            <Route path="/raw-food-scan" element={<ProtectedRoute><RawFoodScan /></ProtectedRoute>} />
            <Route path="/raw-food-result/:id" element={<ProtectedRoute><RawFoodResult /></ProtectedRoute>} />
            <Route path="/food-identification" element={<ProtectedRoute><FoodIdentification /></ProtectedRoute>} />
            <Route path="/rice-intelligence" element={<ProtectedRoute><RiceIntelligence /></ProtectedRoute>} />
            <Route path="/microbial-analysis" element={<ProtectedRoute><MicrobialAnalysis /></ProtectedRoute>} />
            <Route path="/microbial-result/:id" element={<ProtectedRoute><MicrobialResult /></ProtectedRoute>} />
            <Route path="/admin/microbial-dashboard" element={<ProtectedRoute allowedRoles={['officer', 'admin']}><MicrobialDashboard /></ProtectedRoute>} />
            <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
            <Route path="/restaurants/search" element={<ProtectedRoute><RestaurantSearch /></ProtectedRoute>} />
            <Route path="/restaurants/history" element={<ProtectedRoute><RestaurantHistory /></ProtectedRoute>} />
            <Route path="/inspect" element={<ProtectedRoute allowedRoles={['officer', 'admin']}><InspectionForm /></ProtectedRoute>} />
            <Route path="/officer-verification" element={<ProtectedRoute><OfficerVerification /></ProtectedRoute>} />
            <Route path="/complaints/new" element={<ProtectedRoute><ComplaintForm /></ProtectedRoute>} />
          </Routes>
        </ErrorBoundary>
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
