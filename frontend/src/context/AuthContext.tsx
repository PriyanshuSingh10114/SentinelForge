import React, { createContext, useContext, useEffect, useState } from 'react';
import { api, setAuthToken, getAuthToken } from '../api/client';

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  permissions: string[];
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setTokenState] = useState<string | null>(getAuthToken());
  const [loading, setLoading] = useState<boolean>(true);

  const refreshProfile = async () => {
    try {
      if (getAuthToken()) {
        const profile = await api.auth.me();
        setUser(profile);
      } else {
        setUser(null);
      }
    } catch (err) {
      console.warn('Session expired or invalid, logging out', err);
      setAuthToken(null);
      setTokenState(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshProfile();
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.auth.login(email, password);
    setAuthToken(res.access_token);
    setTokenState(res.access_token);
    const profile = await api.auth.me();
    setUser(profile);
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch (e) {
      // Ignore logout errors
    } finally {
      setAuthToken(null);
      setTokenState(null);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        loading,
        login,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};
