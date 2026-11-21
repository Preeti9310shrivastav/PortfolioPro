import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import { formatDate } from '../../utils/formatters';
import AlertBanner from '../../components/common/AlertBanner';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const ProfilePage = () => {
  const { user, updateUser } = useAuth();

  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    phone_number: '',
    city: '',
    state: '',
    bio: ''
  });

  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: ''
  });

  const [loading, setLoading] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  const [profileMsg, setProfileMsg] = useState(null);
  const [passwordMsg, setPasswordMsg] = useState(null);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await api.get('/auth/profile/');
        const u = res.data?.data?.user || res.data?.data || res.data;
        if (u) {
          setProfileData({
            first_name: u.first_name || '',
            last_name: u.last_name || '',
            phone_number: u.phone_number || '',
            city: u.profile?.city || '',
            state: u.profile?.state || '',
            bio: u.profile?.bio || ''
          });
        }
      } catch (err) {
        // Fallback to auth context user
        if (user) {
          setProfileData({
            first_name: user.first_name || '',
            last_name: user.last_name || '',
            phone_number: user.phone_number || '',
            city: user.profile?.city || '',
            state: user.profile?.state || '',
            bio: user.profile?.bio || ''
          });
        }
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, [user]);

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePasswordChangeInput = (e) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({ ...prev, [name]: value }));
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileMsg(null);

    try {
      const res = await api.put('/auth/profile/', profileData);
      const updated = res.data?.data?.user || res.data?.data || res.data;
      if (updated) {
        updateUser(updated);
      }
      setProfileMsg({ type: 'success', text: res.data?.message || 'Profile updated successfully!' });
    } catch (err) {
      const resData = err.response?.data;
      setProfileMsg({
        type: 'danger',
        text: resData?.message || 'Failed to update profile.',
        errors: resData?.errors
      });
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setPasswordMsg(null);

    if (passwordData.new_password !== passwordData.new_password_confirm) {
      setPasswordMsg({ type: 'danger', text: 'New passwords do not match.' });
      return;
    }

    setChangingPassword(true);
    try {
      const res = await api.post('/auth/password-change/', passwordData);
      setPasswordMsg({ type: 'success', text: res.data?.message || 'Password changed successfully.' });
      setPasswordData({ old_password: '', new_password: '', new_password_confirm: '' });
    } catch (err) {
      const resData = err.response?.data;
      setPasswordMsg({
        type: 'danger',
        text: resData?.message || 'Failed to change password.',
        errors: resData?.errors
      });
    } finally {
      setChangingPassword(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading profile..." />;
  }

  return (
    <div className="container py-4">
      {/* Title */}
      <div className="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h2 className="fw-bold mb-1">User Profile &amp; Settings</h2>
          <p className="text-muted mb-0">Manage your account information and security credentials</p>
        </div>
      </div>

      <div className="row g-4">
        {/* Left Column: Account Overview Card */}
        <div className="col-12 col-lg-4">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body text-center p-4">
              <div className="d-inline-flex p-3 rounded-circle bg-primary-subtle text-primary mb-3">
                <i className="bi bi-person-badge fs-1"></i>
              </div>
              <h4 className="fw-bold mb-1">
                {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.username}
              </h4>
              <p className="text-muted small mb-2">@{user?.username}</p>
              <div className="d-flex justify-content-center gap-2 mb-3">
                <span className="badge bg-primary px-3 py-2">
                  <i className="bi bi-shield-check me-1"></i> {user?.role || 'Customer'}
                </span>
                <span className={`badge ${user?.is_active ? 'bg-success' : 'bg-danger'} px-3 py-2`}>
                  {user?.is_active ? 'Active Account' : 'Inactive'}
                </span>
              </div>

              <hr />

              <div className="text-start">
                <div className="mb-2">
                  <small className="text-muted d-block">Email Address</small>
                  <span className="fw-semibold">{user?.email || '—'}</span>
                </div>
                <div className="mb-2">
                  <small className="text-muted d-block">Phone Number</small>
                  <span className="fw-semibold">{user?.phone_number || '—'}</span>
                </div>
                <div className="mb-2">
                  <small className="text-muted d-block">Member Since</small>
                  <span className="fw-semibold">{formatDate(user?.date_joined)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Edit Profile & Password Change */}
        <div className="col-12 col-lg-8">
          {/* Edit Profile Card */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white py-3">
              <h5 className="fw-bold mb-0 text-dark">
                <i className="bi bi-person-lines-fill me-2 text-primary"></i> Edit Personal Information
              </h5>
            </div>
            <div className="card-body p-4">
              {profileMsg && (
                <AlertBanner
                  type={profileMsg.type}
                  message={profileMsg.text}
                  errors={profileMsg.errors}
                  onClose={() => setProfileMsg(null)}
                />
              )}

              <form onSubmit={handleProfileSubmit}>
                <div className="row g-3">
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">First Name</label>
                    <input
                      type="text"
                      name="first_name"
                      className="form-control"
                      value={profileData.first_name}
                      onChange={handleProfileChange}
                    />
                  </div>
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">Last Name</label>
                    <input
                      type="text"
                      name="last_name"
                      className="form-control"
                      value={profileData.last_name}
                      onChange={handleProfileChange}
                    />
                  </div>
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">Phone Number</label>
                    <input
                      type="tel"
                      name="phone_number"
                      className="form-control"
                      value={profileData.phone_number}
                      onChange={handleProfileChange}
                    />
                  </div>
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">City</label>
                    <input
                      type="text"
                      name="city"
                      className="form-control"
                      value={profileData.city}
                      onChange={handleProfileChange}
                    />
                  </div>
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">State</label>
                    <input
                      type="text"
                      name="state"
                      className="form-control"
                      value={profileData.state}
                      onChange={handleProfileChange}
                    />
                  </div>
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">Bio</label>
                    <input
                      type="text"
                      name="bio"
                      className="form-control"
                      placeholder="Short trading bio"
                      value={profileData.bio}
                      onChange={handleProfileChange}
                    />
                  </div>
                </div>

                <div className="mt-4 text-end">
                  <button
                    type="submit"
                    className="btn btn-primary px-4 fw-semibold"
                    disabled={savingProfile}
                  >
                    {savingProfile ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Saving Changes...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check2-circle me-1"></i> Save Changes
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Change Password Card */}
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white py-3">
              <h5 className="fw-bold mb-0 text-dark">
                <i className="bi bi-shield-lock me-2 text-primary"></i> Change Security Password
              </h5>
            </div>
            <div className="card-body p-4">
              {passwordMsg && (
                <AlertBanner
                  type={passwordMsg.type}
                  message={passwordMsg.text}
                  errors={passwordMsg.errors}
                  onClose={() => setPasswordMsg(null)}
                />
              )}

              <form onSubmit={handlePasswordSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold small">Current Password</label>
                  <input
                    type="password"
                    name="old_password"
                    className="form-control"
                    value={passwordData.old_password}
                    onChange={handlePasswordChangeInput}
                    required
                  />
                </div>
                <div className="row g-3">
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">New Password</label>
                    <input
                      type="password"
                      name="new_password"
                      className="form-control"
                      minLength={8}
                      value={passwordData.new_password}
                      onChange={handlePasswordChangeInput}
                      required
                    />
                  </div>
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold small">Confirm New Password</label>
                    <input
                      type="password"
                      name="new_password_confirm"
                      className="form-control"
                      minLength={8}
                      value={passwordData.new_password_confirm}
                      onChange={handlePasswordChangeInput}
                      required
                    />
                  </div>
                </div>

                <div className="mt-4 text-end">
                  <button
                    type="submit"
                    className="btn btn-outline-danger px-4 fw-semibold"
                    disabled={changingPassword}
                  >
                    {changingPassword ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Updating Password...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-key me-1"></i> Update Password
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
