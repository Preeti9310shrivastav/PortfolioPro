import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import { formatINR, formatPercent, getPnlClass } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const MarketPage = () => {
  const navigate = useNavigate();

  const [securities, setSecurities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  // Filters
  const [search, setSearch] = useState('');
  const [selectedExchange, setSelectedExchange] = useState('ALL');
  const [selectedSector, setSelectedSector] = useState('ALL');

  // Fetch securities
  const fetchSecurities = useCallback(async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      let queryParams = [];
      if (search.trim()) queryParams.push(`search=${encodeURIComponent(search.trim())}`);
      if (selectedExchange !== 'ALL') queryParams.push(`exchange=${encodeURIComponent(selectedExchange)}`);
      if (selectedSector !== 'ALL') queryParams.push(`sector=${encodeURIComponent(selectedSector)}`);

      const queryString = queryParams.length ? `?${queryParams.join('&')}` : '';
      const res = await api.get(`/market/securities/${queryString}`);
      const list = res.data?.data || res.data?.results || res.data;
      if (Array.isArray(list)) {
        setSecurities(list);
      } else {
        setSecurities([]);
      }
    } catch (err) {
      console.warn('Failed to fetch securities:', err);
      setErrorMsg('Failed to load market securities. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [search, selectedExchange, selectedSector]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchSecurities();
    }, 300);
    return () => clearTimeout(timer);
  }, [fetchSecurities]);

  // Unique sectors for dropdown
  const sectors = ['ALL', 'Information Technology', 'Banking & Finance', 'Automobile', 'Energy & Power', 'Healthcare', 'Consumer Goods', 'Metals & Mining'];

  return (
    <div className="container-fluid px-4 py-4">
      {/* Page Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Market Watch</h2>
          <p className="text-muted mb-0">Browse real-time quotes, technical levels, and equity fundamentals</p>
        </div>
      </div>

      <AlertBanner type="danger" message={errorMsg} onClose={() => setErrorMsg('')} />

      {/* Filter and Search Bar Card */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-body p-3">
          <div className="row g-3">
            {/* Search */}
            <div className="col-12 col-md-5">
              <div className="input-group">
                <span className="input-group-text bg-white text-muted">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search by symbol or company name (e.g. RELIANCE, TCS)..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
                {search && (
                  <button
                    className="btn btn-outline-secondary"
                    type="button"
                    onClick={() => setSearch('')}
                  >
                    <i className="bi bi-x"></i>
                  </button>
                )}
              </div>
            </div>

            {/* Exchange Filter */}
            <div className="col-6 col-md-3">
              <select
                className="form-select"
                value={selectedExchange}
                onChange={(e) => setSelectedExchange(e.target.value)}
              >
                <option value="ALL">All Exchanges (NSE &amp; BSE)</option>
                <option value="NSE">NSE Only</option>
                <option value="BSE">BSE Only</option>
              </select>
            </div>

            {/* Sector Filter */}
            <div className="col-6 col-md-4">
              <select
                className="form-select"
                value={selectedSector}
                onChange={(e) => setSelectedSector(e.target.value)}
              >
                {sectors.map((sec) => (
                  <option key={sec} value={sec}>
                    {sec === 'ALL' ? 'All Sectors' : sec}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Securities Table Card */}
      <div className="card shadow-sm border-0">
        <div className="card-body p-0">
          {loading ? (
            <LoadingSpinner message="Fetching live market securities..." />
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead className="table-light">
                  <tr>
                    <th className="ps-4">Symbol</th>
                    <th>Company Name</th>
                    <th>Exchange</th>
                    <th>Sector</th>
                    <th className="text-end">LTP</th>
                    <th className="text-end">Change</th>
                    <th className="text-end">Change %</th>
                    <th className="pe-4 text-end">Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {securities.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="text-center py-5 text-muted">
                        <i className="bi bi-search fs-2 d-block mb-2 text-secondary"></i>
                        No securities found matching your search or filter criteria.
                      </td>
                    </tr>
                  ) : (
                    securities.map((sec) => {
                      const quote = sec.quote || {};
                      const ltp = parseFloat(quote.ltp || sec.ltp || 0);
                      const change = parseFloat(quote.change_amount || sec.change_amount || 0);
                      const changePct = parseFloat(quote.change_percent || sec.change_percent || 0);
                      const volume = quote.volume || sec.volume || 0;

                      return (
                        <tr
                          key={sec.id || sec.symbol}
                          onClick={() => navigate(`/market/${sec.symbol}`)}
                          style={{ cursor: 'pointer' }}
                        >
                          <td className="ps-4 fw-bold text-primary">
                            {sec.symbol}
                          </td>
                          <td className="fw-medium text-dark">
                            {sec.company_name}
                          </td>
                          <td>
                            <span className="badge bg-light text-dark border">
                              {sec.exchange || 'NSE'}
                            </span>
                          </td>
                          <td>
                            <span className="badge bg-secondary-subtle text-secondary">
                              {sec.sector || 'General'}
                            </span>
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
                          <td className="pe-4 text-end text-muted">
                            {Number(volume).toLocaleString('en-IN')}
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

export default MarketPage;
