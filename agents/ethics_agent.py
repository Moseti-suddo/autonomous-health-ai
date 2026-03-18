import os
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class EthicsAgent:
    
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
    
    def calculate_priority(self, health_result, resource_result, patient):
        prompt = f"""
        You are a medical ethics and triage priority AI.
        Your job is to assign a fair priority score to each patient.
        
        Consider these factors:
        1. Severity - how serious is the condition?
        2. Urgency - how quickly does the patient need care?
        3. Fairness - vulnerable groups (elderly, pregnant, children) get extra consideration
        4. Resource availability - scarce resources must be allocated wisely
        
        Patient details:
        - ID: {patient['id']}
        - Age: {patient['age']}
        - Gender: {patient['gender']}
        - Symptoms: {', '.join(patient['symptoms'])}
        - Risk factors: {', '.join(patient.get('risk_factors', ['none']))}
        
        Health Analysis result:
        - Risk level: {health_result['risk_level']}
        - Confidence: {health_result['confidence']}
        - Key indicators: {', '.join(health_result['key_indicators'])}
        
        Resource situation:
        - Resource status: {resource_result['resource_status']}
        - Bed available: {resource_result['bed_available']}
        - ICU available: {resource_result['icu_available']}
        - Staff available: {resource_result['staff_available']}
        
        Respond ONLY with a JSON object, no extra text:
        {{
            "patient_id": "{patient['id']}",
            "priority_score": 1 to 100,
            "severity_score": 1 to 10,
            "urgency_score": 1 to 10,
            "fairness_score": 1 to 10,
            "vulnerability_flags": ["flag1", "flag2"],
            "ethical_notes": "brief ethical reasoning"
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
    
    def calculate_batch(self, health_results, resource_results, patients):
        results = []
        for h, r, p in zip(health_results, resource_results, patients):
            print(f"  Calculating priority for Patient {p['id']}...")
            result = self.calculate_priority(h, r, p)
            results.append(result)
            print(f"  → Priority Score: {result['priority_score']}/100")
        
        # Sort by priority score descending
        results.sort(key=lambda x: x['priority_score'], reverse=True)
        return results


if __name__ == "__main__":
    from health_analysis_agent import HealthAnalysisAgent, SAMPLE_PATIENTS
    from resource_agent import ResourceAgent

    print("=" * 50)
    print("ETHICS / PRIORITY AGENT")
    print("=" * 50)

    print("\n[Step 1] Running Health Analysis Agent...")
    health_agent = HealthAnalysisAgent()
    health_results = health_agent.analyse_batch(SAMPLE_PATIENTS)

    print("\n[Step 2] Running Resource Agent...")
    resource_agent = ResourceAgent()
    resource_results = resource_agent.check_batch(health_results)

    print("\n[Step 3] Running Ethics/Priority Agent...")
    ethics_agent = EthicsAgent()
    ethics_results = ethics_agent.calculate_batch(
        health_results, resource_results, SAMPLE_PATIENTS
    )

    print("\n--- PRIORITY RANKING ---")
    print(f"{'Rank':<6} {'ID':<8} {'Score':<8} {'Severity':<10} {'Urgency':<10} {'Ethical Notes'}")
    print("-" * 75)
    for i, r in enumerate(ethics_results, 1):
        print(f"{i:<6} {r['patient_id']:<8} {r['priority_score']:<8} {r['severity_score']:<10} {r['urgency_score']:<10} {r['ethical_notes'][:30]}...")
