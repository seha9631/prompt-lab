import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';
import { Link as MUILink } from '@mui/material';

function NavItem({ to, label }) {
    return (
        <MUILink
            component={NavLink}
            to={to}
            underline="none"
            sx={(theme) => ({
                color: theme.palette.text.secondary,
                fontWeight: 600,
                px: 1,
                py: 0.5,
                borderRadius: 1,
                position: 'relative',
                textDecoration: 'none',
                '&:hover': { color: theme.palette.text.primary },
                '&.active': {
                    color: theme.palette.text.primary,
                },
            })}
        >
            {label}
        </MUILink>
    );
}

NavItem.propTypes = {
    to: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
};

export default NavItem;