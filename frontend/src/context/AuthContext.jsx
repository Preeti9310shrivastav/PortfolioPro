import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [tokens, setTokens] = useState(() => {
    const access = localStorage.getItem('access_token');
    const refresh = localStorage.getItem('refresh_token');
    return access ? { access, refresh } : null;
  });

  const [loading, setLoading] = useState(true);

  // Fetch full profile on mount if tokens exist
  const fetchProfile = useCallback(async () => {
    try {
      const res = await api.get('/auth/profile/');
      const profileData = res.data?.data?.user || res.data?.data || res.data;
      if (profileData && profileData.id) {
        setUser(profileData);
        localStorage.setItem('user', JSON.stringify(profileData));
      }
    } catch (err) {
      console.warn('Failed to fetch profile on initial load:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (localStorage.getItem('access_token')) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [fetchProfile]);

  const login = async (username, password) => {
    const res = await api.post('/auth/login/', { username, password });
    const responseData = res.data?.data || res.data;
    const userData = responseData.user;
    const tokensData = responseData.tokens;

    if (tokensData?.access) {
      localStorage.setItem('access_token', tokensData.access);
      if (tokensData.refresh) {
        localStorage.setItem('refresh_token', tokensData.refresh);
      }
      setTokens(tokensData);
    }

    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
    }

    return responseData;
  };

  const register = async (registrationData) => {
    const res = await api.post('/auth/register/', registrationData);
    const responseData = res.data?.data || res.data;
    const userData = responseData.user;
    const tokensData = responseData.tokens;

    if (tokensData?.access) {
      localStorage.setItem('access_token', tokensData.access);
      if (tokensData.refresh) {
        localStorage.setItem('refresh_token', tokensData.refresh);
      }
      setTokens(tokensData);
    }

    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
    }

    return responseData;
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        await api.post('/auth/logout/', { refresh: refreshToken });
      } catch (err) {
        console.warn('Logout request failed or token was invalid:', err);
      }
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
    setTokens(null);
  };

  const updateUser = (newUserData) => {
    setUser(newUserData);
    localStorage.setItem('user', JSON.stringify(newUserData));
  };

  const roleUpper = user?.role ? String(user.role).toUpperCase() : '';
  const isAuthenticated = !!user && !!localStorage.getItem('access_token');
  const isCustomer = roleUpper === 'CUSTOMER';
  const isFinanceOfficer = roleUpper === 'FINANCE_OFFICER' || roleUpper === 'ADMIN';

  const contextValue = useMemo(() => ({
    user,
    tokens,
    login,
    register,
    logout,
    updateUser,
    loading,
    isAuthenticated,
    isCustomer,
    isFinanceOfficer
  }), [user, tokens, loading, isAuthenticated, isCustomer, isFinanceOfficer]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
