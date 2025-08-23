import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import AppRouter from './AppRouter';
import Navbar from '../widgets/navbar';
import LoginDialog from '../features/auth/ui/LoginDialog';
import SignupDialog from '../features/auth/ui/SignupDialog';

import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { lightTheme, darkTheme } from '../ThemeManager';

import I18nProvider from './providers/I18nProvider';
import AuthProvider, { useAuthContext } from './providers/AuthProvider';
import { api } from '../shared/api/base';

function Shell() {
  const { user, accessToken, signIn, signOut } = useAuthContext();

  const [loginOpen, setLoginOpen] = useState(false);
  const [signupOpen, setSignupOpen] = useState(false);

  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (location.pathname === '/signup') {
      setSignupOpen(true);
    }
  }, [location.pathname]);

  const handleLoginClick = () => setLoginOpen(true);
  const handleLogoutClick = () => signOut();
  const handleLoginSubmit = async (values) => {
    await signIn(values);
    setLoginOpen(false);
  };

  const createAndLogin = async ({ email, password, name, teamName, keep }) => {
    await api.post('/users', {
      app_id: email,
      app_password: password,
      name,
      team_name: teamName,
    });

    await signIn({ id: email, password, keep });

    setSignupOpen(false);
    if (location.pathname === '/signup') navigate('/', { replace: true });
  };

  return (
    <>
      <CssBaseline />
      <Navbar
        isLoggedIn={!!accessToken}
        userName={user?.name || 'User'}
        onLoginClick={handleLoginClick}
        onLogoutClick={handleLogoutClick}
      />

      <LoginDialog
        open={loginOpen}
        onClose={() => setLoginOpen(false)}
        onSubmit={handleLoginSubmit}
      />

      <SignupDialog
        open={signupOpen}
        onClose={() => {
          setSignupOpen(false);
          if (location.pathname === '/signup') navigate('/', { replace: true });
        }}
        onSubmit={createAndLogin}
      />

      <AppRouter />
    </>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <ThemeProvider theme={darkTheme}>
        <AuthProvider>
          <Shell />
        </AuthProvider>
      </ThemeProvider>
    </I18nProvider>
  );
}