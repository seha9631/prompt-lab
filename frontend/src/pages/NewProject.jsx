import { useState, useMemo } from 'react';
import { Box, Stack, Typography, TextField, Button, FormHelperText, Divider } from '@mui/material';
import CloseRoundedIcon from '@mui/icons-material/CloseRounded';
import { useNavigate } from 'react-router-dom';
import { createProject } from '../features/project/api/project';

function NewProject() {
    const navigate = useNavigate();

    const [name, setName] = useState('');
    const [desc, setDesc] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [apiError, setApiError] = useState('');

    const MAX_DESC = 350;

    const nameErrorClient =
        name.trim().length === 0
            ? ''
            : name.trim().length < 2
                ? '프로젝트 이름은 2자 이상이어야 합니다.'
                : '';

    const nameError = apiError || nameErrorClient;

    const canSubmit = useMemo(() => {
        return !!name.trim() && !nameErrorClient && !submitting;
    }, [name, nameErrorClient, submitting]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!canSubmit) return;

        try {
            setSubmitting(true);
            setApiError('');

            const res = await createProject({ name: name.trim() });
            if (res?.success && res?.data?.id) {
                navigate(`/project/${res.data.id}`);
            } else {
                setApiError('프로젝트 생성에 실패했습니다. 다시 시도해 주세요.');
            }
        } catch (err) {
            const detail = err?.response?.data?.detail;
            const message = detail?.message || '프로젝트 생성 중 오류가 발생했습니다.';
            setApiError(message);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{
                px: { xs: 2, md: 6 },
                py: { xs: 6, md: 10 },
                minHeight: 'calc(100vh - 64px)',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'center',
            }}
        >
            <Stack spacing={4} sx={{ width: '100%', maxWidth: 720 }}>
                <Typography variant="h4" align="center" fontWeight={800} sx={{ mb: 2 }}>
                    Create a new project
                </Typography>

                <Divider sx={{ opacity: 0.15 }} />

                <Stack spacing={1.5}>
                    <Typography variant="h6" fontWeight={800}>
                        Project name
                    </Typography>
                    <TextField
                        value={name}
                        onChange={(e) => {
                            setName(e.target.value);
                            if (apiError) setApiError('');
                        }}
                        fullWidth
                        size="medium"
                        error={!!nameError}
                        sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'background.default' } }}
                    />
                    {!!nameError && (
                        <Stack direction="row" alignItems="center" spacing={0.5}>
                            <CloseRoundedIcon fontSize="small" sx={{ color: 'error.main' }} />
                            <FormHelperText sx={{ color: 'error.main', ml: 0 }}>
                                {nameError}
                            </FormHelperText>
                        </Stack>
                    )}
                </Stack>

                <Stack spacing={1.5} sx={{ mt: 2 }}>
                    <Typography variant="h6" fontWeight={800}>
                        Description (optional)
                    </Typography>

                    <TextField
                        value={desc}
                        onChange={(e) => {
                            const v = e.target.value;
                            if (v.length <= MAX_DESC) setDesc(v);
                        }}
                        multiline
                        minRows={6}
                        fullWidth
                        helperText={
                            <Box sx={{ width: '100%', textAlign: 'right', opacity: 0.7 }}>
                                {desc.length}/{MAX_DESC}
                            </Box>
                        }
                        sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'background.default' } }}
                    />
                </Stack>

                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        size="large"
                        disabled={!canSubmit}
                        sx={{ px: 4, py: 1.5, fontWeight: 800, borderRadius: 2, textTransform: 'none', minWidth: 260 }}
                    >
                        {submitting ? 'Creating...' : 'Create Project'}
                    </Button>
                </Box>
            </Stack>
        </Box>
    );
}

export default NewProject;