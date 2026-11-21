import React, { useState, useEffect, useCallback } from 'react';
import api from '../../api/axios';
import { formatINR, formatDateTime } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const AllOrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  // Filters
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [txFilter, setTxFilter] = useState('ALL');

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      let queryParams = [];
      if (statusFilter !== 'ALL') queryParams.push(`status=${statusFilter}`);
      if (txFilter !== 'ALL') queryParams.push(`transaction_type=${txFilter}`);

      const queryString = queryParams.length ? `?${queryParams.join('&')}` : '';

      let list = [];
      try {
        const res = await api.get(`/trading/all-orders/${queryString}`);
        list = res.data?.data || res.data?.results || res.data;
      } catch (e) {
        // Fallback to /trading/orders/
        const res = await api.get(`/trading/orders/${queryString}`);
        list = res.data?.data || res.data?.results || res.data;
      }

      setOrders(Array.isArray(list) ? list : []);
    } catch (err) {
      console.warn('Failed to fetch all orders:', err);
      setErrorMsg('Failed to fetch platform trade orders. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, txFilter]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const getStatusBadge = (status) => {
    const s = String(status || '').toUpperCase();
    if (s === 'FILLED') return <span className="badge bg-success">FILLED</span>;
    if (s === 'PENDING') return <span className="badge bg-warning text-dark">PENDING</span>;
    if (s === 'CANCELLED') return <span className="badge bg-secondary">CANCELLED</span>;
    if (s === 'REJECTED') return <span className="badge bg-danger">REJECTED</span>;
    return <span className="badge bg-light text-dark">{s}</span>;
  };

  return (
    <div className="container-fluid px-4 py-4">
      {/* Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Exchange Trade Orders</h2>
          <p className="text-muted mb-0">System-wide order book audit for all customer transactions</p>
        </div>
        <button className="btn btn-outline-primary" onClick={fetchOrders}>
          <i className="bi bi-arrow-clockwise me-1"></i> Refresh Orders
        </button>
      </div>

      <AlertBanner type="danger" message={errorMsg} onClose={() => setErrorMsg('')} />

      {/* Filters */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-body p-3">
          <div className="row g-3">
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold small text-muted">Order Status</label>
              <select
                className="form-select"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="ALL">All Statuses</option>
                <option value="PENDING">Pending Orders</option>
                <option value="FILLED">Filled / Executed Orders</option>
                <option value="CANCELLED">Cancelled Orders</option>
                <option value="REJECTED">Rejected Orders</option>
              </select>
            </div>

            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold small text-muted">Transaction Side</label>
              <select
                className="form-select"
                value={txFilter}
                onChange={(e) => setTxFilter(e.target.value)}
              >
                <option value="ALL">All Sides (BUY &amp; SELL)</option>
                <option value="BUY">Buy Orders Only</option>
                <option value="SELL">Sell Orders Only</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Orders Table */}
      <div className="card shadow-sm border-0">
        <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
          <h5 className="fw-bold mb-0">
            <i className="bi bi-card-checklist me-2 text-primary"></i> Order Book Records ({orders.length})
          </h5>
        </div>
        <div className="card-body p-0">
          {loading ? (
            <LoadingSpinner message="Fetching all platform orders..." />
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead className="table-light">
                  <tr>
                    <th className="ps-4">Timestamp</th>
                    <th>Trader / User</th>
                    <th>Stock / Symbol</th>
                    <th>Type</th>
                    <th>Side</th>
                    <th className="text-end">Qty</th>
                    <th className="text-end">Price</th>
                    <th className="pe-4 text-center">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="text-center py-5 text-muted">
                        <i className="bi bi-inbox fs-2 d-block mb-2 text-secondary"></i>
                        No orders recorded matching current filters.
                      </td>
                    </tr>
                  ) : (
                    orders.map((ord) => {
                      const userDisplay = ord.user?.username || ord.user_username || 'Customer';
                      const symbol = ord.security?.symbol || ord.symbol || '—';
                      const side = String(ord.transaction_type || ord.side || '').toUpperCase();
                      const status = String(ord.order_status || ord.status || '').toUpperCase();
                      const effectivePrice = ord.limit_price || ord.executed_price || ord.price || 0;

                      return (
                        <tr key={ord.id}>
                          <td className="ps-4 text-muted small">
                            {formatDateTime(ord.created_at)}
                          </td>
                          <td className="fw-semibold text-dark">
                            {userDisplay}
                          </td>
                          <td>
                            <span className="fw-bold text-primary">{symbol}</span>
                            <div className="text-muted small">{ord.security?.company_name || ''}</div>
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
                          <td className="pe-4 text-center">
                            {getStatusBadge(status)}
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

export default AllOrdersPage;
