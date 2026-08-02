import React, { useState } from 'react';
import './index.scss';

const scene = {
  temple: 'Kedara Mandapa',
  gathering: 'Mahashivaratri Royal Assembly',
  title: 'Darshana Initiation',
  authority: 'Maha Deva',
  telemetry: 'Lajja-Avarana',
  breath: 32,
  pressure: 'Rising',
};

const participants = [
  { name: 'Maha Deva', role: 'Sovereign Authority', cycle: null },
  { name: 'Princess Kuma Ree Rati', role: 'Active Initiate', cycle: 'Day 16 — Sattva-Kala' },
  { name: 'Padma', role: 'Witness / Disciple', cycle: 'Day 12 — Soma-Kala' },
];

const roster = [
  { name: 'Maha Deva', status: 'Present' },
  { name: 'Princess Kuma Ree Rati', status: 'Present' },
  { name: 'Padma', status: 'Present' },
  { name: 'Champa', status: 'Absent' },
  { name: 'Kamini Anisa', status: 'Absent' },
  { name: 'Shrinagar', status: 'Absent' },
  { name: 'Tarana', status: 'Absent' },
  { name: 'Roxana', status: 'Outer Gate' },
  { name: 'Jahzara', status: 'Patrol' },
  { name: 'Sevda', status: 'Vault' },
  { name: 'Malika', status: 'Subterranean Wing' },
  { name: 'Reva', status: 'Chorus Hall' },
  { name: 'Zola', status: 'Chorus Hall' },
  { name: 'Altani', status: 'Temple Sentinel' },
];

export default function Stage() {
  const [showRoster, setShowRoster] = useState(false);
  const [protocols] = useState({
    adhikara: true,
    sammati: false,
    maryada: true,
    darshana: false,
    punyasiddhi: 'Level I Available',
  });

  return (
    <div className="stage-root">
      <div className="plinth">
        <h1>ANTAHPURA MONITORING PLINTH V14</h1>

        <div className="section">
          <h2>Temple Architecture</h2>
          <div><strong>Temple:</strong> {scene.temple}</div>
          <div><strong>Gathering:</strong> {scene.gathering}</div>
          <div><strong>Scene:</strong> {scene.title}</div>
        </div>

        <div className="section">
          <h2>Scene-Aware Participants</h2>
          {participants.map((p) => (
            <div key={p.name} className="participant">
              <div><strong>{p.name}</strong></div>
              <div>{p.role}</div>
              <div>{p.cycle ? `Cycle: ${p.cycle}` : 'Cycle: —'}</div>
            </div>
          ))}
        </div>

        <div className="section">
          <h2>Sanskrit Protocol Engine</h2>
          <div>Adhikara: {protocols.adhikara ? 'Established' : 'Pending'}</div>
          <div>Sammati: {protocols.sammati ? 'Granted' : 'Pending'}</div>
          <div>Maryada: {protocols.maryada ? 'Observed' : 'Violated'}</div>
          <div>Darshana: {protocols.darshana ? 'Acknowledged' : 'Awaiting Recognition'}</div>
        </div>

        <div className="section">
          <h2>Punyasiddhi Progression</h2>
          <div><strong>Initiator:</strong> Princess Kuma Ree Rati</div>
          <div><strong>Disciple:</strong> Padma</div>
          <div><strong>Lesson:</strong> Atma-Puja (Self-Worship)</div>
          <div><strong>Status:</strong> {protocols.punyasiddhi}</div>
        </div>

        <div className="section">
          <h2>Somatic Telemetry</h2>
          <div><strong>Phase:</strong> {scene.telemetry}</div>
          <div><strong>Voice Resonance:</strong> High</div>
          <div><strong>Breath Synchronization:</strong> {scene.breath}%</div>
          <div><strong>Emotional Pressure:</strong> {scene.pressure}</div>
          <div><strong>Scene Authority:</strong> {scene.authority}</div>
        </div>

        <div className="section">
          <button onClick={() => setShowRoster(!showRoster)}>
            {showRoster ? 'Hide Full Roster' : 'Show Full Roster'}
          </button>

          {showRoster && (
            <div className="roster">
              <h2>Imperial Character Registry</h2>
              {roster.map((r) => (
                <div key={r.name} className="roster-row">
                  <span>{r.name}</span>
                  <span>{r.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
