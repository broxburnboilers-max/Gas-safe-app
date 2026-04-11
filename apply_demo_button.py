import sys

path = r"C:\Users\Andrew\Documents\gas-safety-multiuser\src\App.jsx"
with open(path, encoding="utf-8") as f:
    src = f.read()

# ── EDIT 1: Add seedDemoData function before HomeScreen ───────────────────────
SEED_FN = r'''
// ─── Demo Data Seeder ─────────────────────────────────────────────────────────
function seedDemoData(setRecords) {
  const TODAY = new Date();
  const fmt = d => d.toISOString().slice(0, 10);
  const addDays = (d, n) => { const r = new Date(d); r.setDate(r.getDate() + n); return r; };

  const ENG = {
    engineerName:"James Taylor", companyName:"West Lothian Gas Services",
    companyAddr:"14 Brucefield Avenue", companyAddr2:"Livingston",
    companyPostcode:"EH54 6BY", companyTel:"01506 448821",
    companyEmail:"info@westlothiangas.co.uk", gasSafeNo:"123456",
    gasId:"ENG-7891", certDate:fmt(TODAY), issueDate:fmt(TODAY), issueTime:"10:30 AM",
  };
  const APP1 = { location:"Kitchen", type:"Cooker", make:"Hotpoint", model:"HD5V92KCW", co2:"8.9", co:"12", combustion:"0.001", flueType:"N/A", landlordsAppliance:"Yes", applianceInspected:"Yes", operatingPressure:"20", heatInput:"12.5", spillageTest:"N/A", flueFlow:"N/A", ventilation:"Yes", flueVisual:"N/A", fluePerformance:"N/A", applianceServiced:"Yes", applianceSafe:"Yes", safetyDevices:"Yes" };
  const APP2 = { location:"Airing Cupboard", type:"Combi", make:"Worcester", model:"Greenstar 30i", co2:"9.1", co:"8", combustion:"0.001", flueType:"RS", landlordsAppliance:"Yes", applianceInspected:"Yes", operatingPressure:"20", heatInput:"30", spillageTest:"Pass", flueFlow:"Pass", ventilation:"Yes", flueVisual:"Yes", fluePerformance:"Pass", applianceServiced:"Yes", applianceSafe:"Yes", safetyDevices:"Yes" };
  const FAULT1 = { details:"Gas smell detected near cooker connection — flexible hose showing signs of wear.", remedial:"Flexible hose replaced and tested. Gas tightness confirmed satisfactory.", warningNotice:"Yes" };
  const FAULT2 = { details:"Boiler pressure relief valve weeping — pressure slightly elevated.", remedial:"PRV replaced. System re-pressurised to 1.2 bar and tested satisfactory.", warningNotice:"No" };
  const CLIENT = { clientName:"Margaret Henderson", clientAddr1:"42 Calder Road", clientAddr2:"Livingston", clientAddr3:"West Lothian", clientPostcode:"EH54 9AB", clientTel:"07712 334455", clientEmail:"m.henderson@email.co.uk", instName:"Margaret Henderson", instAddr1:"42 Calder Road", instAddr2:"Livingston", instAddr3:"West Lothian", instPostcode:"EH54 9AB", instTel:"07712 334455" };
  const FINAL = { gasTightness:"Yes", pipeworkVisual:"YES", emergencyControl:"YES", bonding:"YES", installationPass:"YES", inspectionDate:fmt(addDays(TODAY,365)), coAlarm:"Yes", smokeAlarm:"Yes" };
  const SIG = { signatureImage:null, customerDeclaration:"I confirm the above checks have been carried out." };

  const newRecords = [
    // 1. Domestic GSC
    { isDemo:true, certData:{...CLIENT,certRef:"DEMO-GSC-001"}, appliances:[APP1,APP2], faults:[FAULT1,FAULT2], finalChecks:FINAL, signatureData:SIG, engineerData:ENG, savedAt:new Date().toISOString() },
    // 2. GSC + Warning Notice Combined
    { isDemo:true, type:"gsc_wn_combined", certData:{...CLIENT,certRef:"DEMO-GSCWN-002"}, appliances:[APP1,APP2], faults:[FAULT1,FAULT2], finalChecks:FINAL, signatureData:SIG, engineerData:ENG, warningData:{ certRef:"DEMO-GSCWN-002 Warning", clientName:"Margaret Henderson", clientAddr1:"42 Calder Road", clientAddr2:"Livingston", clientAddr3:"West Lothian", clientPostcode:"EH54 9AB", clientTel:"07712 334455", instAddr1:"42 Calder Road", instAddr2:"Livingston", instAddr3:"West Lothian", instPostcode:"EH54 9AB", make:"Hotpoint", model:"HD5V92KCW", type:"Cooker", serialNo:"HTK-293847", locationRoom:"Kitchen", idGasEscape:"YES", idDisconnected:"YES", idRefused:"NO", gasEmergencyRef:"N/A", arReason:"Flexible hose showing signs of wear.", arTurnedOff:"YES", arRefused:"NO", arTurningOffNoHelp:"NO", contactName:"Margaret Henderson", contactTel:"07712 334455", riddor:"NO", remedialAction:"Flexible hose replaced and tested.", issueDate:fmt(TODAY), issueTime:"10:30 AM" }, warningSigData:{signatureImage:null}, savedAt:new Date().toISOString() },
    // 3. Boiler Service
    { isDemo:true, type:"bs", serviceData:{ certRef:"DEMO-BS-003", clientName:"Robert Sinclair", clientAddr1:"7 Dechmont View", clientAddr2:"Broxburn", clientAddr3:"West Lothian", clientPostcode:"EH52 5QR", clientTel:"07823 556677", clientEmail:"r.sinclair@email.co.uk", instName:"Robert Sinclair", instAddr1:"7 Dechmont View", instAddr2:"Broxburn", instAddr3:"West Lothian", instPostcode:"EH52 5QR", instTel:"07823 556677", typeOfWorkService:"Yes", typeOfWorkBreakdown:"N/A", boilerMake:"Vaillant", boilerModel:"ecoTEC plus 831", boilerSerial:"VAI-558821", applianceMake:"Vaillant", applianceModel:"ecoTEC plus 831", applianceSerial:"VAI-558821", coReading:"15", co2Reading:"9.2", coCo2Ratio:"0.001", additionalNotes:"Annual service completed. Filter cleaned. System flushed.", sparesRequired:"None", flueType:"Pass", ventilationSize:"Pass", waterFuelSound:"Pass", electricallyFused:"Pass", correctValving:"Pass", isolationAvailable:"Pass", boilerPlantroom:"N/A", heatExchanger:"Pass", ignition:"Pass", gasValve:"Pass", fan:"Pass", safetyDevice:"Pass", controlBox:"Pass", burnersAndPilot:"Pass", fuelPressure:"Pass", burnerWashed:"Pass", pilotAssembly:"Pass", ignitionSystem:"Pass", burnerFan:"Pass", heatExchangerFlueways:"Pass", fuelElectrical:"Pass" }, bsSigData:{signatureImage:null}, bsEngData:{...ENG,certDate:fmt(TODAY)}, savedAt:new Date().toISOString() },
    // 4. Warning Notice
    { isDemo:true, type:"wn", wnFormData:{ certRef:"DEMO-WN-004", clientName:"Patricia Lawson", clientAddr1:"19 Almondbank Terrace", clientAddr2:"Edinburgh", clientAddr3:"", clientPostcode:"EH11 1SB", clientTel:"07934 221133", clientEmail:"p.lawson@email.co.uk", instAddr1:"19 Almondbank Terrace", instAddr2:"Edinburgh", instAddr3:"", instPostcode:"EH11 1SB", make:"Baxi", model:"Platinum+ 33HE", type:"Combi", serialNo:"BAX-774412", locationRoom:"Kitchen cupboard", idGasEscape:"YES", idDisconnected:"YES", idRefused:"NO", gasEmergencyRef:"GE-2024-4421", arReason:"CO readings elevated beyond safe limits.", arTurnedOff:"YES", arRefused:"NO", arTurningOffNoHelp:"NO", contactName:"Patricia Lawson", contactTel:"07934 221133", riddor:"NO", remedialAction:"Appliance isolated. Client advised not to use until repaired.", issueDate:fmt(TODAY), issueTime:"14:15 PM" }, wnEngData:{...ENG,issueDate:fmt(TODAY),issueTime:"14:15 PM"}, wnSigData:{signatureImage:null}, savedAt:new Date().toISOString() },
    // 5. LPG
    { isDemo:true, type:"lpg_gsc", certLabel:"Liquified Petroleum Gas Safety Record", form:{ certRef:"DEMO-LPG-005", tradingTitle:"West Lothian Gas Services", engAddr:"14 Brucefield Avenue", engCity:"Livingston", engPostcode:"EH54 6BY", gasSafeNo:"123456", engTel:"01506 448821", gasId:"ENG-7891", clientName:"Beecraigs Caravan Park", clientAddr:"Beecraigs Country Park", clientCity:"Linlithgow", clientPostcode:"EH49 6PL", clientTel:"01506 284516", instAddr:"Beecraigs Country Park", instCity:"Linlithgow", instPostcode:"EH49 6PL", gasTightness:"Pass", pipeworkInspection:"Yes", appliances:[{ location:"Unit 12", type:"Hob", make:"Dometic", model:"PI8022", co2Reading:"9.0", coReading:"10", flueType:"N/A", applianceInspected:"Yes", combustionReading:"0.001", opPressure:"37", landlordsAppliance:"Yes", heatInput:"8.5", safetyDevices:"Yes", ventilation:"Yes", flueCondition:"N/A", fluePerformance:"N/A", applianceServiced:"Yes", safeToUse:"Yes" },{ location:"Unit 12", type:"Space Heater", make:"Calor", model:"Provence 4200", co2Reading:"8.8", coReading:"14", flueType:"OF", applianceInspected:"Yes", combustionReading:"0.002", opPressure:"37", landlordsAppliance:"Yes", heatInput:"4.2", safetyDevices:"Yes", ventilation:"Yes", flueCondition:"Yes", fluePerformance:"Pass", applianceServiced:"Yes", safeToUse:"Yes" }], faults:[{ faultNo:"1", applianceNo:"1", details:"Hob burner seal deteriorating.", remedial:"Burner seal replaced and tested.", warningNotice:"No" },{ faultNo:"2", applianceNo:"2", details:"Space heater thermocouple slow to respond.", remedial:"Thermocouple replaced.", warningNotice:"No" }] }, engineerData:ENG, savedAt:new Date().toISOString() },
    // 6. Leisure
    { isDemo:true, type:"leisure_gsc", certLabel:"Leisure Industry Gas Safety Record", form:{ certRef:"DEMO-LEISURE-006", tradingTitle:"West Lothian Gas Services", engAddr:"14 Brucefield Avenue", engCity:"Livingston", engPostcode:"EH54 6BY", gasSafeNo:"123456", engTel:"01506 448821", gasId:"ENG-7891", clientName:"Almond Valley Heritage Trust", clientAddr:"Millfield", clientCity:"Livingston", clientPostcode:"EH54 7AR", clientTel:"01506 414957", instAddr:"Millfield", instCity:"Livingston", instPostcode:"EH54 7AR", gasTightness:"Pass", pipeworkInspection:"Yes", appliances:[{ location:"Café Kitchen", type:"Hob", make:"Falcon", model:"Continental 900", co2Reading:"9.2", coReading:"11", flueType:"N/A", applianceInspected:"Yes", combustionReading:"0.001", opPressure:"20", landlordsAppliance:"Yes", heatInput:"18", safetyDevices:"Yes", ventilation:"Yes", flueCondition:"N/A", fluePerformance:"N/A", applianceServiced:"Yes", safeToUse:"Yes" },{ location:"Café Kitchen", type:"Combi", make:"Worcester", model:"Greenstar 30i", co2Reading:"9.0", coReading:"9", flueType:"RS", applianceInspected:"Yes", combustionReading:"0.001", opPressure:"20", landlordsAppliance:"Yes", heatInput:"30", safetyDevices:"Yes", ventilation:"Yes", flueCondition:"Yes", fluePerformance:"Pass", applianceServiced:"Yes", safeToUse:"Yes" }], faults:[{ faultNo:"1", applianceNo:"1", details:"Burner igniter electrode cracked.", remedial:"Electrode replaced and tested.", warningNotice:"No" },{ faultNo:"2", applianceNo:"2", details:"Condensate pipe partially blocked.", remedial:"Condensate pipe cleared and repositioned.", warningNotice:"No" }] }, engineerData:ENG, savedAt:new Date().toISOString() },
    // 7. Commercial GSC
    { isDemo:true, type:"commercial_gsc", certLabel:"Commercial Gas Safety Certificate", form:{ certRef:"DEMO-COMM-007", tradingTitle:"West Lothian Gas Services", engAddr:"14 Brucefield Avenue", engCity:"Livingston", engPostcode:"EH54 6BY", gasSafeNo:"123456", engTel:"01506 448821", gasId:"ENG-7891", clientName:"Livingston FC Community Trust", clientAddr:"Tony Macaroni Arena", clientCity:"Livingston", clientPostcode:"EH54 7GQ", clientTel:"01506 417000", instAddr:"Tony Macaroni Arena", instCity:"Livingston", instPostcode:"EH54 7GQ", gasTightness:"Pass", pipeworkInspection:"Yes", appliancesTested:"2", appliances:[{ location:"Main Kitchen", type:"Hob", make:"Falcon", model:"G350/40", co2Reading:"9.1", coReading:"10", flueType:"N/A", applianceInspected:"Yes", combustionReading:"0.001", opPressure:"20", landlordsAppliance:"Yes", heatInput:"20", safetyDevices:"Yes", ventilation:"Yes", flueCondition:"N/A", fluePerformance:"N/A", applianceServiced:"Yes", safeToUse:"Yes" },{ location:"Boiler Room", type:"Heat Only", make:"Ideal", model:"Imax Xtra 120", co2Reading:"9.3", coReading:"7", flueType:"FL", applianceInspected:"Yes", combustionReading:"0.001", opPressure:"20", landlordsAppliance:"Yes", heatInput:"120", safetyDevices:"Yes", ventilation:"Yes", flueCondition:"Yes", fluePerformance:"Pass", applianceServiced:"Yes", safeToUse:"Yes" }], faults:[{ faultNo:"1", applianceNo:"1", details:"Hob wok burner flame uneven.", remedial:"Burner ports cleaned.", warningNotice:"No" },{ faultNo:"2", applianceNo:"2", details:"Heat exchanger flueways partially sooted.", remedial:"Flueways cleaned. Boiler serviced.", warningNotice:"No" }] }, engineerData:ENG, savedAt:new Date().toISOString() },
    // 8. Benchmark
    { isDemo:true, type:"benchmark", certLabel:"Benchmark Commissioning Checklist", form:{ certRef:"DEMO-BENCH-008", propertyType:"Semi-Detached House", newBoiler:"Yes", make:"Worcester", model:"Greenstar 30i", serial:"WB-338821-A", gasSafeNo:"123456", gasId:"ENG-7891", installationDate:fmt(TODAY), clientName:"David Morrison", clientAddr1:"55 Bankton Park", clientAddr2:"Livingston", clientAddr3:"West Lothian", clientPostcode:"EH54 9HB", clientTel:"07445 667788", systemFlushed:"Yes", inhibitorAdded:"Yes", inhibitorConcentration:"Fernox F1", filterFitted:"Yes", filterType:"Fernox TF1", chFlowTemp:"75", chReturnTemp:"62", chGasRateFt:"3.2", chGasRateM3:"0.091", chPressure:"20", hwFlowTemp:"60", hwReturnTemp:"N/A", hwGasRateFt:"3.8", hwGasRateM3:"0.108", hwPressure:"20", supplyVoltage:"230", frequency:"50", ctrlRoomStat:"Yes", ctrlTimeClock:"Yes", ctrlHeatZone:"Not Fitted", ctrlTrvs:"Yes", ctrlBypassValve:"Not Fitted", ctrlBoilerInterlock:"Yes", ctrlOptimumStart:"Not Fitted", handoverCompleted:"Yes", benchmarkSigned:"Yes" }, engineerData:ENG, savedAt:new Date().toISOString() },
    // 9. Cooling Off
    { isDemo:true, type:"cooling_off", certLabel:"7 Day Cooling Off Period Exemption", form:{ certRef:"DEMO-COOL-009", tradingTitle:"West Lothian Gas Services", engAddr:"14 Brucefield Avenue", engCity:"Livingston", engPostcode:"EH54 6BY", gasSafeNo:"123456", engTel:"01506 448821", gasId:"ENG-7891", clientName:"Susan Reid", clientAddr:"8 Riverside Road", clientCity:"Bathgate", clientPostcode:"EH48 2AA", clientTel:"07561 334422", instAddr:"8 Riverside Road", instCity:"Bathgate", instPostcode:"EH48 2AA", workDescription:"Emergency boiler replacement — existing boiler irreparable. No heating or hot water. Client consents to waive cooling off period due to urgency.", expiryDate:fmt(addDays(TODAY,7)), clientSignature:"S Reid", engineerSignature:"J Taylor" }, engineerData:ENG, savedAt:new Date().toISOString() },
    // 10. Gas Install Report
    { isDemo:true, type:"gas_install_report", certLabel:"Gas Installation Safety Report", form:{ certRef:"DEMO-GISR-010", gasSafeNo:"123456", gasId:"ENG-7891", clientName:"Livingston Development Corporation", clientAddr:"Almondvale Business Park", clientCity:"Livingston", clientPostcode:"EH54 6HR", clientTel:"01506 431000", instAddr:"Unit 14, Almondvale Business Park", instCity:"Livingston", instPostcode:"EH54 6HR", installationType:"New Installation", gasTightness:"Pass", pipeworkInspection:"Yes", purgeCompleted:"Yes", standingPressure:"21", workingPressure:"20", sigOperative:"James Taylor", appliances:[{ location:"Plant Room", type:"Heat Only", make:"Ideal", model:"Imax Xtra 150", serialNo:"IXB-992211", applianceInspected:"Yes", safeToUse:"Yes", applianceServiced:"Yes", siWarning:"No", faultDetails:"Pilot assembly required cleaning on commissioning.", remedialAction:"Pilot assembly cleaned. Boiler commissioned and tested.", warningNotice:"No" },{ location:"Mezzanine Office", type:"System", make:"Vaillant", model:"ecoTEC plus 630", serialNo:"VAI-664433", applianceInspected:"Yes", safeToUse:"Yes", applianceServiced:"Yes", siWarning:"No", faultDetails:"Pump running slightly noisy on commissioning.", remedialAction:"Air bled from pump. Now running quietly.", warningNotice:"No" }] }, engineerData:ENG, savedAt:new Date().toISOString() },
    // 11. Catering Inspection
    { isDemo:true, type:"catering_inspection", certLabel:"Commercial Catering Inspection Record", form:{ certRef:"DEMO-CAT-011", gasSafeNo:"123456", licenceNo:"ENG-7891", clientName:"The Waterfront Restaurant", bizAddr:"Dock Road", bizCity:"South Queensferry", bizPostcode:"EH30 9SP", bizTel:"0131 331 5000", instAddr:"Dock Road", instCity:"South Queensferry", instPostcode:"EH30 9SP", installationDetails:"Commercial catering kitchen — annual gas safety inspection.", gasTightness:"Pass", emergencyControl:"Yes", gasIsolationValve:"Yes", appliances:[{ location:"Main Kitchen", type:"Hob", make:"Falcon", model:"G350/40F", serialNo:"FAL-881234", applianceInspected:"Yes", safeToUse:"Yes", applianceServiced:"Yes", gasIsolation:"Yes", gasHose:"Yes", co2:"9.2", co:"10", combustion:"0.001", opPressure:"20", heatInput:"22", flueType:"N/A", flueVisual:"N/A", fluePerformance:"N/A", ventilation:"Yes", safetyDevices:"Yes", siWarningNotice:"No", faultDetails:"One burner ring blocked.", remedialAction:"Burner ring cleaned.", warningNotice:"No" },{ location:"Main Kitchen", type:"Appliance", make:"Rational", model:"SCC WE 61", serialNo:"RAT-556677", applianceInspected:"Yes", safeToUse:"Yes", applianceServiced:"Yes", gasIsolation:"Yes", gasHose:"Yes", co2:"9.0", co:"8", combustion:"0.001", opPressure:"20", heatInput:"18", flueType:"FL", flueVisual:"Yes", fluePerformance:"Pass", ventilation:"Yes", safetyDevices:"Yes", siWarningNotice:"No", faultDetails:"Door seal showing early signs of wear.", remedialAction:"Door seal replaced. Oven re-tested.", warningNotice:"No" }] }, engineerData:ENG, savedAt:new Date().toISOString() },
    // 12. Gas Test & Purge
    { isDemo:true, type:"gas_test_purge", certLabel:"Gas Testing and Purging Record", form:{ certRef:"DEMO-GTP-012", gasSafeNo:"123456", gasId:"ENG-7891", clientName:"Bathgate Leisure Centre", clientAddr:"Balbardie Park", clientCity:"Bathgate", clientPostcode:"EH48 4LA", clientTel:"01506 776644", instAddr:"Balbardie Park", instCity:"Bathgate", instPostcode:"EH48 4LA", workDescription:"New gas supply installation — testing and purging prior to commissioning.", ttGasType:"Natural Gas (NG)", standingPressure:"21", workingPressure:"20", ppVolMeter:"0.24", ppDetector:"Yes", purgePoint:"All appliance isolation valves", purgeMethod:"Displacement method using natural gas", tightnessTest:"Pass", installationPass:"Pass", sigOperative:"James Taylor", unsafeOperative:"N/A" }, engineerData:ENG, savedAt:new Date().toISOString() },
  ];

  if (setRecords) {
    setRecords(prev => {
      const cleaned = prev.filter(r => !r.isDemo);
      return [...cleaned, ...newRecords];
    });
  }
  return newRecords.length;
}
// ─────────────────────────────────────────────────────────────────────────────

// ─── Demo Certificates Records Screen ────────────────────────────────────────
function DemoCertificatesScreen({ records, onBack, onHome, onDelete }) {
  const [selected, setSelected] = useState(null);
  const [viewing, setViewing] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const DEMO_COLOR = "#555";

  const demoRecords = records.map((r,i)=>({...r,_origIdx:i})).filter(r=>r.isDemo);

  const getLabel = (r) => {
    if (!r.type || r.type==="gsc") return "Gas Safety Certificate";
    if (r.type==="gsc_wn_combined") return "GSC + Warning Notice";
    if (r.type==="bs") return "Boiler Service Record";
    if (r.type==="wn") return "Warning Notice";
    return r.certLabel || r.type;
  };
  const getClient = (r) => r.certData?.clientName || r.serviceData?.clientName || r.wnFormData?.clientName || r.form?.clientName || r.form?.tradingTitle || "Demo Client";
  const getRef = (r) => r.certData?.certRef || r.serviceData?.certRef || r.wnFormData?.certRef || r.form?.certRef || "";

  if (viewing !== null) {
    const r = demoRecords[viewing];
    const close = () => setViewing(null);
    if (!r.type || r.type==="gsc") return <PDFPreview certData={r.certData} appliances={r.appliances||[]} faults={r.faults||[]} finalChecks={r.finalChecks||{}} signatureData={r.signatureData||{}} engineerData={r.engineerData||{}} warningData={r.warningData} warningSigData={r.warningSigData} onClose={close}/>;
    if (r.type==="gsc_wn_combined") return <CombinedGSCWNPreview certData={r.certData} appliances={r.appliances||[]} faults={r.faults||[]} finalChecks={r.finalChecks||{}} signatureData={r.signatureData||{}} engineerData={r.engineerData||{}} wnData={r.warningData||{}} wnSigData={r.warningSigData||{}} onClose={close}/>;
    if (r.type==="bs") return <BSPDFPreview serviceData={r.serviceData} engineerData={r.bsEngData} signatureData={r.bsSigData} onClose={close}/>;
    if (r.type==="wn") return <WNPDFPreview wnFormData={{...r.wnFormData,issueDate:r.wnEngData?.issueDate,issueTime:r.wnEngData?.issueTime}} wnEngData={r.wnEngData} wnSigData={r.wnSigData||{}} onClose={close}/>;
    const config = Object.values(GENERIC_CERT_CONFIGS||{}).find(c=>c.type===r.type);
    if (config) return <GenericCertPDF certLabel={r.certLabel} config={config} form={r.form} engineerData={r.engineerData} onClose={close} onSave={()=>{}}/>;
    return <div style={{padding:40,textAlign:"center"}}><p>Preview not available for this type.</p><button onClick={close}>Back</button></div>;
  }

  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100dvh", background:LIGHT_BG, fontFamily:"'Segoe UI',sans-serif" }}>
      <Header title="🧪 Demo Certificates" onBack={onBack}/>
      <div style={{ flex:1, overflowY:"auto", padding:16, paddingBottom:80 }}>
        <div style={{ background:"#f0f0f0", border:"1.5px solid #999", borderRadius:12, padding:"10px 14px", marginBottom:16, fontSize:13, color:"#444", lineHeight:1.5 }}>
          These are sample records for testing. They show how each certificate type looks and downloads. Delete them when you're done testing.
        </div>
        {demoRecords.length===0 ? (
          <div style={{ textAlign:"center", color:"#aaa", marginTop:60, fontSize:15 }}>No demo records yet — tap Demo on the home screen to generate them.</div>
        ) : demoRecords.map((r,i) => (
          <div key={i} onClick={()=>setSelected(i)}
            style={{ background:"#fff", borderRadius:10, padding:"14px 16px", marginBottom:10, boxShadow:"0 2px 8px rgba(0,0,0,0.06)", borderLeft:`4px solid ${DEMO_COLOR}`, cursor:"pointer", display:"flex", alignItems:"center", gap:12 }}>
            <div style={{ flex:1 }}>
              <div style={{ fontWeight:700, fontSize:15, color:"#222" }}>{getClient(r)}</div>
              <div style={{ fontSize:13, color:"#888", marginTop:2 }}>{getRef(r)}</div>
              <div style={{ fontSize:12, color:DEMO_COLOR, marginTop:3 }}>🧪 {getLabel(r)} · {r.savedAt ? new Date(r.savedAt).toLocaleDateString("en-GB") : ""}</div>
            </div>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M5 3L10 8L5 13" stroke="#bbb" strokeWidth="2" strokeLinecap="round"/></svg>
          </div>
        ))}
      </div>
      <BottomBar onHome={onHome}/>
      {selected !== null && (
        <RecordActionSheet title={getClient(demoRecords[selected])} onClose={()=>setSelected(null)}
          onPreview={()=>{ setViewing(selected); setSelected(null); }}
          onDownload={()=>{ setViewing(selected); setSelected(null); }}
          onDelete={()=>{ setConfirmDelete(selected); setSelected(null); }}/>
      )}
      {confirmDelete !== null && (
        <ConfirmDeleteModal onCancel={()=>setConfirmDelete(null)} onConfirm={()=>{ onDelete(demoRecords[confirmDelete]._origIdx); setConfirmDelete(null); }}/>
      )}
    </div>
  );
}
// ─────────────────────────────────────────────────────────────────────────────

'''

