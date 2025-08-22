import { createContext, useContext, useMemo, useEffect } from 'react';
import useAuth from '../../features/auth/model/useAuth';
import { attachTokenRefresh } from '../../features/auth/model/attachTokenRefresh';

const AuthContext = createContext(undefined);

function AuthProvider({ children }) {
    const auth = useAuth();
    const value = useMemo(() => auth, [auth]);

    useEffect(() => {
        const eject = attachTokenRefresh(auth.setAccessToken, () => {
            try {
                sessionStorage.removeItem('access_token');
                sessionStorage.removeItem('user');
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                localStorage.removeItem('auth_storage');
            } catch { }
            auth.setAccessToken(null);
        });
        return eject;
    }, [auth.setAccessToken]);

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuthContext must be used within <AuthProvider>.');
    return ctx;
}

export default AuthProvider;