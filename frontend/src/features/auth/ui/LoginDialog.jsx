import { useMemo, useState } from 'react';
import {
    Dialog, DialogContent, Stack, Typography, TextField, Button,
    FormControlLabel, Checkbox, Link, Box, Alert
} from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { useTranslation } from 'react-i18next';

function LoginDialog({
    open,
    onClose,
    onSubmit,
    onOpenSignup,
    onOpenFindId,
    onOpenFindPw
}) {
    const { t } = useTranslation('auth');

    const [values, setValues] = useState({ id: '', password: '', keep: false });
    const [touched, setTouched] = useState({ id: false, password: false });
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState('');

    const errors = useMemo(() => {
        const e = {};

        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$/;
        if (touched.id && !emailRegex.test(values.id.trim())) {
            e.id = t('errId');
        }

        const pw = values.password || '';
        const pwRules = [
            { ok: pw.length >= 8, msg: t('errPW.minLength') },
            { ok: /[A-Z]/.test(pw), msg: t('errPW.upper') },
            { ok: /[a-z]/.test(pw), msg: t('errPW.lower') },
            { ok: /\d/.test(pw), msg: t('errPW.number') },
            { ok: /[\W_]/.test(pw), msg: t('errPW.special') },
        ];

        if (touched.password) {
            const firstFail = pwRules.find(r => !r.ok);
            if (firstFail) {
                e.password = firstFail.msg;
            }
        }

        return e;
    }, [touched, values, t]);

    const hasError = (k) => Boolean(errors[k]);

    const handleChange = (field) => (e) => {
        const v = field === 'keep' ? e.target.checked : e.target.value;
        setValues((s) => ({ ...s, [field]: v }));
        if (formError) setFormError('');
    };

    const handleBlur = (field) => () => setTouched((s) => ({ ...s, [field]: true }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        setTouched({ id: true, password: true });
        if (errors.id || errors.password) return;

        try {
            setSubmitting(true);
            setFormError('');
            await onSubmit?.(values);
            onClose?.();
        } catch (err) {
            const code = err?.response?.data?.error_code;
            if (code === 'E2001') {
                setFormError(t('errInvalidCredentials'));
            } else {
                const fallback =
                    err?.response?.data?.message ||
                    t('errGeneric');
                setFormError(fallback);
            }
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

                {formError && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {formError}
                    </Alert>
                )}

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
                            <Link component="button" type="button" onClick={onOpenSignup} underline="hover" sx={{ mx: 0.5 }}>
                                {t('signup')}
                            </Link>
                            /
                            <Link component="button" type="button" onClick={onOpenFindId} underline="hover" sx={{ mx: 0.5 }}>
                                {t('findId')}
                            </Link>
                            /
                            <Link component="button" type="button" onClick={onOpenFindPw} underline="hover" sx={{ mx: 0.5 }}>
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