import os
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class DecisionAgent:
    
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
    
    def decide(self, patient, health_result, resource_result, ethics_result):
        prompt = f"""
        You are the final decision-making AI in a hospital triage system.
        You receive inputs from three other AI agents and make the final treatment decision.
        
        Patient details:
        - ID: {patient['id']}
        - Age: {patient['age']}
        - Gender: {patient['gender']}
        - Symptoms: {', '.join(patient['symptoms'])}
        - Risk factors: {', '.join(patient.get('risk_factors', ['none']))}
        - Vitals: {patient.get('vitals', 'not provided')}
        
        Health Analysis Agent says:
        - Risk level: {health_result['risk_level']}
        - Key indicators: {', '.join(health_result['key_indicators'])}
        - Reasoning: {health_result['reasoning']}
        
        Resource Agent says:
        - Resource status: {resource_result['resource_status']}
        - Bed available: {resource_result['bed_available']}
        - ICU available: {resource_result['icu_available']}
        - Recommended resources: {', '.join(resource_result['recommended_resources'])}
        
        Ethics/Priority Agent says:
        - Priority score: {ethics_result['priority_score']}/100
        - Severity: {ethics_result['severity_score']}/10
        - Urgency: {ethics_result['urgency_score']}/10
        - Vulnerability flags: {', '.join(ethics_result.get('vulnerability_flags', ['none']))}
        - Ethical notes: {ethics_result['ethical_notes']}
        
        Based on ALL of the above, make a final decision.
        Possible actions: "Admit", "Admit to ICU", "Nurse Visit", "Home Treatment", "Refer to Specialist"
        
        Respond ONLY with a JSON object, no extra text:
        {{
            "patient_id": "{patient['id']}",
            "final_action": "one of the possible actions above",
            "priority_score": {ethics_result['priority_score']},
            "risk_level": "{health_result['risk_level']}",
            "reasoning": "clear explanation of why this decision was made",
            "follow_up": "what should happen next for this patient",
            "estimated_wait": "immediate / within 1 hour / within 4 hours / scheduled"
        }}
        """
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        raw = response.choices[0].message.content.strip()
        start = raw.find('{')
        end = raw.rfind('}') + 1
        result = json.loads(raw[start:end])
        return result
    
    def decide_batch(self, patients, health_results, resource_results, ethics_results):
        # Match ethics results back to original patient order
        ethics_map = {r['patient_id']: r for r in ethics_results}
        
        results = []
        for p, h, r in zip(patients, health_results, resource_results):
            e = ethics_map[p['id']]
            print(f"  Making decision for Patient {p['id']}...")
            result = self.decide(p, h, r, e)
            results.append(result)
            print(f"  → Decision: {result['final_action']} | Wait: {result['estimated_wait']}")
        
        # Sort by priority score
        results.sort(key=lambda x: x['priority_score'], reverse=True)
        return results


if __name__ == "__main__":
    from health_analysis_agent import HealthAnalysisAgent, SAMPLE_PATIENTS
    from resource_agent import ResourceAgent
    from ethics_agent import EthicsAgent

    print("=" * 60)
    print("AUTONOMOUS HEALTH DECISION AI - FULL PIPELINE")
    print("=" * 60)

    print("\n[Agent 1] Health Analysis...")
    health_agent = HealthAnalysisAgent()
    health_results = health_agent.analyse_batch(SAMPLE_PATIENTS)

    print("\n[Agent 2] Resource Check...")
    resource_agent = ResourceAgent()
    resource_results = resource_agent.check_batch(health_results)

    print("\n[Agent 3] Ethics & Priority...")
    ethics_agent = EthicsAgent()
    ethics_results = ethics_agent.calculate_batch(
        health_results, resource_results, SAMPLE_PATIENTS
    )

    print("\n[Agent 4] Final Decisions...")
    decision_agent = DecisionAgent()
    decisions = decision_agent.decide_batch(
        SAMPLE_PATIENTS, health_results, resource_results, ethics_results
    )

    print("\n" + "=" * 60)
    print("FINAL DECISION TABLE")
    print("=" * 60)
    print(f"{'Rank':<6} {'ID':<8} {'Risk':<8} {'Score':<8} {'Action':<22} {'Wait'}")
    print("-" * 70)
    for i, d in enumerate(decisions, 1):
        print(f"{i:<6} {d['patient_id']:<8} {d['risk_level']:<8} {d['priority_score']:<8} {d['final_action']:<22} {d['estimated_wait']}")

    print("\n--- REASONING ---")
    for d in decisions:
        print(f"\nPatient {d['patient_id']} → {d['final_action']}")
        print(f"  Reason: {d['reasoning']}")
        print(f"  Follow-up: {d['follow_up']}")
