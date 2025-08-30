import { useState, useMemo } from 'react';
import {
    Box, Stack, Typography, TextField, Button, FormHelperText, Divider
} from '@mui/material';
import CloseRoundedIcon from '@mui/icons-material/CloseRounded';

function NewProject({ onCreate }) {
    const [name, setName] = useState('');
    const [desc, setDesc] = useState('');
    const MAX_DESC = 350;

    const nameError =
        name.trim().length === 0
            ? ''
            : name.trim().length < 2
                ? '프로젝트 이름은 2자 이상이어야 합니다.'
                : '';

    const canSubmit = useMemo(() => {
        return name.trim().length >= 2 && !nameError;
    }, [name, nameError]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!canSubmit) return;
        onCreate?.({
            name: name.trim(),
            description: desc.trim(),
        });
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
            <Stack
                spacing={4}
                sx={{
                    width: '100%',
                    maxWidth: 720,
                }}
            >
                <Typography
                    variant="h4"
                    align="center"
                    fontWeight={800}
                    sx={{ mb: 2 }}
                >
                    Create a new project
                </Typography>

                <Divider sx={{ opacity: 0.15 }} />

                <Stack spacing={1.5}>
                    <Typography variant="h6" fontWeight={800}>
                        Project name
                    </Typography>
                    <TextField
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder=""
                        fullWidth
                        size="medium"
                        error={!!nameError}
                        sx={{
                            '& .MuiOutlinedInput-root': {
                                bgcolor: 'background.default',
                            },
                        }}
                    />

                    {nameError && (
                        <Stack direction="row" alignItems="center" spacing={0.5}>
                            <CloseRoundedIcon fontSize="small" sx={{ color: 'error.main' }} />
                            <FormHelperText sx={{ color: 'error.main', ml: 0 }}>
                                {nameError || '프로젝트 이름 검증 내용 출력'}
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
                        placeholder=""
                        sx={{
                            '& .MuiOutlinedInput-root': {
                                bgcolor: 'background.default',
                            },
                        }}
                        helperText={
                            <Box sx={{ width: '100%', textAlign: 'right', opacity: 0.7 }}>
                                {desc.length}/{MAX_DESC}
                            </Box>
                        }
                    />
                </Stack>

                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        size="large"
                        disabled={!canSubmit}
                        sx={{
                            px: 4,
                            py: 1.5,
                            fontWeight: 800,
                            borderRadius: 2,
                            textTransform: 'none',
                            minWidth: 260,
                        }}
                    >
                        Create Project
                    </Button>
                </Box>
            </Stack>
        </Box>
    );
}

export default NewProject;