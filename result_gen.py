
import requests

url = 'http://localhost:5000/receive'

def send_classification():
    
    form_data = {
        'operation': 'classification',
        'username': 'user123'
    }
    response = requests.post(url, data=form_data)
    return response.json()

def send_translation():
    form_data = {
        'operation': 'translation',
        'username': 'user123'
    }
    response = requests.post(url, data=form_data)
    return response.json()