import json
import urllib.request

url = "http://localhost:5001/v1/chat/completions"
payload = {
    "model": "koboldcpp",
    "messages": [{"role": "user", "content": "Say hello in one word."}],
    "max_tokens": 20,
    "temperature": 0.7,
}
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as resp:
    print(resp.read().decode("utf-8"))