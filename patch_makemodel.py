import sys, re
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

path = r'C:\Users\Andrew\Documents\gas-safety-multiuser\src\App.jsx'
with open(path, encoding='utf-8') as f:
    src = f.read()

changes = 0

# ── 1. GSC Appliance Details screen (centred form) → row style ────────────────
OLD1 = '''          <MakeModelInput value={data.boilerMake||""} category="make" onChange={v=>onChange({...data,boilerMake:v,boilerModel:""})} placeholder="Boiler Make (e.g. ALPHA)" inputStyle={{ width:"100%", boxSizing:"border-box", padding:"14px", border:"1px solid #ddd", borderRadius:8, fontSize:15, outline:"none", marginBottom:10 }}/>
          <MakeModelInput value={data.boilerModel||""} category="model" makeValue={data.boilerMake||""} onChange={v=>onChange({...data,boilerModel:v})} placeholder="Boiler Model (e.g. 100/2 HE)" inputStyle={{ width:"100%", boxSizing:"border-box", padding:"14px", border:"1px solid #ddd", borderRadius:8, fontSize:15, outline:"none", marginBottom:10 }}/>'''
NEW1 = '''          <MakeModelInput value={data.boilerMake||""} category="make" label="Boiler Make" onChange={v=>onChange({...data,boilerMake:v,boilerModel:""})} rowStyle={{ borderRadius:8, marginBottom:6, border:"1px solid #ddd" }}/>
          <MakeModelInput value={data.boilerModel||""} category="model" label="Boiler Model" makeValue={data.boilerMake||""} onChange={v=>onChange({...data,boilerModel:v})} rowStyle={{ borderRadius:8, marginBottom:6, border:"1px solid #ddd" }}/>'''
if OLD1 in src:
    src = src.replace(OLD1, NEW1, 1); print("OK 1: GSC Appliance Details row style"); changes+=1
else: print("WARN 1: GSC Appliance Details not found")

# ── 2. BS form inline rows — replace div+span wrapper with MakeModelInput row ─
OLD2 = '''        <div style={{ display:"flex", alignItems:"center", padding:"8px 16px", borderBottom:"1px solid #e8eaf0", background:"#fff", gap:12 }}><span style={{ width:160, fontSize:14, color:"#555", fontFamily:"'Segoe UI',sans-serif", flexShrink:0 }}>Boiler Make :</span><MakeModelInput value={data.boilerMake||""} category="make" onChange={v=>onChange({...data,boilerMake:v,boilerModel:""})} inputStyle={{ flex:1, padding:"8px 10px", border:"1px solid #ddd", borderRadius:4, fontSize:14, fontFamily:"'Segoe UI',sans-serif", outline:"none", background:"#f9f9f9" }}/></div>
        <div style={{ display:"flex", alignItems:"center", padding:"8px 16px", borderBottom:"1px solid #e8eaf0", background:"#fff", gap:12 }}><span style={{ width:160, fontSize:14, color:"#555", fontFamily:"'Segoe UI',sans-serif", flexShrink:0 }}>Boiler Model :</span><MakeModelInput value={data.boilerModel||""} category="model" makeValue={data.boilerMake||""} onChange={v=>onChange({...data,boilerModel:v})} inputStyle={{ flex:1, padding:"8px 10px", border:"1px solid #ddd", borderRadius:4, fontSize:14, fontFamily:"'Segoe UI',sans-serif", outline:"none", background:"#f9f9f9" }}/></div>'''
NEW2 = '''        <MakeModelInput value={data.boilerMake||""} category="make" label="Boiler Make" onChange={v=>onChange({...data,boilerMake:v,boilerModel:""})}/>
        <MakeModelInput value={data.boilerModel||""} category="model" label="Boiler Model" makeValue={data.boilerMake||""} onChange={v=>onChange({...data,boilerModel:v})}/>'''
if OLD2 in src:
    src = src.replace(OLD2, NEW2, 1); print("OK 2: BS boiler make/model rows"); changes+=1
else: print("WARN 2: BS boiler make/model not found")

OLD3 = '''        <div style={{ display:"flex", alignItems:"center", padding:"8px 16px", borderBottom:"1px solid #e8eaf0", background:"#fff", gap:12 }}><span style={{ width:160, fontSize:14, color:"#555", fontFamily:"'Segoe UI',sans-serif", flexShrink:0 }}>Appliance Make :</span><MakeModelInput value={data.applianceMake||""} category="make" onChange={v=>onChange({...data,applianceMake:v,applianceModel:""})} inputStyle={{ flex:1, padding:"8px 10px", border:"1px solid #ddd", borderRadius:4, fontSize:14, fontFamily:"'Segoe UI',sans-serif", outline:"none", background:"#f9f9f9" }}/></div>
        <div style={{ display:"flex", alignItems:"center", padding:"8px 16px", borderBottom:"1px solid #e8eaf0", background:"#fff", gap:12 }}><span style={{ width:160, fontSize:14, color:"#555", fontFamily:"'Segoe UI',sans-serif", flexShrink:0 }}>Appliance Model :</span><MakeModelInput value={data.applianceModel||""} category="model" makeValue={data.applianceMake||""} onChange={v=>onChange({...data,applianceModel:v})} inputStyle={{ flex:1, padding:"8px 10px", border:"1px solid #ddd", borderRadius:4, fontSize:14, fontFamily:"'Segoe UI',sans-serif", outline:"none", background:"#f9f9f9" }}/></div>'''
