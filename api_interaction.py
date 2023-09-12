import requests


def get_release_version(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        release_info = response.json()
        version = release_info["tag_name"]

        # Remove 'v' prefix if it exists
        if version.startswith("v"):
            version = version[1:]

        return str(version)

    except requests.exceptions.RequestException as e:
        print("Error:", e)
    except KeyError:
        print("Error: Unable to fetch release information from GitHub API.")


def upload_encoded_xml_file(url, payload, headers):
    response = requests.post(url, data=payload, headers=headers)
    return response
