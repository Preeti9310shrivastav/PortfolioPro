export const formatINR = (amount) => {
  if (amount === null || amount === undefined || isNaN(Number(amount))) return '₹ 0.00';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2
  }).format(amount);
};

export const formatDate = (dateStr) => {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  } catch {
    return '—';
  }
};

export const formatDateTime = (dateStr) => {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return '—';
  }
};

export const formatPercent = (val) => {
  if (val === null || val === undefined || isNaN(Number(val))) return '0.00%';
  const num = parseFloat(val);
  return `${num >= 0 ? '+' : ''}${num.toFixed(2)}%`;
};

export const getPnlClass = (val) => {
  const num = parseFloat(val);
  if (isNaN(num)) return 'text-muted';
  if (num > 0) return 'text-success';
  if (num < 0) return 'text-danger';
  return 'text-muted';
};
