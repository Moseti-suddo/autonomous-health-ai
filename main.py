import sys
sys.path.insert(0, 'agents')

from agents.health_analysis_agent import HealthAnalysisAgent, SAMPLE_PATIENTS
from agents.resource_agent import ResourceAgent
from agents.ethics_agent import EthicsAgent
from agents.decision_agent import DecisionAgent

def run_pipeline(patients):
    print("=" * 60)
    print("  AUTONOMOUS HEALTH DECISION AI")
    print("  Powered by Multi-Agent System")
    print("=" * 60)

    print("\n[Agent 1/4] Health Analysis Agent running...")
    health_agent = HealthAnalysisAgent()
    health_results = health_agent.analyse_batch(patients)

    print("\n[Agent 2/4] Resource Agent running...")
    resource_agent = ResourceAgent()
    resource_results = resource_agent.check_batch(health_results)

    print("\n[Agent 3/4] Ethics & Priority Agent running...")
    ethics_agent = EthicsAgent()
    ethics_results = ethics_agent.calculate_batch(
        health_results, resource_results, patients
    )

    print("\n[Agent 4/4] Decision & Judge Agent running...")
    decision_agent = DecisionAgent()
    decisions = decision_agent.decide_batch(
        patients, health_results, resource_results, ethics_results
    )

    print("\n" + "=" * 60)
    print("  FINAL DECISION TABLE")
    print("=" * 60)
    print(f"{'Rank':<6} {'ID':<8} {'Risk':<8} {'Score':<8} {'Action':<22} {'Wait'}")
    print("-" * 70)
    for i, d in enumerate(decisions, 1):
        print(f"{i:<6} {d['patient_id']:<8} {d['risk_level']:<8} {d['priority_score']:<8} {d['final_action']:<22} {d['estimated_wait']}")

    print("\n--- FULL REASONING ---")
    for d in decisions:
        print(f"\nPatient {d['patient_id']} → {d['final_action'].upper()}")
        print(f"  Risk:      {d['risk_level']}")
        print(f"  Priority:  {d['priority_score']}/100")
        print(f"  Reason:    {d['reasoning']}")
        print(f"  Follow-up: {d['follow_up']}")
        print(f"  Wait:      {d['estimated_wait']}")

    return decisions

if __name__ == "__main__":
    run_pipeline(SAMPLE_PATIENTS)
