import React from 'react';
import ReactDOM from 'react-dom/client';
import Stage from './Stage';

// Create a static mockup history array to feed the component variables directly
const mockHistory = [
  { text: "Princess Kuma Ree Kama executes her classical erotological yoga posture..." }
];

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <div style={{ backgroundColor: '#111', minHeight: '100vh', padding: '20px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <Stage chatHistory={mockHistory} characterData={{}} updateStageState={() => {}} />
    </div>
  </React.StrictMode>
);

