import { useMemo, useState } from 'react';
import {
    Dialog, DialogContent, Stack, Typography, TextField, Button,
    FormControlLabel, Checkbox, Link, Box
} from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { useTranslation } from 'react-i18next';

function LoginDialog({
    open,
    onClose,
    onSubmit
}) {
    const { t } = useTranslation('auth');

    const [values, setValues] = useState({ id: '', password: '', keep: false });
    const [touched, setTouched] = useState({ id: false, password: false });
    const [submitting, setSubmitting] = useState(false);

    const errors = useMemo(() => {
        const e = {};
        if (touched.id && values.id.trim().length < 3) e.id = t('errId');
        if (touched.password && values.password.length < 8) e.password = t('errPw');
        return e;
    }, [touched, values, t]);

    const hasError = (k) => Boolean(errors[k]);

    const handleChange = (field) => (e) => {
        const v = field === 'keep' ? e.target.checked : e.target.value;
        setValues((s) => ({ ...s, [field]: v }));
    };

    const handleBlur = (field) => () => setTouched((s) => ({ ...s, [field]: true }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        setTouched({ id: true, password: true });
        if (errors.id || errors.password) return;

        try {
            setSubmitting(true);
            await onSubmit?.(values);
            onClose?.();
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
            <DialogContent sx={{ p: 4 }}>
                <Typography variant="h3" textAlign="center" sx={{ mb: 3 }}>
                    {t('brand')}
                </Typography>

                <Box component="form" onSubmit={handleSubmit} noValidate>
                    <Stack spacing={2.5}>
                        <Typography variant="h5" fontWeight={800}>
                            {t('idLabel')}
                        </Typography>
                        <TextField
                            placeholder=""
                            value={values.id}
                            onChange={handleChange('id')}
                            onBlur={handleBlur('id')}
                            error={hasError('id')}
                        />
                        {hasError('id') && (
                            <Stack direction="row" alignItems="center" spacing={1} sx={{ color: 'error.main', mt: -1 }}>
                                <ErrorOutlineIcon fontSize="small" />
                                <Typography variant="body2">{errors.id}</Typography>
                            </Stack>
                        )}

                        <Typography variant="h5" fontWeight={800} sx={{ mt: 1 }}>
                            {t('passwordLabel')}
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

                        <FormControlLabel
                            control={<Checkbox checked={values.keep} onChange={handleChange('keep')} />}
                            label={t('keepSignedIn')}
                            sx={{ mt: 0.5 }}
                        />

                        <Button type="submit" variant="contained" size="large" disabled={submitting} sx={{ mt: 1 }}>
                            {t('signin')}
                        </Button>

                        <Typography variant="body2" textAlign="center" sx={{ color: 'text.secondary', mt: 1 }}>
                            <Link href="/signup" underline="hover" sx={{ mx: 0.5 }}>
                                {t('signup')}
                            </Link>
                            /
                            <Link href="/find-id" underline="hover" sx={{ mx: 0.5 }}>
                                {t('findId')}
                            </Link>
                            /
                            <Link href="/find-password" underline="hover" sx={{ mx: 0.5 }}>
                                {t('findPw')}
                            </Link>
                        </Typography>
                    </Stack>
                </Box>
            </DialogContent>
        </Dialog>
    );
}

export default LoginDialog;