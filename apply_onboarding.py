import sys, re
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

path = r'C:\Users\Andrew\Documents\gas-safety-multiuser\src\App.jsx'
with open(path, encoding='utf-8') as f:
    src = f.read()

# ── EDIT 1: Mark new registrations with onboardingStep:"payment" ──────────────
# In AppWithAuth, when a new user saves their profile, mark them for onboarding
OLD1 = '''      const profileWithDate = { ...profile, registeredAt: new Date().toISOString() };
      try { localStorage.setItem(`${userEntry.username}_user_profile`, JSON.stringify(profileWithDate)); } catch {}
      // Auto-login
      setAuthed(true);'''
NEW1 = '''      const profileWithDate = { ...profile, registeredAt: new Date().toISOString(), onboardingStep: "payment" };
      try { localStorage.setItem(`${userEntry.username}_user_profile`, JSON.stringify(profileWithDate)); } catch {}
      // Auto-login
      setAuthed(true);'''
if OLD1 not in src:
    print("ERROR Edit 1: new user profile save"); sys.exit(1)
src = src.replace(OLD1, NEW1, 1)
print("OK Edit 1: new registrations get onboardingStep=payment")

# ── EDIT 2: Add onboarding helper functions ───────────────────────────────────
# Insert before function App(
OLD2 = 'function App({ onLogout }) {'
NEW2 = '''// ─── Onboarding helpers ──────────────────────────────────────────────────────
function getOnboardingStep() {
  try {
    const p = JSON.parse(localStorage.getItem(sk("user_profile")) || "{}");
    return p.onboardingStep || null; // null = fully onboarded
  } catch { return null; }
}
function setOnboardingStep(step) {
  try {
    const p = JSON.parse(localStorage.getItem(sk("user_profile")) || "{}");
    if (step === null) { delete p.onboardingStep; }
    else { p.onboardingStep = step; }
    localStorage.setItem(sk("user_profile"), JSON.stringify(p));
  } catch {}
}
function hasPaymentDetails() {
  try {
    const p = JSON.parse(localStorage.getItem(sk("user_profile")) || "{}");
    return !!(p.paymentAccountName || p.paymentSortCode || p.paymentAccountNumber);
  } catch { return false; }
}
function hasClientContacts() {
  try { return JSON.parse(localStorage.getItem(sk("client_contacts")) || "[]").length > 0; }
  catch { return false; }
}
// ─────────────────────────────────────────────────────────────────────────────

function App({ onLogout }) {'''
if OLD2 not in src:
    print("ERROR Edit 2: function App anchor"); sys.exit(1)
src = src.replace(OLD2, NEW2, 1)
print("OK Edit 2: onboarding helpers added")

# ── EDIT 3: Wire onboarding screens in App before home screen ────────────────
OLD3 = '''  if (screen === "home") return <HomeScreen onNew={()=>setScreen("newJob")} onRecords={()=>setScreen("records")} onGscEmail={()=>setScreen("gscEmail")} onBsEmail={()=>setScreen("bsEmail")} onReport={()=>setScreen("report")} onLogout={onLogout} currentUser={currentUser} onProfile={()=>setScreen("profileEdit")} onPayment={()=>setScreen("paymentDetails")} onClientDetails={()=>setScreen("contacts")} onDemo={()=>{ const n=seedDemoData(setRecords); alert("✅ "+n+" demo records added!\\n\\nGo to Records → Demo Certificates to view them."); }}/>;'''
NEW3 = '''  // ── Onboarding gate ────────────────────────────────────────────────────────
  if (screen === "home") {
    const _ob = getOnboardingStep();
    if (_ob === "payment") return <OnboardingPaymentScreen onDone={()=>{ setOnboardingStep("contacts"); setScreen("home"); }}/>;
    if (_ob === "contacts") return <OnboardingContactsScreen onDone={()=>{ setOnboardingStep("demo"); setScreen("home"); }}/>;
    if (_ob === "demo") return <OnboardingDemoScreen setRecords={setRecords} setInvoices={setInvoices} setQuotes={setQuotes} onDone={()=>{ setOnboardingStep(null); setScreen("home"); }}/>;
  }
  if (screen === "home") return <HomeScreen onNew={()=>setScreen("newJob")} onRecords={()=>setScreen("records")} onGscEmail={()=>setScreen("gscEmail")} onBsEmail={()=>setScreen("bsEmail")} onReport={()=>setScreen("report")} onLogout={onLogout} currentUser={currentUser} onProfile={()=>setScreen("profileEdit")} onPayment={()=>setScreen("paymentDetails")} onClientDetails={()=>setScreen("contacts")} onDemo={()=>{ const n=seedDemoData(setRecords); alert("✅ "+n+" demo records added!\\n\\nGo to Records → Demo Certificates to view them."); }}/>;'''
if OLD3 not in src:
    print("ERROR Edit 3: HomeScreen JSX call not found"); sys.exit(1)
src = src.replace(OLD3, NEW3, 1)
print("OK Edit 3: onboarding gate added")

