import runtime from '../data/constitution/observer_runtime.json';

const C = {
  bg:'#090909',
  panel:'#121212',
  panel2:'#151515',
  border:'#3a2a10',
  gold:'#d4af37',
  ivory:'#f4e6b8',
  muted:'#9ca3af',
  emerald:'#22c55e',
  amber:'#eab308',
  crimson:'#ef4444',
  cyan:'#38bdf8',
  violet:'#a78bfa',
  rose:'#fb7185',
  blue:'#60a5fa',
};

function toneForFlag(key: string, value: any) {
  const k = key.toLowerCase();
  if (k.includes('pup')) return { ring:'#92400e', fill:'#1b1409', text:C.amber, label:'DORMANT' };
  if (k.includes('champa')) return { ring:'#1d4ed8', fill:'#0d1725', text:C.blue, label:'INACTIVE' };
  if (k.includes('witness')) return { ring:'#1d4ed8', fill:'#0d1725', text:C.blue, label:'ACTIVE' };
  if (value) return { ring:'#14532d', fill:'#0d2013', text:C.emerald, label:'ACTIVE' };
  return { ring:'#7f1d1d', fill:'#211010', text:C.crimson, label:'LOCKED' };
}

const Panel = ({ title, children, style = {} }: { title: string; children: any; style?: React.CSSProperties }) => (
  <div style={{
    border:`1px solid ${C.border}`,
    borderRadius:14,
    background:C.panel,
    padding:12,
    marginBottom:14,
    ...style
  }}>
    <div style={{
      fontSize:12,
      color:C.ivory,
      fontWeight:700,
      letterSpacing:'0.04em',
      marginBottom:8
    }}>
      {title}
    </div>
    {children}
  </div>
);

const Seal = ({ value, size = 34 }: { value: number | string; size?: number }) => (
  <div style={{
    width:size,
    height:size,
    borderRadius:'50%',
    border:`1.5px solid ${C.gold}`,
    color:C.ivory,
    display:'grid',
    placeItems:'center',
    fontSize:14,
    fontWeight:600,
    background:'#181106',
    boxShadow:'inset 0 0 0 1px rgba(212,175,55,0.15)'
  }}>
    {value}
  </div>
);

const Meter = ({label,value,color}:{label:string,value:number,color:string}) => (
  <div style={{display:'grid',gap:4}}>
    <div style={{display:'flex',justifyContent:'space-between',alignItems:'baseline',fontSize:10.5}}>
      <span style={{color:C.muted,letterSpacing:'0.02em'}}>{label}</span>
      <span style={{color,fontWeight:600,fontSize:11.5}}>{value}%</span>
    </div>
    <div style={{height:6,borderRadius:999,background:'#222',overflow:'hidden'}}>
      <div style={{width:`${value}%`,height:'100%',borderRadius:999,background:color}} />
    </div>
  </div>
);

const SeatCard = ({seat}:{seat:any}) => (
  <div style={{
    display:'flex',
    alignItems:'center',
    gap:10,
    border:`1px solid ${C.border}`,
    borderRadius:12,
    padding:10,
    background:C.panel2
  }}>
    <div style={{
      width:44,
      height:44,
      borderRadius:'50%',
      overflow:'hidden',
      flex:'0 0 40px',
      border:`2px solid ${C.gold}`,
      background:'#1b1304'
    }}>
      <img
        src={seat.portrait || '/portraits/maha_deva.png'}
        alt={seat.character}
        style={{
          width:'100%',
          height:'100%',
          objectFit:'cover',
          display:'block'
        }}
      />
    </div>
    <div style={{minWidth:0}}>
      <div style={{fontSize:10,color:C.ivory,fontWeight:700,letterSpacing:'0.02em'}}>{seat.seat}</div>
      <div style={{fontSize:11,color:C.ivory,lineHeight:1.25,wordBreak:'break-word'}}>{seat.title} • {seat.character}</div>
    </div>
  </div>
);

