import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AlertBanner from '../../components/common/AlertBanner';

const RegisterPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    password: '',
    password_confirm: ''
  });

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear field-specific error as user types
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setFieldErrors({});

    if (formData.password !== formData.password_confirm) {
      setFieldErrors({ password_confirm: ['Passwords do not match.'] });
      return;
    }

    setLoading(true);
    try {
      await register(formData);
      navigate('/', { replace: true });
    } catch (err) {
      const resData = err.response?.data;
      setErrorMessage(resData?.message || 'Registration failed. Please check the form.');
      if (resData?.errors && typeof resData.errors === 'object') {
        setFieldErrors(resData.errors);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center align-items-center" style={{ minHeight: '85vh' }}>
        <div className="col-12 col-md-10 col-lg-7 col-xl-6">
          <div className="card shadow-lg border-0 rounded-4">
            <div className="card-body p-4 p-md-5">
              {/* Header */}
              <div className="text-center mb-4">
                <div className="d-inline-flex p-3 rounded-circle bg-primary-subtle text-primary mb-3">
                  <i className="bi bi-person-plus fs-2"></i>
                </div>
                <h3 className="fw-bold mb-1">Create Account</h3>
                <p className="text-muted small">Join PortfolioPro and start investing in Indian stocks</p>
              </div>

              {/* General error message */}
              <AlertBanner
                type="danger"
                message={errorMessage}
                onClose={() => setErrorMessage('')}
              />

              <form onSubmit={handleSubmit}>
                <div className="row g-3">
                  {/* Username */}
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">Username</label>
                    <input
                      type="text"
                      name="username"
                      className={`form-control ${fieldErrors.username ? 'is-invalid' : ''}`}
                      placeholder="e.g. rahul_sharma"
                      value={formData.username}
                      onChange={handleChange}
                      required
                    />
                    {fieldErrors.username && (
                      <div className="invalid-feedback">{fieldErrors.username.join(', ')}</div>
                    )}
                  </div>

                  {/* Email */}
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">Email Address</label>
                    <input
                      type="email"
                      name="email"
                      className={`form-control ${fieldErrors.email ? 'is-invalid' : ''}`}
                      placeholder="e.g. rahul@example.com"
                      value={formData.email}
                      onChange={handleChange}
                      required
                    />
                    {fieldErrors.email && (
                      <div className="invalid-feedback">{fieldErrors.email.join(', ')}</div>
                    )}
                  </div>

                  {/* First Name */}
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">First Name</label>
                    <input
                      type="text"
                      name="first_name"
                      className={`form-control ${fieldErrors.first_name ? 'is-invalid' : ''}`}
                      placeholder="e.g. Rahul"
                      value={formData.first_name}
                      onChange={handleChange}
                      required
                    />
                    {fieldErrors.first_name && (
                      <div className="invalid-feedback">{fieldErrors.first_name.join(', ')}</div>
                    )}
                  </div>

                  {/* Last Name */}
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">Last Name</label>
                    <input
                      type="text"
                      name="last_name"
                      className={`form-control ${fieldErrors.last_name ? 'is-invalid' : ''}`}
                      placeholder="e.g. Sharma"
                      value={formData.last_name}
                      onChange={handleChange}
                      required
                    />
                    {fieldErrors.last_name && (
                      <div className="invalid-feedback">{fieldErrors.last_name.join(', ')}</div>
                    )}
                  </div>

                  {/* Phone */}
                  <div className="col-12">
                    <label className="form-label fw-semibold small">Phone Number</label>
                    <input
                      type="tel"
                      name="phone_number"
                      className={`form-control ${fieldErrors.phone_number ? 'is-invalid' : ''}`}
                      placeholder="e.g. 9876543210"
                      value={formData.phone_number}
                      onChange={handleChange}
                    />
                    {fieldErrors.phone_number && (
                      <div className="invalid-feedback">{fieldErrors.phone_number.join(', ')}</div>
                    )}
                  </div>

                  {/* Password */}
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">Password</label>
                    <input
                      type="password"
                      name="password"
                      className={`form-control ${fieldErrors.password ? 'is-invalid' : ''}`}
                      placeholder="Min 8 characters"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      minLength={8}
                    />
                    {fieldErrors.password && (
                      <div className="invalid-feedback">{fieldErrors.password.join(', ')}</div>
                    )}
                  </div>

                  {/* Confirm Password */}
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">Confirm Password</label>
                    <input
                      type="password"
                      name="password_confirm"
                      className={`form-control ${fieldErrors.password_confirm ? 'is-invalid' : ''}`}
                      placeholder="Re-enter password"
                      value={formData.password_confirm}
                      onChange={handleChange}
                      required
                      minLength={8}
                    />
                    {fieldErrors.password_confirm && (
                      <div className="invalid-feedback">{fieldErrors.password_confirm.join(', ')}</div>
                    )}
                  </div>
                </div>

                <div className="mt-4">
                  <button
                    type="submit"
                    className="btn btn-primary w-100 py-2 fw-semibold shadow-sm"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Creating Account...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-person-check me-2"></i>
                        Register
                      </>
                    )}
                  </button>
                </div>
              </form>

              {/* Footer link */}
              <div className="text-center mt-4 pt-2 border-top">
                <p className="text-muted small mb-0">
                  Already have an account?{' '}
                  <Link to="/login" className="text-primary text-decoration-none fw-semibold">
                    Sign In
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

export default RegisterPage;
