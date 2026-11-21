import React, { useState, useEffect, useCallback } from 'react';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { formatDateTime } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const TicketManagementPage = () => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  // Modal State
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [newStatus, setNewStatus] = useState('IN_PROGRESS');

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setAlert(null);
    try {
      let queryParams = [];
      if (statusFilter !== 'ALL') queryParams.push(`status=${statusFilter}`);
      if (priorityFilter !== 'ALL') queryParams.push(`priority=${priorityFilter}`);

      const queryString = queryParams.length ? `?${queryParams.join('&')}` : '';

      let list = [];
      try {
        const res = await api.get(`/support/all-tickets/${queryString}`);
        list = res.data?.data || res.data?.results || res.data;
      } catch (e) {
        // Fallback to /support/tickets/
        const res = await api.get(`/support/tickets/${queryString}`);
        list = res.data?.data || res.data?.results || res.data;
      }

      setTickets(Array.isArray(list) ? list : []);
    } catch (err) {
      console.warn('Failed to fetch support tickets:', err);
      setAlert({
        type: 'danger',
        message: 'Failed to retrieve support tickets. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  }, [statusFilter, priorityFilter]);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  const handleOpenTicketModal = async (ticket) => {
    setSelectedTicket(ticket);
    setNewStatus(ticket.status || 'IN_PROGRESS');
    setLoadingMessages(true);
    try {
      const res = await api.get(`/support/tickets/${ticket.id}/messages/`);
      const msgList = res.data?.data || res.data?.results || res.data;
      setMessages(Array.isArray(msgList) ? msgList : []);
    } catch (err) {
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleUpdateStatus = async () => {
    if (!selectedTicket) return;
    setUpdatingStatus(true);
    try {
      await api.patch(`/support/tickets/${selectedTicket.id}/`, {
        status: newStatus
      });
      setSelectedTicket((prev) => ({ ...prev, status: newStatus }));
      setAlert({ type: 'success', message: `Ticket status updated to ${newStatus}.` });
      fetchTickets();
    } catch (err) {
      // Try alternate status update endpoint
      try {
        await api.post(`/support/tickets/${selectedTicket.id}/status/`, { status: newStatus });
        setSelectedTicket((prev) => ({ ...prev, status: newStatus }));
        setAlert({ type: 'success', message: `Ticket status updated to ${newStatus}.` });
        fetchTickets();
      } catch (e) {
        alert(err.response?.data?.message || 'Failed to update ticket status.');
      }
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleAssignToMe = async () => {
    if (!selectedTicket) return;
    try {
      await api.patch(`/support/tickets/${selectedTicket.id}/`, {
        assigned_to: user?.id
      });
      setSelectedTicket((prev) => ({ ...prev, assigned_to: user }));
      setAlert({ type: 'success', message: 'Ticket assigned to you.' });
      fetchTickets();
    } catch (err) {
      alert('Could not assign ticket.');
    }
  };

  const handleSendReply = async (e) => {
    e.preventDefault();
    if (!replyText.trim() || !selectedTicket) return;

    try {
      const res = await api.post(`/support/tickets/${selectedTicket.id}/messages/`, {
        message_text: replyText.trim()
      });
      const newMsg = res.data?.data || res.data;
      setMessages((prev) => [
        ...prev,
        newMsg || {
          id: Date.now(),
          sender: { username: user?.username },
          message_text: replyText.trim(),
          created_at: new Date().toISOString()
        }
      ]);
      setReplyText('');
    } catch (err) {
      alert('Failed to send officer reply.');
    }
  };

  const getStatusBadge = (status) => {
    const s = String(status || '').toUpperCase();
    if (s === 'OPEN') return <span className="badge bg-primary">Open</span>;
    if (s === 'IN_PROGRESS') return <span className="badge bg-info text-dark">In Progress</span>;
    if (s === 'PENDING_CUSTOMER') return <span className="badge bg-warning text-dark">Pending Feedback</span>;
    if (s === 'RESOLVED') return <span className="badge bg-success">Resolved</span>;
    if (s === 'CLOSED') return <span className="badge bg-secondary">Closed</span>;
    return <span className="badge bg-light text-dark">{s}</span>;
  };

  const getPriorityBadge = (prio) => {
    const p = String(prio || '').toUpperCase();
    if (p === 'URGENT') return <span className="badge bg-danger">Urgent</span>;
    if (p === 'HIGH') return <span className="badge bg-warning text-dark">High</span>;
    if (p === 'MEDIUM') return <span className="badge bg-secondary">Medium</span>;
    return <span className="badge bg-light text-muted border">Low</span>;
  };

  return (
    <div className="container-fluid px-4 py-4">
      {/* Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Ticket Resolution Desk</h2>
          <p className="text-muted mb-0">Manage customer queries, dispute tickets, and resolve trading inquiries</p>
        </div>
        <button className="btn btn-outline-primary" onClick={fetchTickets}>
          <i className="bi bi-arrow-clockwise me-1"></i> Refresh Desk
        </button>
      </div>

      {alert && (
        <AlertBanner
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
        />
      )}

      {/* Filters */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-body p-3">
          <div className="row g-3">
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold small text-muted">Filter by Status</label>
              <select
                className="form-select"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="ALL">All Statuses</option>
                <option value="OPEN">Open (Awaiting Review)</option>
                <option value="IN_PROGRESS">In Progress (Under Investigation)</option>
                <option value="PENDING_CUSTOMER">Pending Customer</option>
                <option value="RESOLVED">Resolved</option>
                <option value="CLOSED">Closed</option>
              </select>
            </div>

            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold small text-muted">Filter by Priority</label>
              <select
                className="form-select"
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
              >
                <option value="ALL">All Priorities</option>
                <option value="URGENT">Urgent Priority</option>
                <option value="HIGH">High Priority</option>
                <option value="MEDIUM">Medium Priority</option>
                <option value="LOW">Low Priority</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Tickets Table */}
      <div className="card shadow-sm border-0">
        <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
          <h5 className="fw-bold mb-0">
            <i className="bi bi-headset me-2 text-primary"></i> Support Tickets ({tickets.length})
          </h5>
        </div>
        <div className="card-body p-0">
          {loading ? (
            <LoadingSpinner message="Loading all platform tickets..." />
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead className="table-light">
                  <tr>
                    <th className="ps-4">Ticket #</th>
                    <th>Customer</th>
                    <th>Subject</th>
                    <th>Category</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Assigned Officer</th>
                    <th className="pe-4 text-end">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="text-center py-5 text-muted">
                        <i className="bi bi-inbox fs-2 d-block mb-2 text-secondary"></i>
                        No tickets matching current filters.
                      </td>
                    </tr>
                  ) : (
                    tickets.map((t) => {
                      const userDisplay = t.user?.username || t.username || 'Customer';
                      const assignedDisplay = t.assigned_to?.username || 'Unassigned';

                      return (
                        <tr
                          key={t.id}
                          onClick={() => handleOpenTicketModal(t)}
                          style={{ cursor: 'pointer' }}
                        >
                          <td className="ps-4 fw-bold text-primary">
                            {t.ticket_number || `#${String(t.id).slice(0, 8)}`}
                          </td>
                          <td className="fw-semibold text-dark">
                            {userDisplay}
                          </td>
                          <td className="fw-medium">
                            {t.subject}
                          </td>
                          <td>
                            <span className="badge bg-light text-dark border">
                              {t.category ? t.category.replace('_', ' ') : 'General'}
                            </span>
                          </td>
                          <td>{getPriorityBadge(t.priority)}</td>
                          <td>{getStatusBadge(t.status)}</td>
                          <td className="text-muted small">
                            {assignedDisplay === 'Unassigned' ? (
                              <span className="text-danger fw-semibold">Unassigned</span>
                            ) : (
                              assignedDisplay
                            )}
                          </td>
                          <td className="pe-4 text-end text-muted small">
                            {formatDateTime(t.created_at)}
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

      {/* Ticket Management Modal */}
      {selectedTicket && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
            <div className="modal-content shadow-lg border-0 rounded-4">
              <div className="modal-header">
                <div>
                  <h5 className="modal-title fw-bold mb-1">
                    {selectedTicket.ticket_number || `#${String(selectedTicket.id).slice(0, 8)}`}: {selectedTicket.subject}
                  </h5>
                  <div className="d-flex align-items-center gap-2">
                    <span className="badge bg-light text-dark border">User: {selectedTicket.user?.username || 'Customer'}</span>
                    {getStatusBadge(selectedTicket.status)}
                    {getPriorityBadge(selectedTicket.priority)}
                  </div>
                </div>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setSelectedTicket(null)}
                ></button>
              </div>

              <div className="modal-body p-4">
                {/* Officer Status Controls Bar */}
                <div className="p-3 bg-light rounded-3 mb-4">
                  <div className="row g-2 align-items-center">
                    <div className="col-12 col-sm-auto">
                      <span className="fw-semibold small">Update Status:</span>
                    </div>
                    <div className="col-12 col-sm-auto">
                      <select
                        className="form-select form-select-sm"
                        value={newStatus}
                        onChange={(e) => setNewStatus(e.target.value)}
                      >
                        <option value="OPEN">OPEN</option>
                        <option value="IN_PROGRESS">IN_PROGRESS</option>
                        <option value="PENDING_CUSTOMER">PENDING_CUSTOMER</option>
                        <option value="RESOLVED">RESOLVED</option>
                        <option value="CLOSED">CLOSED</option>
                      </select>
                    </div>
                    <div className="col-auto">
                      <button
                        className="btn btn-sm btn-primary"
                        disabled={updatingStatus}
                        onClick={handleUpdateStatus}
                      >
                        {updatingStatus ? 'Updating...' : 'Save Status'}
                      </button>
                    </div>
                    <div className="col-auto ms-auto">
                      <button
                        className="btn btn-sm btn-outline-secondary"
                        onClick={handleAssignToMe}
                      >
                        <i className="bi bi-person-check me-1"></i> Assign to Me
                      </button>
                    </div>
                  </div>
                </div>

                {/* Messages Thread */}
                <h6 className="fw-bold mb-3 text-secondary">Discussion Thread</h6>
                {loadingMessages ? (
                  <div className="py-4 text-center">
                    <div className="spinner-border text-primary" role="status"></div>
                  </div>
                ) : (
                  <div className="d-flex flex-column gap-3 mb-4" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {messages.length === 0 ? (
                      <div className="text-muted text-center py-4 bg-light rounded">
                        No messages in this ticket thread yet.
                      </div>
                    ) : (
                      messages.map((m) => {
                        const isMe = m.sender?.username === user?.username;
                        return (
                          <div
                            key={m.id}
                            className={`p-3 rounded-3 ${isMe ? 'bg-primary-subtle ms-auto' : 'bg-light me-auto'}`}
                            style={{ maxWidth: '80%' }}
                          >
                            <div className="d-flex justify-content-between align-items-center mb-1">
                              <span className="fw-bold small text-dark">
                                {m.sender?.username || 'User'}
                              </span>
                              <span className="text-muted small ms-3">
                                {formatDateTime(m.created_at)}
                              </span>
                            </div>
                            <div className="text-dark" style={{ whiteSpace: 'pre-wrap' }}>
                              {m.message_text}
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                )}

                {/* Reply Form */}
                <form onSubmit={handleSendReply}>
                  <label className="form-label fw-semibold small">Finance Officer Reply</label>
                  <textarea
                    className="form-control mb-3"
                    rows="3"
                    placeholder="Type official reply or resolution details to customer..."
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    required
                  ></textarea>
                  <div className="text-end">
                    <button type="submit" className="btn btn-primary fw-semibold px-4">
                      Send Reply
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TicketManagementPage;
