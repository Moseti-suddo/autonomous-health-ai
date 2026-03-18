import google.auth
import google.auth.transport.requests
from google import genai

credentials, project = google.auth.default()
request = google.auth.transport.requests.Request()
credentials.refresh(request)

client = genai.Client(
    vertexai=True,
    credentials=credentials,
    project="moseti-490206",
    location="us-central1"
)

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="Say hello in one sentence."
)
print(response.text)
