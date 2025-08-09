import { Routes, Route } from 'react-router-dom';
import PATH from './path';

import Home from '../pages/Home';
import Project from '../pages/Project';
import Projects from '../pages/Projects';
import NewProject from '../pages/NewProject'
import My from '../pages/My';
import Notfound from '../pages/Notfound';

function AppRouter() {
    return (
        <Routes>
            <Route path={PATH.HOME} element={<Home />} />
            <Route path={PATH.PROJECT} element={<Project />} />
            <Route path={PATH.PROJECTS} element={<Projects />} />
            <Route path={PATH.NEWPROJECT} element={<NewProject />} />
            <Route path={PATH.MY} element={<My />} />
            <Route path={PATH.NOT_FOUND} element={<Notfound />} />
        </Routes>
    );
}

export default AppRouter;