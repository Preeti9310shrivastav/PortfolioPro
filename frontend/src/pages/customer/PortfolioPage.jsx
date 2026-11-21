import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import { formatINR, formatPercent, getPnlClass } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const PortfolioPage = () => {
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const [portfolio, setPortfolio] = useState(null);
  const [summary, setSummary] = useState({
    total_invested: 0,
    current_value: 0,
    unrealized_pnl: 0,
    realized_pnl: 0,
    return_percent: 0
  });
  const [holdings, setHoldings] = useState([]);

  const fetchPortfolioData = useCallback(async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      // 1. Get portfolios list
      const portRes = await api.get('/portfolio/portfolios/');
      const portList = portRes.data?.data || portRes.data?.results || portRes.data;
      let selectedPort = null;
      if (Array.isArray(portList) && portList.length > 0) {
        selectedPort = portList[0];
      } else if (portList && portList.id) {
        selectedPort = portList;
      }

      if (!selectedPort) {
        setHoldings([]);
        setLoading(false);
        return;
      }

      setPortfolio(selectedPort);
      const portId = selectedPort.id;

      // 2. Fetch Holdings
      try {
        const holdRes = await api.get(`/portfolio/portfolios/${portId}/holdings/`);
        const holdList = holdRes.data?.data || holdRes.data?.results || holdRes.data;
        if (Array.isArray(holdList)) {
          setHoldings(holdList);
        }
      } catch (e) {
        console.warn('Holdings endpoint error:', e);
      }

      // 3. Fetch Summary
      try {
        const sumRes = await api.get(`/portfolio/portfolios/${portId}/summary/`);
        const sumData = sumRes.data?.data || sumRes.data;
        if (sumData) {
          setSummary(sumData);
        }
      } catch (e) {
        console.warn('Summary endpoint error:', e);
      }
    } catch (err) {
      console.warn('Failed to load portfolio:', err);
      setErrorMsg('Failed to load portfolio holdings. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPortfolioData();
  }, [fetchPortfolioData]);

  // Aggregate stats dynamically if summary endpoint returned zeroes but holdings exist
  const totalInvested = parseFloat(summary.total_invested) || holdings.reduce((acc, h) => acc + parseFloat(h.total_invested || (h.quantity * (h.average_buy_price || 0))), 0);
  const currentValue = parseFloat(summary.current_value) || holdings.reduce((acc, h) => {
    const ltp = parseFloat(h.security?.quote?.ltp || h.current_price || h.average_buy_price || 0);
    return acc + (h.quantity * ltp);
  }, 0);
  const unrealizedPnl = parseFloat(summary.unrealized_pnl) || (currentValue - totalInvested);
  const realizedPnl = parseFloat(summary.realized_pnl || 0);
  const overallReturn = totalInvested > 0 ? (unrealizedPnl / totalInvested) * 100 : 0;

  if (loading) {
    return <LoadingSpinner message="Calculating your portfolio valuation..." />;
  }

  return (
    <div className="container-fluid px-4 py-4">
      {/* Page Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Portfolio &amp; Holdings</h2>
          <p className="text-muted mb-0">Consolidated equity holdings, realized &amp; unrealized gain/loss</p>
        </div>
        <div className="d-flex gap-2">
          <Link to="/trading" className="btn btn-primary fw-semibold">
            <i className="bi bi-cart-plus me-1"></i> Buy Equities
          </Link>
        </div>
      </div>

      <AlertBanner type="danger" message={errorMsg} onClose={() => setErrorMsg('')} />

      {/* KPI Cards */}
      <div className="row g-3 mb-4">
        {/* Total Invested */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-primary border-4 h-100">
            <div className="card-body">
              <span className="text-muted small fw-semibold text-uppercase">Total Invested</span>
              <h3 className="fw-bold my-1">{formatINR(totalInvested)}</h3>
              <small className="text-muted">Total Capital Cost</small>
            </div>
          </div>
        </div>

        {/* Current Value */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-info border-4 h-100">
            <div className="card-body">
              <span className="text-muted small fw-semibold text-uppercase">Current Valuation</span>
              <h3 className="fw-bold my-1">{formatINR(currentValue)}</h3>
              <small className="text-muted">Market Value @ CMP</small>
            </div>
          </div>
        </div>

        {/* Unrealized P&L */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className={`card shadow-sm border-0 border-start ${unrealizedPnl >= 0 ? 'border-success' : 'border-danger'} border-4 h-100`}>
            <div className="card-body">
              <span className="text-muted small fw-semibold text-uppercase">Unrealized P&amp;L</span>
              <h3 className={`fw-bold my-1 ${getPnlClass(unrealizedPnl)}`}>
                {formatINR(unrealizedPnl)}
              </h3>
              <small className={getPnlClass(overallReturn)}>
                {formatPercent(overallReturn)} Return
              </small>
            </div>
          </div>
        </div>

        {/* Realized P&L */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className={`card shadow-sm border-0 border-start ${realizedPnl >= 0 ? 'border-success' : 'border-danger'} border-4 h-100`}>
            <div className="card-body">
              <span className="text-muted small fw-semibold text-uppercase">Realized P&amp;L</span>
              <h3 className={`fw-bold my-1 ${getPnlClass(realizedPnl)}`}>
                {formatINR(realizedPnl)}
              </h3>
              <small className="text-muted">Closed Trades Profit/Loss</small>
            </div>
          </div>
        </div>
      </div>

      {/* Holdings Table */}
      <div className="card shadow-sm border-0">
        <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
          <h5 className="fw-bold mb-0">
            <i className="bi bi-pie-chart-fill me-2 text-primary"></i> Equity Holdings
          </h5>
          <span className="badge bg-secondary">
            {holdings.length} {holdings.length === 1 ? 'Position' : 'Positions'}
          </span>
        </div>
        <div className="card-body p-0">
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th className="ps-4">Stock</th>
                  <th className="text-end">Quantity</th>
                  <th className="text-end">Avg Buy Price</th>
                  <th className="text-end">Current Price</th>
                  <th className="text-end">Total Invested</th>
                  <th className="text-end">Current Value</th>
                  <th className="text-end">P&amp;L</th>
                  <th className="pe-4 text-end">Return %</th>
                </tr>
              </thead>
              <tbody>
                {holdings.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="text-center py-5 text-muted">
                      <i className="bi bi-wallet-fill fs-2 d-block mb-2 text-secondary"></i>
                      No stock holdings in this portfolio yet.
                      <div className="mt-3">
                        <Link to="/trading" className="btn btn-sm btn-primary">
                          Explore &amp; Buy Stocks
                        </Link>
                      </div>
                    </td>
                  </tr>
                ) : (
                  holdings.map((h) => {
                    const symbol = h.security?.symbol || h.symbol || '—';
                    const companyName = h.security?.company_name || '';
                    const qty = parseInt(h.quantity, 10) || 0;
                    const avgPrice = parseFloat(h.average_buy_price || 0);
                    const ltp = parseFloat(h.security?.quote?.ltp || h.current_price || avgPrice);

                    const invested = parseFloat(h.total_invested || (qty * avgPrice));
                    const curVal = parseFloat(h.current_value || (qty * ltp));
                    const pnl = parseFloat(h.unrealized_pnl !== undefined ? h.unrealized_pnl : (curVal - invested));
                    const retPct = parseFloat(h.return_percent !== undefined ? h.return_percent : (invested > 0 ? (pnl / invested) * 100 : 0));

                    return (
                      <tr key={h.id || symbol}>
                        <td className="ps-4">
                          <Link to={`/market/${symbol}`} className="text-decoration-none fw-bold text-primary">
                            {symbol}
                          </Link>
                          <div className="text-muted small">{companyName}</div>
                        </td>
                        <td className="text-end fw-semibold">{qty}</td>
                        <td className="text-end">{formatINR(avgPrice)}</td>
                        <td className="text-end fw-semibold">{formatINR(ltp)}</td>
                        <td className="text-end">{formatINR(invested)}</td>
                        <td className="text-end fw-semibold">{formatINR(curVal)}</td>
                        <td className={`text-end fw-bold ${getPnlClass(pnl)}`}>
                          {formatINR(pnl)}
                        </td>
                        <td className={`pe-4 text-end fw-bold ${getPnlClass(retPct)}`}>
                          {formatPercent(retPct)}
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
  );
};

export default PortfolioPage;
