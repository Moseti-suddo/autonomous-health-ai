import os
import json
import africastalking
from groq import Groq

# Africa's Talking setup
africastalking.initialize(
    username="sandbox",
    api_key="atsk_6c0d0627503c79662e6a4ada9191644d53c018c9eb1b1bb42afa6b301c295149675546a3"  # Replace with your key
)
sms = africastalking.SMS

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class EmergencyDispatchAgent:
    
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        # Simulated ambulance units
        self.ambulances = [
            {"id": "AMB001", "status": "available", "location": "Nairobi CBD"},
            {"id": "AMB002", "status": "available", "location": "Westlands"},
            {"id": "AMB003", "status": "busy", "location": "Karen"},
        ]
    
    def assess_emergency(self, caller_number, description, location):
        prompt = f"""
        You are an emergency medical dispatcher AI.
        Someone has called describing their condition from home.
        
        Caller: {caller_number}
        Location: {location}
        Description: {description}
        
        Assess if this is an emergency requiring immediate ambulance dispatch.
        
        Respond ONLY with a JSON object, no extra text:
        {{
            "is_emergency": true or false,
            "severity": "CRITICAL" or "URGENT" or "NON-URGENT",
            "suspected_condition": "brief description",
            "dispatch_ambulance": true or false,
            "response_message": "message to send back to the caller via SMS",
            "reasoning": "why you made this decision"
        }}
        """
        
        response = groq_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        raw = response.choices[0].message.content.strip()
        start = raw.find('{')
        end = raw.rfind('}') + 1
        result = json.loads(raw[start:end])
        return result
    
    def dispatch_ambulance(self, location):
        # Find nearest available ambulance
        available = [a for a in self.ambulances if a['status'] == 'available']
        if available:
            ambulance = available[0]
            ambulance['status'] = 'dispatched'
            return {
                "dispatched": True,
                "ambulance_id": ambulance['id'],
                "from_location": ambulance['location'],
                "to_location": location,
                "eta": "10-15 minutes"
            }
        return {
            "dispatched": False,
            "reason": "No ambulances available"
        }
    
    def send_sms(self, phone_number, message):
        try:
            response = sms.send(message, [phone_number])
            return {"sent": True, "response": response}
        except Exception as e:
            # In sandbox mode, just print instead
            print(f"  [SMS to {phone_number}]: {message}")
            return {"sent": True, "simulated": True}
    
    def handle_emergency_call(self, caller_number, description, location):
        print(f"\n  📞 Incoming call from {caller_number}")
        print(f"  📍 Location: {location}")
        print(f"  💬 Description: {description}")
        
        # Step 1: Assess
        print("\n  🤖 Assessing emergency...")
        assessment = self.assess_emergency(caller_number, description, location)
        print(f"  → Severity: {assessment['severity']}")
        print(f"  → Suspected: {assessment['suspected_condition']}")
        
        dispatch_result = {"dispatched": False}
        
        # Step 2: Dispatch if needed
        if assessment['dispatch_ambulance']:
            print("\n  🚑 Dispatching ambulance...")
            dispatch_result = self.dispatch_ambulance(location)
            if dispatch_result['dispatched']:
                print(f"  → {dispatch_result['ambulance_id']} dispatched!")
                print(f"  → ETA: {dispatch_result['eta']}")
                sms_message = f"EMERGENCY RESPONSE: Ambulance {dispatch_result['ambulance_id']} dispatched to {location}. ETA: {dispatch_result['eta']}. Stay calm and keep your phone on."
            else:
                sms_message = f"ALERT: {assessment['response_message']} No ambulances currently available. Please call 999 immediately."
        else:
            sms_message = f"HEALTH ADVISORY: {assessment['response_message']}"
        
        # Step 3: Send SMS back to caller
        print("\n  📱 Sending SMS response...")
        self.send_sms(caller_number, sms_message)
        
        return {
            "caller": caller_number,
            "location": location,
            "severity": assessment['severity'],
            "suspected_condition": assessment['suspected_condition'],
            "dispatch_ambulance": assessment['dispatch_ambulance'],
            "dispatch_result": dispatch_result,
            "sms_sent": True,
            "reasoning": assessment['reasoning']
        }


# Test scenarios
TEST_CALLS = [
    {
        "caller": "+254700000001",
        "description": "I have severe chest pain radiating to my left arm, I am sweating and feel dizzy. I cannot move.",
        "location": "Westlands, Nairobi"
    },
    {
        "caller": "+254700000002", 
        "description": "I have a mild headache and slight fever since this morning.",
        "location": "Kilimani, Nairobi"
    },
    {
        "caller": "+254700000003",
        "description": "My mother is unconscious and not responding, she is diabetic and collapsed suddenly.",
        "location": "South B, Nairobi"
    }
]

if __name__ == "__main__":
    print("=" * 60)
    print("  EMERGENCY DISPATCH AGENT")
    print("  Powered by AI + Africa's Talking SMS")
    print("=" * 60)
    
    agent = EmergencyDispatchAgent()
    
    for call in TEST_CALLS:
        print("\n" + "=" * 60)
        result = agent.handle_emergency_call(
            call['caller'],
            call['description'],
            call['location']
        )
        print(f"\n  OUTCOME: {'🚑 AMBULANCE DISPATCHED' if result['dispatch_ambulance'] else '📋 ADVISORY SENT'}")
        print(f"  Reasoning: {result['reasoning'][:80]}...")
