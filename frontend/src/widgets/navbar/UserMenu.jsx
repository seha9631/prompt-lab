import PropTypes from 'prop-types';
import { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Chip, Avatar, Menu, MenuItem, Divider } from '@mui/material';

function UserMenu({ userName, onLogoutClick, labels }) {
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);
    const menuId = 'navbar-user-menu';
    const initial = userName?.split(' ')?.[0]?.slice(0, 1)?.toUpperCase() || 'U';

    const handleOpen = (e) => setAnchorEl(e.currentTarget);
    const handleClose = () => setAnchorEl(null);

    return (
        <>
            <Chip
                aria-controls={open ? menuId : undefined}
                aria-haspopup="menu"
                aria-expanded={open ? 'true' : undefined}
                onClick={handleOpen}
                clickable
                color="primary"
                sx={{
                    height: 40,
                    borderRadius: 20,
                    px: 0.5,
                    '& .MuiChip-label': { px: 1.2, fontSize: 12 },
                }}
                avatar={
                    <Avatar
                        sx={(theme) => ({
                            bgcolor: theme.palette.primary.main,
                            color: theme.palette.primary.contrastText,
                            width: 36,
                            height: 36,
                            fontSize: 12,
                        })}
                        aria-hidden
                    >
                        {initial}
                    </Avatar>
                }
                label={userName}
            />

            <Menu
                id={menuId}
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
                <MenuItem component={RouterLink} to="/profile" onClick={handleClose}>
                    {labels.profile}
                </MenuItem>
                <MenuItem component={RouterLink} to="/settings" onClick={handleClose}>
                    {labels.settings}
                </MenuItem>
                <Divider />
                <MenuItem
                    onClick={() => {
                        handleClose();
                        onLogoutClick?.();
                    }}
                    sx={{ color: 'error.main' }}
                >
                    {labels.logout}
                </MenuItem>
            </Menu>
        </>
    );
}

UserMenu.propTypes = {
    userName: PropTypes.string.isRequired,
    onLogoutClick: PropTypes.func,
};

export default UserMenu;