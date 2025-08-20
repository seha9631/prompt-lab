import { useState } from 'react';
import { Button, Menu, MenuItem } from '@mui/material';
import { useTranslation } from 'react-i18next';

const LANGS = [
    { code: 'en', label: 'EN' },
    { code: 'ko', label: 'KO' }
];

function LanguageMenu() {
    const { i18n } = useTranslation();
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);
    const current = (i18n.language || 'en').slice(0, 2);

    const changeLang = async (code) => {
        await i18n.changeLanguage(code);
        localStorage.setItem('i18nextLng', code);
        setAnchorEl(null);
    };

    return (
        <>
            <Button
                variant="text"
                size="small"
                onClick={(e) => setAnchorEl(e.currentTarget)}
                aria-haspopup="menu"
                aria-expanded={open ? 'true' : undefined}
                aria-controls="lang-menu"
                sx={{ textTransform: 'none', fontWeight: 700 }}
            >
                {current.toUpperCase()}
            </Button>
            <Menu
                id="lang-menu"
                anchorEl={anchorEl}
                open={open}
                onClose={() => setAnchorEl(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
                {LANGS.map((l) => (
                    <MenuItem
                        key={l.code}
                        selected={current === l.code}
                        onClick={() => changeLang(l.code)}
                    >
                        {l.label}
                    </MenuItem>
                ))}
            </Menu>
        </>
    );
}

export default LanguageMenu;