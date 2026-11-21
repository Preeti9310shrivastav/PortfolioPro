import React from 'react';

const LoadingSpinner = ({ message = 'Loading...', minHeight = '50vh' }) => {
  return (
    <div
      className="d-flex flex-column justify-content-center align-items-center w-100"
      style={{ minHeight }}
    >
      <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
        <span className="visually-hidden">Loading...</span>
      </div>
      {message && <div className="mt-3 text-muted fw-semibold">{message}</div>}
    </div>
  );
};

export default LoadingSpinner;
