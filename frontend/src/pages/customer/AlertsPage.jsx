import React, { useState, useEffect, useCallback } from 'react';
import api from '../../api/axios';
import { formatINR, formatDateTime } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const AlertsPage = () => {
  const [alerts, setAlerts] = useState([]);
  const [securities, setSecurities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bannerAlert, setBannerAlert] = useState(null);

  // Form State
  const [selectedSecurityId, setSelectedSecurityId] = useState('');
  const [condition, setCondition] = useState('ABOVE'); // ABOVE or BELOW
  const [targetValue, setTargetValue] = useState('');
  const [creating, setCreating] = useState(false);

  const fetchAlertsAndSecurities = useCallback(async () => {
    setLoading(true);
    setBannerAlert(null);
    try {
      const [alertRes, secRes] = await Promise.all([
        api.get('/notifications/alerts/'),
        api.get('/market/securities/')
      ]);

      const aList = alertRes.data?.data || alertRes.data?.results || alertRes.data;
      const sList = secRes.data?.data || secRes.data?.results || secRes.data;

      setAlerts(Array.isArray(aList) ? aList : []);

      const safeSecList = Array.isArray(sList) ? sList : [];
      setSecurities(safeSecList);
      if (safeSecList.length > 0 && !selectedSecurityId) {
        setSelectedSecurityId(safeSecList[0].id);
        const ltp = safeSecList[0].quote?.ltp || safeSecList[0].ltp || 0;
        setTargetValue(ltp.toString());
      }
    } catch (err) {
      console.warn('Failed to fetch price alerts:', err);
      setBannerAlert({
        type: 'danger',
        message: 'Failed to load price alerts. Please try again later.'
      });
    } finally {
      setLoading(false);
    }
  }, [selectedSecurityId]);

  useEffect(() => {
    fetchAlertsAndSecurities();
  }, [fetchAlertsAndSecurities]);

  const handleStockChange = (secId) => {
    setSelectedSecurityId(secId);
    const sec = securities.find((s) => s.id === secId);
    if (sec) {
      const ltp = sec.quote?.ltp || sec.ltp || 0;
      setTargetValue(ltp.toString());
    }
  };

  const handleCreateAlert = async (e) => {
    e.preventDefault();
    if (!selectedSecurityId || !targetValue || parseFloat(targetValue) <= 0) {
      setBannerAlert({ type: 'danger', message: 'Please select a valid stock and target price.' });
      return;
    }

    setCreating(true);
    try {
      const payload = {
        security: selectedSecurityId,
        security_id: selectedSecurityId,
        condition,
        target_value: parseFloat(targetValue)
      };

      await api.post('/notifications/alerts/', payload);
      setBannerAlert({ type: 'success', message: 'Price alert created successfully!' });
      fetchAlertsAndSecurities();
    } catch (err) {
      setBannerAlert({
        type: 'danger',
        message: err.response?.data?.message || 'Failed to create price alert.'
      });
    } finally {
      setCreating(false);
    }
  };

  const handleToggleActive = async (alertItem) => {
    try {
      const newStatus = !alertItem.is_active;
      await api.patch(`/notifications/alerts/${alertItem.id}/`, { is_active: newStatus });
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertItem.id ? { ...a, is_active: newStatus } : a))
      );
    } catch (err) {
      setBannerAlert({
        type: 'danger',
        message: 'Could not toggle alert state.'
      });
    }
  };

  const handleDeleteAlert = async (alertId) => {
    if (!window.confirm('Delete this price alert?')) return;
    try {
      await api.delete(`/notifications/alerts/${alertId}/`);
      setAlerts((prev) => prev.filter((a) => a.id !== alertId));
      setBannerAlert({ type: 'success', message: 'Alert deleted successfully.' });
    } catch (err) {
      setBannerAlert({
        type: 'danger',
        message: 'Failed to delete alert.'
      });
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading price alerts..." />;
  }

  return (
    <div className="container-fluid px-4 py-4">
      {/* Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Price Alerts</h2>
          <p className="text-muted mb-0">Set automated notifications when stocks cross your target price levels</p>
        </div>
      </div>

      {bannerAlert && (
        <AlertBanner
          type={bannerAlert.type}
          message={bannerAlert.message}
          onClose={() => setBannerAlert(null)}
        />
      )}

      <div className="row g-4">
        {/* Left Column: Create Alert Form */}
        <div className="col-12 col-lg-4">
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white py-3">
              <h5 className="fw-bold mb-0">
                <i className="bi bi-bell-plus me-2 text-primary"></i> Create Price Alert
              </h5>
            </div>
            <div className="card-body p-4">
              <form onSubmit={handleCreateAlert}>
                {/* Select Stock */}
                <div className="mb-3">
                  <label className="form-label fw-semibold small">Stock / Security</label>
                  <select
                    className="form-select"
                    value={selectedSecurityId}
                    onChange={(e) => handleStockChange(e.target.value)}
                    required
                  >
                    {securities.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.symbol} ({s.company_name})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Condition */}
                <div className="mb-3">
                  <label className="form-label fw-semibold small">Trigger Condition</label>
                  <select
                    className="form-select"
                    value={condition}
                    onChange={(e) => setCondition(e.target.value)}
                  >
                    <option value="ABOVE">Price Rises Above Target ( &gt;= )</option>
                    <option value="BELOW">Price Drops Below Target ( &lt;= )</option>
                  </select>
                </div>

                {/* Target Price */}
                <div className="mb-4">
                  <label className="form-label fw-semibold small">Target Price (₹)</label>
                  <div className="input-group">
                    <span className="input-group-text bg-light text-muted">₹</span>
                    <input
                      type="number"
                      step="0.05"
                      min="0.05"
                      className="form-control"
                      placeholder="e.g. 2600.00"
                      value={targetValue}
                      onChange={(e) => setTargetValue(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100 py-2 fw-semibold"
                  disabled={creating}
                >
                  {creating ? 'Creating Alert...' : 'Set Price Alert'}
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Right Column: Active Alerts Table */}
        <div className="col-12 col-lg-8">
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 className="fw-bold mb-0">
                <i className="bi bi-bell me-2 text-primary"></i> Configured Alerts
              </h5>
              <span className="badge bg-secondary">{alerts.length} Total</span>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th className="ps-4">Stock</th>
                      <th>Condition</th>
                      <th className="text-end">Target Price</th>
                      <th className="text-center">Active</th>
                      <th className="text-center">Triggered</th>
                      <th className="pe-4 text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {alerts.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="text-center py-5 text-muted">
                          <i className="bi bi-bell-slash fs-2 d-block mb-2 text-secondary"></i>
                          No price alerts created yet. Use the form on the left to set an alert.
                        </td>
                      </tr>
                    ) : (
                      alerts.map((alt) => {
                        const sec = alt.security || {};
                        const symbol = sec.symbol || alt.symbol || '—';
                        const condText = alt.condition === 'ABOVE' ? 'Rises Above' : 'Drops Below';

                        return (
                          <tr key={alt.id}>
                            <td className="ps-4 fw-bold text-primary">
                              {symbol}
                              <div className="text-muted small fw-normal">{sec.company_name}</div>
                            </td>
                            <td>
                              <span className={`badge ${alt.condition === 'ABOVE' ? 'bg-success' : 'bg-warning text-dark'}`}>
                                {condText}
                              </span>
                            </td>
                            <td className="text-end fw-bold">
                              {formatINR(alt.target_value)}
                            </td>
                            <td className="text-center">
                              <div className="form-check form-switch d-inline-block">
                                <input
                                  className="form-check-input cursor-pointer"
                                  type="checkbox"
                                  checked={!!alt.is_active}
                                  onChange={() => handleToggleActive(alt)}
                                />
                              </div>
                            </td>
                            <td className="text-center">
                              {alt.is_triggered ? (
                                <span className="badge bg-danger" title={formatDateTime(alt.triggered_at)}>
                                  Triggered
                                </span>
                              ) : (
                                <span className="badge bg-light text-muted border">
                                  Pending
                                </span>
                              )}
                            </td>
                            <td className="pe-4 text-end">
                              <button
                                className="btn btn-sm btn-outline-danger"
                                onClick={() => handleDeleteAlert(alt.id)}
                                title="Delete Alert"
                              >
                                <i className="bi bi-trash"></i>
                              </button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertsPage;
