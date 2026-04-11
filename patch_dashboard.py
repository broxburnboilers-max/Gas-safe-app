import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

path = r'C:\Users\Andrew\Documents\gas-safety-multiuser\src\App.jsx'
with open(path, encoding='utf-8') as f:
    src = f.read()

changes = 0

# 1. HomeScreen signature
OLD1 = 'function HomeScreen({ onNew, onRecords, onGscEmail, onBsEmail, onReport, onLogout, currentUser, onProfile, onPayment, onClientDetails }) {'
NEW1 = 'function HomeScreen({ onNew, onRecords, onGscEmail, onBsEmail, onReport, onLogout, currentUser, onProfile, onPayment, onClientDetails, onDemo, onResetOnboarding, onAssessment, accountReports, yearlyReports, records, invoices, quotes }) {'
if OLD1 in src:
    src = src.replace(OLD1, NEW1, 1); print("OK 1: HomeScreen signature")
    changes += 1
else:
    print("WARN 1: signature not matched")

# 2. JSX call in App - add missing props
OLD2 = 'onClientDetails={()=>setScreen("contacts")}/>;'
NEW2 = 'onClientDetails={()=>setScreen("contacts")} onDemo={()=>{ const n=seedDemoData(setRecords); alert("✅ "+n+" demo records added!\\n\\nGo to Records → Demo Certificates to view them."); }} onResetOnboarding={()=>advanceOnboarding("payment")} onAssessment={()=>setScreen("safetyAssessment")} accountReports={accountReports} yearlyReports={yearlyReports} records={records} invoices={invoices} quotes={quotes}/>;'
if OLD2 in src:
    src = src.replace(OLD2, NEW2, 1); print("OK 2: JSX props")
    changes += 1
else:
    print("WARN 2: JSX call not matched")

# 3. Desktop CSS in useEffect
OLD3 = '    s.textContent = "@keyframes wlgContactsPulse{0%{box-shadow:0 0 0 0 rgba(211,47,47,0.8);}60%{box-shadow:0 0 0 18px rgba(211,47,47,0);}100%{box-shadow:0 0 0 0 rgba(211,47,47,0);}} .wlg-contacts-pulse{animation:wlgContactsPulse 1.1s ease-in-out infinite;}";\n    document.head.appendChild(s);\n  }, []);'
NEW3 = '    s.textContent = "@keyframes wlgContactsPulse{0%{box-shadow:0 0 0 0 rgba(211,47,47,0.8);}60%{box-shadow:0 0 0 18px rgba(211,47,47,0);}100%{box-shadow:0 0 0 0 rgba(211,47,47,0);}} .wlg-contacts-pulse{animation:wlgContactsPulse 1.1s ease-in-out infinite;}";\n    document.head.appendChild(s);\n    if (!document.getElementById("wlg-desktop-widgets-style")) {\n      const d = document.createElement("style");\n      d.id = "wlg-desktop-widgets-style";\n      d.textContent = "@media(min-width:700px){.wlg-dashboard-widgets{max-width:100%!important;}}";\n      document.head.appendChild(d);\n    }\n  }, []);'
if OLD3 in src:
    src = src.replace(OLD3, NEW3, 1); print("OK 3: Desktop CSS")
    changes += 1
else:
    print("WARN 3: useEffect not matched")

