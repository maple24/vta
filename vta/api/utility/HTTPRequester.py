import requests


class HTTPRequester:
    def __init__(self, base_url):
        self.base_url = base_url

    def send_request(self, method, endpoint, params=None, data=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers)
            else:
                return "Invalid HTTP method"

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"


# Usage
# base_url = "https://api.example.com/"
# requester = RobustHTTPRequester(base_url)

# get_response = requester.send_request("GET", "get_endpoint", params={"param": "value"})
# print("GET Response:", get_response)

# post_data = {"key": "value"}
# post_response = requester.send_request("POST", "post_endpoint", data=post_data)
# print("POST Response:", post_response)
# Data to be sent in the POST request body (as a dictionary)
