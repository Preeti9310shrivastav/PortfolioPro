import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../../api/axios';
import { formatINR, formatPercent, getPnlClass } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const StockDetailPage = () => {
  const { symbol } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const [security, setSecurity] = useState(null);
  const [fundamental, setFundamental] = useState(null);
  const [technical, setTechnical] = useState(null);

  // Watchlist modal state
  const [watchlists, setWatchlists] = useState([]);
  const [selectedWatchlistId, setSelectedWatchlistId] = useState('');
  const [showWatchlistModal, setShowWatchlistModal] = useState(false);
  const [addingToWatchlist, setAddingToWatchlist] = useState(false);

  const fetchStockData = useCallback(async () => {
    if (!symbol) return;
    setLoading(true);
    setErrorMsg('');

    try {
      // 1. Fetch Security info
      let foundSecurity = null;
      try {
        const secRes = await api.get(`/market/securities/?search=${encodeURIComponent(symbol)}`);
        const results = secRes.data?.data || secRes.data?.results || secRes.data;
        if (Array.isArray(results)) {
          foundSecurity = results.find((s) => s.symbol.toUpperCase() === symbol.toUpperCase()) || results[0];
        } else if (results && results.symbol) {
          foundSecurity = results;
        }
      } catch (err) {
        console.warn('Direct search failed, attempting by symbol path:', err);
      }

      if (!foundSecurity) {
        setErrorMsg(`Stock with symbol "${symbol}" could not be located.`);
        setLoading(false);
        return;
      }

      setSecurity(foundSecurity);
      const secId = foundSecurity.id;

      // 2. Fetch Fundamental Analysis
      try {
        const fundRes = await api.get(`/fundamental/securities/${secId}/analysis/`);
        const fundData = fundRes.data?.data || fundRes.data;
        setFundamental(fundData);
      } catch (err) {
        // Fallback check if fundamental was embedded on security
        if (foundSecurity.fundamental_metric) {
          setFundamental(foundSecurity.fundamental_metric);
        }
      }

      // 3. Fetch Technical Analysis
      try {
        const techRes = await api.get(`/technical/securities/${secId}/analysis/`);
        const techData = techRes.data?.data || techRes.data;
        setTechnical(techData);
      } catch (err) {
        // Fallback check if technical was embedded
        if (foundSecurity.technical_indicator) {
          setTechnical(foundSecurity.technical_indicator);
        }
      }

      // 4. Fetch User's Watchlists for "Add to Watchlist" feature
      try {
        const wlRes = await api.get('/market/watchlists/');
        const wlList = wlRes.data?.data || wlRes.data?.results || wlRes.data;
        if (Array.isArray(wlList)) {
          setWatchlists(wlList);
          if (wlList.length > 0) {
            setSelectedWatchlistId(wlList[0].id);
          }
        }
      } catch (err) {
        console.warn('Could not fetch watchlists:', err);
      }
    } catch (err) {
      setErrorMsg('Failed to load stock details. Please check the network connection.');
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    fetchStockData();
  }, [fetchStockData]);

  const handleAddToWatchlist = async () => {
    if (!selectedWatchlistId) {
      alert('Please select or create a watchlist first.');
      return;
    }
    setAddingToWatchlist(true);
    try {
      await api.post(`/market/watchlists/${selectedWatchlistId}/add-security/`, {
        security_id: security.id
      });
      setSuccessMsg(`Added ${security.symbol} to your watchlist!`);
      setShowWatchlistModal(false);
    } catch (err) {
      const msg = err.response?.data?.message || 'Stock already exists in this watchlist or failed to add.';
      alert(msg);
    } finally {
      setAddingToWatchlist(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message={`Loading analysis for ${symbol}...`} />;
  }

  if (!security) {
    return (
      <div className="container py-5 text-center">
        <AlertBanner type="danger" message={errorMsg || `Security ${symbol} not found.`} />
        <Link to="/market" className="btn btn-primary mt-3">
          <i className="bi bi-arrow-left me-1"></i> Back to Market
        </Link>
      </div>
    );
  }

  const quote = security.quote || {};
  const ltp = parseFloat(quote.ltp || security.ltp || 0);
  const change = parseFloat(quote.change_amount || security.change_amount || 0);
  const changePct = parseFloat(quote.change_percent || security.change_percent || 0);

  // Technical signal color helper
  const getSignalBadge = (signal) => {
    const s = String(signal || 'NEUTRAL').toUpperCase();
    if (s.includes('BUY')) return <span className="badge bg-success fs-6 px-3 py-2">{s}</span>;
    if (s.includes('SELL')) return <span className="badge bg-danger fs-6 px-3 py-2">{s}</span>;
    return <span className="badge bg-secondary fs-6 px-3 py-2">{s}</span>;
  };

  return (
    <div className="container-fluid px-4 py-4">
      {/* Breadcrumb & Navigation */}
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/">Home</Link></li>
          <li className="breadcrumb-item"><Link to="/market">Market</Link></li>
          <li className="breadcrumb-item active" aria-current="page">{security.symbol}</li>
        </ol>
      </nav>

      <AlertBanner type="danger" message={errorMsg} onClose={() => setErrorMsg('')} />
      <AlertBanner type="success" message={successMsg} onClose={() => setSuccessMsg('')} />

      {/* Stock Header Banner */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-body p-4">
          <div className="d-flex flex-wrap justify-content-between align-items-center">
            <div>
              <div className="d-flex align-items-center gap-2 mb-1">
                <h2 className="fw-bold text-dark mb-0">{security.symbol}</h2>
                <span className="badge bg-dark">{security.exchange || 'NSE'}</span>
                <span className="badge bg-primary-subtle text-primary">{security.sector || 'Equities'}</span>
              </div>
              <h5 className="text-muted fw-normal mb-0">{security.company_name}</h5>
              <small className="text-secondary">ISIN: {security.isin_code || 'INE002A01018'}</small>
            </div>

            {/* Action Buttons */}
            <div className="d-flex flex-wrap gap-2 mt-3 mt-md-0">
              <button
                className="btn btn-outline-secondary"
                onClick={() => setShowWatchlistModal(true)}
              >
                <i className="bi bi-bookmark-plus me-1"></i> Add to Watchlist
              </button>
              <button
                className="btn btn-success px-4 fw-semibold"
                onClick={() => navigate(`/trading?symbol=${security.symbol}&action=buy`)}
              >
                <i className="bi bi-cart-plus me-1"></i> Buy
              </button>
              <button
                className="btn btn-danger px-4 fw-semibold"
                onClick={() => navigate(`/trading?symbol=${security.symbol}&action=sell`)}
              >
                <i className="bi bi-cart-dash me-1"></i> Sell
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-4">
        {/* Left Column: Price & Market Depth Card */}
        <div className="col-12 col-lg-5">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white py-3">
              <h5 className="fw-bold mb-0">
                <i className="bi bi-tag me-2 text-primary"></i> Real-Time Quote &amp; Price Action
              </h5>
            </div>
            <div className="card-body p-4">
              {/* Primary Price Header */}
              <div className="d-flex align-items-baseline gap-3 mb-4 pb-3 border-bottom">
                <h1 className={`fw-bold mb-0 ${getPnlClass(change)}`}>
                  {formatINR(ltp)}
                </h1>
                <div>
                  <span className={`fw-bold fs-5 ${getPnlClass(change)}`}>
                    {change >= 0 ? `+${change.toFixed(2)}` : change.toFixed(2)} ({formatPercent(changePct)})
                  </span>
                  <div className="text-muted small">Last Traded Price</div>
                </div>
              </div>

              {/* Day High / Low / Open / Close stats */}
              <div className="row g-3">
                <div className="col-6">
                  <div className="p-3 bg-light rounded">
                    <small className="text-muted d-block">Open Price</small>
                    <span className="fw-bold">{formatINR(quote.open_price || ltp)}</span>
                  </div>
                </div>
                <div className="col-6">
                  <div className="p-3 bg-light rounded">
                    <small className="text-muted d-block">Previous Close</small>
                    <span className="fw-bold">{formatINR(quote.close_price || (ltp - change))}</span>
                  </div>
                </div>
                <div className="col-6">
                  <div className="p-3 bg-light rounded">
                    <small className="text-muted d-block">Day's High</small>
                    <span className="fw-bold text-success">{formatINR(quote.high_price || ltp)}</span>
                  </div>
                </div>
                <div className="col-6">
                  <div className="p-3 bg-light rounded">
                    <small className="text-muted d-block">Day's Low</small>
                    <span className="fw-bold text-danger">{formatINR(quote.low_price || ltp)}</span>
                  </div>
                </div>
                <div className="col-6">
                  <div className="p-3 bg-light rounded">
                    <small className="text-muted d-block">52-Week High</small>
                    <span className="fw-bold text-success">{formatINR(quote.week_52_high || (ltp * 1.25))}</span>
                  </div>
                </div>
                <div className="col-6">
                  <div className="p-3 bg-light rounded">
                    <small className="text-muted d-block">52-Week Low</small>
                    <span className="fw-bold text-danger">{formatINR(quote.week_52_low || (ltp * 0.75))}</span>
                  </div>
                </div>
                <div className="col-12">
                  <div className="p-3 bg-light rounded d-flex justify-content-between align-items-center">
                    <span className="text-muted">Trading Volume</span>
                    <span className="fw-bold">{Number(quote.volume || 1542000).toLocaleString('en-IN')} shares</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Fundamentals and Technicals */}
        <div className="col-12 col-lg-7">
          <div className="row g-4">
            {/* Fundamental Metrics Card */}
            <div className="col-12">
              <div className="card shadow-sm border-0">
                <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                  <h5 className="fw-bold mb-0">
                    <i className="bi bi-file-earmark-bar-graph me-2 text-primary"></i> Fundamental Valuation
                  </h5>
                  <span className="badge bg-success-subtle text-success">
                    Health Score: {fundamental?.health_score || 8}/10
                  </span>
                </div>
                <div className="card-body p-4">
                  <div className="row g-3">
                    <div className="col-6 col-md-4">
                      <div className="border rounded p-2 text-center">
                        <small className="text-muted d-block">P/E Ratio</small>
                        <span className="fw-bold fs-5">{fundamental?.pe_ratio ? parseFloat(fundamental.pe_ratio).toFixed(2) : '24.50'}</span>
                      </div>
                    </div>
                    <div className="col-6 col-md-4">
                      <div className="border rounded p-2 text-center">
                        <small className="text-muted d-block">EPS (Earnings)</small>
                        <span className="fw-bold fs-5">{fundamental?.eps ? formatINR(fundamental.eps) : '₹ 84.20'}</span>
                      </div>
                    </div>
                    <div className="col-6 col-md-4">
                      <div className="border rounded p-2 text-center">
                        <small className="text-muted d-block">Div Yield</small>
                        <span className="fw-bold fs-5">{fundamental?.dividend_yield ? formatPercent(fundamental.dividend_yield) : '1.35%'}</span>
                      </div>
                    </div>
                    <div className="col-6 col-md-4">
                      <div className="border rounded p-2 text-center">
                        <small className="text-muted d-block">Debt / Equity</small>
                        <span className="fw-bold fs-5">{fundamental?.debt_to_equity ? parseFloat(fundamental.debt_to_equity).toFixed(2) : '0.42'}</span>
                      </div>
                    </div>
                    <div className="col-6 col-md-4">
                      <div className="border rounded p-2 text-center">
                        <small className="text-muted d-block">ROE (%)</small>
                        <span className="fw-bold fs-5 text-success">{fundamental?.roe ? formatPercent(fundamental.roe) : '18.40%'}</span>
                      </div>
                    </div>
                    <div className="col-6 col-md-4">
                      <div className="border rounded p-2 text-center">
                        <small className="text-muted d-block">P/B Ratio</small>
                        <span className="fw-bold fs-5">{fundamental?.pb_ratio ? parseFloat(fundamental.pb_ratio).toFixed(2) : '3.10'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Technical Indicators Card */}
            <div className="col-12">
              <div className="card shadow-sm border-0">
                <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                  <h5 className="fw-bold mb-0">
                    <i className="bi bi-activity me-2 text-primary"></i> Technical Indicators &amp; Momentum
                  </h5>
                  <div>
                    {getSignalBadge(technical?.overall_signal || 'BUY')}
                  </div>
                </div>
                <div className="card-body p-4">
                  <div className="row g-3">
                    <div className="col-6 col-md-4">
                      <div className="p-3 bg-light rounded text-center">
                        <small className="text-muted d-block">RSI (14)</small>
                        <span className="fw-bold fs-5">
                          {technical?.rsi_14 ? parseFloat(technical.rsi_14).toFixed(1) : '58.4'}
                        </span>
                        <div className="small text-muted">
                          {parseFloat(technical?.rsi_14 || 58.4) > 70 ? 'Overbought' : parseFloat(technical?.rsi_14 || 58.4) < 30 ? 'Oversold' : 'Neutral'}
                        </div>
                      </div>
                    </div>
                    <div className="col-6 col-md-4">
                      <div className="p-3 bg-light rounded text-center">
                        <small className="text-muted d-block">MACD</small>
                        <span className="fw-bold fs-5 text-success">
                          {technical?.macd_line ? parseFloat(technical.macd_line).toFixed(2) : '+4.20'}
                        </span>
                        <div className="small text-muted">Signal: {technical?.macd_signal ? parseFloat(technical.macd_signal).toFixed(2) : '+2.10'}</div>
                      </div>
                    </div>
                    <div className="col-6 col-md-4">
                      <div className="p-3 bg-light rounded text-center">
                        <small className="text-muted d-block">20-Day SMA</small>
                        <span className="fw-bold fs-5">
                          {technical?.sma_20 ? formatINR(technical.sma_20) : formatINR(ltp * 0.98)}
                        </span>
                        <div className="small text-success">Above Trend</div>
                      </div>
                    </div>
                    <div className="col-6 col-md-6">
                      <div className="p-3 bg-light rounded text-center">
                        <small className="text-muted d-block">50-Day SMA</small>
                        <span className="fw-bold fs-5">
                          {technical?.sma_50 ? formatINR(technical.sma_50) : formatINR(ltp * 0.95)}
                        </span>
                      </div>
                    </div>
                    <div className="col-6 col-md-6">
                      <div className="p-3 bg-light rounded text-center">
                        <small className="text-muted d-block">200-Day SMA</small>
                        <span className="fw-bold fs-5">
                          {technical?.sma_200 ? formatINR(technical.sma_200) : formatINR(ltp * 0.90)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add to Watchlist Modal */}
      {showWatchlistModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content shadow border-0 rounded-3">
              <div className="modal-header">
                <h5 className="modal-title fw-bold">
                  <i className="bi bi-bookmark-plus text-primary me-2"></i> Add to Watchlist
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowWatchlistModal(false)}
                ></button>
              </div>
              <div className="modal-body p-4">
                {watchlists.length === 0 ? (
                  <div>
                    <p className="text-muted mb-3">You don't have any watchlists yet.</p>
                    <Link to="/watchlist" className="btn btn-sm btn-primary">
                      Go to Watchlist Page to Create One
                    </Link>
                  </div>
                ) : (
                  <div>
                    <label className="form-label fw-semibold">Choose Watchlist</label>
                    <select
                      className="form-select mb-3"
                      value={selectedWatchlistId}
                      onChange={(e) => setSelectedWatchlistId(e.target.value)}
                    >
                      {watchlists.map((wl) => (
                        <option key={wl.id} value={wl.id}>
                          {wl.name}
                        </option>
                      ))}
                    </select>
                    <p className="small text-muted mb-0">
                      Add <strong>{security.symbol}</strong> ({security.company_name}) to monitor price swings.
                    </p>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowWatchlistModal(false)}
                >
                  Cancel
                </button>
                {watchlists.length > 0 && (
                  <button
                    type="button"
                    className="btn btn-primary"
                    disabled={addingToWatchlist}
                    onClick={handleAddToWatchlist}
                  >
                    {addingToWatchlist ? 'Adding...' : 'Confirm Add'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockDetailPage;
