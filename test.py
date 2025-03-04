import requests

# Base URL of your deployed app
base_url = "https://energyplus-flask-app-950448131349.us-central1.run.app"

# Example: Send a POST request to the /api/run-simulation endpoint
url = f"{base_url}/api/run-simulation"

# Prepare files to upload
files = {
    'idf_file': open('House-2FurnaceAC-UniformPLR.idf', 'rb'),
    'epw_file': open('EGY_Cairo.623660_IWEC.epw', 'rb')
}

# Send the request
response = requests.post(url, files=files)

# Check the response
if response.status_code == 200:
    print("Simulation successful!")
    print(response.text)  # Print the response content (e.g., HTML output)
else:
    print(f"Error: {response.status_code}")
    print(response.text)  # Print the raw response content for debugging