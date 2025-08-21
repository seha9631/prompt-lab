import PropTypes from 'prop-types';
import { Link as RouterLink } from 'react-router-dom';
import { AppBar, Toolbar, Container, Stack, Typography, Button } from '@mui/material';
import { useTranslation } from 'react-i18next';
import BeakerLogo from './BeakerLogo';
import NavItem from './NavItem';
import UserMenu from './UserMenu';
import LanguageMenu from './LanguageMenu';

const NAV_ITEMS_KEYS = [
    { to: '/projects', key: 'projects' },
    { to: '/usage', key: 'usage' }
];

function Navbar({
    isLoggedIn = true,
    userName = 'your name',
    onLoginClick,
    onLogoutClick
}) {
    const { t } = useTranslation('nav');

    return (
        <AppBar
            position="static"
            elevation={0}
            color="default"
            enableColorOnDark
            sx={(theme) => ({
                bgcolor: theme.palette.background.paper,
                borderBottom: `1px solid ${theme.palette.divider}`,
            })}
        >
            <Container maxWidth="lg">
                <Toolbar disableGutters sx={{ minHeight: 64 }}>
                    <Stack
                        component={RouterLink}
                        to="/"
                        direction="row"
                        alignItems="center"
                        gap={1.25}
                        sx={(theme) => ({
                            textDecoration: 'none',
                            color: theme.palette.text.primary,
                            mr: 3,
                        })}
                        aria-label="Go to home"
                    >
                        <BeakerLogo />
                        <Typography variant="h6" fontWeight={800}>{t('brand')}</Typography>
                    </Stack>

                    <Stack direction="row" gap={3} sx={{ flex: 1 }}>
                        {NAV_ITEMS_KEYS.map(({ to, key }) => (
                            <NavItem key={to} to={to} label={t(key)} />
                        ))}
                    </Stack>

                    <Stack direction="row" alignItems="center" gap={2}>
                        <LanguageMenu />
                        {!isLoggedIn ? (
                            <Button
                                variant="contained"
                                color="primary"
                                size="small"
                                onClick={onLoginClick}
                                sx={{ textTransform: 'none', fontWeight: 700, px: 1.75, borderRadius: 2 }}
                                aria-label={t('login')}
                            >
                                {t('login')}
                            </Button>
                        ) : (
                            <UserMenu
                                userName={userName}
                                onLogoutClick={onLogoutClick}
                                labels={{
                                    profile: t('profile'),
                                    settings: t('settings'),
                                    logout: t('logout'),
                                }}
                            />
                        )}
                    </Stack>
                </Toolbar>
            </Container>
        </AppBar>
    );
}

Navbar.propTypes = {
    isLoggedIn: PropTypes.bool,
    userName: PropTypes.string,
    onLoginClick: PropTypes.func,
    onLogoutClick: PropTypes.func
};

export default Navbar;