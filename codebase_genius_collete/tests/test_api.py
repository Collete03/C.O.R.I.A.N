import requests

url = "http://127.0.0.1:8000/generate"
payload = {
    "github_url": "https://github.com/Collete03/C.O.R.I.A.N",
    "use_llm": True
}

response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())
