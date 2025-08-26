import { useState, useEffect } from 'react';
import { useAuthContext } from '../../app/providers/AuthProvider';

import { getProjects } from '../../features/project/api/project';
import { getTeamUsers } from '../../features/team/api/team';
import { getCredentials } from '../../features/credential/api/credential';
import { getSourceModels } from '../../features/source/api/source';

import ProjectHeader from './ProjectHeader';
import StageStepper from './StageStepper';
import TestCasesPanel from './TestCasesPanel';
import ExperimentsPanel from './ExperimentsPanel';

function Project() {
    const { accessToken } = useAuthContext();

    const [project, setProject] = useState(null);
    const [members, setMembers] = useState([]);
    const [models, setModels] = useState([]);
    const [credentials, setCredentials] = useState([]);

    const [cases, setCases] = useState([{ id: '', request: '', expected: '' }]);
    const [stage, setStage] = useState(0);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!accessToken) return;

        (async () => {
            try {
                setLoading(true);

                const projList = await getProjects();
                const p = projList[0] ?? null;
                setProject(p);
                if (!p) return;

                const tasks = [];

                if (p.team_id) {
                    tasks.push(
                        getTeamUsers(p.team_id)
                            .then(users => setMembers(users))
                            .catch(() => setMembers([]))
                    );
                }

                tasks.push(
                    (async () => {
                        const creds = await getCredentials();
                        setCredentials(Array.isArray(creds) ? creds : []);
                        if (!Array.isArray(creds) || creds.length === 0) {
                            setModels([]);
                            return;
                        }
                        const all = [];

                        for (const cred of creds) {
                            if (!cred.source_id) continue;
                            const ms = await getSourceModels(cred.source_id);
                            if (Array.isArray(ms)) all.push(...ms);
                        }
                        setModels(all);
                    })().catch(() => setModels([]))
                );

                await Promise.all(tasks);
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
            {stage === 1 &&
                <ExperimentsPanel
                    cases={cases}
                    models={models}
                    credentialName={credentials[0].name}
                    projectId={project.id}
                />
            }
            {stage === 2 && <div>Results Panel</div>}
        </div>
    );
}

export default Project;