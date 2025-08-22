import { useState } from 'react';
import AppRouter from './AppRouter';
import Navbar from '../widgets/navbar';
import LoginDialog from '../features/auth/ui/LoginDialog';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { lightTheme, darkTheme } from '../ThemeManager';
import I18nProvider from './providers/I18nProvider';
import AuthProvider, { useAuthContext } from './providers/AuthProvider';

function Shell() {
  const [loginOpen, setLoginOpen] = useState(false);
  const { user, accessToken, signIn, signOut } = useAuthContext();

  const handleLoginClick = () => setLoginOpen(true);
  const handleLogoutClick = () => signOut();
  const handleSubmit = async (values) => {
    await signIn(values);
    setLoginOpen(false);
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
        onSubmit={handleSubmit}
      />
      <AppRouter />
    </>
  );
}

function App() {
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

export default App;