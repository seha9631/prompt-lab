import { useRef } from 'react';
import {
    Box,
    Stack,
    Typography,
    Button,
    Card,
    Table,
    TableHead,
    TableBody,
    TableRow,
    TableCell,
    TextField,
    IconButton,
    Tooltip,
} from '@mui/material';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';

function TestCasesPanel({ cases, setCases }) {
    const fileInputRef = useRef(null);

    const onImportCSV = (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        // TODO: CSV 파싱(papaparse 등)
        setCases((prev) => [
            ...prev,
            { id: `c${prev.length + 1}`, request: 'Imported case', expected: 'Imported expected' },
        ]);
    };

    const onAddCase = () => {
        setCases((prev) => [
            ...prev,
            { id: `c${prev.length + 1}`, request: '', expected: '' },
        ]);
    };

    const onDeleteCase = (id) => {
        setCases((prev) => prev.filter((c) => c.id !== id));
    };

    const onClearAll = () => {
        setCases([]);
    };

    const onCellChange = (id, key, value) => {
        setCases((prev) => prev.map((c) => (c.id === id ? { ...c, [key]: value } : c)));
    };

    return (
        <Stack spacing={2} sx={{ mt: 8, mb: 8, width: '60%', mx: 'auto' }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="h6" fontWeight={800}>
                    Test Cases
                </Typography>
                <Stack direction="row" spacing={1}>
                    <Button variant="outlined" onClick={() => fileInputRef.current?.click()}>
                        Import CSV
                    </Button>
                    <input
                        type="file"
                        accept=".csv"
                        ref={fileInputRef}
                        onChange={onImportCSV}
                        hidden
                    />
                    <Button variant="contained" onClick={onAddCase}>
                        New case
                    </Button>
                    <Button
                        variant="text"
                        color="error"
                        onClick={onClearAll}
                        disabled={cases.length === 0}
                    >
                        Clear all
                    </Button>
                </Stack>
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
                            <TableCell align="center" sx={{ fontWeight: 700, borderRight: '1px solid rgba(255,255,255,0.12)' }}>
                                Expected Result
                            </TableCell>
                            <TableCell align="center" sx={{ width: 80, fontWeight: 700 }}>
                                Delete
                            </TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {cases.map((c) => (
                            <TableRow key={c.id}>
                                <TableCell sx={{ borderRight: '1px solid rgba(255,255,255,0.12)' }}>
                                    <TextField
                                        fullWidth
                                        size="small"
                                        placeholder="Case request"
                                        value={c.request}
                                        onChange={(e) => onCellChange(c.id, 'request', e.target.value)}
                                        multiline
                                        minRows={1}
                                        maxRows={4}
                                    />
                                </TableCell>
                                <TableCell sx={{ borderRight: '1px solid rgba(255,255,255,0.12)' }}>
                                    <TextField
                                        fullWidth
                                        size="small"
                                        placeholder="Expected result"
                                        value={c.expected}
                                        onChange={(e) => onCellChange(c.id, 'expected', e.target.value)}
                                        multiline
                                        minRows={1}
                                        maxRows={4}
                                    />
                                </TableCell>
                                <TableCell align="center">
                                    <Tooltip title="Delete case">
                                        <IconButton
                                            color="error"
                                            size="small"
                                            onClick={() => onDeleteCase(c.id)}
                                        >
                                            <DeleteOutlineIcon fontSize="small" />
                                        </IconButton>
                                    </Tooltip>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </Card>
        </Stack>
    );
}

export default TestCasesPanel;