import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

path = r'C:\Users\Andrew\Documents\gas-safety-multiuser\src\App.jsx'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

NEW_COMPONENT = r'''
// ─── Property Safety Assessment (Decision Tree) ──────────────────────────────
const PSA_APPLIANCE_OPTIONS = [
  "Boiler", "Gas Fire", "Cooker / Hob", "Water Heater", "Pipework", "LPG Installation"
];

const PSA_FAULT_CATEGORIES = [
  "Gas Escape", "Flue", "Ventilation", "Combustion", "Safety Device", "Installation"
];

function psaGetQuestions(category) {
  switch(category) {
    case "Gas Escape":   return [{ q:"Is there a smell of gas or confirmed leak?", yes:"ID", no:"NCS" }];
    case "Flue":         return [{ q:"Is the flue disconnected or damaged?", yes:null, no:"NCS" }, { q:"Are combustion products entering the room?", yes:"ID", no:"AR" }];
    case "Ventilation":  return [{ q:"Is ventilation insufficient for safe operation now?", yes:"ID", no:"AR" }];
    case "Combustion":   return [{ q:"Is there evidence of unsafe combustion?", yes:null, no:"NCS" }, { q:"Is it dangerous now?", yes:"ID", no:"AR" }];
    case "Safety Device":return [{ q:"Has a safety device failed?", yes:null, no:"NCS" }, { q:"Does this create immediate danger?", yes:"ID", no:"AR" }];
    case "Installation": return [{ q:"Is installation unsafe right now?", yes:"ID", no:null }, { q:"Could it become unsafe?", yes:"AR", no:"NCS" }];
    default: return [];
  }
}

function GasSafetyAssessmentScreen({ onBack, onHome, engineerData, setRecords, onCreateWN }) {
  const [phase, setPhase]             = useState("details");   // details|appliances|faults|questions|results
  const [details, setDetails]         = useState({ fileRef:"", clientName:"", clientAddr1:"", clientAddr2:"", clientAddr3:"", clientPostcode:"", clientTel:"", clientEmail:"", instAddr1:"", instAddr2:"", instAddr3:"", instPostcode:"" });
  const [selectedAppliances, setSel]  = useState([]);
  const [faultData, setFaultData]     = useState([]);          // [{appliance, category, result}]
  const [idx, setIdx]                 = useState(0);           // current appliance index
  const [qIdx, setQIdx]               = useState(0);           // current question index
  const [contacts, setContacts]       = useState(() => { try { return JSON.parse(localStorage.getItem(sk("client_contacts"))||"[]"); } catch { return []; } });
  const [showContacts, setShowContacts] = useState(false);

  const DARK   = "#03180d";
  const YELLOW = "#fff200";
  const RED    = "#c0392b";
  const ORANGE = "#e67e22";
  const inp    = { width:"100%", padding:"12px 14px", border:"1px solid #e0e0e0", borderRadius:10, fontSize:15, boxSizing:"border-box", fontFamily:"'Segoe UI',sans-serif", outline:"none", background:"#fff", marginBottom:2 };
  const sec    = (title) => (
    <div style={{ background:DARK, color:"#fff", padding:"12px 16px", borderRadius:10, fontWeight:700, fontSize:14, marginTop:20, marginBottom:12 }}>{title}</div>
  );

  function fillFromContact(c) {
    setDetails(d => ({ ...d,
      clientName: c.name||"", clientAddr1: c.addr||"", clientPostcode: c.postcode||"",
      clientTel: c.phone||"", clientEmail: c.email||"",
      instAddr1: c.addr||"", instPostcode: c.postcode||"",
    }));
    setShowContacts(false);
  }

  function toggleAppliance(a) {
    setSel(prev => prev.includes(a) ? prev.filter(x=>x!==a) : [...prev, a]);
  }

  function startFaults() {
    const fd = selectedAppliances.map(a => ({ appliance:a, category:null, result:null }));
    setFaultData(fd); setIdx(0); setQIdx(0); setPhase("faults");
  }

  function selectFault(f) {
    setFaultData(prev => { const n=[...prev]; n[idx]={...n[idx],category:f}; return n; });
    setQIdx(0); setPhase("questions");
  }

  function answer(val) {
    const questions = psaGetQuestions(faultData[idx].category);
    const q = questions[qIdx];
    const resultKey = val ? q.yes : q.no;
    if (resultKey) {
      setFaultData(prev => { const n=[...prev]; n[idx]={...n[idx],result:resultKey}; return n; });
      if (idx < faultData.length - 1) { setIdx(i=>i+1); setQIdx(0); setPhase("faults"); }
      else setPhase("results");
    } else {
      setQIdx(i=>i+1);
    }
  }

  function resultColor(r) { return r==="ID" ? RED : r==="AR" ? ORANGE : "#1d7a4a"; }
  function resultLabel(r) { return r==="ID" ? "IMMEDIATELY DANGEROUS" : r==="AR" ? "AT RISK" : "NOT CURRENTLY AT RISK"; }
  function resultIcon(r)  { return r==="ID" ? "🚨" : r==="AR" ? "⚠️" : "✅"; }

  function handleCreateWN() {
    // Build pre-filled WN data from the assessment
    const dangerItems = faultData.filter(f => f.result === "ID" || f.result === "AR");
    const firstDanger = dangerItems[0] || faultData[0];
    const remedialText = faultData.map(f => `${f.appliance} (${f.category}): ${resultLabel(f.result)}`).join(". ");
    const wnData = {
      certRef:       details.fileRef || "",
      clientName:    details.clientName,
      clientAddr1:   details.clientAddr1,
      clientAddr2:   details.clientAddr2,
      clientAddr3:   details.clientAddr3,
      clientPostcode:details.clientPostcode,
      clientTel:     details.clientTel,
      clientEmail:   details.clientEmail,
      instAddr1:     details.instAddr1 || details.clientAddr1,
      instAddr2:     details.instAddr2 || details.clientAddr2,
      instAddr3:     details.instAddr3 || details.clientAddr3,
      instPostcode:  details.instPostcode || details.clientPostcode,
      instTel:       details.clientTel,
      make:          "", model:"", type: firstDanger?.appliance || "",
      serialNo:"", locationRoom:"",
      idGasEscape:   faultData.some(f=>f.category==="Gas Escape"&&f.result==="ID") ? "YES" : "NO",
      idDisconnected:faultData.some(f=>f.result==="ID") ? "YES" : "NA",
      idRefused:     "NO",
      gasEmergencyRef:"",
      arReason:      dangerItems.map(f=>`${f.appliance}: ${f.category}`).join(", "),
      arTurnedOff:   faultData.some(f=>f.result==="ID") ? "YES" : "NO",
      arRefused:"NO", arTurningOffNoHelp:"NO",
      contactName:   details.clientName,
      contactTel:    details.clientTel,
      riddor:"NO",
      remedialAction: remedialText,
      issueDate: new Date().toISOString().slice(0,10),
      issueTime: new Date().toLocaleTimeString("en-GB",{hour:"2-digit",minute:"2-digit"}),
    };
    if (onCreateWN) onCreateWN(wnData);
  }

  // ── PHASE: details ──
  if (phase === "details") return (
    <div style={{ display:"flex", flexDirection:"column", height:"100dvh", background:LIGHT_BG, fontFamily:"'Segoe UI',sans-serif" }}>
      <Header title="Property Safety Assessment" onBack={onBack} onHome={onHome}/>
      <div style={{ flex:1, overflowY:"auto", padding:"0 16px 88px" }}>
        <div style={{ fontSize:12, color:"#999", textAlign:"center", marginTop:10, marginBottom:4 }}>Please enter a file reference</div>
        <input value={details.fileRef} onChange={e=>setDetails(d=>({...d,fileRef:e.target.value}))} placeholder="File Reference" style={{ ...inp, border:"2px solid #ccc", display:"block", margin:"0 auto 4px", width:"calc(100% - 4px)" }}/>

        {/* Client Details */}
        <div style={{ background:DARK, color:"#fff", padding:"12px 16px", borderRadius:10, fontWeight:700, fontSize:14, marginTop:20, marginBottom:12, display:"flex", justifyContent:"space-between", alignItems:"center" }}>
          <span>Client Details</span>
          <button onClick={()=>setShowContacts(v=>!v)} style={{ background:"rgba(255,255,255,0.15)", border:"1px solid rgba(255,255,255,0.3)", borderRadius:8, color:"#fff", fontSize:12, fontWeight:600, padding:"4px 12px", cursor:"pointer" }}>
            {showContacts ? "Close" : "Contacts"}
          </button>
        </div>
        {showContacts && (
          <div style={{ background:"#fff", borderRadius:10, border:"1px solid #e0e0e0", marginBottom:12, maxHeight:200, overflowY:"auto" }}>
            {contacts.length === 0
              ? <div style={{ padding:16, color:"#aaa", fontSize:14, textAlign:"center" }}>No contacts saved yet</div>
              : contacts.map((c,i) => (
                  <div key={i} onClick={()=>fillFromContact(c)}
                    style={{ padding:"10px 14px", borderBottom:"1px solid #f0f0f0", cursor:"pointer", fontSize:14 }}>
                    <div style={{ fontWeight:600 }}>{c.name}</div>
                    <div style={{ color:"#888", fontSize:12 }}>{c.addr} {c.postcode}</div>
                  </div>
                ))
            }
          </div>
        )}
        {[["Name","clientName","e.g. Margaret Henderson"],["Address line 1","clientAddr1","e.g. 42 Calder Road"],["Address line 2","clientAddr2","e.g. Livingston"],["Address line 3","clientAddr3","e.g. West Lothian"],["Postcode","clientPostcode","e.g. EH54 9AB"],["Telephone","clientTel","e.g. 07712 334455"],["Email","clientEmail","e.g. client@email.co.uk"]].map(([label,key,ph])=>(
          <div key={key} style={{ marginBottom:10 }}>
            <div style={{ fontSize:12, fontWeight:600, color:"#666", marginBottom:3 }}>{label}</div>
            <input value={details[key]} onChange={e=>setDetails(d=>({...d,[key]:e.target.value}))} placeholder={ph} style={inp}/>
          </div>
        ))}

        {/* Installation Address */}
        <div style={{ background:DARK, color:"#fff", padding:"12px 16px", borderRadius:10, fontWeight:700, fontSize:14, marginTop:20, marginBottom:12, display:"flex", justifyContent:"space-between", alignItems:"center" }}>
          <span>Installation Address</span>
          <button onClick={()=>setDetails(d=>({...d, instAddr1:d.clientAddr1, instAddr2:d.clientAddr2, instAddr3:d.clientAddr3, instPostcode:d.clientPostcode }))}
            style={{ background:"rgba(255,255,255,0.15)", border:"1px solid rgba(255,255,255,0.3)", borderRadius:8, color:"#fff", fontSize:12, fontWeight:600, padding:"4px 12px", cursor:"pointer" }}>
            Copy
          </button>
        </div>
        {[["Address line 1","instAddr1","e.g. 42 Calder Road"],["Address line 2","instAddr2","e.g. Livingston"],["Address line 3","instAddr3","e.g. West Lothian"],["Postcode","instPostcode","e.g. EH54 9AB"]].map(([label,key,ph])=>(
          <div key={key} style={{ marginBottom:10 }}>
            <div style={{ fontSize:12, fontWeight:600, color:"#666", marginBottom:3 }}>{label}</div>
            <input value={details[key]} onChange={e=>setDetails(d=>({...d,[key]:e.target.value}))} placeholder={ph} style={inp}/>
          </div>
        ))}

        <button onClick={()=>setPhase("appliances")} style={{ width:"100%", padding:"15px", background:DARK, color:YELLOW, border:"none", borderRadius:14, fontWeight:800, fontSize:16, cursor:"pointer", marginTop:20 }}>
          Next →
        </button>
      </div>
    </div>
  );

  // ── PHASE: appliances ──
  if (phase === "appliances") return (
    <div style={{ display:"flex", flexDirection:"column", height:"100dvh", background:LIGHT_BG, fontFamily:"'Segoe UI',sans-serif" }}>
      <Header title="Property Gas Appliances" onBack={()=>setPhase("details")} onHome={onHome}/>
      <div style={{ flex:1, overflowY:"auto", padding:"16px 16px 88px" }}>
        <div style={{ fontSize:14, color:"#666", marginBottom:16 }}>Select all appliances present at the property:</div>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12, marginBottom:24 }}>
          {PSA_APPLIANCE_OPTIONS.map(a => {
            const sel = selectedAppliances.includes(a);
            return (
              <div key={a} onClick={()=>toggleAppliance(a)}
                style={{ background: sel ? "#e8f5e9" : "#fff", border:`2px solid ${sel?"#1d7a4a":"#e0e0e0"}`, borderRadius:14, padding:"16px 12px", cursor:"pointer", position:"relative", fontSize:14, fontWeight:600, color:"#222", textAlign:"center", boxShadow:"0 2px 6px rgba(0,0,0,0.06)" }}>
                {sel && <div style={{ width:10, height:10, background:"#1d7a4a", borderRadius:"50%", position:"absolute", top:8, left:8 }}/>}
                {a}
              </div>
            );
          })}
        </div>
        {selectedAppliances.length > 0 && (
          <button onClick={startFaults} style={{ width:"100%", padding:"15px", background:DARK, color:YELLOW, border:"none", borderRadius:14, fontWeight:800, fontSize:16, cursor:"pointer" }}>
            Continue ({selectedAppliances.length} appliance{selectedAppliances.length!==1?"s":""})
          </button>
        )}
      </div>
    </div>
  );

  // ── PHASE: faults ──
  if (phase === "faults") {
    const current = faultData[idx];
    return (
      <div style={{ display:"flex", flexDirection:"column", height:"100dvh", background:LIGHT_BG, fontFamily:"'Segoe UI',sans-serif" }}>
        <Header title={current.appliance} onBack={()=>{ if(idx>0){setIdx(i=>i-1);setPhase("faults");}else setPhase("appliances"); }} onHome={onHome}/>
        <div style={{ flex:1, overflowY:"auto", padding:"16px 16px 88px" }}>
          <div style={{ fontSize:13, color:"#999", marginBottom:4 }}>Appliance {idx+1} of {faultData.length}</div>
          <div style={{ fontSize:15, fontWeight:700, color:"#222", marginBottom:16 }}>Select the fault category:</div>
          {PSA_FAULT_CATEGORIES.map(f => {
            const sel = current.category === f;
            return (
              <div key={f} onClick={()=>selectFault(f)}
                style={{ display:"flex", alignItems:"center", gap:12, background: sel ? "#e8f5e9" : "#fff", border:`2px solid ${sel?"#1d7a4a":"#e0e0e0"}`, borderRadius:14, padding:"14px 16px", cursor:"pointer", marginBottom:10, position:"relative", boxShadow:"0 2px 6px rgba(0,0,0,0.05)" }}>
                {sel && <div style={{ width:10, height:10, background:"#1d7a4a", borderRadius:"50%", flexShrink:0 }}/>}
                <span style={{ fontSize:14, fontWeight:600 }}>{f}</span>
                <svg style={{ marginLeft:"auto" }} width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M4 2.5L9.5 7L4 11.5" stroke="#bbb" strokeWidth="2" strokeLinecap="round"/></svg>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // ── PHASE: questions ──
  if (phase === "questions") {
    const current  = faultData[idx];
    const questions = psaGetQuestions(current.category);
    const q        = questions[qIdx];
    return (
      <div style={{ display:"flex", flexDirection:"column", height:"100dvh", background:LIGHT_BG, fontFamily:"'Segoe UI',sans-serif" }}>
        <Header title="Assessment" onBack={()=>setPhase("faults")} onHome={onHome}/>
        <div style={{ flex:1, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", padding:"24px 20px", textAlign:"center" }}>
          <div style={{ fontSize:13, color:"#999", marginBottom:8 }}>{current.appliance} — {current.category}</div>
          <div style={{ fontSize:11, color:"#bbb", marginBottom:20 }}>Question {qIdx+1} of {questions.length}</div>
          <div style={{ fontSize:20, fontWeight:700, color:"#222", lineHeight:1.5, marginBottom:36, maxWidth:340 }}>{q.q}</div>
          <div style={{ display:"flex", gap:16, width:"100%", maxWidth:320 }}>
            <button onClick={()=>answer(true)}  style={{ flex:1, padding:"16px", background:RED,  color:"#fff", border:"none", borderRadius:14, fontWeight:800, fontSize:18, cursor:"pointer" }}>YES</button>
            <button onClick={()=>answer(false)} style={{ flex:1, padding:"16px", background:DARK, color:YELLOW, border:"none", borderRadius:14, fontWeight:800, fontSize:18, cursor:"pointer" }}>NO</button>
          </div>
        </div>
      </div>
    );
  }

  // ── PHASE: results ──
  if (phase === "results") {
    const hasID = faultData.some(f=>f.result==="ID");
    const hasAR = faultData.some(f=>f.result==="AR");
    return (
      <div style={{ display:"flex", flexDirection:"column", height:"100dvh", background:LIGHT_BG, fontFamily:"'Segoe UI',sans-serif" }}>
        <Header title="Assessment Results" onBack={()=>setPhase("faults")} onHome={onHome}/>
        <div style={{ flex:1, overflowY:"auto", padding:"16px 16px 100px" }}>
          {/* Summary banner */}
          <div style={{ background: hasID?RED:hasAR?ORANGE:"#1d7a4a", color:"#fff", borderRadius:14, padding:"16px 20px", marginBottom:20, textAlign:"center" }}>
            <div style={{ fontSize:32, marginBottom:6 }}>{hasID?"🚨":hasAR?"⚠️":"✅"}</div>
            <div style={{ fontWeight:800, fontSize:18 }}>{hasID?"Immediately Dangerous Found":hasAR?"At Risk Found":"No Hazards Found"}</div>
          </div>

          {/* Per-appliance results */}
          {faultData.map((f,i) => (
            <div key={i} style={{ background:"#fff", borderRadius:14, padding:"14px 16px", marginBottom:12, boxShadow:"0 2px 8px rgba(0,0,0,0.07)", display:"flex", alignItems:"center", gap:12 }}>
              <span style={{ fontSize:24 }}>{resultIcon(f.result)}</span>
              <div style={{ flex:1 }}>
                <div style={{ fontWeight:700, fontSize:15, color:"#222" }}>{f.appliance}</div>
                <div style={{ fontSize:13, color:"#888" }}>{f.category}</div>
              </div>
              <div style={{ fontWeight:800, fontSize:13, color:resultColor(f.result), textAlign:"right" }}>{resultLabel(f.result)}</div>
            </div>
          ))}

          {/* Required actions */}
          {(hasID || hasAR) && (
            <div style={{ background:"#fff", borderRadius:14, padding:"14px 16px", marginBottom:20, boxShadow:"0 2px 8px rgba(0,0,0,0.07)" }}>
              <div style={{ fontWeight:700, fontSize:15, marginBottom:10, color:"#222" }}>Required Actions:</div>
              {hasID && (
                <ul style={{ margin:0, paddingLeft:20, fontSize:14, color:"#333", lineHeight:2 }}>
                  <li>Disconnect appliance immediately</li>
                  <li>Isolate gas supply at the meter</li>
                  <li>Attach "Do Not Use" label</li>
                  <li>Advise customer not to reconnect until repaired</li>
                </ul>
              )}
              {hasAR && !hasID && (
                <ul style={{ margin:0, paddingLeft:20, fontSize:14, color:"#333", lineHeight:2 }}>
                  <li>Advise customer not to use appliance</li>
                  <li>Recommend repair by qualified engineer</li>
                </ul>
              )}
            </div>
          )}

          <button onClick={handleCreateWN}
            style={{ width:"100%", padding:"15px", background:DARK, color:YELLOW, border:"none", borderRadius:14, fontWeight:800, fontSize:16, cursor:"pointer", marginBottom:12 }}>
            Create Warning Notice →
          </button>
          <button onClick={()=>{ setSel([]); setFaultData([]); setIdx(0); setQIdx(0); setPhase("details"); }}
            style={{ width:"100%", padding:"13px", background:"#f0f0f0", color:"#555", border:"none", borderRadius:14, fontWeight:600, fontSize:14, cursor:"pointer" }}>
            New Assessment
          </button>
        </div>
      </div>
    );
  }

  return null;
}
// ─────────────────────────────────────────────────────────────────────────────

'''

# Find start and end of old component
start_line = None
end_line   = None
for i, l in enumerate(lines):
    if '// ─── Gas Safety Assessment (Decision Tree)' in l:
        start_line = i
    if start_line and i > start_line and '// ─────────────────────────────────' in l and end_line is None:
        end_line = i + 1   # inclusive of the separator line

if start_line is None or end_line is None:
    print(f"ERROR: start={start_line}, end={end_line}")
    sys.exit(1)

print(f"Replacing lines {start_line+1}–{end_line} ({end_line - start_line} lines)")

new_lines = lines[:start_line] + [NEW_COMPONENT] + lines[end_line:]
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Saved.")
