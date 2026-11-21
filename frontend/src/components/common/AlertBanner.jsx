import React from 'react';

const AlertBanner = ({ type = 'danger', message, errors, onClose }) => {
  if (!message && !errors) return null;

  // Format error details if an errors object or array is passed
  const renderErrorDetails = () => {
    if (!errors) return null;

    if (typeof errors === 'string') {
      return <div className="mt-1">{errors}</div>;
    }

    if (Array.isArray(errors)) {
      return (
        <ul className="mb-0 mt-1 ps-3">
          {errors.map((err, idx) => (
            <li key={idx}>{typeof err === 'string' ? err : JSON.stringify(err)}</li>
          ))}
        </ul>
      );
    }

    if (typeof errors === 'object') {
      return (
        <ul className="mb-0 mt-1 ps-3">
          {Object.entries(errors).map(([field, errList]) => {
            const text = Array.isArray(errList) ? errList.join(', ') : String(errList);
            return (
              <li key={field}>
                <strong>{field}:</strong> {text}
              </li>
            );
          })}
        </ul>
      );
    }

    return null;
  };

  return (
    <div
      className={`alert alert-${type} alert-dismissible fade show`}
      role="alert"
    >
      {message && <div>{message}</div>}
      {renderErrorDetails()}
      {onClose && (
        <button
          type="button"
          className="btn-close"
          aria-label="Close"
          onClick={onClose}
        ></button>
      )}
    </div>
  );
};

export default AlertBanner;
