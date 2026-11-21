import React, { useState, useEffect, useCallback } from 'react';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { formatDateTime } from '../../utils/formatters';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AlertBanner from '../../components/common/AlertBanner';

const SupportPage = () => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);

  // Create Ticket Form State
  const [subject, setSubject] = useState('');
  const [category, setCategory] = useState('TRADE_DISPUTE');
  const [priority, setPriority] = useState('MEDIUM');
  const [description, setDescription] = useState('');
  const [creating, setCreating] = useState(false);

  // Selected Ticket Modal State
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [sendingReply, setSendingReply] = useState(false);

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setAlert(null);
    try {
      const res = await api.get('/support/tickets/');
      const list = res.data?.data || res.data?.results || res.data;
      setTickets(Array.isArray(list) ? list : []);
    } catch (err) {
      console.warn('Failed to load tickets:', err);
      setAlert({
        type: 'danger',
        message: 'Failed to fetch support tickets. Please try again later.'
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  const handleCreateTicket = async (e) => {
    e.preventDefault();
    if (!subject.trim() || !description.trim()) {
      setAlert({ type: 'danger', message: 'Subject and description are required.' });
      return;
    }

    setCreating(true);
    try {
      const payload = {
        subject: subject.trim(),
        category,
        priority,
        description: description.trim(),
        message_text: description.trim()
      };

      await api.post('/support/tickets/', payload);
      setAlert({ type: 'success', message: 'Support ticket submitted successfully!' });
      setSubject('');
      setDescription('');
      fetchTickets();
    } catch (err) {
      setAlert({
        type: 'danger',
        message: err.response?.data?.message || 'Failed to submit ticket.'
      });
    } finally {
      setCreating(false);
    }
  };

  const handleOpenTicketModal = async (ticket) => {
    setSelectedTicket(ticket);
    setLoadingMessages(true);
    try {
      const res = await api.get(`/support/tickets/${ticket.id}/messages/`);
      const msgList = res.data?.data || res.data?.results || res.data;
      setMessages(Array.isArray(msgList) ? msgList : []);
    } catch (err) {
      // If messages endpoint returns empty or error, initialize with empty
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleSendReply = async (e) => {
    e.preventDefault();
    if (!replyText.trim() || !selectedTicket) return;

    setSendingReply(true);
    try {
      const payload = { message_text: replyText.trim() };
      const res = await api.post(`/support/tickets/${selectedTicket.id}/messages/`, payload);
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
      alert(err.response?.data?.message || 'Failed to send reply.');
    } finally {
      setSendingReply(false);
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

  if (loading) {
    return <LoadingSpinner message="Loading support desk..." />;
  }

  return (
    <div className="container-fluid px-4 py-4">
      {/* Page Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Customer Support &amp; Helpdesk</h2>
          <p className="text-muted mb-0">Get assistance from our dedicated finance officers and trading support team</p>
        </div>
      </div>

      {alert && (
        <AlertBanner
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
        />
      )}

      <div className="row g-4">
        {/* Left Column: Create Ticket Form */}
        <div className="col-12 col-lg-5">
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white py-3">
              <h5 className="fw-bold mb-0">
                <i className="bi bi-pencil-square me-2 text-primary"></i> Raise Support Ticket
              </h5>
            </div>
            <div className="card-body p-4">
              <form onSubmit={handleCreateTicket}>
                <div className="mb-3">
                  <label className="form-label fw-semibold small">Subject</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Brief description of the issue"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    required
                  />
                </div>

                <div className="row g-2 mb-3">
                  <div className="col-6">
                    <label className="form-label fw-semibold small">Category</label>
                    <select
                      className="form-select"
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                    >
                      <option value="TRADE_DISPUTE">Trade Dispute</option>
                      <option value="DEPOSIT_WITHDRAWAL">Deposit / Withdrawal</option>
                      <option value="KYC_ACCOUNT">KYC / Account Freeze</option>
                      <option value="TECHNICAL">Platform Bug / Glitch</option>
                      <option value="GENERAL">General Inquiry</option>
                    </select>
                  </div>
                  <div className="col-6">
                    <label className="form-label fw-semibold small">Priority</label>
                    <select
                      className="form-select"
                      value={priority}
                      onChange={(e) => setPriority(e.target.value)}
                    >
                      <option value="LOW">Low</option>
                      <option value="MEDIUM">Medium</option>
                      <option value="HIGH">High</option>
                      <option value="URGENT">Urgent</option>
                    </select>
                  </div>
                </div>

                <div className="mb-4">
                  <label className="form-label fw-semibold small">Description</label>
                  <textarea
                    className="form-control"
                    rows="4"
                    placeholder="Provide relevant details, order IDs, or error messages..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    required
                  ></textarea>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100 py-2 fw-semibold"
                  disabled={creating}
                >
                  {creating ? 'Submitting Ticket...' : 'Submit Support Request'}
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Right Column: Ticket History Table */}
        <div className="col-12 col-lg-7">
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 className="fw-bold mb-0">
                <i className="bi bi-clock-history me-2 text-primary"></i> My Support Tickets
              </h5>
              <span className="badge bg-secondary">{tickets.length} Submitted</span>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th className="ps-4">Ticket #</th>
                      <th>Subject</th>
                      <th>Category</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th className="pe-4 text-end">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tickets.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="text-center py-5 text-muted">
                          <i className="bi bi-headset fs-2 d-block mb-2 text-secondary"></i>
                          No tickets created yet. Submit a request using the form on the left.
                        </td>
                      </tr>
                    ) : (
                      tickets.map((t) => (
                        <tr
                          key={t.id}
                          onClick={() => handleOpenTicketModal(t)}
                          style={{ cursor: 'pointer' }}
                        >
                          <td className="ps-4 fw-bold text-primary">
                            {t.ticket_number || `#${String(t.id).slice(0, 8)}`}
                          </td>
                          <td className="fw-medium text-dark">
                            {t.subject}
                          </td>
                          <td>
                            <span className="badge bg-light text-dark border">
                              {t.category ? t.category.replace('_', ' ') : 'General'}
                            </span>
                          </td>
                          <td>
                            {getPriorityBadge(t.priority)}
                          </td>
                          <td>
                            {getStatusBadge(t.status)}
                          </td>
                          <td className="pe-4 text-end text-muted small">
                            {formatDateTime(t.created_at)}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Ticket Details & Thread Modal */}
      {selectedTicket && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
            <div className="modal-content shadow-lg border-0 rounded-4">
              <div className="modal-header">
                <div>
                  <h5 className="modal-title fw-bold mb-0">
                    {selectedTicket.ticket_number || `#${String(selectedTicket.id).slice(0, 8)}`}: {selectedTicket.subject}
                  </h5>
                  <div className="d-flex gap-2 mt-1">
                    {getStatusBadge(selectedTicket.status)}
                    {getPriorityBadge(selectedTicket.priority)}
                    <span className="text-muted small">
                      Opened: {formatDateTime(selectedTicket.created_at)}
                    </span>
                  </div>
                </div>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setSelectedTicket(null)}
                ></button>
              </div>

              <div className="modal-body p-4">
                {/* Messages Thread */}
                <h6 className="fw-bold mb-3 text-secondary">Discussion Thread</h6>
                {loadingMessages ? (
                  <div className="py-4 text-center">
                    <div className="spinner-border text-primary" role="status"></div>
                  </div>
                ) : (
                  <div className="d-flex flex-column gap-3 mb-4" style={{ maxHeight: '350px', overflowY: 'auto' }}>
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
                  <label className="form-label fw-semibold small">Post a Response</label>
                  <textarea
                    className="form-control mb-3"
                    rows="3"
                    placeholder="Type your message to support officers..."
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    required
                  ></textarea>
                  <div className="text-end">
                    <button
                      type="submit"
                      className="btn btn-primary fw-semibold px-4"
                      disabled={sendingReply}
                    >
                      {sendingReply ? 'Sending...' : 'Send Message'}
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

export default SupportPage;
