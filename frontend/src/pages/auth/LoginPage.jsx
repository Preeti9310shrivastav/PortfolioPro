import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AlertBanner from '../../components/common/AlertBanner';

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [errors, setErrors] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setErrors(null);

    if (!username.trim() || !password) {
      setErrorMessage('Please provide both username/email and password.');
      return;
    }

    setLoading(true);
    try {
      const responseData = await login(username.trim(), password);
      const user = responseData?.user;
      const roleUpper = user?.role ? String(user.role).toUpperCase() : '';

      // Check if redirected from a protected route
      const from = location.state?.from?.pathname;
      if (from) {
        navigate(from, { replace: true });
      } else if (roleUpper === 'FINANCE_OFFICER' || roleUpper === 'ADMIN') {
        navigate('/fo/dashboard', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    } catch (err) {
      const resData = err.response?.data;
      setErrorMessage(resData?.message || 'Failed to authenticate. Please check your credentials.');
      setErrors(resData?.errors || null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
        <div className="col-12 col-sm-10 col-md-8 col-lg-5 col-xl-4">
          <div className="card shadow-lg border-0 rounded-4">
            <div className="card-body p-4 p-md-5">
              {/* Header */}
              <div className="text-center mb-4">
                <div className="d-inline-flex p-3 rounded-circle bg-primary-subtle text-primary mb-3">
                  <i className="bi bi-graph-up-arrow fs-2"></i>
                </div>
                <h3 className="fw-bold mb-1">Portfolio<span className="text-primary">Pro</span></h3>
                <p className="text-muted small">Sign in to manage your stock portfolio</p>
              </div>

              {/* Alert */}
              <AlertBanner
                type="danger"
                message={errorMessage}
                errors={errors}
                onClose={() => { setErrorMessage(''); setErrors(null); }}
              />

              {/* Form */}
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold small">Username or Email</label>
                  <div className="input-group">
                    <span className="input-group-text bg-light text-muted">
                      <i className="bi bi-person"></i>
                    </span>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g. trader1 or trader@example.com"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                      autoFocus
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <div className="d-flex justify-content-between align-items-center">
                    <label className="form-label fw-semibold small">Password</label>
                  </div>
                  <div className="input-group">
                    <span className="input-group-text bg-light text-muted">
                      <i className="bi bi-lock"></i>
                    </span>
                    <input
                      type="password"
                      className="form-control"
                      placeholder="Enter password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100 py-2 fw-semibold shadow-sm"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Authenticating...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-box-arrow-in-right me-2"></i>
                      Sign In
                    </>
                  )}
                </button>
              </form>

              {/* Footer link */}
              <div className="text-center mt-4 pt-2 border-top">
                <p className="text-muted small mb-0">
                  Don't have an account?{' '}
                  <Link to="/register" className="text-primary text-decoration-none fw-semibold">
                    Create Account
                  </Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
