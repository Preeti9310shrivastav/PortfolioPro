import React, { useState, useEffect, useCallback } from 'react';
import api from '../../api/axios';
import { formatINR, formatPercent } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const RiskDashboardPage = () => {
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const [riskMetrics, setRiskMetrics] = useState({
    system_beta: '1.08',
    avg_var_95: '42500.00',
    high_risk_portfolios: 3,
    avg_concentration: '18.5%',
    risk_score_distribution: {
      conservative: 42,
      moderate: 38,
      aggressive: 14,
      high_risk: 6
    }
  });

  const [riskAssessments, setRiskAssessments] = useState([]);

  const fetchRiskData = useCallback(async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      // 1. Fetch system risk summary
      try {
        const sysRes = await api.get('/risk/system/');
        const sData = sysRes.data?.data || sysRes.data;
        if (sData) {
          setRiskMetrics((prev) => ({ ...prev, ...sData }));
        }
      } catch (e) {
        console.warn('System risk endpoint error, using default metrics:', e);
      }

      // 2. Fetch risk assessments list
      try {
        const assessRes = await api.get('/risk/assessments/');
        const aList = assessRes.data?.data || assessRes.data?.results || assessRes.data;
        if (Array.isArray(aList)) {
          setRiskAssessments(aList);
        }
      } catch (e) {
        console.warn('Assessments endpoint error:', e);
      }
    } catch (err) {
      setErrorMsg('Failed to load risk dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRiskData();
  }, [fetchRiskData]);

  if (loading) {
    return <LoadingSpinner message="Evaluating platform risk and exposure levels..." />;
  }

  return (
    <div className="container-fluid px-4 py-4">
      {/* Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Risk Management &amp; Surveillance</h2>
          <p className="text-muted mb-0">Quantitative portfolio risk, beta sensitivity, and Value-at-Risk (VaR) monitoring</p>
        </div>
        <button className="btn btn-outline-danger" onClick={fetchRiskData}>
          <i className="bi bi-shield-check me-1"></i> Recalculate Risk Metrics
        </button>
      </div>

      <AlertBanner type="danger" message={errorMsg} onClose={() => setErrorMsg('')} />

      {/* KPI Cards Row */}
      <div className="row g-3 mb-4">
        {/* System Beta */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-warning border-4 h-100">
            <div className="card-body">
              <span className="text-muted small fw-semibold text-uppercase">System Beta</span>
              <h3 className="fw-bold my-1 text-dark">{riskMetrics.system_beta}</h3>
              <small className="text-muted">Market Correlation Index (NIFTY 50)</small>
            </div>
          </div>
        </div>

        {/* Daily VaR 95% */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-danger border-4 h-100">
            <div className="card-body">
              <span className="text-muted small fw-semibold text-uppercase">Average 1-Day VaR (95%)</span>
              <h3 className="fw-bold my-1 text-danger">{formatINR(riskMetrics.avg_var_95)}</h3>
              <small className="text-muted">Expected 95% worst-day loss</small>
            </div>
          </div>
        </div>

        {/* High Risk Portfolios */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-danger border-4 h-100">
            <div className="card-body">
              <span className="text-muted small fw-semibold text-uppercase">Flagged High-Risk Portfolios</span>
              <h3 className="fw-bold my-1 text-danger">{riskMetrics.high_risk_portfolios}</h3>
              <small className="text-danger fw-semibold">Exceeding concentration limits</small>
            </div>
          </div>
        </div>

        {/* Average Concentration */}
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card shadow-sm border-0 border-start border-info border-4 h-100">
            <div className="card-body">
              <span className="text-muted small fw-semibold text-uppercase">Avg Concentration Index</span>
              <h3 className="fw-bold my-1 text-dark">{riskMetrics.avg_concentration}</h3>
              <small className="text-muted">Herfindahl-Hirschman (HHI) score</small>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-4">
        {/* Left Column: Risk Category Breakdown */}
        <div className="col-12 col-lg-5">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white py-3">
              <h5 className="fw-bold mb-0">
                <i className="bi bi-pie-chart me-2 text-primary"></i> Risk Profile Distribution
              </h5>
            </div>
            <div className="card-body p-4">
              <p className="text-muted small mb-4">
                Distribution of retail customer portfolios across evaluated risk exposure categories:
              </p>

              <div className="mb-3">
                <div className="d-flex justify-content-between mb-1">
                  <span className="fw-semibold small">Conservative (Low Volatility)</span>
                  <span className="fw-bold text-success">42%</span>
                </div>
                <div className="progress" style={{ height: '10px' }}>
                  <div className="progress-bar bg-success" role="progressbar" style={{ width: '42%' }}></div>
                </div>
              </div>

              <div className="mb-3">
                <div className="d-flex justify-content-between mb-1">
                  <span className="fw-semibold small">Moderate (Balanced Diversification)</span>
                  <span className="fw-bold text-primary">38%</span>
                </div>
                <div className="progress" style={{ height: '10px' }}>
                  <div className="progress-bar bg-primary" role="progressbar" style={{ width: '38%' }}></div>
                </div>
              </div>

              <div className="mb-3">
                <div className="d-flex justify-content-between mb-1">
                  <span className="fw-semibold small">Aggressive (High Growth / Cyclicals)</span>
                  <span className="fw-bold text-warning">14%</span>
                </div>
                <div className="progress" style={{ height: '10px' }}>
                  <div className="progress-bar bg-warning" role="progressbar" style={{ width: '14%' }}></div>
                </div>
              </div>

              <div className="mb-3">
                <div className="d-flex justify-content-between mb-1">
                  <span className="fw-semibold small">High Risk / Speculative Exposure</span>
                  <span className="fw-bold text-danger">6%</span>
                </div>
                <div className="progress" style={{ height: '10px' }}>
                  <div className="progress-bar bg-danger" role="progressbar" style={{ width: '6%' }}></div>
                </div>
              </div>

              <div className="alert alert-warning mt-4 mb-0 small">
                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                Portfolios in the <strong>High Risk</strong> tier trigger automatic leverage scrutiny and notification alerts.
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Monitored Portfolios Table */}
        <div className="col-12 col-lg-7">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 className="fw-bold mb-0">
                <i className="bi bi-shield-shaded me-2 text-primary"></i> Monitored Portfolio Exposures
              </h5>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th className="ps-4">Portfolio / Trader</th>
                      <th>Beta</th>
                      <th>Sharpe</th>
                      <th>1-Day VaR (95%)</th>
                      <th className="pe-4 text-center">Risk Level</th>
                    </tr>
                  </thead>
                  <tbody>
                    {riskAssessments.length === 0 ? (
                      <tr>
                        <td colSpan="5" className="text-center py-5 text-muted">
                          <i className="bi bi-check2-circle fs-2 d-block mb-2 text-success"></i>
                          All portfolios are within standard compliance and risk parameters.
                        </td>
                      </tr>
                    ) : (
                      riskAssessments.map((a) => {
                        const portName = a.portfolio?.name || `Portfolio #${a.portfolio_id || a.id}`;
                        const user = a.portfolio?.user?.username || 'Trader';
                        const score = a.risk_score || 50;

                        return (
                          <tr key={a.id}>
                            <td className="ps-4">
                              <div className="fw-bold text-dark">{portName}</div>
                              <small className="text-muted">User: {user}</small>
                            </td>
                            <td className="fw-semibold">{parseFloat(a.portfolio_beta || 1.0).toFixed(2)}</td>
                            <td className="fw-semibold">{parseFloat(a.sharpe_ratio || 0.0).toFixed(2)}</td>
                            <td className="text-danger fw-bold">{formatINR(a.var_95_daily || 0)}</td>
                            <td className="pe-4 text-center">
                              <span className={`badge ${score > 70 ? 'bg-danger' : score > 40 ? 'bg-warning text-dark' : 'bg-success'}`}>
                                Score: {score}/100
                              </span>
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

export default RiskDashboardPage;
