'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthState, User } from '../lib/types';
import { getUserProfile } from '../lib/api';

const AuthContext = createContext<AuthState | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const validateToken = async () => {
      const storedToken = localStorage.getItem('authToken');
      if (storedToken) {
        try {
          const userProfile = await getUserProfile(storedToken);
          setUser(userProfile);
          setToken(storedToken);
        } catch {
          localStorage.removeItem('authToken');
        }
      }
      setLoading(false);
    };
    validateToken();
  }, []);

  const login = (newToken: string, newUser: User) => {
    localStorage.setItem('authToken', newToken);
    setToken(newToken);
    setUser(newUser);
  };

  const logout = () => {
    // Clear auth token
    localStorage.removeItem('authToken');
    
    // Clear user-specific data if user exists
    if (user?.id) {
      const userPrefix = `user_${user.id}_`;
      // Remove user-specific search data
      localStorage.removeItem(`${userPrefix}superconnect_search_results`);
      localStorage.removeItem(`${userPrefix}superconnect_search_query`);
      localStorage.removeItem(`${userPrefix}superconnect_search_filters`);
      
      // Clear any other user-specific localStorage items
      const keysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(userPrefix)) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => localStorage.removeItem(key));
    }
    
    setToken(null);
    setUser(null);
  };

  const value = {
    token,
    user,
    isLoggedIn: !!user,
    loading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};