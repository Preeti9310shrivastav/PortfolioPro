import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import { formatINR, formatPercent, getPnlClass } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const WatchlistPage = () => {
  const [watchlists, setWatchlists] = useState([]);
  const [activeWatchlistId, setActiveWatchlistId] = useState(null);
  const [allSecurities, setAllSecurities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);

  // New Watchlist Form
  const [newWatchlistName, setNewWatchlistName] = useState('');
  const [creatingWatchlist, setCreatingWatchlist] = useState(false);

  // Add Stock Modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedSecToAdd, setSelectedSecToAdd] = useState('');
  const [addingStock, setAddingStock] = useState(false);

  // Load Watchlists & Securities
  const fetchData = useCallback(async () => {
    setLoading(true);
    setAlert(null);
    try {
      const [wlRes, secRes] = await Promise.all([
        api.get('/market/watchlists/'),
        api.get('/market/securities/')
      ]);

      const wlList = wlRes.data?.data || wlRes.data?.results || wlRes.data;
      const secList = secRes.data?.data || secRes.data?.results || secRes.data;

      const safeWlList = Array.isArray(wlList) ? wlList : [];
      setWatchlists(safeWlList);
      if (safeWlList.length > 0 && !activeWatchlistId) {
        setActiveWatchlistId(safeWlList[0].id);
      }

      const safeSecList = Array.isArray(secList) ? secList : [];
      setAllSecurities(safeSecList);
      if (safeSecList.length > 0) {
        setSelectedSecToAdd(safeSecList[0].id);
      }
    } catch (err) {
      console.warn('Failed to load watchlists:', err);
      setAlert({
        type: 'danger',
        message: 'Failed to fetch watchlists. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  }, [activeWatchlistId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Create new Watchlist
  const handleCreateWatchlist = async (e) => {
    e.preventDefault();
    if (!newWatchlistName.trim()) return;

    setCreatingWatchlist(true);
    try {
      const res = await api.post('/market/watchlists/', { name: newWatchlistName.trim() });
      const created = res.data?.data || res.data;
      setNewWatchlistName('');
      setAlert({ type: 'success', message: 'New watchlist created successfully!' });
      if (created?.id) {
        setActiveWatchlistId(created.id);
      }
      fetchData();
    } catch (err) {
      setAlert({
        type: 'danger',
        message: err.response?.data?.message || 'Failed to create watchlist.'
      });
    } finally {
      setCreatingWatchlist(false);
    }
  };

  // Add stock to active watchlist
  const handleAddStock = async (e) => {
    e.preventDefault();
    if (!activeWatchlistId || !selectedSecToAdd) return;

    setAddingStock(true);
    try {
      await api.post(`/market/watchlists/${activeWatchlistId}/add-security/`, {
        security_id: selectedSecToAdd
      });
      setShowAddModal(false);
      setAlert({ type: 'success', message: 'Stock added to watchlist!' });
      fetchData();
    } catch (err) {
      // Try alternate items post endpoint
      try {
        await api.post(`/market/watchlists/${activeWatchlistId}/items/`, {
          security: selectedSecToAdd
        });
        setShowAddModal(false);
        setAlert({ type: 'success', message: 'Stock added to watchlist!' });
        fetchData();
      } catch (e2) {
        setAlert({
          type: 'danger',
          message: err.response?.data?.message || 'Could not add stock to watchlist.'
        });
      }
    } finally {
      setAddingStock(false);
    }
  };

  // Remove stock from watchlist
  const handleRemoveStock = async (itemId, secId) => {
    if (!window.confirm('Remove this stock from the watchlist?')) return;

    try {
      if (itemId) {
        await api.delete(`/market/watchlists/${activeWatchlistId}/items/${itemId}/`);
      } else if (secId) {
        await api.post(`/market/watchlists/${activeWatchlistId}/remove-security/`, {
          security_id: secId
        });
      }
      setAlert({ type: 'success', message: 'Stock removed from watchlist.' });
      fetchData();
    } catch (err) {
      setAlert({
        type: 'danger',
        message: err.response?.data?.message || 'Failed to remove stock from watchlist.'
      });
    }
  };

  // Delete an entire watchlist
  const handleDeleteWatchlist = async (wlId) => {
    if (!window.confirm('Are you sure you want to delete this entire watchlist?')) return;
    try {
      await api.delete(`/market/watchlists/${wlId}/`);
      setAlert({ type: 'success', message: 'Watchlist deleted.' });
      setActiveWatchlistId(null);
      fetchData();
    } catch (err) {
      setAlert({
        type: 'danger',
        message: err.response?.data?.message || 'Could not delete watchlist.'
      });
    }
  };

  const activeWatchlist = watchlists.find((w) => w.id === activeWatchlistId) || watchlists[0] || null;
  const items = activeWatchlist?.items || [];

  if (loading) {
    return <LoadingSpinner message="Loading your watchlists..." />;
  }

  return (
    <div className="container-fluid px-4 py-4">
      {/* Page Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Watchlists</h2>
          <p className="text-muted mb-0">Organize and monitor your favorite equities in customized lists</p>
        </div>
        <div className="d-flex gap-2">
          {activeWatchlist && (
            <button
              className="btn btn-primary"
              onClick={() => setShowAddModal(true)}
            >
              <i className="bi bi-plus-lg me-1"></i> Add Stock to Watchlist
            </button>
          )}
        </div>
      </div>

      {alert && (
        <AlertBanner
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
        />
      )}

      {/* Create New Watchlist Bar */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-body p-3">
          <form onSubmit={handleCreateWatchlist} className="row g-2 align-items-center">
            <div className="col-auto">
              <label className="fw-semibold small text-muted">Create New Watchlist:</label>
            </div>
            <div className="col-12 col-sm-auto flex-grow-1">
              <input
                type="text"
                className="form-control"
                placeholder="e.g. Bluechip Titans, Tech Stars, EV Momentum"
                value={newWatchlistName}
                onChange={(e) => setNewWatchlistName(e.target.value)}
                required
              />
            </div>
            <div className="col-auto">
              <button
                type="submit"
                className="btn btn-outline-primary fw-semibold"
                disabled={creatingWatchlist}
              >
                {creatingWatchlist ? 'Creating...' : '+ Create Watchlist'}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Watchlist Tabs */}
      {watchlists.length === 0 ? (
        <div className="card shadow-sm border-0 py-5 text-center text-muted">
          <div className="card-body">
            <i className="bi bi-bookmark-star fs-1 text-secondary mb-2"></i>
            <h5>No watchlists found</h5>
            <p>Create your first watchlist above to start organizing stocks.</p>
          </div>
        </div>
      ) : (
        <>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <ul className="nav nav-tabs border-bottom-0 gap-2">
              {watchlists.map((wl) => (
                <li className="nav-item" key={wl.id}>
                  <button
                    className={`nav-link fw-semibold px-4 py-2 ${activeWatchlistId === wl.id ? 'active text-primary fw-bold' : 'text-dark'}`}
                    onClick={() => setActiveWatchlistId(wl.id)}
                  >
                    <i className="bi bi-bookmark me-1"></i> {wl.name}
                  </button>
                </li>
              ))}
            </ul>

            {activeWatchlist && (
              <button
                className="btn btn-sm btn-outline-danger"
                onClick={() => handleDeleteWatchlist(activeWatchlist.id)}
              >
                <i className="bi bi-trash me-1"></i> Delete Watchlist
              </button>
            )}
          </div>

          {/* Watchlist Items Table */}
          <div className="card shadow-sm border-0">
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th className="ps-4">Symbol</th>
                      <th>Company Name</th>
                      <th>Exchange</th>
                      <th className="text-end">LTP</th>
                      <th className="text-end">Change</th>
                      <th className="text-end">Change %</th>
                      <th className="pe-4 text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="text-center py-5 text-muted">
                          <i className="bi bi-inbox fs-3 d-block mb-2 text-secondary"></i>
                          This watchlist has no stocks added yet.
                          <div className="mt-2">
                            <button
                              className="btn btn-sm btn-outline-primary"
                              onClick={() => setShowAddModal(true)}
                            >
                              Add Stocks Now
                            </button>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      items.map((item) => {
                        const sec = item.security || item;
                        const quote = sec.quote || {};
                        const ltp = parseFloat(quote.ltp || sec.ltp || 0);
                        const change = parseFloat(quote.change_amount || sec.change_amount || 0);
                        const changePct = parseFloat(quote.change_percent || sec.change_percent || 0);

                        return (
                          <tr key={item.id || sec.id || sec.symbol}>
                            <td className="ps-4">
                              <Link to={`/market/${sec.symbol}`} className="fw-bold text-primary text-decoration-none">
                                {sec.symbol}
                              </Link>
                            </td>
                            <td className="fw-medium text-dark">
                              {sec.company_name}
                            </td>
                            <td>
                              <span className="badge bg-light text-dark border">{sec.exchange || 'NSE'}</span>
                            </td>
                            <td className={`text-end fw-bold ${getPnlClass(change)}`}>
                              {formatINR(ltp)}
                            </td>
                            <td className={`text-end fw-semibold ${getPnlClass(change)}`}>
                              {change >= 0 ? `+${change.toFixed(2)}` : change.toFixed(2)}
                            </td>
                            <td className={`text-end fw-bold ${getPnlClass(changePct)}`}>
                              {formatPercent(changePct)}
                            </td>
                            <td className="pe-4 text-end">
                              <div className="btn-group btn-group-sm">
                                <Link
                                  to={`/trading?symbol=${sec.symbol}&action=buy`}
                                  className="btn btn-outline-success"
                                >
                                  Trade
                                </Link>
                                <button
                                  className="btn btn-outline-danger"
                                  onClick={() => handleRemoveStock(item.id, sec.id)}
                                >
                                  <i className="bi bi-x-lg"></i>
                                </button>
                              </div>
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
        </>
      )}

      {/* Add Stock Modal */}
      {showAddModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content shadow-lg border-0 rounded-4">
              <div className="modal-header">
                <h5 className="modal-title fw-bold">
                  Add Stock to {activeWatchlist?.name}
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowAddModal(false)}
                ></button>
              </div>
              <form onSubmit={handleAddStock}>
                <div className="modal-body p-4">
                  <label className="form-label fw-semibold">Choose Stock</label>
                  <select
                    className="form-select form-select-lg mb-3"
                    value={selectedSecToAdd}
                    onChange={(e) => setSelectedSecToAdd(e.target.value)}
                    required
                  >
                    {allSecurities.map((sec) => (
                      <option key={sec.id} value={sec.id}>
                        {sec.symbol} — {sec.company_name} ({sec.exchange})
                      </option>
                    ))}
                  </select>
                  <small className="text-muted">
                    This security will be pinned to your <strong>{activeWatchlist?.name}</strong> watchlist.
                  </small>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowAddModal(false)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary fw-semibold"
                    disabled={addingStock}
                  >
                    {addingStock ? 'Adding...' : 'Add Stock'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WatchlistPage;
