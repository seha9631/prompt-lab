import ProjectHeader from './ProjectHeader';
import { useState } from 'react';
import StageStepper from './StageStepper';

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

    const [stage, setStage] = useState(0);

    return (
        <div>
            <ProjectHeader project={project} />
            <StageStepper value={stage} onChange={setStage} />
            {stage === 0 && <div>Test Cases Panel</div>}
            {stage === 1 && <div>Experiments Panel</div>}
            {stage === 2 && <div>Results Panel</div>}
        </div>
    );
}

export default Project;