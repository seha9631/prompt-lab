import { useState, useEffect, useCallback } from 'react';
import { api } from '../../../shared/api/base';
import { login as loginApi, logout as logoutApi } from '../api/auth';

const ACCESS_KEY = 'access_token';
const USER_KEY = 'user';
const STORAGE_KEY = 'auth_storage';

function getStorage() {
    const prefer = localStorage.getItem(STORAGE_KEY) || 'session';
    return prefer === 'local' ? localStorage : sessionStorage;
}

function useAuth() {
    const [accessToken, setAccessToken] = useState(null);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const storage = getStorage();
        const token = storage.getItem(ACCESS_KEY);
        const userJson = storage.getItem(USER_KEY);
        if (token) setAccessToken(token);
        if (userJson) setUser(JSON.parse(userJson));
    }, []);

    const signIn = useCallback(async ({ id, password, keep }) => {
        const data = await loginApi({ app_id: id, app_password: password });
        const at = data?.data?.access_token;
        const u = data?.data?.user;

        const storage = keep ? localStorage : sessionStorage;
        localStorage.setItem(STORAGE_KEY, keep ? 'local' : 'session');

        setAccessToken(at);
        setUser(u);
        storage.setItem(ACCESS_KEY, at);
        storage.setItem(USER_KEY, JSON.stringify(u));
    }, []);

    const signOut = useCallback(async () => {
        try { await logoutApi(); } catch { }
        setAccessToken(null);
        setUser(null);
        sessionStorage.removeItem(ACCESS_KEY);
        sessionStorage.removeItem(USER_KEY);
        localStorage.removeItem(ACCESS_KEY);
        localStorage.removeItem(USER_KEY);
        localStorage.removeItem(STORAGE_KEY);
    }, []);

    useEffect(() => {
        const id = api.interceptors.request.use((config) => {
            if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
            return config;
        });
        return () => api.interceptors.request.eject(id);
    }, [accessToken]);

    return { user, accessToken, signIn, signOut, setAccessToken, setUser };
}

export default useAuth;