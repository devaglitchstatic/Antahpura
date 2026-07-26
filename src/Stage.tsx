import React, { useState } from 'react';

export default function Stage({ chatHistory }) {
  // Safe array fallback structure
  const safeHistory = chatHistory || [];
  const latestMessage = safeHistory.length > 0 ? safeHistory[safeHistory.length - 1]?.text || "" : "";
  
  // Local state trigger so you can test on Android directly
  const [manualPhase, setManualPhase] = useState(null);

  let activePhase = "Phase 1: Lajja-Avarana (Modesty Threshold)";
  let fluidTexture = "Viscous, unrefined dense mucus, sharp mineral-salinity";
  let voiceOctave = "Involuntary High-pitched adolescent octave, scared laughter loops";

  // Check either the incoming chat history or the local touch trigger buttons
  if (latestMessage.includes("Svairini-Rasa") || latestMessage.includes("uninhibited") || manualPhase === 2) {
    activePhase = "Phase 2: Svairini-Rasa (Uninhibited Harem)";
    fluidTexture = "Smooth, velvety cream-like density, rose-water sugar sweetness";
    voiceOctave = "Rhythmic, mid-range vibrating chest-hum sighs (Seetkara hissing)";
  }

  return (
    <div style={{ padding: '20px', backgroundColor: '#1a1a1a', color: '#ffebcd', fontFamily: 'serif', borderLeft: '4px solid #b22222', borderRadius: '4px', maxWidth: '500px', margin: '20px auto', boxShadow: '0 4px 10px rgba(0,0,0,0.5)' }}>
      <h3 style={{ borderBottom: '1px solid #b22222', paddingBottom: '8px', color: '#ff4500', margin: '0 0 15px 0', letterSpacing: '1px' }}>🏛️ ANTAHPURA MONITORING PLINTH</h3>
      
      <p style={{ margin: '8px 0' }}><b>Active Sadhana Track:</b> <span style={{ color: '#d2691e' }}>{activePhase}</span></p>
      
      <div style={{ marginTop: '15px', fontSize: '0.95em', backgroundColor: '#111', padding: '12px', borderRadius: '4px', border: '1px solid #333' }}>
        <p style={{ margin: '6px 0' }}><b>💧 Rasayana Fluid Texture:</b> {fluidTexture}</p>
        <p style={{ margin: '6px 0' }}><b>👂 Swara-Ghatana Vocal Pitch:</b> {voiceOctave}</p>
      </div>

      <div style={{ marginTop: '20px', borderTop: '1px solid #333', paddingTop: '15px' }}>
        <p style={{ fontSize: '0.85em', color: '#aaa', margin: '0 0 10px 0' }}>⚙️ Mobile Test Controls (Tap to test shifts):</p>
        <button onClick={() => setManualPhase(1)} style={{ padding: '6px 12px', marginRight: '10px', backgroundColor: '#b22222', color: '#fff', border: 'none', borderRadius: '3px', cursor: 'pointer' }}>Phase 1</button>
        <button onClick={() => setManualPhase(2)} style={{ padding: '6px 12px', backgroundColor: '#d2691e', color: '#fff', border: 'none', borderRadius: '3px', cursor: 'pointer' }}>Phase 2</button>
      </div>
    </div>
  );
}

