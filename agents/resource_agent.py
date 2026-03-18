import os
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Simulated hospital resource database
HOSPITAL_RESOURCES = {
    "beds": {"total": 50, "available": 8},
    "icu_beds": {"total": 10, "available": 2},
    "nurses": {"total": 30, "on_duty": 12},
    "doctors": {"total": 15, "on_duty": 4},
    "medicine": {
        "antibiotics": "sufficient",
        "antimalarials": "low",
        "pain_relievers": "sufficient",
        "iv_fluids": "sufficient",
        "blood_pressure_meds": "sufficient"
    }
}

class ResourceAgent:
    
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        self.resources = HOSPITAL_RESOURCES
    
    def check(self, patient_id, risk_level):
        prompt = f"""
        You are a hospital resource management AI.
        
        Current hospital resources:
        - General beds available: {self.resources['beds']['available']} of {self.resources['beds']['total']}
        - ICU beds available: {self.resources['icu_beds']['available']} of {self.resources['icu_beds']['total']}
        - Nurses on duty: {self.resources['nurses']['on_duty']}
        - Doctors on duty: {self.resources['doctors']['on_duty']}
        - Medicine stock: {json.dumps(self.resources['medicine'])}
        
        Patient {patient_id} has been classified as {risk_level} risk.
        
        Respond ONLY with a JSON object, no extra text:
        {{
            "patient_id": "{patient_id}",
            "risk_level": "{risk_level}",
            "bed_available": true or false,
            "icu_available": true or false,
            "staff_available": true or false,
            "recommended_resources": ["resource1", "resource2"],
            "resource_status": "AVAILABLE" or "LIMITED" or "CRITICAL",
            "notes": "brief note on resource situation"
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
    
    def check_batch(self, health_results):
        results = []
        for h in health_results:
            print(f"  Checking resources for Patient {h['patient_id']}...")
            result = self.check(h['patient_id'], h['risk_level'])
            results.append(result)
            print(f"  → Resources: {result['resource_status']}")
        return results


if __name__ == "__main__":
    from health_analysis_agent import HealthAnalysisAgent, SAMPLE_PATIENTS
    
    print("=" * 50)
    print("RESOURCE AGENT")
    print("=" * 50)

    print("\n[Step 1] Running Health Analysis Agent...")
    health_agent = HealthAnalysisAgent()
    health_results = health_agent.analyse_batch(SAMPLE_PATIENTS)

    print("\n[Step 2] Running Resource Agent...")
    resource_agent = ResourceAgent()
    resource_results = resource_agent.check_batch(health_results)

    print("\n--- RESOURCE SUMMARY ---")
    print(f"{'ID':<8} {'Risk':<10} {'Status':<12} {'Notes'}")
    print("-" * 70)
    for r in resource_results:
        print(f"{r['patient_id']:<8} {r['risk_level']:<10} {r['resource_status']:<12} {r['notes'][:35]}...")
