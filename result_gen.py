import requests

base_url = 'https://ca9f-34-142-241-202.ngrok-free.app'

def send_classification(keypoints):
    url = f"{base_url}/sign_classify"
    form_data = {
        "keypoints": keypoints,
    }
    try:
        response = requests.post(url, json=form_data, timeout=5)
        response.raise_for_status()
        result = response.json()

        # Validate format: Expecting a dictionary of 3 classes with [label, score]
        if isinstance(result, dict) and all(isinstance(v, list) and len(v) == 2 for v in result.values()):
            return result
        else:
            return {
                "1": ["Error", 0.0],
                "2": ["Error", 0.0],
                "3": ["Error", 0.0]
            }

    except requests.exceptions.RequestException as e:
        print(f"Classification request failed: {e}")
        return {
            "1": ["Error", 0.0],
            "2": ["Error", 0.0],
            "3": ["Error", 0.0]
        }

def send_translation(keypoints):
    url = f"{base_url}/sign_translate"
    form_data = {
        "keypoints": keypoints,
    }
    try:
        response = requests.post(url, json=form_data, timeout=8)
        response.raise_for_status()
        result = response.json()

        # Validate format: Expecting { "text": "..." }
        if isinstance(result, dict) and "text" in result:
            return result
        else:
            return {"text": "Error: Unexpected format"}

    except requests.exceptions.RequestException as e:
        print(f"Translation request failed: {e}")
        return {"text": "Error: error"}
