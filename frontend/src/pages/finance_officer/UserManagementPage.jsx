import React, { useState, useEffect, useCallback } from 'react';
import api from '../../api/axios';
import { formatDate } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  // Search & Filter
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      let queryParams = [];
      if (search.trim()) queryParams.push(`search=${encodeURIComponent(search.trim())}`);
      if (roleFilter !== 'ALL') queryParams.push(`role=${encodeURIComponent(roleFilter)}`);

      const queryString = queryParams.length ? `?${queryParams.join('&')}` : '';
      const res = await api.get(`/auth/users/${queryString}`);
      const data = res.data?.data || res.data;
      const list = data?.users || (Array.isArray(data) ? data : []);
      setUsers(list);
    } catch (err) {
      console.warn('Failed to fetch users:', err);
      setErrorMsg('Failed to load user directory. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [search, roleFilter]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchUsers();
    }, 300);
    return () => clearTimeout(timer);
  }, [fetchUsers]);

  const getRoleBadge = (role) => {
    const r = String(role || '').toUpperCase();
    if (r === 'ADMIN') return <span className="badge bg-dark">Administrator</span>;
    if (r === 'FINANCE_OFFICER') return <span className="badge bg-danger">Finance Officer</span>;
    return <span className="badge bg-primary">Customer</span>;
  };

  return (
    <div className="container-fluid px-4 py-4">
      {/* Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">User Directory &amp; Roles</h2>
          <p className="text-muted mb-0">Audit platform registered users, assign roles, and verify statuses</p>
        </div>
      </div>

      <AlertBanner type="danger" message={errorMsg} onClose={() => setErrorMsg('')} />

      {/* Search and Filters */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-body p-3">
          <div className="row g-3">
            <div className="col-12 col-md-7">
              <div className="input-group">
                <span className="input-group-text bg-white text-muted">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search by username, email, or name..."
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

            <div className="col-12 col-md-5">
              <select
                className="form-select"
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
              >
                <option value="ALL">All Roles</option>
                <option value="CUSTOMER">Customers Only</option>
                <option value="FINANCE_OFFICER">Finance Officers</option>
                <option value="ADMIN">Administrators</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="card shadow-sm border-0">
        <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
          <h5 className="fw-bold mb-0">
            <i className="bi bi-people me-2 text-primary"></i> Registered Users ({users.length})
          </h5>
        </div>
        <div className="card-body p-0">
          {loading ? (
            <LoadingSpinner message="Searching users..." />
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead className="table-light">
                  <tr>
                    <th className="ps-4">User</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Phone</th>
                    <th>City / State</th>
                    <th className="text-center">Status</th>
                    <th className="pe-4 text-end">Joined Date</th>
                  </tr>
                </thead>
                <tbody>
                  {users.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="text-center py-5 text-muted">
                        <i className="bi bi-person-x fs-2 d-block mb-2 text-secondary"></i>
                        No users match the search criteria.
                      </td>
                    </tr>
                  ) : (
                    users.map((u) => {
                      const fullName = u.first_name ? `${u.first_name} ${u.last_name || ''}` : u.username;
                      const profile = u.profile || {};
                      const location = [profile.city, profile.state].filter(Boolean).join(', ') || '—';

                      return (
                        <tr key={u.id}>
                          <td className="ps-4">
                            <div className="fw-bold text-dark">{fullName}</div>
                            <small className="text-muted">@{u.username}</small>
                          </td>
                          <td className="text-dark">{u.email}</td>
                          <td>{getRoleBadge(u.role)}</td>
                          <td className="text-muted">{u.phone_number || '—'}</td>
                          <td className="text-muted">{location}</td>
                          <td className="text-center">
                            <span className={`badge ${u.is_active ? 'bg-success' : 'bg-danger'}`}>
                              {u.is_active ? 'Active' : 'Disabled'}
                            </span>
                          </td>
                          <td className="pe-4 text-end text-muted small">
                            {formatDate(u.date_joined)}
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

export default UserManagementPage;
