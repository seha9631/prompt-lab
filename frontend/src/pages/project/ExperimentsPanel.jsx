import {
    Box,
    Stack,
    Typography,
    Button,
    Card,
    TextField,
    Select,
    MenuItem,
    Table,
    TableHead,
    TableBody,
    TableRow,
    TableCell,
} from '@mui/material';

function ExperimentsPanel({ cases = [], onRunCase }) {
    return (
        <Stack spacing={3} sx={{ mt: 8, mb: 8, width: '60%', mx: 'auto' }}>
            <Typography variant="h6" fontWeight={800}>
                Experiments
            </Typography>

            <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
                <Box sx={{ minWidth: 220 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 700 }}>
                        Model
                    </Typography>
                    <Select size="small" fullWidth defaultValue="gpt-4o">
                        <MenuItem value="gpt-4o">gpt-4o</MenuItem>
                        <MenuItem value="gpt-4.1-mini">gpt-4.1-mini</MenuItem>
                        <MenuItem value="gpt-4o-mini">gpt-4o-mini</MenuItem>
                    </Select>
                </Box>

                <Box sx={{ flex: 1, minWidth: 320 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 700 }}>
                        Prompt
                    </Typography>
                    <TextField
                        label="Prompt text"
                        multiline
                        minRows={4}
                        maxRows={8}
                        fullWidth
                    />
                </Box>

                <Box sx={{ minWidth: 260 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 700 }}>
                        External Documents
                    </Typography>
                    <Button variant="outlined">Upload</Button>
                    <Stack spacing={0.5} sx={{ mt: 1 }}>
                        <Typography variant="caption" sx={{ opacity: 0.6 }}>
                            No documents
                        </Typography>
                    </Stack>
                </Box>
            </Stack>

            <Card>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell
                                align="center"
                                sx={{ fontWeight: 700, borderRight: '1px solid rgba(255,255,255,0.12)' }}
                            >
                                Request
                            </TableCell>
                            <TableCell
                                align="center"
                                sx={{ fontWeight: 700, borderRight: '1px solid rgba(255,255,255,0.12)' }}
                            >
                                Expected Result
                            </TableCell>
                            <TableCell align="center" sx={{ fontWeight: 700, borderRight: '1px solid rgba(255,255,255,0.12)' }}>
                                Experiment Result
                            </TableCell>

                            <TableCell align="center" sx={{ fontWeight: 700, width: 120 }}>
                                Run
                            </TableCell>
                        </TableRow>
                    </TableHead>

                    <TableBody>
                        {cases.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={4} align="center" sx={{ py: 4, opacity: 0.7 }}>
                                    No test cases
                                </TableCell>
                            </TableRow>
                        ) : (
                            cases.map((c) => (
                                <TableRow key={c.id}>
                                    <TableCell sx={{ borderRight: '1px solid rgba(255,255,255,0.12)' }}>
                                        {c.request}
                                    </TableCell>
                                    <TableCell sx={{ borderRight: '1px solid rgba(255,255,255,0.12)' }}>
                                        {c.expected}
                                    </TableCell>
                                    <TableCell sx={{ borderRight: '1px solid rgba(255,255,255,0.12)' }}>
                                        {/* 결과 표시 영역 (현재 레이아웃만) */}
                                    </TableCell>
                                    <TableCell align="center">
                                        <Button
                                            size="small"
                                            variant="contained"
                                            onClick={() => onRunCase?.(c)}
                                        >
                                            Run
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </Card>
        </Stack>
    );
}

export default ExperimentsPanel;