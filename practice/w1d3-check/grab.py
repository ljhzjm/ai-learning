import requests

resp = requests.get("https://api.github.com")
print(resp.status_code)
