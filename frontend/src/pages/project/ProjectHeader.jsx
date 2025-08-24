import { useState, useMemo } from 'react';
import { Box, Stack, Typography, Chip, Snackbar, Alert } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

function ProjectHeader({ project }) {
    const [toast, setToast] = useState(false);
    const members = useMemo(() => project.members?.map(m => m.name).join(', '), [project.members]);

    const copyTeamCode = async () => {
        await navigator.clipboard.writeText(project.teamCode);
        setToast(true);
    };

    return (
        <Box sx={{ mt: 4, ml: '18%', maxWidth: '50%' }}>
            <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1 }}>
                <Typography
                    variant="h4"
                    component="h2"
                    sx={{ fontSize: '32px', fontWeight: 800, lineHeight: 1.15 }}
                >
                    {project.name}
                </Typography>

                <Chip
                    size="small"
                    color="primary"
                    icon={<ContentCopyIcon />}
                    label="Copy Teamcode"
                    onClick={copyTeamCode}
                    sx={{
                        height: 24,
                        '& .MuiChip-label': { px: 1 },
                    }}
                />
            </Stack>

            {project.description && (
                <Typography
                    variant="body1"
                    sx={{ color: 'text.secondary', mb: 3, maxWidth: 920 }}
                >
                    {project.description}
                </Typography>
            )}

            <Stack spacing={2.5}>
                <Box>
                    <Typography variant="subtitle1" sx={{ fontSize: '20px', fontWeight: 800, mb: 0.5 }}>
                        Leader
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        {project.leader?.name || '-'}
                    </Typography>
                </Box>

                <Box>
                    <Typography variant="subtitle1" sx={{ fontSize: '20px', fontWeight: 800, mb: 0.5 }}>
                        Members
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        {members || '-'}
                    </Typography>
                </Box>
            </Stack>

            <Snackbar
                open={toast}
                autoHideDuration={1800}
                onClose={() => setToast(false)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert severity="success" variant="filled">Team code copied!</Alert>
            </Snackbar>
        </Box>
    );
}

export default ProjectHeader;