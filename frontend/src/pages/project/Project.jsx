import ProjectHeader from './ProjectHeader';

function ProjectPage() {
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

    return (
        <div>
            <ProjectHeader project={project} />
        </div>
    );
}

export default ProjectPage;