ANCHOR1 = "function HomeScreen({ onNew, onRecords,"
if ANCHOR1 not in src:
    print("ERROR: Could not find HomeScreen anchor"); sys.exit(1)
src = src.replace(ANCHOR1, SEED_FN + ANCHOR1, 1)
print("✅ Edit 1: seedDemoData + DemoCertificatesScreen added")

# ── EDIT 2: Add onDemo prop to HomeScreen ─────────────────────────────────────
OLD2 = "function HomeScreen({ onNew, onRecords, onGscEmail, onBsEmail, onReport, onLogout, currentUser, onProfile, onPayment, onClientDetails }) {"
NEW2 = "function HomeScreen({ onNew, onRecords, onGscEmail, onBsEmail, onReport, onLogout, currentUser, onProfile, onPayment, onClientDetails, onDemo }) {"
if OLD2 not in src:
    print("ERROR: Could not find HomeScreen props"); sys.exit(1)
src = src.replace(OLD2, NEW2, 1)
print("✅ Edit 2: onDemo prop added to HomeScreen")

# ── EDIT 3: Add Demo PillBtn in HomeScreen ────────────────────────────────────
OLD3 = '''        <div className={!hasContacts ? "wlg-contacts-pulse" : ""}
          style={{ width:"100%", maxWidth:360, borderRadius:999, overflow:"visible" }}>
          <PillBtn onClick={onClientDetails} label="Client Details"'''
