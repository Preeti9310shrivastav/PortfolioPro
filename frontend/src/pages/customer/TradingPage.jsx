import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import { formatINR, getPnlClass } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const TradingPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [securities, setSecurities] = useState([]);
  const [account, setAccount] = useState(null);
  const [loadingInitial, setLoadingInitial] = useState(true);

  // Form State
  const [selectedSecurityId, setSelectedSecurityId] = useState('');
  const [transactionType, setTransactionType] = useState('BUY'); // BUY or SELL
  const [orderType, setOrderType] = useState('MARKET'); // MARKET or LIMIT
  const [quantity, setQuantity] = useState(1);
  const [limitPrice, setLimitPrice] = useState('');

  // Submission & Feedback State
  const [submitting, setSubmitting] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [alert, setAlert] = useState(null);

  // Fetch securities and trading account
  const loadInitialData = useCallback(async () => {
    setLoadingInitial(true);
    try {
      // Fetch securities
      const secRes = await api.get('/market/securities/');
      const secList = secRes.data?.data || secRes.data?.results || secRes.data;
      const list = Array.isArray(secList) ? secList : [];
      setSecurities(list);

      // Fetch account
      const accRes = await api.get('/accounts/trading-accounts/');
      const accList = accRes.data?.data || accRes.data?.results || accRes.data;
      if (Array.isArray(accList) && accList.length > 0) {
        setAccount(accList[0]);
      } else if (accList && typeof accList === 'object' && !Array.isArray(accList)) {
        setAccount(accList);
      }

      // Check query parameters
      const symbolParam = searchParams.get('symbol');
      const actionParam = searchParams.get('action');

      if (actionParam && (actionParam.toUpperCase() === 'BUY' || actionParam.toUpperCase() === 'SELL')) {
        setTransactionType(actionParam.toUpperCase());
      }

      if (symbolParam && list.length > 0) {
        const found = list.find((s) => s.symbol.toUpperCase() === symbolParam.toUpperCase());
        if (found) {
          setSelectedSecurityId(found.id);
          const price = found.quote?.ltp || found.ltp || 0;
          setLimitPrice(price.toString());
        }
      } else if (list.length > 0) {
        setSelectedSecurityId(list[0].id);
        const price = list[0].quote?.ltp || list[0].ltp || 0;
        setLimitPrice(price.toString());
      }
    } catch (err) {
      console.warn('Error loading trading page data:', err);
      setAlert({
        type: 'danger',
        message: 'Failed to initialize trading form. Please refresh.'
      });
    } finally {
      setLoadingInitial(false);
    }
  }, [searchParams]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Selected Security details
  const selectedSecurity = useMemo(() => {
    return securities.find((s) => s.id === selectedSecurityId) || null;
  }, [securities, selectedSecurityId]);

  // Handle stock change
  const handleSecuritySelect = (secId) => {
    setSelectedSecurityId(secId);
    const sec = securities.find((s) => s.id === secId);
    if (sec) {
      const price = sec.quote?.ltp || sec.ltp || 0;
      setLimitPrice(price.toString());
    }
  };

  const currentLtp = parseFloat(selectedSecurity?.quote?.ltp || selectedSecurity?.ltp || 0);
  const effectivePrice = orderType === 'MARKET' ? currentLtp : parseFloat(limitPrice || 0);
  const estimatedTotal = effectivePrice * (parseInt(quantity, 10) || 0);

  const availableBalance = parseFloat(account?.cash_balance || 0) - parseFloat(account?.margin_used || 0);

  // Validate and open confirmation
  const handleReviewOrder = (e) => {
    e.preventDefault();
    setAlert(null);

    const qty = parseInt(quantity, 10);
    if (!qty || qty <= 0) {
      setAlert({ type: 'danger', message: 'Quantity must be at least 1 share.' });
      return;
    }

    if (orderType === 'LIMIT' && (!limitPrice || parseFloat(limitPrice) <= 0)) {
      setAlert({ type: 'danger', message: 'Please specify a valid limit price greater than ₹0.' });
      return;
    }

    if (transactionType === 'BUY' && estimatedTotal > availableBalance) {
      setAlert({
        type: 'danger',
        message: `Insufficient funds. Available: ${formatINR(availableBalance)}, Required: ${formatINR(estimatedTotal)}.`
      });
      return;
    }

    setShowConfirmModal(true);
  };

  // Submit order to API
  const handleConfirmOrder = async () => {
    setSubmitting(true);
    setAlert(null);

    const payload = {
      security: selectedSecurity?.id,
      security_id: selectedSecurity?.id,
      symbol: selectedSecurity?.symbol,
      transaction_type: transactionType,
      order_type: orderType,
      quantity: parseInt(quantity, 10),
      limit_price: orderType === 'LIMIT' ? parseFloat(limitPrice) : null
    };

    try {
      const res = await api.post('/trading/orders/', payload);
      setShowConfirmModal(false);
      setAlert({
        type: 'success',
        message: res.data?.message || `Order placed successfully! ${transactionType} ${quantity}x ${selectedSecurity?.symbol}.`
      });

      // Refresh account balance
      try {
        const accRes = await api.get('/accounts/trading-accounts/');
        const accList = accRes.data?.data || accRes.data?.results || accRes.data;
        if (Array.isArray(accList) && accList.length > 0) {
          setAccount(accList[0]);
        }
      } catch (e) {
        // Silent error
      }
    } catch (err) {
      const resData = err.response?.data;
      setShowConfirmModal(false);
      setAlert({
        type: 'danger',
        message: resData?.message || 'Failed to submit order. Please check inputs.',
        errors: resData?.errors
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingInitial) {
    return <LoadingSpinner message="Preparing trading console..." />;
  }

  return (
    <div className="container-fluid px-4 py-4">
      {/* Page Title */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Place Trade Order</h2>
          <p className="text-muted mb-0">Direct market order entry for equities on NSE/BSE</p>
        </div>
        <button
          className="btn btn-outline-secondary"
          onClick={() => navigate('/orders')}
        >
          <i className="bi bi-clock-history me-1"></i> Order Book
        </button>
      </div>

      {alert && (
        <AlertBanner
          type={alert.type}
          message={alert.message}
          errors={alert.errors}
          onClose={() => setAlert(null)}
        />
      )}

      <div className="row g-4">
        {/* Left Column: Order Ticket Form */}
        <div className="col-12 col-lg-7">
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white py-3">
              <h5 className="fw-bold mb-0">
                <i className="bi bi-terminal me-2 text-primary"></i> Order Entry Ticket
              </h5>
            </div>
            <div className="card-body p-4">
              <form onSubmit={handleReviewOrder}>
                {/* Transaction Type: BUY / SELL Buttons */}
                <div className="mb-4">
                  <label className="form-label fw-semibold small text-uppercase text-muted">Transaction Side</label>
                  <div className="btn-group w-100" role="group">
                    <button
                      type="button"
                      className={`btn py-2 fw-bold ${transactionType === 'BUY' ? 'btn-success text-white' : 'btn-outline-success'}`}
                      onClick={() => setTransactionType('BUY')}
                    >
                      <i className="bi bi-arrow-up-circle me-1"></i> BUY (LONG)
                    </button>
                    <button
                      type="button"
                      className={`btn py-2 fw-bold ${transactionType === 'SELL' ? 'btn-danger text-white' : 'btn-outline-danger'}`}
                      onClick={() => setTransactionType('SELL')}
                    >
                      <i className="bi bi-arrow-down-circle me-1"></i> SELL (EXIT)
                    </button>
                  </div>
                </div>

                {/* Stock Selector */}
                <div className="mb-3">
                  <label className="form-label fw-semibold small">Select Security / Stock</label>
                  <select
                    className="form-select form-select-lg"
                    value={selectedSecurityId}
                    onChange={(e) => handleSecuritySelect(e.target.value)}
                    required
                  >
                    {securities.map((sec) => (
                      <option key={sec.id} value={sec.id}>
                        {sec.symbol} — {sec.company_name} ({sec.exchange}) — CMP: {formatINR(sec.quote?.ltp || sec.ltp || 0)}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Order Type Toggle: MARKET / LIMIT */}
                <div className="mb-3">
                  <label className="form-label fw-semibold small">Order Type</label>
                  <div className="d-flex gap-3">
                    <div className="form-check">
                      <input
                        className="form-check-input"
                        type="radio"
                        name="orderType"
                        id="marketOrderRadio"
                        value="MARKET"
                        checked={orderType === 'MARKET'}
                        onChange={() => setOrderType('MARKET')}
                      />
                      <label className="form-check-label fw-semibold" htmlFor="marketOrderRadio">
                        Market Order <span className="text-muted fw-normal small">(Immediate fill @ CMP)</span>
                      </label>
                    </div>
                    <div className="form-check">
                      <input
                        className="form-check-input"
                        type="radio"
                        name="orderType"
                        id="limitOrderRadio"
                        value="LIMIT"
                        checked={orderType === 'LIMIT'}
                        onChange={() => setOrderType('LIMIT')}
                      />
                      <label className="form-check-label fw-semibold" htmlFor="limitOrderRadio">
                        Limit Order <span className="text-muted fw-normal small">(Specified price or better)</span>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Quantity and Price Row */}
                <div className="row g-3 mb-4">
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">Quantity (Shares)</label>
                    <div className="input-group">
                      <span className="input-group-text bg-light text-muted">
                        <i className="bi bi-stack"></i>
                      </span>
                      <input
                        type="number"
                        min="1"
                        step="1"
                        className="form-control"
                        placeholder="e.g. 10"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  {orderType === 'LIMIT' && (
                    <div className="col-12 col-md-6">
                      <label className="form-label fw-semibold small">Limit Price (₹)</label>
                      <div className="input-group">
                        <span className="input-group-text bg-light text-muted">₹</span>
                        <input
                          type="number"
                          step="0.05"
                          min="0.05"
                          className="form-control"
                          placeholder="e.g. 2450.50"
                          value={limitPrice}
                          onChange={(e) => setLimitPrice(e.target.value)}
                          required
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Order Summary & Submit Button */}
                <div className="p-3 bg-light rounded mb-4">
                  <div className="d-flex justify-content-between mb-1">
                    <span className="text-muted">Estimated Execution Price:</span>
                    <span className="fw-semibold">{formatINR(effectivePrice)}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1">
                    <span className="text-muted">Estimated Order Total:</span>
                    <span className="fw-bold fs-5 text-dark">{formatINR(estimatedTotal)}</span>
                  </div>
                  <div className="d-flex justify-content-between">
                    <span className="text-muted">Available Cash Balance:</span>
                    <span className={`fw-semibold ${availableBalance >= estimatedTotal ? 'text-success' : 'text-danger'}`}>
                      {formatINR(availableBalance)}
                    </span>
                  </div>
                </div>

                <button
                  type="submit"
                  className={`btn w-100 py-3 fw-bold shadow-sm ${transactionType === 'BUY' ? 'btn-success' : 'btn-danger'}`}
                >
                  <i className="bi bi-send-check me-2"></i>
                  Review &amp; Place {transactionType} Order
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Right Column: Selected Stock Overview */}
        <div className="col-12 col-lg-5">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white py-3">
              <h5 className="fw-bold mb-0">
                <i className="bi bi-info-circle me-2 text-primary"></i> Market Snapshot
              </h5>
            </div>
            <div className="card-body p-4">
              {selectedSecurity ? (
                <>
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <div>
                      <h4 className="fw-bold mb-0 text-dark">{selectedSecurity.symbol}</h4>
                      <small className="text-muted">{selectedSecurity.company_name}</small>
                    </div>
                    <span className="badge bg-primary px-3 py-2">{selectedSecurity.exchange || 'NSE'}</span>
                  </div>

                  <div className="p-3 bg-light rounded mb-3">
                    <div className="text-muted small">Current Market Price (CMP)</div>
                    <h3 className={`fw-bold mb-0 ${getPnlClass(selectedSecurity.quote?.change_percent)}`}>
                      {formatINR(currentLtp)}
                    </h3>
                  </div>

                  <ul className="list-group list-group-flush small">
                    <li className="list-group-item d-flex justify-content-between px-0">
                      <span className="text-muted">Sector</span>
                      <span className="fw-semibold">{selectedSecurity.sector || 'General'}</span>
                    </li>
                    <li className="list-group-item d-flex justify-content-between px-0">
                      <span className="text-muted">Lot Size</span>
                      <span className="fw-semibold">{selectedSecurity.lot_size || 1} share</span>
                    </li>
                    <li className="list-group-item d-flex justify-content-between px-0">
                      <span className="text-muted">Day High / Low</span>
                      <span className="fw-semibold">
                        {formatINR(selectedSecurity.quote?.high_price || currentLtp)} / {formatINR(selectedSecurity.quote?.low_price || currentLtp)}
                      </span>
                    </li>
                    <li className="list-group-item d-flex justify-content-between px-0">
                      <span className="text-muted">Volume</span>
                      <span className="fw-semibold">{Number(selectedSecurity.quote?.volume || 0).toLocaleString('en-IN')}</span>
                    </li>
                  </ul>
                </>
              ) : (
                <div className="text-center text-muted py-4">No stock selected.</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content shadow-lg border-0 rounded-4">
              <div className="modal-header">
                <h5 className="modal-title fw-bold">
                  Confirm {transactionType} Order
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowConfirmModal(false)}
                ></button>
              </div>
              <div className="modal-body p-4">
                <p className="text-muted mb-3">
                  Please review the order details before transmitting to the exchange:
                </p>
                <div className="p-3 bg-light rounded">
                  <div className="d-flex justify-content-between mb-2">
                    <span className="text-muted">Stock Symbol:</span>
                    <span className="fw-bold">{selectedSecurity?.symbol}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-2">
                    <span className="text-muted">Side:</span>
                    <span className={`badge ${transactionType === 'BUY' ? 'bg-success' : 'bg-danger'}`}>
                      {transactionType}
                    </span>
                  </div>
                  <div className="d-flex justify-content-between mb-2">
                    <span className="text-muted">Order Type:</span>
                    <span className="fw-bold">{orderType}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-2">
                    <span className="text-muted">Quantity:</span>
                    <span className="fw-bold">{quantity} shares</span>
                  </div>
                  <div className="d-flex justify-content-between mb-2">
                    <span className="text-muted">Price:</span>
                    <span className="fw-bold">{orderType === 'MARKET' ? 'Market (CMP)' : formatINR(limitPrice)}</span>
                  </div>
                  <hr className="my-2" />
                  <div className="d-flex justify-content-between">
                    <span className="fw-bold">Total Consideration:</span>
                    <span className="fw-bold fs-5 text-primary">{formatINR(estimatedTotal)}</span>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowConfirmModal(false)}
                >
                  Modify Order
                </button>
                <button
                  type="button"
                  className={`btn ${transactionType === 'BUY' ? 'btn-success' : 'btn-danger'} fw-bold px-4`}
                  disabled={submitting}
                  onClick={handleConfirmOrder}
                >
                  {submitting ? 'Placing Order...' : 'Confirm & Transmit'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TradingPage;
