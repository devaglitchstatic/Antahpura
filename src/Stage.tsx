import React from 'react';
import './index.scss';

const princess = {
  name: 'Kuma Ree Rati',
  archetype: 'Chhala-Audhatya',
  role: 'Pravartaka (Initiator)',
  age: 22,
  arts: 'Yoga • Poetry • Dance',
  ojas: 72,
  kama: 55,
  portrait: 'https://avatars.charhub.io/avatars/austere_sweet_62889/princess-kuma-ree-kama-b40508c4faf7/chara_card_v2.png?nocache=2026-07-30T12:12:17Z',
  chub: 'https://chub.ai/characters/austere_sweet_62889/princess-kuma-ree-kama-b40508c4faf7'
};

const mahaDeva = {
  name: 'Mahā Deva',
  portrait: 'https://avatars.charhub.io/avatars/austere_sweet_62889/maha-deva-0683f297e053/chara_card_v2.png?nocache=2026-08-02T21:10:42Z',
  chub: 'https://chub.ai/characters/austere_sweet_62889/maha-deva-0683f297e053'
};

const padma = {
  name: 'Padmā',
  portrait: 'https://avatars.charhub.io/avatars/austere_sweet_62889/padma-6f6d56dd4121/chara_card_v2.png?nocache=2026-07-29T20:45:59Z',
  chub: 'https://chub.ai/characters/austere_sweet_62889/padma-6f6d56dd4121'
};