# ── EDIT 4: Add three Onboarding screens before HomeScreen ──────────────────
ONBOARDING_SCREENS = r'''
// ─── Onboarding Screen 1: Payment Details ────────────────────────────────────
function OnboardingPaymentScreen({ onDone }) {
  const [saved, setSaved] = useState(false);
  return (
    <div style={{ minHeight:"100dvh", background:"linear-gradient(160deg,#03180d 0%,#0d4a26 60%,#03180d 100%)", display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", fontFamily:"'Segoe UI',sans-serif", padding:24 }}>
      <div style={{ width:"100%", maxWidth:400 }}>
        <div style={{ textAlign:"center", marginBottom:32 }}>
          <div style={{ fontSize:48, marginBottom:12 }}>👋</div>
          <div style={{ color:"#fff200", fontWeight:800, fontSize:24, marginBottom:8 }}>Welcome to West Lothian Gas</div>
          <div style={{ color:"rgba(255,255,255,0.8)", fontSize:15, lineHeight:1.6 }}>Let's get your account set up. First, add your payment details so they auto-populate on every invoice.</div>
        </div>
        <div style={{ background:"#fff", borderRadius:20, padding:24, boxShadow:"0 8px 32px rgba(0,0,0,0.3)" }}>
          <div style={{ fontWeight:700, fontSize:16, color:"#03180d", marginBottom:4 }}>💳 Step 1 of 3 — Payment Details</div>
          <div style={{ fontSize:13, color:"#888", marginBottom:20 }}>Your bank details for invoice notes</div>
          <PaymentDetailsInner onSaved={()=>setSaved(true)}/>
        </div>
        {saved && (
          <button onClick={onDone}
            style={{ marginTop:20, width:"100%", padding:"16px", background:"#fff200", color:"#03180d", border:"none", borderRadius:14, fontWeight:800, fontSize:17, cursor:"pointer", boxShadow:"0 4px 16px rgba(0,0,0,0.25)" }}>
            Continue →
          </button>
        )}
      </div>
    </div>
  );
}

// Extracted inner form so we can reuse in onboarding
function PaymentDetailsInner({ onSaved }) {
  const DEFAULT_MSG = "Includes your 1 year warranty, thank you for your business.";
  const load = () => { try { const p=JSON.parse(localStorage.getItem(sk("user_profile"))||"{}"); return { accountName:p.paymentAccountName||"", sortCode:p.paymentSortCode||"", accountNumber:p.paymentAccountNumber||"", personalMessage:p.paymentPersonalMessage||DEFAULT_MSG }; } catch { return {accountName:"",sortCode:"",accountNumber:"",personalMessage:DEFAULT_MSG}; } };
  const [form, setForm] = useState(load);
  const [error, setError] = useState("");
  const inp = { width:"100%", padding:"11px 12px", border:"1px solid #ddd", borderRadius:8, fontSize:14, boxSizing:"border-box", marginBottom:12, fontFamily:"'Segoe UI',sans-serif", outline:"none" };
  function save() {
    const sc=form.sortCode.replace(/[^0-9]/g,"");
    if (form.sortCode && sc.length!==6) { setError("Sort code must be 6 digits."); return; }
    const an=form.accountNumber.replace(/[^0-9]/g,"");
    if (form.accountNumber && an.length!==8) { setError("Account number must be 8 digits."); return; }
    try {
      const p=JSON.parse(localStorage.getItem(sk("user_profile"))||"{}");
      p.paymentAccountName=form.accountName; p.paymentSortCode=form.sortCode;
      p.paymentAccountNumber=form.accountNumber; p.paymentPersonalMessage=form.personalMessage;
      localStorage.setItem(sk("user_profile"),JSON.stringify(p));
      setError(""); if (onSaved) onSaved();
    } catch { setError("Failed to save."); }
  }
  return (
    <div>
      {[["Account Name","accountName","e.g. West Lothian Gas Ltd"],["Sort Code","sortCode","12-34-56"],["Account Number","accountNumber","12345678"]].map(([label,key,ph])=>(
        <div key={key}>
          <div style={{fontSize:12,fontWeight:600,color:"#555",marginBottom:3}}>{label}</div>
          <input value={form[key]} onChange={e=>setForm(f=>({...f,[key]:e.target.value}))} placeholder={ph} style={inp}/>
        </div>
      ))}
      <div style={{fontSize:12,fontWeight:600,color:"#555",marginBottom:3}}>Invoice Message</div>
      <textarea value={form.personalMessage} onChange={e=>setForm(f=>({...f,personalMessage:e.target.value}))} rows={2} style={{...inp,resize:"none"}}/>
      {error && <div style={{color:"#c00",fontSize:13,marginBottom:8}}>{error}</div>}
      <button onClick={save} style={{width:"100%",padding:"12px",background:"#03180d",color:"#fff200",border:"none",borderRadius:10,fontWeight:700,fontSize:15,cursor:"pointer"}}>
        Save Payment Details
      </button>
    </div>
  );
}

// ─── Onboarding Screen 2: Client Contacts ─────────────────────────────────────
function OnboardingContactsScreen({ onDone }) {
  const [count, setCount] = useState(() => { try { return JSON.parse(localStorage.getItem(sk("client_contacts"))||"[]").length; } catch { return 0; } });
  const refresh = () => { try { setCount(JSON.parse(localStorage.getItem(sk("client_contacts"))||"[]").length); } catch {} };
  return (
    <div style={{ minHeight:"100dvh", background:"linear-gradient(160deg,#03180d 0%,#0d4a26 60%,#03180d 100%)", display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", fontFamily:"'Segoe UI',sans-serif", padding:24 }}>
      <div style={{ width:"100%", maxWidth:400 }}>
        <div style={{ textAlign:"center", marginBottom:32 }}>
          <div style={{ fontSize:48, marginBottom:12 }}>👥</div>
          <div style={{ color:"#fff200", fontWeight:800, fontSize:24, marginBottom:8 }}>Add Your Clients</div>
          <div style={{ color:"rgba(255,255,255,0.8)", fontSize:15, lineHeight:1.6 }}>Import your client contacts so they auto-fill certificates. You can add more any time.</div>
        </div>
        <div style={{ background:"#fff", borderRadius:20, padding:24, boxShadow:"0 8px 32px rgba(0,0,0,0.3)" }}>
          <div style={{ fontWeight:700, fontSize:16, color:"#03180d", marginBottom:4 }}>Step 2 of 3 — Client Contacts</div>
          <div style={{ fontSize:13, color:"#888", marginBottom:20 }}>Add at least one client to continue</div>
          <ClientContactsInner onContactsChanged={refresh}/>
          {count > 0 && <div style={{marginTop:12,fontSize:13,color:"#1d7a4a",fontWeight:600}}>✅ {count} contact{count!==1?"s":""} saved</div>}
        </div>
        {count > 0 && (
          <button onClick={onDone} style={{ marginTop:20, width:"100%", padding:"16px", background:"#fff200", color:"#03180d", border:"none", borderRadius:14, fontWeight:800, fontSize:17, cursor:"pointer", boxShadow:"0 4px 16px rgba(0,0,0,0.25)" }}>
            Continue →
          </button>
        )}
        <button onClick={onDone} style={{ marginTop:10, width:"100%", padding:"12px", background:"transparent", color:"rgba(255,255,255,0.5)", border:"1px solid rgba(255,255,255,0.2)", borderRadius:14, fontWeight:600, fontSize:14, cursor:"pointer" }}>
          Skip for now
        </button>
      </div>
    </div>
  );
}

// Minimal inline contact adder for onboarding
function ClientContactsInner({ onContactsChanged }) {
  const [name, setName] = useState("");
  const [addr, setAddr] = useState("");
  const [postcode, setPostcode] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");
  const inp = { width:"100%", padding:"10px 12px", border:"1px solid #ddd", borderRadius:8, fontSize:14, boxSizing:"border-box", marginBottom:10, fontFamily:"'Segoe UI',sans-serif", outline:"none" };
  function addContact() {
    if (!name.trim()) { setMsg("Name is required"); return; }
    try {
      const contacts = JSON.parse(localStorage.getItem(sk("client_contacts"))||"[]");
      contacts.push({ id:Date.now().toString(), name:name.trim(), addr1:addr.trim(), postcode:postcode.trim(), phone:phone.trim(), email:email.trim() });
      localStorage.setItem(sk("client_contacts"), JSON.stringify(contacts));
      setName(""); setAddr(""); setPostcode(""); setPhone(""); setEmail("");
      setMsg("✅ Contact added!");
      if (onContactsChanged) onContactsChanged();
    } catch { setMsg("Failed to save."); }
  }
  return (
    <div>
      {[["Client Name *","text",name,setName,"e.g. Margaret Henderson"],["Address","text",addr,setAddr,"e.g. 42 Calder Road, Livingston"],["Postcode","text",postcode,setPostcode,"e.g. EH54 9AB"],["Phone","tel",phone,setPhone,"e.g. 07712 334455"],["Email","email",email,setEmail,"e.g. client@email.co.uk"]].map(([label,type,val,set,ph])=>(
        <div key={label}>
          <div style={{fontSize:12,fontWeight:600,color:"#555",marginBottom:3}}>{label}</div>
          <input type={type} value={val} onChange={e=>set(e.target.value)} placeholder={ph} style={inp}/>
        </div>
      ))}
      {msg && <div style={{fontSize:13,color:msg.startsWith("✅")?"#1d7a4a":"#c00",marginBottom:8}}>{msg}</div>}
      <button onClick={addContact} style={{width:"100%",padding:"11px",background:"#03180d",color:"#fff200",border:"none",borderRadius:10,fontWeight:700,fontSize:14,cursor:"pointer"}}>
        + Add Contact
      </button>
    </div>
  );
}

// ─── Onboarding Screen 3: Demo Walkthrough ────────────────────────────────────
const DEMO_CERT_STEPS = [
  { id:"gsc",               label:"Gas Safety Certificate",             icon:"🛡️" },
  { id:"gsc_wn_combined",   label:"GSC + Warning Notice Combined",      icon:"⚠️" },
  { id:"bs",                label:"Boiler Service Record",              icon:"🔩" },
  { id:"wn",                label:"Warning Notice",                     icon:"🚨" },
  { id:"lpg_gsc",           label:"LPG Gas Safety Record",              icon:"🔶" },
  { id:"leisure_gsc",       label:"Leisure Industry Gas Safety Record", icon:"🏗️" },
  { id:"commercial_gsc",    label:"Commercial Gas Safety Certificate",  icon:"🏛️" },
  { id:"benchmark",         label:"Benchmark Commissioning Checklist",  icon:"📋" },
  { id:"cooling_off",       label:"7 Day Cooling Off Exemption",        icon:"📅" },
  { id:"gas_install_report",label:"Gas Installation Safety Report",     icon:"📐" },
  { id:"catering_inspection",label:"Commercial Catering Inspection",    icon:"🍴" },
  { id:"gas_test_purge",    label:"Gas Testing & Purging Record",       icon:"⚗️" },
  { id:"invoice",           label:"Invoice",                            icon:"💼" },
  { id:"quote",             label:"Quote",                              icon:"📄" },
];

function OnboardingDemoScreen({ setRecords, setInvoices, setQuotes, onDone }) {
  const [currentStep, setCurrentStep] = useState(-1); // -1 = intro
  const [done, setDone] = useState(false);
  const [running, setRunning] = useState(false);

  async function runWalkthrough() {
    setRunning(true);
    const delay = ms => new Promise(r => setTimeout(r, ms));

    const TODAY = new Date();
    const fmt = d => d.toISOString().slice(0, 10);
    const addDays = (d, n) => { const r = new Date(d); r.setDate(r.getDate() + n); return r; };
    const ENG = { engineerName:"James Taylor", companyName:"West Lothian Gas Services", companyAddr:"14 Brucefield Avenue", companyAddr2:"Livingston", companyPostcode:"EH54 6BY", companyTel:"01506 448821", companyEmail:"info@westlothiangas.co.uk", gasSafeNo:"123456", gasId:"ENG-7891", certDate:fmt(TODAY), issueDate:fmt(TODAY), issueTime:"10:30 AM" };
    const APP1 = { location:"Kitchen", type:"Cooker", make:"Hotpoint", model:"HD5V92KCW", co2:"8.9", co:"12", combustion:"0.001", flueType:"N/A", landlordsAppliance:"Yes", applianceInspected:"Yes", operatingPressure:"20", heatInput:"12.5", spillageTest:"N/A", flueFlow:"N/A", ventilation:"Yes", flueVisual:"N/A", fluePerformance:"N/A", applianceServiced:"Yes", applianceSafe:"Yes", safetyDevices:"Yes" };
    const APP2 = { location:"Airing Cupboard", type:"Combi", make:"Worcester", model:"Greenstar 30i", co2:"9.1", co:"8", combustion:"0.001", flueType:"RS", landlordsAppliance:"Yes", applianceInspected:"Yes", operatingPressure:"20", heatInput:"30", spillageTest:"Pass", flueFlow:"Pass", ventilation:"Yes", flueVisual:"Yes", fluePerformance:"Pass", applianceServiced:"Yes", applianceSafe:"Yes", safetyDevices:"Yes" };
    const FAULT1 = { details:"Gas smell near cooker — flexible hose showing signs of wear.", remedial:"Flexible hose replaced and tested.", warningNotice:"Yes" };
    const FAULT2 = { details:"Boiler PRV weeping — pressure slightly elevated.", remedial:"PRV replaced. System re-pressurised.", warningNotice:"No" };
    const CLIENT = { clientName:"Margaret Henderson", clientAddr1:"42 Calder Road", clientAddr2:"Livingston", clientAddr3:"West Lothian", clientPostcode:"EH54 9AB", clientTel:"07712 334455", clientEmail:"m.henderson@email.co.uk", instName:"Margaret Henderson", instAddr1:"42 Calder Road", instAddr2:"Livingston", instAddr3:"West Lothian", instPostcode:"EH54 9AB", instTel:"07712 334455" };
    const FINAL = { gasTightness:"Yes", pipeworkVisual:"YES", emergencyControl:"YES", bonding:"YES", installationPass:"YES", inspectionDate:fmt(addDays(TODAY,365)), coAlarm:"Yes", smokeAlarm:"Yes" };
    const SIG = { signatureImage:null, customerDeclaration:"I confirm the above checks have been carried out." };
    const WN_DATA = { certRef:"DEMO-GSCWN-002 Warning", clientName:"Margaret Henderson", clientAddr1:"42 Calder Road", clientAddr2:"Livingston", clientAddr3:"West Lothian", clientPostcode:"EH54 9AB", clientTel:"07712 334455", instAddr1:"42 Calder Road", instAddr2:"Livingston", instAddr3:"West Lothian", instPostcode:"EH54 9AB", make:"Hotpoint", model:"HD5V92KCW", type:"Cooker", serialNo:"HTK-293847", locationRoom:"Kitchen", idGasEscape:"YES", idDisconnected:"YES", idRefused:"NO", gasEmergencyRef:"N/A", arReason:"Flexible hose showing signs of wear.", arTurnedOff:"YES", arRefused:"NO", arTurningOffNoHelp:"NO", contactName:"Margaret Henderson", contactTel:"07712 334455", riddor:"NO", remedialAction:"Flexible hose replaced and tested.", issueDate:fmt(TODAY), issueTime:"10:30 AM" };

    const newCerts = [
      { isDemo:true, certData:{...CLIENT,certRef:"DEMO-GSC-001"}, appliances:[APP1,APP2], faults:[FAULT1,FAULT2], finalChecks:FINAL, signatureData:SIG, engineerData:ENG, savedAt:new Date().toISOString() },
      { isDemo:true, type:"gsc_wn_combined", certData:{...CLIENT,certRef:"DEMO-GSCWN-002"}, appliances:[APP1,APP2], faults:[FAULT1,FAULT2], finalChecks:FINAL, signatureData:SIG, engineerData:ENG, warningData:WN_DATA, warningSigData:{signatureImage:null}, savedAt:new Date().toISOString() },
      { isDemo:true, type:"bs", serviceData:{ certRef:"DEMO-BS-003", clientName:"Robert Sinclair", clientAddr1:"7 Dechmont View", clientAddr2:"Broxburn", clientAddr3:"West Lothian", clientPostcode:"EH52 5QR", clientTel:"07823 556677", clientEmail:"r.sinclair@email.co.uk", instName:"Robert Sinclair", instAddr1:"7 Dechmont View", instAddr2:"Broxburn", instAddr3:"West Lothian", instPostcode:"EH52 5QR", instTel:"07823 556677", typeOfWorkService:"Yes", typeOfWorkBreakdown:"N/A", boilerMake:"Vaillant", boilerModel:"ecoTEC plus 831", boilerSerial:"VAI-558821", applianceMake:"Vaillant", applianceModel:"ecoTEC plus 831", applianceSerial:"VAI-558821", coReading:"15", co2Reading:"9.2", coCo2Ratio:"0.001", additionalNotes:"Annual service completed. Filter cleaned.", sparesRequired:"None", flueType:"Pass", ventilationSize:"Pass", waterFuelSound:"Pass", electricallyFused:"Pass", correctValving:"Pass", isolationAvailable:"Pass", boilerPlantroom:"N/A", heatExchanger:"Pass", ignition:"Pass", gasValve:"Pass", fan:"Pass", safetyDevice:"Pass", controlBox:"Pass", burnersAndPilot:"Pass", fuelPressure:"Pass", burnerWashed:"Pass", pilotAssembly:"Pass", ignitionSystem:"Pass", burnerFan:"Pass", heatExchangerFlueways:"Pass", fuelElectrical:"Pass" }, bsSigData:{signatureImage:null}, bsEngData:{...ENG,certDate:fmt(TODAY)}, savedAt:new Date().toISOString() },
      { isDemo:true, type:"wn", wnFormData:{ certRef:"DEMO-WN-004", clientName:"Patricia Lawson", clientAddr1:"19 Almondbank Terrace", clientAddr2:"Edinburgh", clientAddr3:"", clientPostcode:"EH11 1SB", clientTel:"07934 221133", clientEmail:"p.lawson@email.co.uk", instAddr1:"19 Almondbank Terrace", instAddr2:"Edinburgh", instAddr3:"", instPostcode:"EH11 1SB", make:"Baxi", model:"Platinum+ 33HE", type:"Combi", serialNo:"BAX-774412", locationRoom:"Kitchen cupboard", idGasEscape:"YES", idDisconnected:"YES", idRefused:"NO", gasEmergencyRef:"GE-2024-4421", arReason:"CO readings elevated beyond safe limits.", arTurnedOff:"YES", arRefused:"NO", arTurningOffNoHelp:"NO", contactName:"Patricia Lawson", contactTel:"07934 221133", riddor:"NO", remedialAction:"Appliance isolated. Client advised not to use until repaired.", issueDate:fmt(TODAY), issueTime:"14:15 PM" }, wnEngData:{...ENG,issueDate:fmt(TODAY),issueTime:"14:15 PM"}, wnSigData:{signatureImage:null}, savedAt:new Date().toISOString() },
      { isDemo:true, type:"lpg_gsc", certLabel:"Liquified Petroleum Gas Safety Record", form:{ certRef:"DEMO-LPG-005", tradingTitle:"West Lothian Gas Services", engAddr:"14 Brucefield Avenue", engCity:"Livingston", engPostcode:"EH54 6BY", gasSafeNo:"123456", engTel:"01506 448821", gasId:"ENG-7891", clientName:"Beecraigs Caravan Park", clientAddr:"Beecraigs Country Park", clientCity:"Linlithgow", clientPostcode:"EH49 6PL", clientTel:"01506 284516", instAddr:"Beecraigs Country Park", instCity:"Linlithgow", instPostcode:"EH49 6PL", gasTightness:"Pass", pipeworkInspection:"Yes", appliances:[{location:"Unit 12",type:"Hob",make:"Dometic",model:"PI8022",co2Reading:"9.0",coReading:"10",flueType:"N/A",applianceInspected:"Yes",combustionReading:"0.001",opPressure:"37",landlordsAppliance:"Yes",heatInput:"8.5",safetyDevices:"Yes",ventilation:"Yes",flueCondition:"N/A",fluePerformance:"N/A",applianceServiced:"Yes",safeToUse:"Yes"},{location:"Unit 12",type:"Space Heater",make:"Calor",model:"Provence 4200",co2Reading:"8.8",coReading:"14",flueType:"OF",applianceInspected:"Yes",combustionReading:"0.002",opPressure:"37",landlordsAppliance:"Yes",heatInput:"4.2",safetyDevices:"Yes",ventilation:"Yes",flueCondition:"Yes",fluePerformance:"Pass",applianceServiced:"Yes",safeToUse:"Yes"}], faults:[{faultNo:"1",applianceNo:"1",details:"Hob burner seal deteriorating.",remedial:"Burner seal replaced.",warningNotice:"No"},{faultNo:"2",applianceNo:"2",details:"Thermocouple slow to respond.",remedial:"Thermocouple replaced.",warningNotice:"No"}] }, engineerData:ENG, savedAt:new Date().toISOString() },
      { isDemo:true, type:"leisure_gsc", certLabel:"Leisure Industry Gas Safety Record", form:{ certRef:"DEMO-LEISURE-006", tradingTitle:"West Lothian Gas Services", engAddr:"14 Brucefield Avenue", engCity:"Livingston", engPostcode:"EH54 6BY", gasSafeNo:"123456", engTel:"01506 448821", gasId:"ENG-7891", clientName:"Almond Valley Heritage Trust", clientAddr:"Millfield", clientCity:"Livingston", clientPostcode:"EH54 7AR", clientTel:"01506 414957", instAddr:"Millfield", instCity:"Livingston", instPostcode:"EH54 7AR", gasTightness:"Pass", pipeworkInspection:"Yes", appliances:[{location:"Café Kitchen",type:"Hob",make:"Falcon",model:"Continental 900",co2Reading:"9.2",coReading:"11",flueType:"N/A",applianceInspected:"Yes",combustionReading:"0.001",opPressure:"20",landlordsAppliance:"Yes",heatInput:"18",safetyDevices:"Yes",ventilation:"Yes",flueCondition:"N/A",fluePerformance:"N/A",applianceServiced:"Yes",safeToUse:"Yes"},{location:"Café Kitchen",type:"Combi",make:"Worcester",model:"Greenstar 30i",co2Reading:"9.0",coReading:"9",flueType:"RS",applianceInspected:"Yes",combustionReading:"0.001",opPressure:"20",landlordsAppliance:"Yes",heatInput:"30",safetyDevices:"Yes",ventilation:"Yes",flueCondition:"Yes",fluePerformance:"Pass",applianceServiced:"Yes",safeToUse:"Yes"}], faults:[{faultNo:"1",applianceNo:"1",details:"Igniter electrode cracked.",remedial:"Electrode replaced.",warningNotice:"No"},{faultNo:"2",applianceNo:"2",details:"Condensate pipe blocked.",remedial:"Pipe cleared.",warningNotice:"No"}] }, engineerData:ENG, savedAt:new Date().toISOString() },
      { isDemo:true, type:"commercial_gsc", certLabel:"Commercial Gas Safety Certificate", form:{ certRef:"DEMO-COMM-007", tradingTitle:"West Lothian Gas Services", engAddr:"14 Brucefield Avenue", engCity:"Livingston", engPostcode:"EH54 6BY", gasSafeNo:"123456", engTel:"01506 448821", gasId:"ENG-7891", clientName:"Livingston FC Community Trust", clientAddr:"Tony Macaroni Arena", clientCity:"Livingston", clientPostcode:"EH54 7GQ", clientTel:"01506 417000", instAddr:"Tony Macaroni Arena", instCity:"Livingston", instPostcode:"EH54 7GQ", gasTightness:"Pass", pipeworkInspection:"Yes", appliancesTested:"2", appliances:[{location:"Main Kitchen",type:"Hob",make:"Falcon",model:"G350/40",co2Reading:"9.1",coReading:"10",flueType:"N/A",applianceInspected:"Yes",combustionReading:"0.001",opPressure:"20",landlordsAppliance:"Yes",heatInput:"20",safetyDevices:"Yes",ventilation:"Yes",flueCondition:"N/A",fluePerformance:"N/A",applianceServiced:"Yes",safeToUse:"Yes"},{location:"Boiler Room",type:"Heat Only",make:"Ideal",model:"Imax Xtra 120",co2Reading:"9.3",coReading:"7",flueType:"FL",applianceInspected:"Yes",combustionReading:"0.001",opPressure:"20",landlordsAppliance:"Yes",heatInput:"120",safetyDevices:"Yes",ventilation:"Yes",flueCondition:"Yes",fluePerformance:"Pass",applianceServiced:"Yes",safeToUse:"Yes"}], faults:[{faultNo:"1",applianceNo:"1",details:"Hob wok burner flame uneven.",remedial:"Burner ports cleaned.",warningNotice:"No"},{faultNo:"2",applianceNo:"2",details:"Flueways partially sooted.",remedial:"Flueways cleaned.",warningNotice:"No"}] }, engineerData:ENG, savedAt:new Date().toISOString() },
      { isDemo:true, type:"benchmark", certLabel:"Benchmark Commissioning Checklist", form:{ certRef:"DEMO-BENCH-008", propertyType:"Semi-Detached House", newBoiler:"Yes", make:"Worcester", model:"Greenstar 30i", serial:"WB-338821-A", gasSafeNo:"123456", gasId:"ENG-7891", installationDate:fmt(TODAY), clientName:"David Morrison", clientAddr1:"55 Bankton Park", clientAddr2:"Livingston", clientAddr3:"West Lothian", clientPostcode:"EH54 9HB", clientTel:"07445 667788", systemFlushed:"Yes", inhibitorAdded:"Yes", inhibitorConcentration:"Fernox F1", filterFitted:"Yes", filterType:"Fernox TF1", chFlowTemp:"75", chReturnTemp:"62", chGasRateFt:"3.2", chGasRateM3:"0.091", chPressure:"20", hwFlowTemp:"60", hwReturnTemp:"N/A", hwGasRateFt:"3.8", hwGasRateM3:"0.108", hwPressure:"20", supplyVoltage:"230", frequency:"50", ctrlRoomStat:"Yes", ctrlTimeClock:"Yes", ctrlHeatZone:"Not Fitted", ctrlTrvs:"Yes", ctrlBypassValve:"Not Fitted", ctrlBoilerInterlock:"Yes", ctrlOptimumStart:"Not Fitted", handoverCompleted:"Yes", benchmarkSigned:"Yes" }, engineerData:ENG, savedAt:new Date().toISOString() },
      { isDemo:true, type:"cooling_off", certLabel:"7 Day Cooling Off Period Exemption", form:{ certRef:"DEMO-COOL-009", tradingTitle:"West Lothian Gas Services", engAddr:"14 Brucefield Avenue", engCity:"Livingston", engPostcode:"EH54 6BY", gasSafeNo:"123456", engTel:"01506 448821", gasId:"ENG-7891", clientName:"Susan Reid", clientAddr:"8 Riverside Road", clientCity:"Bathgate", clientPostcode:"EH48 2AA", clientTel:"07561 334422", instAddr:"8 Riverside Road", instCity:"Bathgate", instPostcode:"EH48 2AA", workDescription:"Emergency boiler replacement — existing boiler irreparable. No heating or hot water.", expiryDate:fmt(addDays(TODAY,7)), clientSignature:"S Reid", engineerSignature:"J Taylor" }, engineerData:ENG, savedAt:new Date().toISOString() },
      { isDemo:true, type:"gas_install_report", certLabel:"Gas Installation Safety Report", form:{ certRef:"DEMO-GISR-010", gasSafeNo:"123456", gasId:"ENG-7891", clientName:"Livingston Development Corporation", clientAddr:"Almondvale Business Park", clientCity:"Livingston", clientPostcode:"EH54 6HR", clientTel:"01506 431000", instAddr:"Unit 14, Almondvale Business Park", instCity:"Livingston", instPostcode:"EH54 6HR", installationType:"New Installation", gasTightness:"Pass", pipeworkInspection:"Yes", purgeCompleted:"Yes", standingPressure:"21", workingPressure:"20", sigOperative:"James Taylor", appliances:[{location:"Plant Room",type:"Heat Only",make:"Ideal",model:"Imax Xtra 150",serialNo:"IXB-992211",applianceInspected:"Yes",safeToUse:"Yes",applianceServiced:"Yes",siWarning:"No",faultDetails:"Pilot assembly needed cleaning.",remedialAction:"Pilot assembly cleaned.",warningNotice:"No"},{location:"Mezzanine Office",type:"System",make:"Vaillant",model:"ecoTEC plus 630",serialNo:"VAI-664433",applianceInspected:"Yes",safeToUse:"Yes",applianceServiced:"Yes",siWarning:"No",faultDetails:"Pump running noisy.",remedialAction:"Air bled from pump.",warningNotice:"No"}] }, engineerData:ENG, savedAt:new Date().toISOString() },
      { isDemo:true, type:"catering_inspection", certLabel:"Commercial Catering Inspection Record", form:{ certRef:"DEMO-CAT-011", gasSafeNo:"123456", licenceNo:"ENG-7891", clientName:"The Waterfront Restaurant", bizAddr:"Dock Road", bizCity:"South Queensferry", bizPostcode:"EH30 9SP", bizTel:"0131 331 5000", instAddr:"Dock Road", instCity:"South Queensferry", instPostcode:"EH30 9SP", installationDetails:"Annual gas safety inspection.", gasTightness:"Pass", emergencyControl:"Yes", gasIsolationValve:"Yes", appliances:[{location:"Main Kitchen",type:"Hob",make:"Falcon",model:"G350/40F",serialNo:"FAL-881234",applianceInspected:"Yes",safeToUse:"Yes",applianceServiced:"Yes",gasIsolation:"Yes",gasHose:"Yes",co2:"9.2",co:"10",combustion:"0.001",opPressure:"20",heatInput:"22",flueType:"N/A",flueVisual:"N/A",fluePerformance:"N/A",ventilation:"Yes",safetyDevices:"Yes",siWarningNotice:"No",faultDetails:"One burner ring blocked.",remedialAction:"Burner ring cleaned.",warningNotice:"No"},{location:"Main Kitchen",type:"Appliance",make:"Rational",model:"SCC WE 61",serialNo:"RAT-556677",applianceInspected:"Yes",safeToUse:"Yes",applianceServiced:"Yes",gasIsolation:"Yes",gasHose:"Yes",co2:"9.0",co:"8",combustion:"0.001",opPressure:"20",heatInput:"18",flueType:"FL",flueVisual:"Yes",fluePerformance:"Pass",ventilation:"Yes",safetyDevices:"Yes",siWarningNotice:"No",faultDetails:"Door seal worn.",remedialAction:"Door seal replaced.",warningNotice:"No"}] }, engineerData:ENG, savedAt:new Date().toISOString() },
      { isDemo:true, type:"gas_test_purge", certLabel:"Gas Testing and Purging Record", form:{ certRef:"DEMO-GTP-012", gasSafeNo:"123456", gasId:"ENG-7891", clientName:"Bathgate Leisure Centre", clientAddr:"Balbardie Park", clientCity:"Bathgate", clientPostcode:"EH48 4LA", clientTel:"01506 776644", instAddr:"Balbardie Park", instCity:"Bathgate", instPostcode:"EH48 4LA", workDescription:"New gas supply — testing and purging prior to commissioning.", ttGasType:"Natural Gas (NG)", standingPressure:"21", workingPressure:"20", ppVolMeter:"0.24", ppDetector:"Yes", purgePoint:"All appliance isolation valves", purgeMethod:"Displacement method", tightnessTest:"Pass", installationPass:"Pass", sigOperative:"James Taylor", unsafeOperative:"N/A" }, engineerData:ENG, savedAt:new Date().toISOString() },
    ];

    const demoInvoice = { isDemo:true, invoiceNo:"DEMO-INV-001", createdAt:new Date().toISOString(), clientName:"Margaret Henderson", clientAddr1:"42 Calder Road", clientAddr2:"Livingston", clientPostcode:"EH54 9AB", clientTel:"07712 334455", items:[{ description:"Annual Gas Safety Certificate — 2 appliances", qty:1, unitPrice:90, total:90 },{ description:"Flexible hose replacement — kitchen cooker", qty:1, unitPrice:45, total:45 }], subtotal:135, vatRate:20, vatAmount:27, total:162, notes:"Includes your 1 year warranty, thank you for your business.\nBank: West Lothian Gas Services · Sort: 83-14-22 · Acc: 00123456", fullyPaid:false, paid:0, outstanding:162 };
    const demoQuote = { isDemo:true, quoteNo:"DEMO-QUO-001", createdAt:new Date().toISOString(), clientName:"Robert Sinclair", clientAddr1:"7 Dechmont View", clientAddr2:"Broxburn", clientPostcode:"EH52 5QR", clientTel:"07823 556677", items:[{ description:"Annual Boiler Service — Vaillant ecoTEC plus 831", qty:1, unitPrice:85, total:85 },{ description:"Fernox TF1 Magnetic Filter supply & fit", qty:1, unitPrice:120, total:120 }], subtotal:205, vatRate:20, vatAmount:41, total:246, notes:"Quote valid for 30 days. All work carried out by Gas Safe registered engineers.", fullyPaid:false, paid:0, outstanding:246 };

    // Animate through each step
    for (let i = 0; i < DEMO_CERT_STEPS.length; i++) {
      setCurrentStep(i);
      await delay(900);
    }

    // Save all demo records
    setRecords(prev => { const cleaned = prev.filter(r => !r.isDemo); return [...cleaned, ...newCerts]; });
    setInvoices(prev => { const cleaned = prev.filter(i => !i.isDemo); return [...cleaned, demoInvoice]; });
    setQuotes(prev => { const cleaned = prev.filter(q => !q.isDemo); return [...cleaned, demoQuote]; });

    setDone(true);
    setRunning(false);
  }

  if (done) {
    return (
      <div style={{ minHeight:"100dvh", background:"linear-gradient(160deg,#03180d 0%,#0d4a26 60%,#03180d 100%)", display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", fontFamily:"'Segoe UI',sans-serif", padding:24 }}>
        <div style={{ width:"100%", maxWidth:420, textAlign:"center" }}>
          <div style={{ fontSize:64, marginBottom:16 }}>🎉</div>
          <div style={{ color:"#fff200", fontWeight:800, fontSize:26, marginBottom:12 }}>You're all set!</div>
          <div style={{ color:"rgba(255,255,255,0.85)", fontSize:15, lineHeight:1.7, marginBottom:28 }}>
            14 demo documents have been saved to <strong style={{color:"#fff200"}}>Records → Demo Certificates</strong>.<br/>
            Review them to see how each certificate looks, then start creating your own.
          </div>
          <div style={{ background:"rgba(255,255,255,0.1)", borderRadius:16, padding:20, marginBottom:24, textAlign:"left" }}>
            <div style={{ color:"#fff200", fontWeight:700, fontSize:14, marginBottom:12 }}>What's been created:</div>
            {DEMO_CERT_STEPS.map(s => (
              <div key={s.id} style={{ color:"rgba(255,255,255,0.85)", fontSize:13, padding:"4px 0", borderBottom:"1px solid rgba(255,255,255,0.08)" }}>
                {s.icon} {s.label}
              </div>
            ))}
            <div style={{ color:"rgba(255,255,255,0.85)", fontSize:13, padding:"4px 0" }}>💼 Invoice · 📄 Quote</div>
          </div>
          <button onClick={onDone} style={{ width:"100%", padding:"16px", background:"#fff200", color:"#03180d", border:"none", borderRadius:14, fontWeight:800, fontSize:18, cursor:"pointer", boxShadow:"0 4px 16px rgba(0,0,0,0.3)" }}>
            Go to Dashboard →
          </button>
        </div>
      </div>
    );
  }

  if (currentStep === -1) {
    return (
      <div style={{ minHeight:"100dvh", background:"linear-gradient(160deg,#03180d 0%,#0d4a26 60%,#03180d 100%)", display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", fontFamily:"'Segoe UI',sans-serif", padding:24 }}>
        <div style={{ width:"100%", maxWidth:420, textAlign:"center" }}>
          <div style={{ fontSize:56, marginBottom:16 }}>🧪</div>
          <div style={{ color:"#fff200", fontWeight:800, fontSize:24, marginBottom:12 }}>Step 3 of 3 — Demo Documents</div>
          <div style={{ color:"rgba(255,255,255,0.85)", fontSize:15, lineHeight:1.7, marginBottom:8 }}>
            We'll now create a sample of every certificate type, plus an invoice and a quote, so you can see exactly how they look.
          </div>
          <div style={{ color:"rgba(255,255,255,0.6)", fontSize:13, marginBottom:28 }}>They'll be saved in <strong style={{color:"#fff"}}>Records → Demo Certificates</strong> for you to review and download.</div>
          <div style={{ background:"rgba(255,255,255,0.08)", borderRadius:14, padding:16, marginBottom:28, textAlign:"left" }}>
            {DEMO_CERT_STEPS.map(s => (
              <div key={s.id} style={{ color:"rgba(255,255,255,0.7)", fontSize:13, padding:"3px 0" }}>{s.icon} {s.label}</div>
            ))}
            <div style={{ color:"rgba(255,255,255,0.7)", fontSize:13, padding:"3px 0" }}>💼 Invoice · 📄 Quote</div>
          </div>
          <button onClick={runWalkthrough} disabled={running}
            style={{ width:"100%", padding:"16px", background:"#fff200", color:"#03180d", border:"none", borderRadius:14, fontWeight:800, fontSize:18, cursor:"pointer", boxShadow:"0 4px 16px rgba(0,0,0,0.3)" }}>
            Create Demo Documents
          </button>
          <button onClick={onDone} style={{ marginTop:12, width:"100%", padding:"12px", background:"transparent", color:"rgba(255,255,255,0.5)", border:"1px solid rgba(255,255,255,0.2)", borderRadius:14, fontWeight:600, fontSize:14, cursor:"pointer" }}>
            Skip — go straight to the app
          </button>
        </div>
      </div>
    );
  }

  // Running — animated progress
  const step = DEMO_CERT_STEPS[currentStep];
  const progress = Math.round(((currentStep + 1) / DEMO_CERT_STEPS.length) * 100);
  return (
    <div style={{ minHeight:"100dvh", background:"linear-gradient(160deg,#03180d 0%,#0d4a26 60%,#03180d 100%)", display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", fontFamily:"'Segoe UI',sans-serif", padding:24 }}>
      <div style={{ width:"100%", maxWidth:420, textAlign:"center" }}>
        <div style={{ fontSize:60, marginBottom:16, transition:"all 0.3s" }}>{step.icon}</div>
        <div style={{ color:"#fff200", fontWeight:800, fontSize:20, marginBottom:8 }}>Creating Documents…</div>
        <div style={{ color:"rgba(255,255,255,0.9)", fontSize:16, marginBottom:24 }}>{step.label}</div>
        <div style={{ background:"rgba(255,255,255,0.15)", borderRadius:999, height:10, marginBottom:12, overflow:"hidden" }}>
          <div style={{ height:"100%", background:"#fff200", borderRadius:999, width:progress+"%", transition:"width 0.8s ease" }}/>
        </div>
        <div style={{ color:"rgba(255,255,255,0.6)", fontSize:13 }}>{currentStep + 1} of {DEMO_CERT_STEPS.length} documents</div>
        <div style={{ marginTop:24, display:"flex", flexDirection:"column", gap:6, maxHeight:260, overflowY:"hidden" }}>
          {DEMO_CERT_STEPS.map((s, i) => (
            <div key={s.id} style={{ display:"flex", alignItems:"center", gap:10, padding:"6px 12px", borderRadius:8, background: i < currentStep ? "rgba(255,255,255,0.1)" : i === currentStep ? "rgba(255,242,0,0.15)" : "transparent", transition:"all 0.3s" }}>
              <span style={{ fontSize:16 }}>{i < currentStep ? "✅" : i === currentStep ? "⏳" : "○"}</span>
              <span style={{ fontSize:13, color: i < currentStep ? "rgba(255,255,255,0.6)" : i === currentStep ? "#fff200" : "rgba(255,255,255,0.3)" }}>{s.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
// ─────────────────────────────────────────────────────────────────────────────

'''

# Find the anchor to insert before
ANCHOR4 = 'function HomeScreen({ onNew, onRecords, onGscEmail,'
if ANCHOR4 not in src:
    print("ERROR Edit 4: HomeScreen anchor"); sys.exit(1)
src = src.replace(ANCHOR4, ONBOARDING_SCREENS + ANCHOR4, 1)
print("OK Edit 4: Onboarding screens added")

# ── Write ─────────────────────────────────────────────────────────────────────
with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
print("\nAll edits applied. Run npm run build to verify.")
