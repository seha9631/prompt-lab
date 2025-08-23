import { useState } from 'react';

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
  const [dialogType, setDialogType] = useState(null);

  const openLogin = () => setDialogType('login');
  const openSignup = () => setDialogType('signup');
  const closeDialog = () => setDialogType(null);

  const handleLogoutClick = () => signOut();

  const handleLoginSubmit = async (values) => {
    await signIn(values);
    closeDialog();
  };

  const createAndLogin = async ({ email, password, name, teamName, keep }) => {
    await api.post('/users', {
      app_id: email,
      app_password: password,
      name,
      team_name: teamName,
    });

    await signIn({ id: email, password, keep });
    closeDialog();
  };

  return (
    <>
      <CssBaseline />
      <Navbar
        isLoggedIn={!!accessToken}
        userName={user?.name || 'User'}
        onLoginClick={openLogin}
        onLogoutClick={handleLogoutClick}
      />

      <LoginDialog
        open={dialogType === 'login'}
        onClose={closeDialog}
        onSubmit={handleLoginSubmit}
        onOpenSignup={openSignup}
      // onOpenFindId={() => setDialogType('findId')}
      // onOpenFindPw={() => setDialogType('findPw')}
      />

      <SignupDialog
        open={dialogType === 'signup'}
        onClose={closeDialog}
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