import requests

BASE = "http://localhost:5000/"
response = requests.get(BASE+"turninactive")
print(response.json())