NEW3 = '''        <PillBtn onClick={onDemo} label="Demo" color="#444" iconBg="#222">
          <span style={{ fontSize:26 }}>🧪</span>
        </PillBtn>
        <div className={!hasContacts ? "wlg-contacts-pulse" : ""}
          style={{ width:"100%", maxWidth:360, borderRadius:999, overflow:"visible" }}>
          <PillBtn onClick={onClientDetails} label="Client Details"'''
if OLD3 not in src:
    print("ERROR: Could not find Client Details PillBtn anchor"); sys.exit(1)
src = src.replace(OLD3, NEW3, 1)
print("✅ Edit 3: Demo PillBtn added to HomeScreen")

# ── EDIT 4: Wire onDemo in App's HomeScreen call ──────────────────────────────
OLD4 = 'if (screen === "home") return <HomeScreen onNew={()=>setScreen("newJob")} onRecords={()=>setScreen("records")} onGscEmail={()=>setScreen("gscEmail")} onBsEmail={()=>setScreen("bsEmail")} onReport={()=>setScreen("report")} onLogout={onLogout} currentUser={currentUser} onProfile={()=>setScreen("profileEdit")} onPayment={()=>setScreen("paymentDetails")} onClientDetails={()=>setScreen("contacts")}/>;'
NEW4 = '''if (screen === "home") return <HomeScreen onNew={()=>setScreen("newJob")} onRecords={()=>setScreen("records")} onGscEmail={()=>setScreen("gscEmail")} onBsEmail={()=>setScreen("bsEmail")} onReport={()=>setScreen("report")} onLogout={onLogout} currentUser={currentUser} onProfile={()=>setScreen("profileEdit")} onPayment={()=>setScreen("paymentDetails")} onClientDetails={()=>setScreen("contacts")} onDemo={()=>{ const n=seedDemoData(setRecords); alert("✅ "+n+" demo records added!\\n\\nGo to Records → Demo Certificates to view them."); }}/>;'''
if OLD4 not in src:
    print("ERROR: Could not find HomeScreen JSX call"); sys.exit(1)
