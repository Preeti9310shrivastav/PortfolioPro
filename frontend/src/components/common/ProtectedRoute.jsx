import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, loading, isAuthenticated } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingSpinner message="Authenticating..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole) {
    const userRole = user?.role ? String(user.role).toUpperCase() : '';
    const reqRole = requiredRole.toUpperCase();

    // Allow ADMIN to access FO routes as well
    const isAuthorized = userRole === reqRole || (reqRole === 'FINANCE_OFFICER' && userRole === 'ADMIN');

    if (!isAuthorized) {
      // Redirect unauthorized user based on their actual role
      if (userRole === 'FINANCE_OFFICER' || userRole === 'ADMIN') {
        return <Navigate to="/fo/dashboard" replace />;
      }
      return <Navigate to="/" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
