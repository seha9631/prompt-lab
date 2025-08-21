import AppRouter from './AppRouter';
import Navbar from '../widgets/navbar';
import LoginDialog from '../features/auth/LoginDialog';
import CssBaseline from '@mui/material/CssBaseline';
import { lightTheme, darkTheme } from '../ThemeManager'
import { ThemeProvider } from '@mui/material/styles';
import I18nProvider from './providers/I18nProviders';
import { useState } from 'react';

function App() {
  const [loginOpen, setLoginOpen] = useState(false);

  const handleLoginClick = () => {
    setLoginOpen(true);
  };

  const handleLogoutClick = () => {
    console.log('logout');
  };

  return (
    <>
      <I18nProvider>
        <ThemeProvider theme={darkTheme}>
          <CssBaseline />
          <Navbar
            isLoggedIn={false}
            userName="Guest"
            onLoginClick={handleLoginClick}
            onLogoutClick={handleLogoutClick}
          />
          <LoginDialog open={loginOpen} onClose={() => setLoginOpen(false)} />
          <AppRouter />
        </ThemeProvider>
      </I18nProvider>
    </>
  )
}

export default App