src = src.replace(OLD4, NEW4, 1)
print("✅ Edit 4: onDemo wired in App")

# ── EDIT 5: Add Demo folder route in RecordsScreen ───────────────────────────
OLD5 = '  if (folder === "commissioning") return <CommissioningRecordsScreen'
NEW5 = '  if (folder === "demo") return <DemoCertificatesScreen records={records} onBack={()=>setFolder(null)} onHome={onHome} onDelete={onDelete}/>;\n  if (folder === "commissioning") return <CommissioningRecordsScreen'
if OLD5 not in src:
    print("ERROR: Could not find commissioning folder route"); sys.exit(1)
src = src.replace(OLD5, NEW5, 1)
print("✅ Edit 5: Demo folder route added to RecordsScreen")

# ── EDIT 6: Add Demo folder to folders array ──────────────────────────────────
OLD6 = '    { id:"inv", label:"Invoices",'
NEW6 = '''    { id:"demo", label:"Demo Certificates", icon:"🧪", count: records.filter(r=>r.isDemo).length, color:"#555", desc:"Sample records for testing — delete when done" },
    { id:"inv", label:"Invoices",'''
if OLD6 not in src:
    print("ERROR: Could not find Invoices folder entry"); sys.exit(1)
src = src.replace(OLD6, NEW6, 1)
print("✅ Edit 6: Demo folder added to folders list")

# ── Write output ──────────────────────────────────────────────────────────────
with open(path, "w", encoding="utf-8") as f:
    f.write(src)
print("\n✅ All edits applied successfully. Run npm run build to verify.")
