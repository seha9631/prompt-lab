import { useMemo, useState } from 'react';
import {
    Dialog, DialogContent, Stack, Typography, TextField, Button,
    Box, Alert, CircularProgress, IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { useTranslation } from 'react-i18next';

const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$/;
const pwRules = [
    { test: (pw) => pw.length >= 8, i18n: 'errPW.minLength', fallback: 'Password must be at least 8 characters.' },
    { test: (pw) => /[A-Z]/.test(pw), i18n: 'errPW.upper', fallback: 'At least one uppercase letter is required.' },
    { test: (pw) => /[a-z]/.test(pw), i18n: 'errPW.lower', fallback: 'At least one lowercase letter is required.' },
    { test: (pw) => /\d/.test(pw), i18n: 'errPW.number', fallback: 'At least one number is required.' },
    { test: (pw) => /[\W_]/.test(pw), i18n: 'errPW.special', fallback: 'At least one special character is required.' },
];

function SignupDialog({ open, onClose, onSubmit }) {
    const { t } = useTranslation('auth');

    const [values, setValues] = useState({
        email: '',
        password: '',
        confirm: '',
        name: '',
        teamName: '',
    });
    const [touched, setTouched] = useState({
        email: false, password: false, confirm: false, name: false, teamName: false,
    });

    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState('');
    const [emailTaken, setEmailTaken] = useState(false);
    const [teamNameValid, setteamNameValid] = useState(null);

    const errors = useMemo(() => {
        const e = {};

        if (touched.email) {
            if (!values.email.trim()) e.email = t('required') || 'Required.';
            else if (!emailRegex.test(values.email.trim())) e.email = t('errId') || 'Please enter a valid email address.';
            else if (emailTaken) e.email = t('errEmailTaken') || 'This email is already in use.';
        }

        if (touched.password) {
            const pw = values.password || '';
            if (!pw) e.password = t('required') || 'Required.';
            else {
                const firstFail = pwRules.find(r => !r.test(pw));
                if (firstFail) e.password = t(firstFail.i18n) || firstFail.fallback;
            }
        }

        if (touched.confirm) {
            if (!values.confirm) e.confirm = t('required') || 'Required.';
            else if (values.confirm !== values.password)
                e.confirm = t('errPW.mismatch') || 'Passwords do not match.';
        }

        if (touched.name) {
            const len = values.name.trim().length;
            if (len === 0) e.name = t('required') || 'Required.';
            else if (len < 2 || len > 30)
                e.name = t('name.length') || 'Name must be 2–30 characters.';
        }

        if (touched.teamName && values.teamName.trim()) {
            if (teamNameValid === false) {
                e.teamName = t('team.invalid') || 'Invalid team code. You can still sign up.';
            }
        }

        return e;
    }, [touched, values, t, emailTaken, teamNameValid]);

    const hasError = (k) => Boolean(errors[k]);

    const handleChange = (field) => (e) => {
        const v = e.target.value;
        setValues(s => ({ ...s, [field]: v }));
        if (formError) setFormError('');
        if (field === 'email' && emailTaken) setEmailTaken(false);
        if (field === 'teamName' && teamNameValid === false) setteamNameValid(null);
    };

    const handleBlur = (field) => () => {
        setTouched(s => ({ ...s, [field]: true }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setTouched({ email: true, password: true, confirm: true, name: true, teamName: true });
        if (Object.keys(errors).length > 0) return;

        try {
            setSubmitting(true);
            setFormError('');

            await onSubmit?.({
                email: values.email.trim(),
                password: values.password,
                name: values.name.trim(),
                teamName: values.teamName.trim() || undefined,
            });

            onClose?.();
        } catch (err) {
            const resp = err?.response;
            const code = resp?.data?.error_code;

            if (code === 'E4002' || resp?.status === 409) {
                setEmailTaken(true);
                setTouched(s => ({ ...s, email: true }));
            } else if (code === 'E3002') {
                setteamNameValid(false);
                setTouched(s => ({ ...s, teamName: true }));
            } else {
                const fallback = resp?.data?.message || (t('errGeneric') || 'Something went wrong. Please try again.');
                setFormError(fallback);
            }
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
            <DialogContent sx={{ p: 4, position: 'relative' }}>
                <IconButton
                    aria-label="close"
                    onClick={onClose}
                    sx={{ position: 'absolute', right: 8, top: 8 }}
                >
                    <CloseIcon />
                </IconButton>

                <Typography variant="h3" textAlign="center" sx={{ mb: 3 }}>
                    {t('signup') || 'Sign Up'}
                </Typography>

                {formError && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {formError}
                    </Alert>
                )}

                <Box component="form" onSubmit={handleSubmit} noValidate>
                    <Stack spacing={2.5}>
                        <Typography variant="h5" fontWeight={800}>
                            {t('idLabel') || 'Email'}
                        </Typography>
                        <TextField
                            value={values.email}
                            onChange={handleChange('email')}
                            onBlur={handleBlur('email')}
                            error={hasError('email')}
                        />
                        {hasError('email') && (
                            <Stack direction="row" alignItems="center" spacing={1} sx={{ color: 'error.main', mt: -1 }}>
                                <ErrorOutlineIcon fontSize="small" />
                                <Typography variant="body2">{errors.email}</Typography>
                            </Stack>
                        )}

                        <Typography variant="h5" fontWeight={800} sx={{ mt: 1 }}>
                            {t('passwordLabel') || 'Password'}
                        </Typography>
                        <TextField
                            type="password"
                            value={values.password}
                            onChange={handleChange('password')}
                            onBlur={handleBlur('password')}
                            error={hasError('password')}
                        />
                        {hasError('password') && (
                            <Stack direction="row" alignItems="center" spacing={1} sx={{ color: 'error.main', mt: -1 }}>
                                <ErrorOutlineIcon fontSize="small" />
                                <Typography variant="body2">{errors.password}</Typography>
                            </Stack>
                        )}

                        <Typography variant="h5" fontWeight={800} sx={{ mt: 1 }}>
                            {t('passwordConfirm') || 'Confirm Password'}
                        </Typography>
                        <TextField
                            type="password"
                            value={values.confirm}
                            onChange={handleChange('confirm')}
                            onBlur={handleBlur('confirm')}
                            error={hasError('confirm')}
                        />
                        {hasError('confirm') && (
                            <Stack direction="row" alignItems="center" spacing={1} sx={{ color: 'error.main', mt: -1 }}>
                                <ErrorOutlineIcon fontSize="small" />
                                <Typography variant="body2">{errors.confirm}</Typography>
                            </Stack>
                        )}

                        <Typography variant="h5" fontWeight={800} sx={{ mt: 1 }}>
                            {t('name') || 'Name'}
                        </Typography>
                        <TextField
                            value={values.name}
                            onChange={handleChange('name')}
                            onBlur={handleBlur('name')}
                            error={hasError('name')}
                        />
                        {hasError('name') && (
                            <Stack direction="row" alignItems="center" spacing={1} sx={{ color: 'error.main', mt: -1 }}>
                                <ErrorOutlineIcon fontSize="small" />
                                <Typography variant="body2">{errors.name}</Typography>
                            </Stack>
                        )}

                        <Typography variant="h5" fontWeight={800} sx={{ mt: 1 }}>
                            {t('teamName') || 'Team Name (optional)'}
                        </Typography>
                        <TextField
                            value={values.teamName}
                            onChange={handleChange('teamName')}
                            onBlur={handleBlur('teamName')}
                            error={hasError('teamName')}
                            placeholder={t('team.placeholder') || 'If you have a team code, enter it here'}
                        />
                        {(hasError('teamName')) && (
                            <Stack direction="row" alignItems="center" spacing={1} sx={{ color: 'error.main', mt: -1 }}>
                                <ErrorOutlineIcon fontSize="small" />
                                <Typography variant="body2">{errors.teamName}</Typography>
                            </Stack>
                        )}

                        <Button
                            type="submit"
                            variant="contained"
                            size="large"
                            disabled={submitting}
                            sx={{ mt: 1 }}
                            startIcon={submitting ? <CircularProgress size={18} /> : null}
                        >
                            {t('signup') || 'Sign up'}
                        </Button>
                    </Stack>
                </Box>
            </DialogContent>
        </Dialog>
    );
}

export default SignupDialog;