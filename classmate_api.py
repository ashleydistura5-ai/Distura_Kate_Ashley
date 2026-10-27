import requests

url = "https://ladoing-kc-jane-marie.onrender.com/students"

try:
    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        data = response.json()

        print("Successfully connected to classmate's API!")
        print("API Response:")

        for key, value in data.items():
            print(f"{key}: {value}")

    else:
        print("Request failed.")
        print("Status Code:", response.status_code)

except requests.exceptions.RequestException as e:
    print("Connection error:", e)