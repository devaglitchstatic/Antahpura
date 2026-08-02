import React, { useMemo, useState } from 'react';
import './index.scss';
import { constitution } from './engine/constitution';

export default function Stage() {
  const [sceneKey] = useState('darshana');
  const [showRoster, setShowRoster] = useState(false);

  const scene = constitution.scenes[sceneKey];
  const participants = useMemo(
    () => constitution.characters.filter(c => scene.participants.includes(c.name)),
    [scene]
  );

  return (
    <div className="stage-root">
      <div className="plinth">
        <h1>ANTAHPURA MONITORING PLINTH {constitution.version}</h1>

        <div className="section">
          <h2>Temple Architecture</h2>
          <div><strong>Temple:</strong> {scene.temple}</div>
          <div><strong>Gathering:</strong> {scene.gathering}</div>
          <div><strong>Scene:</strong> {scene.title}</div>
        </div>

        <div className="section">
          <h2>Scene-Aware Participants</h2>
          {participants.map(p => (
            <div key={p.name} className="participant">
              <div><strong>{p.name}</strong></div>
              <div>{p.role}</div>
              <div>{p.cycle ? `Cycle: ${p.cycle}` : 'Cycle: —'}</div>
            </div>
          ))}
        </div>

        <div className="section">
          <h2>Sanskrit Protocol Engine</h2>
          {Object.entries(scene.protocols).map(([k, v]) => (
            <div key={k}>
              <strong>{k}:</strong> {v ? constitution.protocols[k] : 'Pending'}
            </div>
          ))}
        </div>

        <div className="section">
          <h2>Punyasiddhi Progression</h2>
          <div><strong>Initiator:</strong> {scene.punyasiddhi.initiator}</div>
          <div><strong>Disciple:</strong> {scene.punyasiddhi.disciple}</div>
          <div><strong>Lesson:</strong> {scene.punyasiddhi.lesson}</div>
          <div><strong>Level:</strong> {scene.punyasiddhi.level}</div>
        </div>

        <div className="section">
          <h2>Somatic Telemetry</h2>
          <div><strong>Phase:</strong> {scene.telemetry}</div>
          <div><strong>Voice Resonance:</strong> High</div>
          <div><strong>Breath Synchronization:</strong> 32%</div>
          <div><strong>Emotional Pressure:</strong> Rising</div>
          <div><strong>Scene Authority:</strong> {scene.authority}</div>
        </div>

        <div className="section">
          <button onClick={() => setShowRoster(!showRoster)}>
            {showRoster ? 'Hide Full Roster' : 'Show Full Roster'}
          </button>

          {showRoster && (
            <div className="roster">
              <h2>Imperial Character Registry</h2>
              {constitution.characters.map(c => (
                <div key={c.name} className="roster-row">
                  <span>{c.name}</span>
                  <span>{c.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
