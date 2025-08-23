import ProjectHeader from './ProjectHeader';
import { useState } from 'react';
import StageStepper from './StageStepper';
import TestCasesPanel from './TestCasesPanel';

function Project() {
    const project = {
        id: 'proj_1',
        name: 'Project name',
        description: 'description...',
        teamCode: 'ABCD-1234',
        leader: { id: 'u1', name: 'Leader name' },
        members: [
            { id: 'u2', name: 'Member 1' },
            { id: 'u3', name: 'Member 2' },
        ],
    };

    const [cases, setCases] = useState([
        { id: 'c1', request: 'Case 1 input', expected: 'Expected result 1' },
    ]);

    const [stage, setStage] = useState(0);

    return (
        <div>
            <ProjectHeader project={project} />
            <StageStepper value={stage} onChange={setStage} />
            {stage === 0 && <TestCasesPanel cases={cases} setCases={setCases} />}
            {stage === 1 && (
                <div>
                    <h3>Experiments Panel</h3>
                    <pre>{JSON.stringify(cases, null, 2)}</pre>
                </div>
            )}
            {stage === 2 && <div>Results Panel</div>}
        </div>
    );
}

export default Project;