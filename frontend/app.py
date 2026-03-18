import streamlit as st
import sys
sys.path.insert(0, '..')
from agents.health_analysis_agent import HealthAnalysisAgent
from agents.resource_agent import ResourceAgent
from agents.ethics_agent import EthicsAgent
from agents.decision_agent import DecisionAgent

st.set_page_config(
    page_title="Autonomous Health Decision AI",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Autonomous Health Decision AI")
st.markdown("*Multi-agent AI system for autonomous medical triage decisions*")
st.divider()

# --- Input Form ---
st.subheader("📋 Patient Input")

col1, col2, col3 = st.columns(3)

with col1:
    patient_id = st.text_input("Patient ID", value="P001")
    age = st.number_input("Age", min_value=0, max_value=120, value=30)
    gender = st.selectbox("Gender", ["Female", "Male", "Other"])

with col2:
    symptoms_input = st.text_area(
        "Symptoms (one per line)",
        value="fever\nheadache\nfatigue"
    )

with col3:
    risk_factors_input = st.text_area(
        "Risk Factors (one per line)",
        value="none"
    )
    vitals = st.text_input(
        "Vitals",
        value="BP 120/80, Temp 37.5C, SpO2 98%"
    )

st.divider()

# --- Run Pipeline ---
if st.button("🚀 Analyse Patient", type="primary", use_container_width=True):
    
    patient = {
        "id": patient_id,
        "age": age,
        "gender": gender,
        "symptoms": [s.strip() for s in symptoms_input.split('\n') if s.strip()],
        "risk_factors": [r.strip() for r in risk_factors_input.split('\n') if r.strip()],
        "vitals": vitals
    }

    st.divider()
    st.subheader("🤖 Agents Processing...")

    # Agent 1
    with st.status("Agent 1: Health Analysis...", expanded=False) as status:
        health_agent = HealthAnalysisAgent()
        health_result = health_agent.analyse(patient)
        status.update(label=f"✅ Agent 1: Health Analysis — {health_result['risk_level']} risk", state="complete")

    # Agent 2
    with st.status("Agent 2: Resource Check...", expanded=False) as status:
        resource_agent = ResourceAgent()
        resource_result = resource_agent.check(patient_id, health_result['risk_level'])
        status.update(label=f"✅ Agent 2: Resources — {resource_result['resource_status']}", state="complete")

    # Agent 3
    with st.status("Agent 3: Ethics & Priority...", expanded=False) as status:
        ethics_agent = EthicsAgent()
        ethics_result = ethics_agent.calculate_priority(health_result, resource_result, patient)
        status.update(label=f"✅ Agent 3: Priority Score — {ethics_result['priority_score']}/100", state="complete")

    # Agent 4
    with st.status("Agent 4: Final Decision...", expanded=False) as status:
        decision_agent = DecisionAgent()
        decision = decision_agent.decide(patient, health_result, resource_result, ethics_result)
        status.update(label=f"✅ Agent 4: Decision — {decision['final_action']}", state="complete")

    # --- Results ---
    st.divider()
    st.subheader("📊 Results")

    col1, col2, col3, col4 = st.columns(4)

    risk_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(health_result['risk_level'], "⚪")
    status_color = {"AVAILABLE": "🟢", "LIMITED": "🟡", "CRITICAL": "🔴"}.get(resource_result['resource_status'], "⚪")

    col1.metric("Risk Level", f"{risk_color} {health_result['risk_level']}")
    col2.metric("Priority Score", f"{ethics_result['priority_score']}/100")
    col3.metric("Resources", f"{status_color} {resource_result['resource_status']}")
    col4.metric("Est. Wait", decision['estimated_wait'])

    # Final decision banner
    st.divider()
    action = decision['final_action']
    if "ICU" in action:
        st.error(f"🚨 FINAL DECISION: {action.upper()}")
    elif action == "Admit":
        st.warning(f"⚠️ FINAL DECISION: {action.upper()}")
    elif action == "Nurse Visit":
        st.info(f"ℹ️ FINAL DECISION: {action.upper()}")
    else:
        st.success(f"✅ FINAL DECISION: {action.upper()}")

    # Reasoning
    with st.expander("📝 Full Reasoning", expanded=True):
        st.markdown(f"**Decision Reasoning:** {decision['reasoning']}")
        st.markdown(f"**Follow-up:** {decision['follow_up']}")
        st.markdown(f"**Key Health Indicators:** {', '.join(health_result['key_indicators'])}")
        if ethics_result.get('vulnerability_flags'):
            st.markdown(f"**Vulnerability Flags:** {', '.join(ethics_result['vulnerability_flags'])}")
        st.markdown(f"**Ethical Notes:** {ethics_result['ethical_notes']}")
