import { useState, useEffect, useCallback, useRef } from 'react';
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
    const tokenRef = useRef(null);

    useEffect(() => {
        const storage = getStorage();
        const token = storage.getItem(ACCESS_KEY);
        const userJson = storage.getItem(USER_KEY);
        if (token) {
            setAccessToken(token);
            tokenRef.current = token;
        }
        if (userJson) setUser(JSON.parse(userJson));
    }, []);

    const signIn = useCallback(async ({ id, password, keep }) => {
        const data = await loginApi({ app_id: id, app_password: password });
        const at = data?.data?.access_token;
        const u = data?.data?.user;

        const storage = keep ? localStorage : sessionStorage;
        localStorage.setItem(STORAGE_KEY, keep ? 'local' : 'session');

        setAccessToken(at);
        tokenRef.current = at;
        setUser(u);
        storage.setItem(ACCESS_KEY, at);
        storage.setItem(USER_KEY, JSON.stringify(u));
    }, []);

    const signOut = useCallback(async () => {
        try { await logoutApi(); } catch { }
        setAccessToken(null);
        tokenRef.current = null;
        setUser(null);
        sessionStorage.removeItem(ACCESS_KEY);
        sessionStorage.removeItem(USER_KEY);
        localStorage.removeItem(ACCESS_KEY);
        localStorage.removeItem(USER_KEY);
        localStorage.removeItem(STORAGE_KEY);

        delete api.defaults.headers.common.Authorization;
    }, []);

    useEffect(() => {
        const token = accessToken && String(accessToken).trim();
        if (token) {
            api.defaults.headers.common.Authorization = `Bearer ${token}`;
        } else {
            delete api.defaults.headers.common.Authorization;
        }
    }, [accessToken]);

    useEffect(() => {
        const id = api.interceptors.request.use(
            (config) => {
                const token = tokenRef.current && String(tokenRef.current).trim();
                if (token) {
                    if (typeof config.headers?.set === 'function') {
                        config.headers.set('Authorization', `Bearer ${token}`);
                    } else {
                        config.headers = config.headers || {};
                        config.headers.Authorization = `Bearer ${token}`;
                    }
                }
                return config;
            },
            (error) => Promise.reject(error)
        );
        return () => api.interceptors.request.eject(id);
    }, []);

    return { user, accessToken, signIn, signOut, setAccessToken, setUser };
}

export default useAuth;