NEW3 = '''        <MakeModelInput value={data.applianceMake||""} category="make" label="Appliance Make" onChange={v=>onChange({...data,applianceMake:v,applianceModel:""})}/>
        <MakeModelInput value={data.applianceModel||""} category="model" label="Appliance Model" makeValue={data.applianceMake||""} onChange={v=>onChange({...data,applianceModel:v})}/>'''
if OLD3 in src:
    src = src.replace(OLD3, NEW3, 1); print("OK 3: BS appliance make/model rows"); changes+=1
else: print("WARN 3: BS appliance make/model not found")

# ── 3. GSC/LPG/Leisure/Commercial appliance editor inline wraps → PickField row
OLD4 = '''        <div style={{ padding:"12px 16px", background:"#fff", borderBottom:"1px solid #eee" }}>
          <span style={{ fontSize:14, color:"#666" }}>Make:</span>
          <MakeModelInput
            value={a.make||""}
            category="make"
            onChange={v=>{ set("make",v); set("model",""); }}
            inputStyle={{ width:"100%", boxSizing:"border-box", padding:"8px 0", border:"none", borderBottom:"1px solid #eee", fontSize:14, fontFamily:"'Segoe UI',sans-serif", outline:"none", background:"transparent" }}
          />
        </div>
        <div style={{ padding:"12px 16px", background:"#fff", borderBottom:"1px solid #eee" }}>
          <span style={{ fontSize:14, color:"#666" }}>Model:</span>
          <MakeModelInput
            value={a.model||""}
            category="model"
            makeValue={a.make||""}
            onChange={v=>set("model",v)}
            inputStyle={{ width:"100%", boxSizing:"border-box", padding:"8px 0", border:"none", borderBottom:"1px solid #eee", fontSize:14, fontFamily:"'Segoe UI',sans-serif", outline:"none", background:"transparent" }}
          />
        </div>'''
NEW4 = '''        <MakeModelInput value={a.make||""} category="make" label="Make" onChange={v=>{ set("make",v); set("model",""); }}/>
        <MakeModelInput value={a.model||""} category="model" label="Model" makeValue={a.make||""} onChange={v=>set("model",v)}/>'''
if OLD4 in src:
    src = src.replace(OLD4, NEW4, 1); print("OK 4: Appliance editor make/model PickField style"); changes+=1
else: print("WARN 4: Appliance editor make/model not found")

# ── 4. WN standalone (already row, just ensure no inputStyle) ─────────────────
OLD5 = '''        <MakeModelInput value={data.make||""} category="make" onChange={v=>{ set("make",v); set("model",""); }}/>
        <MakeModelInput value={data.model||""} category="model" makeValue={data.make||""} onChange={v=>set("model",v)}/>'''
NEW5 = '''        <MakeModelInput value={data.make||""} category="make" label="Make" onChange={v=>{ set("make",v); set("model",""); }}/>
        <MakeModelInput value={data.model||""} category="model" label="Model" makeValue={data.make||""} onChange={v=>set("model",v)}/>'''
if OLD5 in src:
    src = src.replace(OLD5, NEW5, 1); print("OK 5: WN make/model labels added"); changes+=1
else: print("WARN 5: WN make/model not found")

# ── 5. GSC mmInp helper — update to use row mode (no inputStyle) ──────────────
OLD6 = '''    <MakeModelInput
      value={(apps[i]||{})[key]||""}
      category={key}
      makeValue={key==="model" ? (apps[i]||{}).make||"" : undefined}
      onChange={v=>update(i,key,v)}
      placeholder={key==="make" ? "e.g. Worcester Bosch" : "e.g. Greenstar 30i"}
      id={"wlg-mm-"+key+"-"+i}
      inputStyle={{ width:"100%", padding:"7px 8px", border:"1px solid #ddd", borderRadius:6, fontSize:12, boxSizing:"border-box" }}
    />'''
NEW6 = '''    <MakeModelInput
      value={(apps[i]||{})[key]||""}
      category={key}
      label={key==="make" ? "Make" : "Model"}
      makeValue={key==="model" ? (apps[i]||{}).make||"" : undefined}
      onChange={v=>{ update(i,key,v); if(key==="make") update(i,"model",""); }}
    />'''
count6 = src.count(OLD6)
src = src.replace(OLD6, NEW6)
print(f"OK 6: GSC mmInp helper updated ({count6} occurrences)"); changes+=count6

print(f"\nTotal changes: {changes}")
with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
print("Saved.")
