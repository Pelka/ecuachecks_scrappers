import requests

# Your API token
api_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1NDkyNWE3ZjhiZDEwY2ExMzI4ZWQwYyIsIm5iZiI6MTY5OTMxOTA4NywidXNlcm5hbWUiOiJhZG1pbiJ9.YTEKrmJXYuM5hKPDJIZua-Gg4KRHmSYCNmLNtgCKeFg'

# URL of the API endpoint you want to access
url = 'http://5.161.59.45:8080/api/spiders'

# Set up the request headers with the token
headers = {
    'Authorization': api_token,
    # 'X-API-Key': api_token,  # For API keys
    'Content-Type': 'application/json',  # Adjust content type as needed
}

# Make the HTTP request
response = requests.get(url, headers=headers)

# Process the response
if response.status_code == 200:
    data = response.json()  # Assuming the response is in JSON format
    print(data)
else:
    print(f'Request failed with status code {response.status_code}')
