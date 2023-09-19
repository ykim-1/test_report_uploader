import base64
import os
import json
import xml.etree.ElementTree as ET


from linode_commands import get_list_command, get_download_command, get_remove_command
from command_execution import execute_command
from api_interaction import upload_encoded_xml_file, get_release_version
from setup_configuration import check_and_install_linode_cli


def get_software_name(file_name: str):
    if 'cli' in file_name:
        return "linode-cli"
    elif 'sdk' in file_name:
        return "linode_api4"
    elif 'linodego' in file_name:
        return "linodego"
    elif 'terraform' in file_name:
        return "linode-terraform"
    else:
        "unknown software type"


# Download all xml test reports
def download_and_upload_xml_files(cluster, bucket, url):
    list_process = execute_command(get_list_command(cluster))

    lines_of_all_files = list_process.stdout.decode().split('\n')

    xml_files = []

    team_name = os.environ.get('TEAM_NAME')

    for line in lines_of_all_files:
        if bucket in line and line.endswith(".xml"):
            xml_file = line.split("/")[-1]
            xml_files.append(xml_file)

    # Upload each xml file to TOD
    for file in xml_files:
        # Construct the full path to the XML file
        result = execute_command(get_download_command(cluster, bucket, file))
        # Parse the XML file
        tree = ET.parse(file)
        root = tree.getroot()
        branch_name_element = root.find('branch_name')
        gha_run_id_element = root.find('gha_run_id')
        gha_run_number_element = root.find('gha_run_number')

        branch_name_value = branch_name_element.text if branch_name_element is not None else None

        gha_id_value = gha_run_id_element.text if gha_run_id_element is not None else None

        gha_number_value = gha_run_number_element.text if gha_run_number_element is not None else None

        release_version = get_release_version(file)

        # if above command was successful encode the xml file for upload
        f = open(file, "r")
        lines = f.read()
        encoded_file = str(base64.b64encode(lines.encode('utf-8')).decode('utf-8'))

        # get softwarename
        software_name = get_software_name(file_name=file)

        # Define the data as a dictionary
        data = {
            "team": team_name,
            "softwareName": software_name,
            "semanticVersion": release_version,
            # Change semantic version current release (e.g. 5.48.1)
            "buildName": software_name + " " + release_version,
            "pass": True,
            "xunitResults": [encoded_file],
            "tag": "branch: " + branch_name_value + " GHA_ID/RUN#:" + gha_id_value + "/" + gha_number_value
        }

        headers = {"Content-Type": "application/json"}

        data_json = json.dumps(data)

        response = upload_encoded_xml_file(url, data_json, headers)

        # Check the response
        if response.status_code == 201:
            print(f"{file} uploaded successful...")

            # delete the xml files from the object storage because it will create a duplicate entry in TOD
            result = execute_command(get_remove_command(cluster, bucket, file))

            if result.returncode == 0:
                print(f"{file} deleted from object storage...")

        else:
            print(f"POST request for file {file} failed with status code: {response.status_code}")
            print(response.text)


def main():
    cluster = os.environ.get("CLUSTER")
    bucket = os.environ.get("BUCKET")
    url = os.environ.get("URL")

    check_and_install_linode_cli()
    download_and_upload_xml_files(cluster, bucket, url)


if __name__ == "__main__":
    main()
