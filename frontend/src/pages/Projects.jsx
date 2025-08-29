import { useMemo, useState, useEffect } from 'react';
import {
    Box, Stack, Typography, Button, TextField,
    Card, CardActionArea, CardContent, Chip, Pagination
} from '@mui/material';
import TuneIcon from '@mui/icons-material/Tune';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

const mockProjects = Array.from({ length: 40 }).map((_, i) => ({
    id: `proj_${i + 1}`,
    name: `Project Name ${i + 1}`,
    team: 'Team',
    description: 'description',
}));

function ProjectCard({ project, onClick }) {
    return (
        <Card variant="outlined" sx={{ bgcolor: 'background.paper', borderColor: 'rgba(255,255,255,0.12)', borderRadius: 2, height: 220 }}>
            <CardActionArea onClick={() => onClick?.(project)} sx={{ height: '100%', p: 1.5 }}>
                <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Stack direction="row" alignItems="center" justifyContent="space-between">
                        <Typography variant="subtitle1" fontWeight={800}>{project.name}</Typography>
                        <ChevronRightIcon sx={{ opacity: 0.8 }} />
                    </Stack>
                    <Typography variant="body2" sx={{ opacity: 0.8 }}>{project.team}</Typography>
                    <Typography variant="caption" sx={{ opacity: 0.65 }}>{project.description}</Typography>
                </CardContent>
            </CardActionArea>
        </Card>
    );
}

function Projects({
    projects: initialProjects = mockProjects,
    onCreate,
    onOpenProject,
    pageSize: pageSizeProp = 6,
}) {
    const [query, setQuery] = useState('');
    const [page, setPage] = useState(1);
    const pageSize = pageSizeProp;

    const filtered = useMemo(() => {
        if (!query.trim()) return initialProjects;
        const q = query.toLowerCase();
        return initialProjects.filter(
            (p) =>
                p.name.toLowerCase().includes(q) ||
                p.team?.toLowerCase().includes(q) ||
                p.description?.toLowerCase().includes(q)
        );
    }, [initialProjects, query]);

    useEffect(() => { setPage(1); }, [query]);

    const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
    const start = (page - 1) * pageSize;
    const visible = filtered.slice(start, start + pageSize);

    return (
        <Box sx={{ px: { xs: 2, md: 6 }, py: 8 }}>
            <Stack direction="row" alignItems="center" justifyContent="center" spacing={2} sx={{ mb: 8, flexWrap: 'wrap' }}>
                <Stack direction="row" spacing={1.5} alignItems="center" sx={{ width: '100%', flex: '0 0 auto', minWidth: 320, maxWidth: 720 }}>
                    <Chip
                        icon={<TuneIcon />}
                        label=""
                        variant="outlined"
                        sx={{
                            width: 40,
                            height: 40,
                            borderRadius: 2,
                            bgcolor: 'background.paper',
                            borderColor: 'rgba(255,255,255,0.12)',
                            px: 0,
                            '& .MuiChip-label': {
                                p: 0,
                                display: 'none',
                            },
                            '& .MuiChip-icon': {
                                m: 0,
                            },
                        }}
                    />
                    <TextField
                        size='small'
                        fullWidth
                        placeholder="Search for a project"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                </Stack>

                <Button variant="contained" color="primary" onClick={onCreate} sx={{ height: 36, textTransform: 'none', fontWeight: 700, borderRadius: 2, px: 2 }}>
                    New project
                </Button>
            </Stack>

            <Box
                sx={{
                    display: 'grid',
                    gap: 6,
                    gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: '1fr 1fr 1fr' },
                    mx: { xs: 0, md: 'auto' },
                    maxWidth: 1100,
                }}
            >
                {visible.map((p) => (
                    <ProjectCard key={p.id} project={p} onClick={(proj) => onOpenProject?.(proj)} />
                ))}
            </Box>

            {filtered.length === 0 && (
                <Stack alignItems="center" sx={{ mt: 8, opacity: 0.7 }}>
                    <Typography variant="body2">No projects found.</Typography>
                </Stack>
            )}

            {filtered.length > 0 && (
                <Stack alignItems="center" sx={{ mt: 8 }}>
                    <Pagination
                        count={pageCount}
                        page={page}
                        onChange={(_, v) => setPage(v)}
                        color="primary"
                        siblingCount={1}
                        boundaryCount={1}
                        size="medium"
                        showFirstButton
                        showLastButton
                    />
                    <Typography variant="caption" sx={{ mt: 1, opacity: 0.7 }}>
                        {start + 1}–{Math.min(start + pageSize, filtered.length)} of {filtered.length}
                    </Typography>
                </Stack>
            )}
        </Box>
    );
}

export default Projects;