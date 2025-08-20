import { createTheme } from '@mui/material/styles';

export const lightTheme = createTheme({
    palette: {
        mode: 'light',
        primary: { main: '#7b57ff' },
    },
})

export const darkTheme = createTheme({
    palette: {
        mode: 'dark',
        primary: { main: '#7b57ff' },
    },
})