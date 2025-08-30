import { useMemo, useState, useEffect } from 'react';
import {
    Box, Stack, Typography, Button, TextField, Card, CardActionArea,
    CardContent, Chip, Pagination, Popover, Divider, MenuItem, ToggleButtonGroup, ToggleButton
} from '@mui/material';
import TuneIcon from '@mui/icons-material/Tune';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { Link as RouterLink } from 'react-router-dom';

import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';

import { getProjects } from '../features/project/api/project';
import { useAuthContext } from '../app/providers/AuthProvider';

function ProjectCard({ project, onClick }) {
    const desc = project.description ?? '';
    return (
        <Card variant="outlined" sx={{ bgcolor: 'background.paper', borderColor: 'rgba(255,255,255,0.12)', borderRadius: 2, height: 220 }}>
            <CardActionArea onClick={() => onClick?.(project)} sx={{ height: '100%', p: 1.5 }}>
                <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Stack direction="row" alignItems="center" justifyContent="space-between">
                        <Typography variant="subtitle1" fontWeight={800}>{project.name}</Typography>
                        <ChevronRightIcon sx={{ opacity: 0.8 }} />
                    </Stack>
                    <Typography variant="caption" sx={{ opacity: 0.65 }}>{desc}</Typography>
                </CardContent>
            </CardActionArea>
        </Card>
    );
}