# 4. Insert widgets before button list
OLD4 = '      {/* Button list */}\n      <div style={{ flex:1, overflowY:"auto", padding:"8px 20px 88px", display:"flex", flexDirection:"column", alignItems:"center", gap:12 }}>'
NEW4 = '''      {/* ── Stat Cards ─────────────────────────────────────────────── */}
      {(() => {
        const now=new Date(), tm=now.getMonth(), ty=now.getFullYear();
        const lm=tm===0?11:tm-1, ly=tm===0?ty-1:ty;
        const isT=d=>{try{const x=new Date(d);return x.getMonth()===tm&&x.getFullYear()===ty;}catch{return false;}};
        const isL=d=>{try{const x=new Date(d);return x.getMonth()===lm&&x.getFullYear()===ly;}catch{return false;}};
        const aR=(records||[]).filter(r=>!r.isDemo),aI=(invoices||[]).filter(r=>!r.isDemo),aQ=(quotes||[]).filter(r=>!r.isDemo);
        const rT=aR.filter(r=>isT(r.savedAt)).length,rL=aR.filter(r=>isL(r.savedAt)).length;
        const iT=aI.filter(r=>isT(r.createdAt)).length,iL=aI.filter(r=>isL(r.createdAt)).length;
        const qT=aQ.filter(r=>isT(r.createdAt)).length,qL=aQ.filter(r=>isL(r.createdAt)).length;
        const pct=(c,p)=>p===0?(c>0?100:0):Math.round(((c-p)/p)*100);
        const Card=({label,count,prev})=>{const ch=pct(count,prev),up=ch>0,nl=ch===0;return(
          <div style={{flex:1,background:"rgba(255,255,255,0.10)",borderRadius:14,padding:"10px 10px 8px",backdropFilter:"blur(4px)",minWidth:0}}>
            <div style={{color:"rgba(255,255,255,0.55)",fontSize:9,fontWeight:700,textTransform:"uppercase",letterSpacing:0.6,marginBottom:6,lineHeight:1.3}}>{label}</div>
            <div style={{display:"flex",alignItems:"center",gap:5,marginBottom:4}}>
              <span style={{color:nl?"#fff200":up?"#4ade80":"#f87171",fontSize:12}}>{nl?"→":up?"↑":"↓"}</span>
              <span style={{color:"#fff",fontWeight:800,fontSize:22,lineHeight:1}}>{count}</span>
            </div>
            <div style={{color:nl?"rgba(255,255,255,0.45)":up?"#4ade80":"#f87171",fontSize:9,fontWeight:600}}>{ch===0?"0% from last month":`${Math.abs(ch)}% ${up?"▲":"▼"} last month`}</div>
          </div>);};
        return(<div className="wlg-dashboard-widgets" style={{width:"100%",maxWidth:440,display:"flex",gap:8,marginBottom:8}}>
          <Card label="Reports Created" count={rT} prev={rL}/>
          <Card label="Invoices Created" count={iT} prev={iL}/>
          <Card label="Quotes Created" count={qT} prev={qL}/>
        </div>);
      })()}

      {/* ── Monthly + Turnover ──────────────────────────────────────── */}
      {(() => {
        const yr=(yearlyReports||[]).find(r=>r.year===new Date().getFullYear())||(yearlyReports||[])[0];
        const months=[...(accountReports||[])].sort((a,b)=>new Date(a.createdAt||0)-new Date(b.createdAt||0)).slice(-6);
        const maxVal=months.reduce((m,r)=>Math.max(m,parseFloat(r.totalIncome||0),parseFloat(r.totalExpenses||0)),1);
        const barH=70;
        const ml=r=>{try{return new Date(r.createdAt).toLocaleString("en-GB",{month:"short"});}catch{return "";}};
        return(<div className="wlg-dashboard-widgets" style={{width:"100%",maxWidth:440,display:"flex",gap:10,marginBottom:4,marginTop:4}}>
          <div style={{flex:1.2,background:"rgba(255,255,255,0.10)",borderRadius:16,padding:"10px 10px 8px",backdropFilter:"blur(4px)"}}>
            <div style={{color:"rgba(255,255,255,0.6)",fontSize:10,fontWeight:700,textTransform:"uppercase",letterSpacing:0.5,marginBottom:8}}>Monthly Overview</div>
            {months.length===0
              ?<div style={{color:"rgba(255,255,255,0.35)",fontSize:11,textAlign:"center",padding:"12px 4px",lineHeight:1.6}}>No reports yet.<br/>Import bank statements<br/>to see your chart.</div>
              :(<div style={{display:"flex",alignItems:"flex-end",gap:4,height:barH+20}}>
                {months.map((r,i)=>{const inc=parseFloat(r.totalIncome||0),exp=parseFloat(r.totalExpenses||0),iH=Math.round((inc/maxVal)*barH),eH=Math.round((exp/maxVal)*barH);return(
                  <div key={i} style={{flex:1,display:"flex",flexDirection:"column",alignItems:"center",gap:1}}>
                    <div style={{display:"flex",alignItems:"flex-end",gap:1,height:barH}}>
                      <div style={{width:7,height:iH||2,background:"#4ade80",borderRadius:"2px 2px 0 0"}}/>
                      <div style={{width:7,height:eH||2,background:"#f87171",borderRadius:"2px 2px 0 0"}}/>
                    </div>
                    <div style={{fontSize:8,color:"rgba(255,255,255,0.5)",marginTop:2,textAlign:"center"}}>{ml(r)}</div>
                  </div>);})}
              </div>)}
            <div style={{display:"flex",gap:8,marginTop:4}}>
              <div style={{display:"flex",alignItems:"center",gap:3}}><div style={{width:8,height:8,background:"#4ade80",borderRadius:2}}/><span style={{fontSize:9,color:"rgba(255,255,255,0.55)"}}>Income</span></div>
              <div style={{display:"flex",alignItems:"center",gap:3}}><div style={{width:8,height:8,background:"#f87171",borderRadius:2}}/><span style={{fontSize:9,color:"rgba(255,255,255,0.55)"}}>Expenses</span></div>
            </div>
          </div>
          <div style={{flex:1,background:"rgba(255,255,255,0.10)",borderRadius:16,padding:"10px 12px",backdropFilter:"blur(4px)",display:"flex",flexDirection:"column"}}>
            <div style={{color:"rgba(255,255,255,0.6)",fontSize:10,fontWeight:700,textTransform:"uppercase",letterSpacing:0.5,marginBottom:8}}>Annual Turnover</div>
            {!yr
              ?<div style={{color:"rgba(255,255,255,0.35)",fontSize:11,textAlign:"center",flex:1,display:"flex",alignItems:"center",justifyContent:"center",lineHeight:1.6}}>No yearly report yet.<br/>Import bank statements<br/>to see your company turnover.</div>
              :(()=>{const inc=parseFloat(yr.totalIncome||0),exp=parseFloat(yr.totalExpenses||0),bal=inc-exp;return(
                <div style={{display:"flex",flexDirection:"column",gap:6}}>
                  <div><div style={{color:"rgba(255,255,255,0.5)",fontSize:9,textTransform:"uppercase",letterSpacing:0.3}}>Total Income</div><div style={{color:"#4ade80",fontWeight:800,fontSize:15}}>£{inc.toLocaleString("en-GB",{minimumFractionDigits:2,maximumFractionDigits:2})}</div></div>
                  <div><div style={{color:"rgba(255,255,255,0.5)",fontSize:9,textTransform:"uppercase",letterSpacing:0.3}}>Total Expenses</div><div style={{color:"#f87171",fontWeight:800,fontSize:15}}>£{exp.toLocaleString("en-GB",{minimumFractionDigits:2,maximumFractionDigits:2})}</div></div>
                  <div style={{borderTop:"1px solid rgba(255,255,255,0.15)",paddingTop:6}}><div style={{color:"rgba(255,255,255,0.5)",fontSize:9,textTransform:"uppercase",letterSpacing:0.3}}>Bank Balance</div><div style={{color:bal>=0?"#fff200":"#f87171",fontWeight:800,fontSize:15}}>£{bal.toLocaleString("en-GB",{minimumFractionDigits:2,maximumFractionDigits:2})}</div></div>
                </div>);})()} 
          </div>
        </div>);
      })()}

      {/* Button list */}
      <div style={{ flex:1, overflowY:"auto", padding:"8px 20px 88px", display:"flex", flexDirection:"column", alignItems:"center", gap:12 }}>'''

if OLD4 in src:
    src = src.replace(OLD4, NEW4, 1); print("OK 4: Widgets inserted")
    changes += 1
else:
    print("WARN 4: Button list anchor not found")

print(f"\nTotal changes applied: {changes}/4")
with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
print("Saved.")