const RitualTile = ({icon,label,value,border,fill,text}:{icon:string,label:string,value:string,border:string,fill:string,text:string}) => (
  <div style={{
    border:`1px solid ${border}`,
    background:fill,
    borderRadius:12,
    minHeight:64,
    padding:'10px 8px',
    display:'grid',
    placeItems:'center',
    textAlign:'center',
    gap:4
  }}>
    <div style={{fontSize:18,lineHeight:1}}>{icon}</div>
    <div style={{fontSize:10,color:text,fontWeight:700,letterSpacing:'0.05em'}}>{label}</div>
    <div style={{fontSize:11,color:C.ivory,fontWeight:500,lineHeight:1.15}}>{value}</div>
  </div>
);

export default function Stage() {
  const hero = runtime.hero || {};
  const seats = runtime.seats || [];
  const maha = seats.find((s:any)=>s.seat==='Prativaktā');
  const padma = seats.find((s:any)=>s.seat==='Nitya-Saṅginī');
  const champa = seats.find((s:any)=>s.seat==='Svatantra-Gṛha' || s.seat==='Chāyā-Saṅginī');

  const mk = runtime.mandira_kala || {};
  const flags = runtime.story_flags || {};
  const flagsEntries = Object.entries(flags);

  const level = runtime.punyasiddhi?.level ?? 1;
  const chronicle = runtime.chronicle_entries ?? 0;
  const scene = runtime.scene?.title ?? 'Constitutional Silence';
  const constellations = Array.isArray(runtime.constellations) ? runtime.constellations.join(', ') : (runtime.constellations ?? '—');

  return (
    <div style={{
      maxWidth:460,
      margin:'0 auto',
      padding:16,
      color:C.ivory,
      background:C.bg,
      minHeight:'100vh',
      fontFamily:'serif'
    }}>
      <div style={{textAlign:'center',marginBottom:16}}>
        <div style={{fontSize:28,color:C.ivory,fontWeight:700,lineHeight:1.05}}>Sākṣī Pīṭha</div>
        <div style={{fontSize:11,color:C.muted}}>Constitutional Witness Engine</div>
      </div>

      <Panel title="LATEST REVELATION ●">
        <div style={{fontSize:11,lineHeight:1.45}}>{runtime.latest_revelation}</div>
      </Panel>

      <Panel title="JĪVA-MAṆḌALA">
        <div style={{
          display:'grid',
          gridTemplateColumns:'1.35fr 1fr',
          gap:10
        }}>
          <div style={{
            border:`1px solid ${C.border}`,
            borderRadius:16,
            padding:12,
            background:C.panel2
          }}>
            <div style={{
              width:88,
              height:88,
              borderRadius:'50%',
              overflow:'hidden',
              border:`3px solid ${C.gold}`,
              margin:'0 auto 10px',
              background:'#1b1304'
            }}>
              <img
                src={hero.portrait || '/portraits/maha_deva.png'}
                alt={hero.character || 'Kuma Ree Rati'}
                style={{width:'100%',height:'100%',objectFit:'cover',display:'block'}}
              />
            </div>

            <div style={{textAlign:'center',marginBottom:8}}>
              <div style={{fontWeight:700,fontSize:15,lineHeight:1.05,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{hero.character || 'Kuma Ree Rati'}</div>
              <div style={{fontSize:11,color:C.ivory,marginTop:4}}>{hero.character || 'Kuma Ree Rati'} • {hero.archetype || 'Chhala-Audhatya'}</div>
            </div>

            <div style={{fontSize:11,display:'grid',gap:6,lineHeight:1.35}}>
              <div><b style={{color:C.ivory}}>Pravartaka:</b> Initiator • <b style={{color:C.ivory}}>Age:</b> {hero.age ?? 22}</div>
              <div>{hero.arts || 'Yoga • Poetry • Dance'}</div>
              <div>
                <b style={{color:C.ivory}}>Ojas:</b> <span style={{color:C.ivory,fontWeight:700}}>{hero.ojas ?? 72}</span>
                {' '}•{' '}
                <b style={{color:C.ivory}}>Kāma:</b> <span style={{color:C.rose,fontWeight:700}}>{hero.kama ?? 55}%</span>
              </div>
              <div style={{color:C.muted}}>Disciplined, curious, emotionally precise.</div>
              <a href={hero.chub || '#'} target="_blank" rel="noreferrer" style={{color:C.ivory,textDecoration:'none'}}>View Character Card</a>
            </div>
          </div>

          <div style={{display:'grid',gap:8}}>
            {maha && <SeatCard seat={maha} />}
            {padma && <SeatCard seat={padma} />}
            {champa && <SeatCard seat={champa} />}
          </div>
        </div>
      </Panel>

      <Panel title="MANDIRA • KĀLA">
        <div style={{
          display:'grid',
          gridTemplateColumns:'1fr 1fr',
          gap:12,
          alignItems:'stretch'
        }}>
          <div style={{
            display:'grid',
            gap:10,
            alignContent:'start'
          }}>
            <div style={{fontSize:11,lineHeight:1.45}}>
              <div><span style={{color:C.ivory,fontSize:10,fontWeight:700,letterSpacing:'0.04em'}}>Mandira</span><br/>{mk.mandira || 'Kedāra'}</div>
            </div>
            <div style={{fontSize:11,lineHeight:1.45}}>
              <div><span style={{color:C.ivory,fontSize:10,fontWeight:700,letterSpacing:'0.04em'}}>Dṛśya</span><br/>{mk.drisya || mk.drishya || 'Darśana'}</div>
            </div>
          </div>

          <div style={{
            display:'grid',
            gridTemplateColumns:'1fr 1fr',
            gap:10
          }}>
            <RitualTile icon="🌧" label="ṚTU" value={mk.rtu || 'Varṣā'} border="#1f3b6d" fill="#0d1725" text={C.blue} />
            <RitualTile icon="🕯" label="SABHĀ" value={mk.sabha || 'Mahāśivarātri'} border="#5b3b9c" fill="#1b1430" text={C.violet} />
            <RitualTile icon="🌑" label="TITHI" value={mk.tithi || 'Amāvasyā'} border="#475569" fill="#141414" text={C.muted} />
            <RitualTile icon="✨" label="SĀKṢĪ" value={mk.saksi || 'Awakened'} border="#14532d" fill="#0d2013" text={C.emerald} />
          </div>
        </div>
      </Panel>

      <Panel title="VIDHI-YANTRA">
        <div style={{display:'grid',gap:8}}>
          {flagsEntries.map(([k,v]) => {
            const t = toneForFlag(k, v);
            return (
              <div key={k} style={{
                display:'flex',
                justifyContent:'space-between',
                alignItems:'center',
                border:`1px solid ${t.ring}`,
                background:t.fill,
                borderRadius:10,
                padding:'8px 10px',
                fontSize:11,
                lineHeight:1.2
              }}>
                <span style={{color:C.ivory, wordBreak:'break-word', paddingRight:10}}>{k}</span>
                <span style={{color:t.text, fontWeight:700, letterSpacing:'0.02em'}}>{t.label}</span>
              </div>
            );
          })}
        </div>
      </Panel>

      <Panel title="PUṆYASIDDHI">
        <div style={{
          display:'grid',
          gridTemplateColumns:'1fr 1fr',
          gap:12,
          alignItems:'start'
        }}>
          <div style={{display:'grid',gap:6,fontSize:11,lineHeight:1.35}}>
            <div><span style={{color:C.ivory,fontSize:10,fontWeight:700,letterSpacing:'0.04em'}}>Initiator</span><br/>{hero.character || 'Kuma Ree Rati'}</div>
            <div><span style={{color:C.ivory,fontSize:10,fontWeight:700,letterSpacing:'0.04em'}}>Disciple</span><br/>{padma?.character || 'Baha Soren (Padmā)'}</div>
          </div>

          <div style={{display:'grid',gap:8}}>
            <div style={{
              border:`1px solid ${C.border}`,
              borderRadius:10,
              padding:'8px 10px',
              background:C.panel2
            }}>
              <div style={{fontSize:10,color:C.ivory,fontWeight:700,letterSpacing:'0.04em'}}>Lesson</div>
              <div style={{fontSize:11,lineHeight:1.25}}>Ātma-Pūjā (Self-Worship)</div>
            </div>

            <div style={{
              border:`1px solid ${C.border}`,
              borderRadius:10,
              padding:'8px 10px',
              background:C.panel2,
              display:'grid',
              justifyItems:'center',
              gap:4
            }}>
              <div style={{fontSize:10,color:C.ivory,fontWeight:700,letterSpacing:'0.04em'}}>Level</div>
              <Seal value={level} size={34} />
            </div>
          </div>
        </div>
      </Panel>

      <Panel title="ŚARĪRA-TELEMETRY">
        <div style={{
          display:'grid',
          gridTemplateColumns:'1fr 1fr',
          gap:18,
          alignItems:'start'
        }}>
          <div style={{display:'grid',gap:10}}>
            <div style={{display:'grid',gap:2}}>
              <div style={{fontSize:10,color:C.ivory,letterSpacing:'0.05em',fontWeight:700}}>Avasthā</div>
              <div style={{fontSize:12,color:C.ivory,fontWeight:500,lineHeight:1.2}}>Lajjā-Āvaraṇa</div>
            </div>

            <div style={{display:'grid',gap:2}}>
              <div style={{fontSize:10,color:C.ivory,letterSpacing:'0.05em',fontWeight:700}}>Vāk Resonance</div>
              <div style={{fontSize:12,color:C.violet,fontWeight:500,lineHeight:1.2}}>High</div>
            </div>

            <div style={{
              gridColumn:'1 / -1',
              marginTop:4,
              paddingTop:10,
              borderTop:`1px solid ${C.border}`,
              display:'grid',
              gap:2
            }}>
              <div style={{fontSize:10,color:C.ivory,letterSpacing:'0.05em',fontWeight:700}}>SCENE AUTHORITY</div>
              <div style={{fontSize:12,color:C.blue,fontWeight:500,lineHeight:1.2}}>Mahā Deva</div>
            </div>
          </div>

          <div style={{display:'grid',gap:10}}>
            <Meter label="Prāṇa Sync" value={32} color={C.cyan}/>
            <Meter label="Bhāva Pressure" value={68} color={C.amber}/>
          </div>
        </div>
      </Panel>

      <Panel title="OBSERVER">
        <div style={{
          display:'grid',
          gridTemplateColumns:'1fr 1fr',
          gap:12,
          alignItems:'start'
        }}>
          <div style={{display:'grid',gap:8,fontSize:11,lineHeight:1.35}}>
            <div><span style={{color:C.ivory,fontSize:10,fontWeight:700,letterSpacing:'0.04em'}}>Current Scene</span><br/>{scene}</div>
            <div><span style={{color:C.ivory,fontSize:10,fontWeight:700,letterSpacing:'0.04em'}}>Mode</span><br/><span style={{color:C.blue}}>Observe</span></div>
          </div>

          <div style={{display:'grid',gap:8}}>
            <div style={{
              border:`1px solid ${C.border}`,
              borderRadius:10,
              padding:'8px 10px',
              background:C.panel2,
              display:'grid',
              justifyItems:'start',
              gap:4
            }}>
              <div style={{fontSize:10,color:C.ivory,fontWeight:700,letterSpacing:'0.04em'}}>Constellations</div>
              <div style={{fontSize:11,lineHeight:1.25,wordBreak:'break-word'}}>{constellations}</div>
            </div>

            <div style={{
              border:`1px solid ${C.border}`,
              borderRadius:10,
              padding:'8px 10px',
              background:C.panel2,
              display:'grid',
              justifyItems:'center',
              gap:4
            }}>
              <div style={{fontSize:10,color:C.ivory,fontWeight:700,letterSpacing:'0.04em'}}>Chronicle Entries</div>
              <Seal value={chronicle} size={34} />
            </div>
          </div>
        </div>
      </Panel>
    </div>
  );
}
