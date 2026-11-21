import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Layout & Components
import Navbar from './components/navigation/Navbar';
import ProtectedRoute from './components/common/ProtectedRoute';

// Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ProfilePage from './pages/auth/ProfilePage';

// Customer Pages
import DashboardPage from './pages/customer/DashboardPage';
import MarketPage from './pages/customer/MarketPage';
import StockDetailPage from './pages/customer/StockDetailPage';
import TradingPage from './pages/customer/TradingPage';
import OrdersPage from './pages/customer/OrdersPage';
import PortfolioPage from './pages/customer/PortfolioPage';
import WatchlistPage from './pages/customer/WatchlistPage';
import AlertsPage from './pages/customer/AlertsPage';
import SupportPage from './pages/customer/SupportPage';

// Finance Officer Pages
import FODashboardPage from './pages/finance_officer/FODashboardPage';
import UserManagementPage from './pages/finance_officer/UserManagementPage';
import AllOrdersPage from './pages/finance_officer/AllOrdersPage';
import RiskDashboardPage from './pages/finance_officer/RiskDashboardPage';
import TicketManagementPage from './pages/finance_officer/TicketManagementPage';

function App() {
  return (
    <div className="min-vh-100 d-flex flex-column">
      <Navbar />
      <main className="flex-grow-1">
        <Routes>
          {/* Public Authentication Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Customer Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/market"
            element={
              <ProtectedRoute>
                <MarketPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/market/:symbol"
            element={
              <ProtectedRoute>
                <StockDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trading"
            element={
              <ProtectedRoute>
                <TradingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders"
            element={
              <ProtectedRoute>
                <OrdersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/portfolio"
            element={
              <ProtectedRoute>
                <PortfolioPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/watchlist"
            element={
              <ProtectedRoute>
                <WatchlistPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/alerts"
            element={
              <ProtectedRoute>
                <AlertsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/support"
            element={
              <ProtectedRoute>
                <SupportPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />

          {/* Protected Finance Officer Routes */}
          <Route
            path="/fo/dashboard"
            element={
              <ProtectedRoute requiredRole="FINANCE_OFFICER">
                <FODashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/fo/users"
            element={
              <ProtectedRoute requiredRole="FINANCE_OFFICER">
                <UserManagementPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/fo/orders"
            element={
              <ProtectedRoute requiredRole="FINANCE_OFFICER">
                <AllOrdersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/fo/risk"
            element={
              <ProtectedRoute requiredRole="FINANCE_OFFICER">
                <RiskDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/fo/tickets"
            element={
              <ProtectedRoute requiredRole="FINANCE_OFFICER">
                <TicketManagementPage />
              </ProtectedRoute>
            }
          />

          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