function Projects({
    onOpenProject,
    pageSize: pageSizeProp = 6,
}) {
    const { accessToken } = useAuthContext();

    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState(null);

    const [query, setQuery] = useState('');
    const [page, setPage] = useState(1);
    const pageSize = pageSizeProp;

    const [dateFrom, setDateFrom] = useState(null);
    const [dateTo, setDateTo] = useState(null);

    const [dateField, setDateField] = useState('updated');
    const [sortField, setSortField] = useState('updated');
    const [sortDir, setSortDir] = useState('desc');

    const [filterAnchor, setFilterAnchor] = useState(null);
    const popOpen = Boolean(filterAnchor);

    const [tmpFrom, setTmpFrom] = useState(null);
    const [tmpTo, setTmpTo] = useState(null);
    const [tmpDateField, setTmpDateField] = useState('updated');

    useEffect(() => {
        if (!accessToken) return;
        (async () => {
            try {
                setLoading(true);
                setLoadError(null);
                const list = await getProjects();
                setProjects(Array.isArray(list) ? list : []);
            } catch (e) {
                setLoadError(e?.response?.data ?? e);
                setProjects([]);
            } finally {
                setLoading(false);
            }
        })();
    }, [accessToken]);

    const inDateRange = (iso, from, to) => {
        if (!iso) return false;
        const d = new Date(iso);
        if (Number.isNaN(+d)) return false;
        const toEnd = to ? new Date(to.getFullYear(), to.getMonth(), to.getDate(), 23, 59, 59, 999) : null;
        if (from && d < new Date(from.getFullYear(), from.getMonth(), from.getDate())) return false;
        if (toEnd && d > toEnd) return false;
        return true;
    };

    const filtered = useMemo(() => {
        const pickDate = (p) => {
            const created = p.created_at || p.createdAt;
            const updated = p.updated_at || p.updatedAt;
            return dateField === 'created' ? created : updated;
        };

        return projects
            .filter(p => {
                if (!dateFrom && !dateTo) return true;
                const ts = pickDate(p);
                return inDateRange(ts, dateFrom, dateTo);
            })
            .filter(p => {
                const q = query.trim().toLowerCase();
                if (!q) return true;
                const name = (p.name ?? '').toLowerCase();
                const desc = (p.description ?? '').toLowerCase();
                return name.includes(q) || desc.includes(q);
            })
            .sort((a, b) => {
                const dir = sortDir === 'asc' ? 1 : -1;

                if (sortField === 'name') {
                    const ax = (a.name ?? '').toLowerCase();
                    const bx = (b.name ?? '').toLowerCase();
                    return ax < bx ? -1 * dir : ax > bx ? 1 * dir : 0;
                }

                const aDate = (sortField === 'created'
                    ? (a.created_at || a.createdAt)
                    : (a.updated_at || a.updatedAt));
                const bDate = (sortField === 'created'
                    ? (b.created_at || b.createdAt)
                    : (b.updated_at || b.updatedAt));

                const at = new Date(aDate).getTime() || 0;
                const bt = new Date(bDate).getTime() || 0;
                return (bt - at) * (dir === 1 ? -1 : 1);
            });
    }, [projects, query, dateFrom, dateTo, dateField, sortField, sortDir]);

    const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
    const start = (page - 1) * pageSize;
    const visible = filtered.slice(start, start + pageSize);

    useEffect(() => { setPage(1); }, [query, dateFrom, dateTo, dateField, sortField, sortDir]);

    const openFilter = (e) => {
        setFilterAnchor(e.currentTarget);
        setTmpFrom(dateFrom);
        setTmpTo(dateTo);
        setTmpDateField(dateField);
    };
    const closeFilter = () => setFilterAnchor(null);

    const applyFilter = () => {
        setDateFrom(tmpFrom);
        setDateTo(tmpTo);
        setDateField(tmpDateField);
        setFilterAnchor(null);
    };
    const clearFilter = () => {
        setTmpFrom(null);
        setTmpTo(null);
        setTmpDateField('updated');

        setDateFrom(null);
        setDateTo(null);
        setDateField('updated');
        setFilterAnchor(null);
    };

    const filterActive = Boolean(
        dateFrom || dateTo || dateField !== 'updated'
    );

    if (!accessToken) return <Box sx={{ p: 4 }}>Signing in…</Box>;
    if (loading) return <Box sx={{ p: 4 }}>Loading projects…</Box>;
    if (loadError) {
        return (
            <Box sx={{ p: 4, color: 'error.main' }}>
                Error: {typeof loadError === 'string' ? loadError : JSON.stringify(loadError)}
            </Box>
        );
    }

    const setQuickToday = () => {
        const now = new Date();
        const start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const end = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        setTmpFrom(start);
        setTmpTo(end);
    };
    const setQuickLast7 = () => {
        const now = new Date();
        const end = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const start = new Date(end);
        start.setDate(start.getDate() - 6);
        setTmpFrom(start);
        setTmpTo(end);
    };

    return (
        <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Box sx={{ px: { xs: 2, md: 6 }, py: 8 }}>
                <Stack direction="row" alignItems="center" justifyContent="center" spacing={2} sx={{ mb: 8, flexWrap: 'wrap' }}>
                    <Stack
                        direction="row"
                        spacing={1.5}
                        alignItems="center"
                        sx={{ width: '100%', flex: '0 0 auto', minWidth: 320, maxWidth: 980, flexWrap: 'wrap', rowGap: 1.5 }}
                    >
                        <TextField
                            label="Sort by"
                            size="small"
                            select
                            value={sortField}
                            onChange={(e) => setSortField(e.target.value)}
                            sx={{ width: { xs: '40%', sm: 140 } }}
                        >
                            <MenuItem value="updated">Updated</MenuItem>
                            <MenuItem value="created">Created</MenuItem>
                            <MenuItem value="name">Name</MenuItem>
                        </TextField>

                        <TextField
                            label="Order"
                            size="small"
                            select
                            value={sortDir}
                            onChange={(e) => setSortDir(e.target.value)}
                            sx={{ width: { xs: '40%', sm: 140 } }}
                        >
                            <MenuItem value="asc">Ascending</MenuItem>
                            <MenuItem value="desc">Descending</MenuItem>
                        </TextField>

                        <Chip
                            icon={<TuneIcon />}
                            label=""
                            onClick={openFilter}
                            variant="outlined"
                            sx={{
                                width: 40,
                                height: 40,
                                borderRadius: 2,
                                px: 0,
                                cursor: 'pointer',
                                '& .MuiChip-label': { display: 'none' },
                                '& .MuiChip-icon': { m: 0 },
                                ...(filterActive
                                    ? {
                                        bgcolor: 'primary.main',
                                        borderColor: 'primary.main',
                                        color: 'primary.contrastText',
                                        '&:hover': { bgcolor: 'primary.dark', borderColor: 'primary.dark' },
                                    }
                                    : {
                                        bgcolor: 'background.paper',
                                        color: 'text.primary',
                                        borderColor: 'rgba(255,255,255,0.12)',
                                        '&:hover': { borderColor: 'rgba(255,255,255,0.24)' },
                                    }),
                            }}
                        />

                        <TextField
                            size="small"
                            placeholder="Search for a project"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            sx={{ flex: 1, minWidth: 240 }}
                        />
                    </Stack>

                    <Button
                        variant="contained"
                        color="primary"
                        component={RouterLink}
                        to="/NewProject"
                        sx={{ height: 36, textTransform: 'none', fontWeight: 700, borderRadius: 2, px: 2 }}
                    >
                        New project
                    </Button>
                </Stack>

                <Popover
                    open={popOpen}
                    anchorEl={filterAnchor}
                    onClose={closeFilter}
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
                    transformOrigin={{ vertical: 'top', horizontal: 'left' }}
                    PaperProps={{ sx: { p: 2, bgcolor: 'background.paper', width: 420 } }}
                >
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                        <Typography variant="caption" sx={{ opacity: 0.7, minWidth: 82 }}>Date field</Typography>
                        <ToggleButtonGroup
                            exclusive
                            value={tmpDateField}
                            onChange={(_, v) => v && setTmpDateField(v)}
                            size="small"
                        >
                            <ToggleButton value="updated">Updated</ToggleButton>
                            <ToggleButton value="created">Created</ToggleButton>
                        </ToggleButtonGroup>
                    </Stack>

                    <Stack spacing={1} sx={{ mb: 1 }}>
                        <DatePicker
                            label="From"
                            value={tmpFrom}
                            onChange={(v) => setTmpFrom(v)}
                            slots={{ openPickerIcon: () => <CalendarTodayIcon sx={{ color: 'white' }} /> }}
                            slotProps={{ textField: { size: 'small', fullWidth: true } }}
                        />
                        <DatePicker
                            label="To"
                            value={tmpTo}
                            onChange={(v) => setTmpTo(v)}
                            slots={{ openPickerIcon: () => <CalendarTodayIcon sx={{ color: 'white' }} /> }}
                            slotProps={{ textField: { size: 'small', fullWidth: true } }}
                        />
                        <Stack direction="row" spacing={1}>
                            <Button size="small" variant="outlined" onClick={setQuickToday}>Today</Button>
                            <Button size="small" variant="outlined" onClick={setQuickLast7}>Last 7 days</Button>
                        </Stack>
                    </Stack>

                    <Divider sx={{ my: 1.5, opacity: 0.2 }} />

                    <Stack direction="row" spacing={1} justifyContent="flex-end" sx={{ pt: 1.5 }}>
                        <Button variant="text" onClick={clearFilter}>Clear</Button>
                        <Button variant="contained" onClick={applyFilter}>Apply</Button>
                    </Stack>
                </Popover>

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
        </LocalizationProvider>
    );
}

export default Projects;