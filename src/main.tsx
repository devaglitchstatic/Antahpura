import React from 'react';
import ReactDOM from 'react-dom/client';
import { Stage } from './Stage';

const testStage = new Stage({
    // minimal InitialData; TestRunner bypasses this path anyway
    initial: {},
    characters: [],
    user: { anonymizedId: '0', name: 'You' },
} as any);

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        {testStage.render()}
    </React.StrictMode>
);