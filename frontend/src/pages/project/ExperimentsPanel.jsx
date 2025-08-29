import { useState, useEffect } from 'react';
import {
    Box, Stack, Typography, Button, Card, TextField, Select, MenuItem,
    Table, TableHead, TableBody, TableRow, TableCell, CircularProgress
} from '@mui/material';
import { createLlmRequest, getLlmRequest } from '../../features/llm/api/llm';


const POLL_INTERVAL_MS = 1200;
const POLL_MAX_TRIES = 30;

async function pollUntilDone(id, onTick) {
    let tries = 0;
    while (tries < POLL_MAX_TRIES) {
        const data = await getLlmRequest(id);
        onTick?.(data);

        if (data?.status === 'completed') return data;
        if (data?.status === 'failed' || data?.status === 'error') {
            const err = new Error(data?.error_message || 'LLM request failed');
            err.response = { data };
            throw err;
        }

        await new Promise(r => setTimeout(r, POLL_INTERVAL_MS));
        tries += 1;
    }
    throw new Error('Timed out while waiting for LLM result');
}

function ExperimentsPanel({
    cases = [],
    models = [],
    onRunCase,
    credentialName,
    projectId,
}) {
    const [selectedModel, setSelectedModel] = useState('');
    const [systemPrompt, setSystemPrompt] = useState('');

    useEffect(() => {
        if (!selectedModel && Array.isArray(models) && models.length > 0) {
            setSelectedModel(models[0].name);
        }
    }, [models, selectedModel]);

    const [running, setRunning] = useState({});
    const [results, setResults] = useState({});
    const [errors, setErrors] = useState({});

    const handleRun = async (row) => {
        if (onRunCase) return onRunCase(row, { model: selectedModel, systemPrompt });

        const question = (row?.request || '').trim();
        if (!question) {
            setErrors(s => ({ ...s, [row.id]: 'Request is empty.' }));
            return;
        }
        if (!selectedModel) {
            setErrors(s => ({ ...s, [row.id]: 'Select a model first.' }));
            return;
        }
        if (!credentialName) {
            setErrors(s => ({ ...s, [row.id]: 'credential_name is required.' }));
            return;
        }
        if (!projectId) {
            setErrors(s => ({ ...s, [row.id]: 'project_id is required.' }));
            return;
        }

        setRunning(s => ({ ...s, [row.id]: true }));
        setErrors(s => ({ ...s, [row.id]: '' }));

        try {
            const payload = {
                system_prompt: systemPrompt || '',
                question,
                model_name: selectedModel,
                credential_name: credentialName,
                project_id: projectId,
                file_paths: []
            };
            const created = await createLlmRequest(payload);

            const reqId = created?.id;
            if (!reqId) throw new Error('No request id returned');

            const final = await pollUntilDone(reqId);
            const text = final?.result ?? '(no result)';
            setResults(s => ({ ...s, [row.id]: text }));
        } catch (e) {
            const msg = e?.response?.data?.error_message
                || e?.response?.data?.message
                || e.message
                || 'Request failed';
            setErrors(s => ({ ...s, [row.id]: msg }));
        } finally {
            setRunning(s => ({ ...s, [row.id]: false }));
        }
    };

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
                    <Select
                        size="small"
                        fullWidth
                        displayEmpty
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                    >
                        {models.length === 0 ? (
                            <MenuItem value="" disabled>No models</MenuItem>
                        ) : (
                            models.map(m => (
                                <MenuItem key={m.id} value={m.name}>
                                    {m.name}{m.description ? ` (${m.description})` : ''}
                                </MenuItem>
                            ))
                        )}
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
                        value={systemPrompt}
                        onChange={(e) => setSystemPrompt(e.target.value)}
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
                            <TableCell align="center" sx={{ fontWeight: 700, borderRight: '1px solid rgba(255,255,255,0.12)' }}>
                                Request
                            </TableCell>
                            <TableCell align="center" sx={{ fontWeight: 700, borderRight: '1px solid rgba(255,255,255,0.12)' }}>
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
                            cases.map((c) => {
                                const disabled =
                                    !selectedModel ||
                                    !credentialName ||
                                    !projectId ||
                                    !(c.request || '').trim() ||
                                    running[c.id];

                                return (
                                    <TableRow key={c.id}>
                                        <TableCell sx={{ borderRight: '1px solid rgba(255,255,255,0.12)' }}>
                                            {c.request}
                                        </TableCell>
                                        <TableCell sx={{ borderRight: '1px solid rgba(255,255,255,0.12)' }}>
                                            {c.expected}
                                        </TableCell>
                                        <TableCell sx={{ borderRight: '1px solid rgba(255,255,255,0.12)', whiteSpace: 'pre-wrap' }}>
                                            {running[c.id] ? (
                                                <Stack direction="row" spacing={1} alignItems="center" justifyContent="center">
                                                    <CircularProgress size={16} /> Running…
                                                </Stack>
                                            ) : errors[c.id] ? (
                                                <span style={{ color: '#ff6b6b' }}>{errors[c.id]}</span>
                                            ) : (
                                                results[c.id] ?? ''
                                            )}
                                        </TableCell>
                                        <TableCell align="center">
                                            <Button
                                                size="small"
                                                variant="contained"
                                                disabled={disabled}
                                                onClick={() => handleRun(c)}
                                            >
                                                {running[c.id] ? 'Running…' : 'Run'}
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                );
                            })
                        )}
                    </TableBody>
                </Table>
            </Card>
        </Stack>
    );
}

export default ExperimentsPanel;