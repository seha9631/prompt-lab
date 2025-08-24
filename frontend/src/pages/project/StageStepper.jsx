import { Box, Stepper, Step, StepLabel } from '@mui/material';

export default function StageStepper({ value, onChange }) {
    const steps = ['Test Cases', 'Experiments', 'Results'];

    return (
        <Box sx={{ mt: 8, width: '60%', mx: 'auto' }}>
            <Stepper nonLinear activeStep={value} alternativeLabel>
                {steps.map((label, index) => (
                    <Step key={label} onClick={() => onChange?.(index)}>
                        <StepLabel>{label}</StepLabel>
                    </Step>
                ))}
            </Stepper>
        </Box>
    );
}