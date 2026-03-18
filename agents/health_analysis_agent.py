import os
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class HealthAnalysisAgent:
    
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
    
    def analyse(self, patient):
        prompt = f"""
        You are a medical triage AI. Analyse this patient and classify their risk.
        
        Patient ID: {patient['id']}
        Age: {patient['age']}
        Gender: {patient['gender']}
        Symptoms: {', '.join(patient['symptoms'])}
        Risk Factors: {', '.join(patient.get('risk_factors', ['none']))}
        Vitals: {patient.get('vitals', 'not provided')}
        
        Respond ONLY with a JSON object, no extra text:
        {{
            "patient_id": "{patient['id']}",
            "risk_level": "LOW" or "MEDIUM" or "HIGH",
            "confidence": 0.0 to 1.0,
            "key_indicators": ["indicator1", "indicator2"],
            "reasoning": "brief explanation"
        }}
        """
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        raw = response.choices[0].message.content.strip()
        
        # Clean up response in case model adds extra text
        start = raw.find('{')
        end = raw.rfind('}') + 1
        result = json.loads(raw[start:end])
        return result
    
    def analyse_batch(self, patients):
        results = []
        for patient in patients:
            print(f"  Analysing Patient {patient['id']}...")
            result = self.analyse(patient)
            results.append(result)
            print(f"  → Risk: {result['risk_level']} ({result['confidence']:.0%} confidence)")
        return results


# Test patients
SAMPLE_PATIENTS = [
    {
        "id": "P001",
        "age": 28,
        "gender": "Female",
        "symptoms": ["mild headache", "runny nose", "slight fatigue"],
        "risk_factors": [],
        "vitals": "BP 118/76, Temp 37.1C, SpO2 99%"
    },
    {
        "id": "P002",
        "age": 67,
        "gender": "Male",
        "symptoms": ["chest pain", "shortness of breath", "dizziness", "sweating"],
        "risk_factors": ["hypertension", "diabetes", "smoker"],
        "vitals": "BP 165/100, Temp 36.8C, SpO2 94%"
    },
    {
        "id": "P003",
        "age": 35,
        "gender": "Female",
        "symptoms": ["fever", "severe headache", "vomiting", "neck stiffness"],
        "risk_factors": ["recent travel to malaria zone"],
        "vitals": "BP 110/70, Temp 39.4C, SpO2 97%"
    },
    {
        "id": "P004",
        "age": 45,
        "gender": "Male",
        "symptoms": ["lower back pain", "mild fever"],
        "risk_factors": ["obesity"],
        "vitals": "BP 130/85, Temp 37.8C, SpO2 98%"
    },
    {
        "id": "P005",
        "age": 29,
        "gender": "Female",
        "symptoms": ["abdominal pain", "reduced fetal movement", "swollen feet"],
        "risk_factors": ["32 weeks pregnant", "previous complicated delivery"],
        "vitals": "BP 145/95, Temp 37.0C, SpO2 99%"
    }
]

if __name__ == "__main__":
    print("=" * 50)
    print("HEALTH ANALYSIS AGENT")
    print("=" * 50)
    
    agent = HealthAnalysisAgent()
    results = agent.analyse_batch(SAMPLE_PATIENTS)
    
    print("\n--- SUMMARY ---")
    print(f"{'ID':<8} {'Risk':<10} {'Confidence':<12} {'Reasoning'}")
    print("-" * 60)
    for r in results:
        print(f"{r['patient_id']:<8} {r['risk_level']:<10} {r['confidence']:<12.0%} {r['reasoning'][:40]}...")
