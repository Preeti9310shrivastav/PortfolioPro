import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const { user, isAuthenticated, isFinanceOfficer, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(true);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  const toggleNavbar = () => {
    setCollapsed(!collapsed);
  };

  const closeNavbar = () => {
    setCollapsed(true);
  };

  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  if (!isAuthenticated) {
    return null; // Don't show navigation on public pages like login/register
  }

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow-sm">
      <div className="container-fluid px-4">
        {/* Brand */}
        <Link
          className="navbar-brand d-flex align-items-center gap-2 fw-bold text-primary"
          to={isFinanceOfficer ? '/fo/dashboard' : '/'}
          onClick={closeNavbar}
        >
          <i className="bi bi-graph-up-arrow fs-4 text-primary"></i>
          <span className="text-white">Portfolio<span className="text-primary">Pro</span></span>
        </Link>

        {/* Mobile toggle */}
        <button
          className="navbar-toggler"
          type="button"
          onClick={toggleNavbar}
          aria-controls="portfolioProNavbar"
          aria-expanded={!collapsed}
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* Links */}
        <div className={`collapse navbar-collapse ${!collapsed ? 'show' : ''}`} id="portfolioProNavbar">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            {isFinanceOfficer ? (
              <>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/fo/dashboard') ? 'active text-primary' : ''}`}
                    to="/fo/dashboard"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-speedometer2 me-1"></i> Dashboard
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/fo/users') ? 'active text-primary' : ''}`}
                    to="/fo/users"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-people me-1"></i> Users
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/fo/orders') ? 'active text-primary' : ''}`}
                    to="/fo/orders"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-card-checklist me-1"></i> All Orders
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/fo/risk') ? 'active text-primary' : ''}`}
                    to="/fo/risk"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-shield-exclamation me-1"></i> Risk
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/fo/tickets') ? 'active text-primary' : ''}`}
                    to="/fo/tickets"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-headset me-1"></i> Tickets
                  </Link>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/') ? 'active text-primary' : ''}`}
                    to="/"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-speedometer2 me-1"></i> Dashboard
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/market') ? 'active text-primary' : ''}`}
                    to="/market"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-graph-up me-1"></i> Market
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/trading') ? 'active text-primary' : ''}`}
                    to="/trading"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-arrow-left-right me-1"></i> Trading
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/orders') ? 'active text-primary' : ''}`}
                    to="/orders"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-card-list me-1"></i> Orders
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/portfolio') ? 'active text-primary' : ''}`}
                    to="/portfolio"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-pie-chart me-1"></i> Portfolio
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/watchlist') ? 'active text-primary' : ''}`}
                    to="/watchlist"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-bookmark-star me-1"></i> Watchlist
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/alerts') ? 'active text-primary' : ''}`}
                    to="/alerts"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-bell me-1"></i> Alerts
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${isActive('/support') ? 'active text-primary' : ''}`}
                    to="/support"
                    onClick={closeNavbar}
                  >
                    <i className="bi bi-question-circle me-1"></i> Support
                  </Link>
                </li>
              </>
            )}
          </ul>

          {/* User controls on right */}
          <div className="d-flex align-items-center gap-3">
            <span className="navbar-text d-flex align-items-center gap-2">
              <i className="bi bi-person-circle fs-5 text-light"></i>
              <span className="text-light fw-medium">{user?.username}</span>
              <span className={`badge ${isFinanceOfficer ? 'bg-danger' : 'bg-primary'} ms-1`}>
                {user?.role || 'Customer'}
              </span>
            </span>

            <Link
              to="/profile"
              className={`btn btn-sm btn-outline-light ${isActive('/profile') ? 'active' : ''}`}
              onClick={closeNavbar}
            >
              <i className="bi bi-gear me-1"></i> Profile
            </Link>

            <button
              onClick={handleLogout}
              className="btn btn-sm btn-outline-danger"
              type="button"
            >
              <i className="bi bi-box-arrow-right me-1"></i> Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
