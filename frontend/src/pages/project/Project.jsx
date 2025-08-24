import { useState, useEffect } from 'react';
import { getProjects } from '../../features/project/api/project';
import { getTeamUsers } from '../../features/team/api/team';
import { useAuthContext } from '../../app/providers/AuthProvider';
import ProjectHeader from './ProjectHeader';
import StageStepper from './StageStepper';
import TestCasesPanel from './TestCasesPanel';
import ExperimentsPanel from './ExperimentsPanel';

function Project() {
    const { accessToken } = useAuthContext();
    const [project, setProject] = useState(null);
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [cases, setCases] = useState([{ id: '', request: '', expected: '' }]);
    const [stage, setStage] = useState(0);

    useEffect(() => {
        if (!accessToken) return;
        (async () => {
            try {
                const list = await getProjects();
                const p = list[0] ?? null;
                setProject(p);
                if (p?.team_id) {
                    const users = await getTeamUsers(p.team_id);
                    setMembers(users);
                }
            } catch (e) {
                setError(e?.response?.data ?? e);
            } finally {
                setLoading(false);
            }
        })();
    }, [accessToken]);

    if (!accessToken) return <div>Signing in...</div>;
    if (loading) return <div>Loading projects...</div>;
    if (error) return <div style={{ color: 'red' }}>Error: {JSON.stringify(error)}</div>;
    if (!project) return <div>No projects found.</div>;

    return (
        <div>
            <ProjectHeader project={project} members={members} />
            <StageStepper value={stage} onChange={setStage} />
            {stage === 0 && <TestCasesPanel cases={cases} setCases={setCases} />}
            {stage === 1 && <ExperimentsPanel cases={cases} />}
            {stage === 2 && <div>Results Panel</div>}
        </div>
    );
}

export default Project;