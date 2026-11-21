import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import { formatINR, formatDateTime } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('ALL'); // ALL, PENDING, FILLED, CANCELLED, REJECTED
  const [cancellingId, setCancellingId] = useState(null);
  const [alert, setAlert] = useState(null);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setAlert(null);
    try {
      let url = '/trading/orders/';
      if (activeTab !== 'ALL') {
        url += `?status=${activeTab}`;
      }
      const res = await api.get(url);
      const list = res.data?.data || res.data?.results || res.data;
      if (Array.isArray(list)) {
        setOrders(list);
      } else {
        setOrders([]);
      }
    } catch (err) {
      console.warn('Failed to fetch orders:', err);
      setAlert({
        type: 'danger',
        message: 'Failed to fetch trade orders. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this pending order?')) {
      return;
    }

    setCancellingId(orderId);
    setAlert(null);
    try {
      await api.post(`/trading/orders/${orderId}/cancel/`);
      setAlert({ type: 'success', message: 'Order was successfully cancelled.' });
      fetchOrders();
    } catch (err) {
      // Try alternate DELETE endpoint
      try {
        await api.delete(`/trading/orders/${orderId}/`);
        setAlert({ type: 'success', message: 'Order was cancelled.' });
        fetchOrders();
      } catch (e) {
        const msg = err.response?.data?.message || 'Could not cancel order. It may have already been filled.';
        setAlert({ type: 'danger', message: msg });
      }
    } finally {
      setCancellingId(null);
    }
  };

  const getStatusBadge = (status) => {
    const s = String(status || '').toUpperCase();
    if (s === 'FILLED') return <span className="badge bg-success">Filled</span>;
    if (s === 'PENDING') return <span className="badge bg-warning text-dark">Pending</span>;
    if (s === 'CANCELLED') return <span className="badge bg-secondary">Cancelled</span>;
    if (s === 'REJECTED') return <span className="badge bg-danger">Rejected</span>;
    return <span className="badge bg-light text-dark">{s}</span>;
  };

  const filteredOrders = orders.filter((o) => {
    if (activeTab === 'ALL') return true;
    return String(o.order_status || o.status).toUpperCase() === activeTab;
  });

  return (
    <div className="container-fluid px-4 py-4">
      {/* Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Order Book &amp; Trade History</h2>
          <p className="text-muted mb-0">Track active order executions, cancellations, and order records</p>
        </div>
        <Link to="/trading" className="btn btn-primary fw-semibold">
          <i className="bi bi-plus-circle me-1"></i> New Trade
        </Link>
      </div>

      {alert && (
        <AlertBanner
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
        />
      )}

      {/* Tabs */}
      <ul className="nav nav-pills mb-4 gap-2">
        {['ALL', 'PENDING', 'FILLED', 'CANCELLED', 'REJECTED'].map((tab) => (
          <li className="nav-item" key={tab}>
            <button
              className={`nav-link fw-semibold px-4 py-2 ${activeTab === tab ? 'active' : 'bg-white text-dark border'}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0) + tab.slice(1).toLowerCase()}
            </button>
          </li>
        ))}
      </ul>

      {/* Table Card */}
      <div className="card shadow-sm border-0">
        <div className="card-body p-0">
          {loading ? (
            <LoadingSpinner message="Fetching your orders..." />
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead className="table-light">
                  <tr>
                    <th className="ps-4">Date &amp; Time</th>
                    <th>Stock / Symbol</th>
                    <th>Type</th>
                    <th>Side</th>
                    <th className="text-end">Qty</th>
                    <th className="text-end">Price</th>
                    <th className="text-center">Status</th>
                    <th className="pe-4 text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredOrders.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="text-center py-5 text-muted">
                        <i className="bi bi-receipt fs-2 d-block mb-2 text-secondary"></i>
                        No orders found under <strong>{activeTab}</strong> tab.
                      </td>
                    </tr>
                  ) : (
                    filteredOrders.map((ord) => {
                      const side = String(ord.transaction_type || ord.side || '').toUpperCase();
                      const symbol = ord.security?.symbol || ord.symbol || '—';
                      const status = String(ord.order_status || ord.status || '').toUpperCase();
                      const isPending = status === 'PENDING';
                      const effectivePrice = ord.limit_price || ord.executed_price || ord.price || 0;

                      return (
                        <tr key={ord.id}>
                          <td className="ps-4 text-muted small">
                            {formatDateTime(ord.created_at)}
                          </td>
                          <td>
                            <div className="fw-bold text-dark">{symbol}</div>
                            <small className="text-muted">{ord.security?.company_name || ''}</small>
                          </td>
                          <td>
                            <span className="badge bg-light text-dark border">
                              {ord.order_type || 'MARKET'}
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${side === 'BUY' ? 'bg-success' : 'bg-danger'}`}>
                              {side}
                            </span>
                          </td>
                          <td className="text-end fw-semibold">
                            {ord.quantity}
                          </td>
                          <td className="text-end fw-semibold">
                            {formatINR(effectivePrice)}
                          </td>
                          <td className="text-center">
                            {getStatusBadge(status)}
                          </td>
                          <td className="pe-4 text-end">
                            {isPending ? (
                              <button
                                className="btn btn-sm btn-outline-danger"
                                disabled={cancellingId === ord.id}
                                onClick={() => handleCancelOrder(ord.id)}
                              >
                                {cancellingId === ord.id ? (
                                  <>
                                    <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                                    Cancelling...
                                  </>
                                ) : (
                                  <>
                                    <i className="bi bi-x-circle me-1"></i> Cancel
                                  </>
                                )}
                              </button>
                            ) : (
                              <span className="text-muted small">—</span>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrdersPage;
