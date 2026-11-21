import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const FODashboardPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const [metrics, setMetrics] = useState({
    total_users: 0,
    total_customers: 0,
    total_orders: 0,
    total_tickets: 0
  });

  const fetchConsoleData = useCallback(async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      // 1. Fetch FO console metrics
      let totalUsers = 0;
      let totalCustomers = 0;
      try {
        const consoleRes = await api.get('/auth/console/finance-officer/');
        const cData = consoleRes.data?.data || consoleRes.data;
        if (cData?.system_metrics) {
          totalUsers = cData.system_metrics.total_users || 0;
          totalCustomers = cData.system_metrics.total_customers || 0;
        }
      } catch (err) {
        // Fallback fetch from /auth/users/
        try {
          const uRes = await api.get('/auth/users/');
          const uData = uRes.data?.data || uRes.data;
          totalUsers = uData?.count || (Array.isArray(uData?.users) ? uData.users.length : 0);
          totalCustomers = totalUsers;
        } catch (e2) {
          console.warn('Failed fallback user fetch:', e2);
        }
      }

      // 2. Orders count
      let totalOrders = 0;
      try {
        const ordRes = await api.get('/trading/all-orders/');
        const oData = ordRes.data?.data || ordRes.data?.results || ordRes.data;
        totalOrders = Array.isArray(oData) ? oData.length : (oData?.count || 0);
      } catch (e) {
        try {
          const ordRes = await api.get('/trading/orders/');
          const oData = ordRes.data?.data || ordRes.data?.results || ordRes.data;
          totalOrders = Array.isArray(oData) ? oData.length : (oData?.count || 0);
        } catch (e3) {
          totalOrders = 0;
        }
      }

      // 3. Tickets count
      let totalTickets = 0;
      try {
        const tktRes = await api.get('/support/all-tickets/');
        const tData = tktRes.data?.data || tktRes.data?.results || tktRes.data;
        totalTickets = Array.isArray(tData) ? tData.length : (tData?.count || 0);
      } catch (e) {
        try {
          const tktRes = await api.get('/support/tickets/');
          const tData = tktRes.data?.data || tktRes.data?.results || tktRes.data;
          totalTickets = Array.isArray(tData) ? tData.length : (tData?.count || 0);
        } catch (e3) {
          totalTickets = 0;
        }
      }

      setMetrics({
        total_users: totalUsers,
        total_customers: totalCustomers,
        total_orders: totalOrders,
        total_tickets: totalTickets
      });
    } catch (err) {
      setErrorMsg('Failed to load system metrics. Please check network connection.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConsoleData();
  }, [fetchConsoleData]);

  if (loading) {
    return <LoadingSpinner message="Loading finance officer supervisory console..." />;
  }

  return (
    <div className="container-fluid px-4 py-4">
      {/* Title */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 pb-2 border-bottom">
        <div>
          <h2 className="fw-bold mb-1">
            Finance Officer Console
          </h2>
          <p className="text-muted mb-0">
            System overview and supervisory controls for Officer <strong>{user?.username}</strong>
          </p>
        </div>
        <div className="badge bg-danger fs-6 px-3 py-2">
          <i className="bi bi-shield-check me-1"></i> Supervisory Access
        </div>
      </div>

      <AlertBanner type="danger" message={errorMsg} onClose={() => setErrorMsg('')} />

      {/* KPI Cards Row */}
      <div className="row g-3 mb-4">
        {/* Total Users */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-primary border-4 h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="text-muted small fw-semibold text-uppercase">Total Accounts</span>
                <i className="bi bi-people-fill fs-3 text-primary"></i>
              </div>
              <h2 className="fw-bold mb-1">{metrics.total_users}</h2>
              <small className="text-muted">Registered platform profiles</small>
            </div>
          </div>
        </div>

        {/* Total Customers */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-success border-4 h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="text-muted small fw-semibold text-uppercase">Active Customers</span>
                <i className="bi bi-person-check-fill fs-3 text-success"></i>
              </div>
              <h2 className="fw-bold mb-1">{metrics.total_customers}</h2>
              <small className="text-muted">Retail trading accounts</small>
            </div>
          </div>
        </div>

        {/* Total Orders */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-info border-4 h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="text-muted small fw-semibold text-uppercase">Total Orders</span>
                <i className="bi bi-card-checklist fs-3 text-info"></i>
              </div>
              <h2 className="fw-bold mb-1">{metrics.total_orders}</h2>
              <small className="text-muted">Orders submitted across exchange</small>
            </div>
          </div>
        </div>

        {/* Total Tickets */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-warning border-4 h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="text-muted small fw-semibold text-uppercase">Support Tickets</span>
                <i className="bi bi-headset fs-3 text-warning"></i>
              </div>
              <h2 className="fw-bold mb-1">{metrics.total_tickets}</h2>
              <small className="text-muted">Disputes and customer requests</small>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Links & Management Operations */}
      <h4 className="fw-bold mb-3">Supervisory Modules</h4>
      <div className="row g-4">
        {/* User Management */}
        <div className="col-12 col-md-6 col-xl-3">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body p-4 d-flex flex-column justify-content-between">
              <div>
                <div className="p-3 bg-primary-subtle text-primary rounded-circle d-inline-flex mb-3">
                  <i className="bi bi-people fs-3"></i>
                </div>
                <h5 className="fw-bold text-dark">User Management</h5>
                <p className="text-muted small">
                  Audit user identities, inspect roles, verify KYC credentials, and manage trading accounts.
                </p>
              </div>
              <Link to="/fo/users" className="btn btn-outline-primary fw-semibold mt-3">
                Manage Users <i className="bi bi-arrow-right ms-1"></i>
              </Link>
            </div>
          </div>
        </div>

        {/* All Orders */}
        <div className="col-12 col-md-6 col-xl-3">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body p-4 d-flex flex-column justify-content-between">
              <div>
                <div className="p-3 bg-success-subtle text-success rounded-circle d-inline-flex mb-3">
                  <i className="bi bi-card-checklist fs-3"></i>
                </div>
                <h5 className="fw-bold text-dark">Platform Orders</h5>
                <p className="text-muted small">
                  Audit real-time execution logs, filter by order side, and monitor high-value trades.
                </p>
              </div>
              <Link to="/fo/orders" className="btn btn-outline-success fw-semibold mt-3">
                Review Orders <i className="bi bi-arrow-right ms-1"></i>
              </Link>
            </div>
          </div>
        </div>

        {/* Risk Dashboard */}
        <div className="col-12 col-md-6 col-xl-3">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body p-4 d-flex flex-column justify-content-between">
              <div>
                <div className="p-3 bg-danger-subtle text-danger rounded-circle d-inline-flex mb-3">
                  <i className="bi bi-shield-exclamation fs-3"></i>
                </div>
                <h5 className="fw-bold text-dark">Risk Governance</h5>
                <p className="text-muted small">
                  Assess system-wide beta exposure, Value-at-Risk (VaR), and margin limits across customer portfolios.
                </p>
              </div>
              <Link to="/fo/risk" className="btn btn-outline-danger fw-semibold mt-3">
                Risk Analytics <i className="bi bi-arrow-right ms-1"></i>
              </Link>
            </div>
          </div>
        </div>

        {/* Support Tickets */}
        <div className="col-12 col-md-6 col-xl-3">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body p-4 d-flex flex-column justify-content-between">
              <div>
                <div className="p-3 bg-warning-subtle text-warning rounded-circle d-inline-flex mb-3">
                  <i className="bi bi-headset fs-3"></i>
                </div>
                <h5 className="fw-bold text-dark">Disputes &amp; Tickets</h5>
                <p className="text-muted small">
                  Investigate customer trade disputes, respond to queries, and resolve helpdesk tickets.
                </p>
              </div>
              <Link to="/fo/tickets" className="btn btn-outline-warning text-dark fw-semibold mt-3">
                Open Tickets <i className="bi bi-arrow-right ms-1"></i>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FODashboardPage;
