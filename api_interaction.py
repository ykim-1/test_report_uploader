import requests


def upload_encoded_xml_file(url, payload, headers):
    response = requests.post(url, data=payload, headers=headers)
    return response