export default function Stage() {
  return (
    <div className="stage-root" style={{background:'#0b0907', minHeight:'100vh', padding:'16px'}}>
      <div style={{
        background:'#111',
        border:'1px solid #6b4f1d',
        borderRadius:'22px',
        padding:'16px',
        color:'#efe6c9',
        maxWidth:'420px',
        margin:'0 auto'
      }}>

        <div style={{fontSize:'18px', fontWeight:700, color:'#d4af37', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>
          Sākṣī Pīṭha
        </div>

        <div style={{
          marginTop:'12px',
          border:'1px solid #8a6a2a',
          borderRadius:'12px',
          padding:'10px',
          background:'#1a1206'
        }}>
          <div style={{fontSize:'10px', color:'#f4d36b', fontWeight:700}}>LATEST REVELATION ●</div>
          <div style={{fontSize:'11px', lineHeight:1.4}}>
            Exhibition pending — Darśana resonance increased by Mahā Deva.
          </div>
        </div>

        <hr style={{borderColor:'#3a2a10', margin:'16px 0'}} />

        <div style={{fontSize:'13px', color:'#d4af37', fontWeight:700, marginBottom:'8px'}}>MANDIRA • KĀLA</div>
        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'6px 14px', fontSize:'11px'}}>
          <div><b>Mandira:</b> Kedāra</div>
          <div><b>Ṛtu:</b> Varṣā</div>
          <div><b>Sabhā:</b> Mahāśivarātri</div>
          <div><b>Tithi:</b> Amāvasyā</div>
          <div><b>Dṛśya:</b> Darśana</div>
          <div><b>Sākṣī:</b> Awakened</div>
        </div>

        <hr style={{borderColor:'#3a2a10', margin:'16px 0'}} />

        <div style={{fontSize:'13px', color:'#d4af37', fontWeight:700, marginBottom:'8px'}}>JĪVA-MAṆḌALA</div>

        <div style={{
          display:'flex',
          gap:'10px',
          border:'1px solid #3a2a10',
          borderRadius:'14px',
          padding:'10px',
          background:'#151515'
        }}>
          <img
            src={princess.portrait}
            alt={princess.name}
            style={{width:'56px',height:'56px',borderRadius:'50%',objectFit:'cover',border:'2px solid #d4af37'}}
          />
          <div style={{fontSize:'11px', lineHeight:1.45}}>
            <div style={{fontWeight:700, color:'#f4e6b8'}}>
              {princess.name} • {princess.archetype}
            </div>
            <div><b>Pravartaka:</b> Initiator • <b>Age:</b> {princess.age}</div>
            <div>{princess.arts}</div>
            <div><b>Ojas:</b> {princess.ojas} • <b>Kāma:</b> {princess.kama}%</div>
            <div>Disciplined, curious, emotionally precise.</div>
            <a href={princess.chub} target="_blank" rel="noreferrer" style={{color:'#d4af37', textDecoration:'none'}}>
              View Character Card
            </a>
          </div>
        </div>

        <div style={{display:'flex', gap:'8px', flexWrap:'wrap', marginTop:'10px'}}>
          <a href={mahaDeva.chub} target="_blank" rel="noreferrer" style={{textDecoration:'none'}}>
            <div style={{
              display:'flex',alignItems:'center',gap:'6px',
              border:'1px solid #7f5af0',borderRadius:'999px',
              padding:'6px 10px',background:'#1a1626',
              fontSize:'10px',color:'#d9c9ff'
            }}>
              <img
                src={mahaDeva.portrait}
                alt={mahaDeva.name}
                style={{width:'18px',height:'18px',borderRadius:'50%',objectFit:'cover'}}
              />
              Prativaktā • {mahaDeva.name}
            </div>
          </a>

          <a href={padma.chub} target="_blank" rel="noreferrer" style={{textDecoration:'none'}}>
            <div style={{
              display:'flex',alignItems:'center',gap:'6px',
              border:'1px solid #2cb67d',borderRadius:'999px',
              padding:'6px 10px',background:'#13231d',
              fontSize:'10px',color:'#b9f2d0'
            }}>
              <img
                src={padma.portrait}
                alt={padma.name}
                style={{width:'18px',height:'18px',borderRadius:'50%',objectFit:'cover'}}
              />
              Sākṣī-Bhūta • {padma.name}
            </div>
          </a>
        </div>

        <hr style={{borderColor:'#3a2a10', margin:'16px 0'}} />

        <div style={{fontSize:'13px', color:'#d4af37', fontWeight:700, marginBottom:'8px'}}>VIDHI-YANTRA</div>

        <div style={{display:'grid', gap:'8px'}}>
          <div style={{
            display:'flex',justifyContent:'space-between',alignItems:'center',
            border:'1px solid #14532d',background:'#0f2416',
            borderRadius:'10px',padding:'8px 10px',fontSize:'11px'
          }}>
            <span><b>Adhikāra</b> (Authority)</span>
            <span style={{color:'#22c55e',fontWeight:700}}>ACTIVE</span>
          </div>

          <div style={{
            display:'flex',justifyContent:'space-between',alignItems:'center',
            border:'1px solid #854d0e',background:'#2a1a05',
            borderRadius:'10px',padding:'8px 10px',fontSize:'11px'
          }}>
            <span><b>Sammati</b> (Consent)</span>
            <span style={{color:'#eab308',fontWeight:700}}>PENDING</span>
          </div>

          <div style={{
            display:'flex',justifyContent:'space-between',alignItems:'center',
            border:'1px solid #14532d',background:'#0f2416',
            borderRadius:'10px',padding:'8px 10px',fontSize:'11px'
          }}>
            <span><b>Maryādā</b> (Boundary)</span>
            <span style={{color:'#22c55e',fontWeight:700}}>SECURE</span>
          </div>

          <div style={{
            display:'flex',justifyContent:'space-between',alignItems:'center',
            border:'1px solid #7f1d1d',background:'#2a0f0f',
            borderRadius:'10px',padding:'8px 10px',fontSize:'11px'
          }}>
            <span><b>Darśana</b> (Witness Threshold)</span>
            <span style={{color:'#ef4444',fontWeight:700}}>LOCKED</span>
          </div>
        </div>

        <hr style={{borderColor:'#3a2a10', margin:'16px 0'}} />

        <div style={{fontSize:'13px', color:'#d4af37', fontWeight:700, marginBottom:'8px'}}>PUṆYASIDDHI</div>
        <div style={{fontSize:'11px', lineHeight:1.5}}>
          <div><b>Initiator:</b> {princess.name}</div>
          <div><b>Disciple:</b> {padma.name}</div>
          <div><b>Lesson:</b> Ātma-Pūjā (Self-Worship)</div>
          <div><b>Level:</b> 1</div>
        </div>

        <hr style={{borderColor:'#3a2a10', margin:'16px 0'}} />

        <div style={{fontSize:'13px', color:'#d4af37', fontWeight:700, marginBottom:'8px'}}>ŚARĪRA-TELEMETRY</div>
        <div style={{display:'grid', gap:'6px'}}>
          <div style={{display:'flex',justifyContent:'space-between',fontSize:'11px'}}><span>Avasthā</span><b>Lajjā-Āvaraṇa</b></div>
          <div style={{display:'flex',justifyContent:'space-between',fontSize:'11px'}}><span>Vāk Resonance</span><b>High</b></div>
          <div style={{display:'flex',justifyContent:'space-between',fontSize:'11px'}}><span>Prāṇa Sync</span><b>32%</b></div>
          <div style={{display:'flex',justifyContent:'space-between',fontSize:'11px'}}><span>Bhāva Pressure</span><b>Rising</b></div>
          <div style={{display:'flex',justifyContent:'space-between',fontSize:'11px'}}><span>Scene Authority</span><b>{mahaDeva.name}</b></div>
        </div>

      </div>
    </div>
  );
}
