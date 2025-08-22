"""

Copyright (c) 2025 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""
__author__ = "Shirin Khan <shirkhan@cisco.com>"
__copyright__ = "Copyright (c) 2025 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import json
import logging
import pandas as pd
import requests
import urllib3
import time

from dnac_config import (
    CAPABILITY,
    DEV_ID_TXT,
    DATA_JSON,
    DNAC_PASS_REGION1,
    DNAC_USER_REGION1,
    HOLD_TIME,
    INF,
    LIMIT,
    PLATFORM,
    PORT_ID,
    RESPONSE_CODE,
    RESPONSE_IN_JSON,
    RESPONSE_KEY
)
from glom import glom, T
from math import ceil
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from requests.auth import HTTPBasicAuth  # for Basic Auth

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings
DNAC_AUTH1 = HTTPBasicAuth(DNAC_USER_REGION1, DNAC_PASS_REGION1)


def get_dnac_jwt_token(auth, url):
    """
    Create the authorization token required to access DNA C
    Call to DNA C - /api/system/v1/auth/login
    :param auth - DNA C Basic Auth string
    :param  url: IP Address of DNAC for Different Regions
    :return dnac_jwt_token: Authentication token
    """
    region_url = url + "/api/system/v1/auth/token"
    header = {"content-type": DATA_JSON}
    auth_token = ""
    # If DNAC has a certificate signed by a trusted authority change verify to True
    try:
        response = requests.post(region_url, auth=auth, headers=header, verify=False)
        if response.status_code == 200:
            auth_token = response.json()["Token"]
    except requests.exceptions.HTTPError as errHttp:
        logging.error(errHttp)
    except requests.exceptions.ConnectionError as errConnection:
        logging.error(errConnection)
    except requests.exceptions.Timeout as errTimeOut:
        logging.error(errTimeOut)
    except requests.exceptions.RequestException as err:
        logging.error(err)
    except Exception as parseException:
        logging.error(parseException)
    return auth_token


def get_network_device_count(auth_token, url):
    """
    This function counts all network device
    :param auth_token: login token
    :param url: dnac region url
    :return: count of devices found
    """
    region_url = url + "/dna/intent/api/v1/network-device/count"
    header = {"content-type": DATA_JSON, "x-auth-token": auth_token}
    total_count = 0
    count_json = {}
    try:
        count_response = requests.get(region_url, headers=header, verify=False)
        if count_response.status_code == 200:
            count_json = count_response.json()
            total_count = count_json["response"]
    except requests.exceptions.HTTPError as errHttp:
        logging.error(errHttp)
    except requests.exceptions.ConnectionError as errConnection:
        logging.error(errConnection)
    except requests.exceptions.Timeout as errTimeOut:
        logging.error(errTimeOut)
    except requests.exceptions.RequestException as err:
        logging.error(err)
    except Exception as parseException:
        logging.error(parseException)
    return total_count


def get_network_device_list(auth_token, url, total_count):
    """
    This function gets all devices of role access and border router from DNACenter Inventory
    :param auth_token: DNAC auth token
    :param url: DNAC region url
    :param total_count: number of all devices
    :return: all devices list
    """
    device_list = []
    offset_value = 1
    logging.info("Limit:{} offset: {}".format(LIMIT, offset_value))
    network_device = {}
    iterator_num = ceil(total_count / LIMIT)
    network_device = {"device_total_count": total_count}
    for idx in range(0, iterator_num):
        device_list = get_inventory(url, offset_value, auth_token, device_list)
        offset_value += LIMIT
    network_device.update({"devices": device_list})
    logging.info("Print Network Device List {}".format(network_device))
    logging.info(
        "Switch, router and wireless controllers present in DNAC Inventory: {}".format(
            len(network_device["devices"])
        )
    )
    return network_device["devices"]


def get_inventory(url, offset, token, device_list):
    """
    This function gets all network devices from DNAC Center inventory of type access and border router
    :param url: DNAC Region URL
    :param offset: offset to pull network device from inventory
    :param token: DNAC auth token
    :param device_list: device list
    :return: devices_list
    """
    region_url = f"{url}/dna/intent/api/v1/network-device"
    logging.info("Region url {}".format(region_url))
    querystring = {"limit": LIMIT, "offset": offset}
    logging.info("Querystring {}".format(querystring))
    header = {"content-type": DATA_JSON, "x-auth-token": token}
    try:
        devices_response = requests.get(
            region_url, headers=header, verify=False, params=querystring
        )
        logging.info(RESPONSE_CODE.format(devices_response.status_code))
        logging.info(
            RESPONSE_IN_JSON.format(json.dumps(devices_response.json(), indent=4))
        )
        if devices_response.status_code == 200:
            devices = devices_response.json()
            if RESPONSE_KEY in devices.keys():
                for item in devices.get("response"):
                    device = {}
                    device["hostname"] = item.get("hostname", "unknown")
                    device["role"] = item.get("role", "not defined")
                    device["reachability"] = item.get("reachabilityStatus", "unknown")
                    device["family"] = item.get("family", "not defined")
                    device["platform"] = item.get("platformId", "unknown")
                    device["managementIpAddress"] = item.get(
                        "managementIpAddress", "unknown"
                    )
                    device["deviceId"] = item.get("instanceUuid", "unknown")
                    if len(device) > 0:
                        device_list.append(device)
                        logging.info(
                            "Append Device to Device list Length check: {}".format(
                                len(device_list)
                            )
                        )
    except requests.exceptions.HTTPError as errHttp:
        logging.error(errHttp)
    except requests.exceptions.ConnectionError as errConnection:
        logging.error(errConnection)
    except requests.exceptions.Timeout as errTimeOut:
        logging.error(errTimeOut)
    except requests.exceptions.RequestException as err:
        logging.error(err)
    except Exception as parseException:
        logging.error(parseException)
    return device_list


def check_task_id_detail(task_id, dnac_jwt_token, catc_url):
    """
    This function will check the status of the task with the id {task_id}. Loop one seconds increments until task is completed
    :param task_id: task id
    :param dnac_jwt_token: DNA C token
    :param catc_url: Catalyst Center url
    :return:
    """
    file_id = ""
    completed = "no"
    url = f"{catc_url}/dna/intent/api/v1/tasks/{task_id}/detail"
    header = {"content-type": DATA_JSON, "x-auth-token": dnac_jwt_token}
    while completed == "no":
        logging.info(f"completed: {completed}")
        try:
            task_response = requests.get(url, headers=header, verify=False)
            if task_response.status_code == 200:
                task_json = task_response.json()
                logging.info(f"task response {task_json}")
                progress = glom(task_json, "response.progress")

                if progress == "CLI Runner Request Creation":
                    completed = "no"
                    time.sleep(1)
                    logging.info(f"completed-No: {completed}")
                else:
                    progress_dict = json.loads(progress)
                    file_id = glom(progress_dict, "fileId")
                    logging.info(f"taskid {task_id} contains {file_id}")
                    completed = "yes"
                    logging.info(f"completed-Yes: {completed}")
        except requests.exceptions.ConnectionError as errConnection:
            logging.error(errConnection)
        except requests.exceptions.Timeout as errTimeOut:
            logging.error(errTimeOut)
        except requests.exceptions.RequestException as err:
            logging.error(err)
        except Exception as parseException:
            logging.error(parseException)
    return file_id


def get_content_file_id(file_id, dnac_jwt_token, catc_url):
    """
    This function will download a file specified by the {file_id}
    :param file_id: file id
    :param dnac_jwt_token: DNA C token
    :param catc_url: Catalyst Center url
    :return: file
    """
    response_json = ""
    url = f"{catc_url}/api/v1/file/{file_id}"
    logging.info(f"url: {url}")
    header = {"content-type": "application/json", "x-auth-token": dnac_jwt_token}
    try:
        response = requests.get(url, headers=header, verify=False)
        if response.status_code == 200:
            response_json = response.json()
    except requests.exceptions.HTTPError as errHttp:
        logging.error(errHttp)
    except requests.exceptions.ConnectionError as errConnection:
        logging.error(errConnection)
    except requests.exceptions.Timeout as errTimeOut:
        logging.error(errTimeOut)
    except Exception as parseException:
        logging.error(parseException)
    return response_json


def get_output_command_runner(command, device_id, dnac_jwt_token, catc_url):
    """
    This function will return the output of the CLI command specified in the {command}, sent to the device with the
    hostname {device}
    :param command: CLI command list
    :param device_id: device id
    :param dnac_jwt_token: DNA C token
    :param catc_url: Catalyst Center url
    :return: file with the command output
    """
    payload = {"commands": [command], "deviceUuids": [device_id], "timeout": 10}
    task_id = ""
    command_output = ""
    response_json = {}
    url = f"{catc_url}/api/v1/network-device-poller/cli/read-request"
    header = {"content-type": "application/json", "x-auth-token": dnac_jwt_token}
    logging.info(f"url: {url}")
    try:
        response = requests.post(
            url, data=json.dumps(payload), headers=header, verify=False
        )
        if response.status_code == 202:
            response_json = response.json()
            logging.info(f"RESPONSE JSON: {response_json}")
            task_id = glom(response_json, "response.taskId", default="")
            logging.info(f"Task ID: {task_id}")
    except requests.exceptions.HTTPError as errHttp:
        logging.error(errHttp)
    except requests.exceptions.ConnectionError as errConnection:
        logging.error(errConnection)
    except requests.exceptions.Timeout as errTimeOut:
        logging.error(errTimeOut)
    except Exception as parseException:
        logging.error(parseException)
    if task_id == "" and response_json:
        command_output = f"{glom(response_json, 'response.errorCode')}:{glom(response_json, 'response.errorCode')}"
        return command_output
    # time.sleep(3)
    file_id = check_task_id_detail(task_id, dnac_jwt_token, catc_url)
    time.sleep(3)
    if file_id and file_id != "":
        file_output = get_content_file_id(file_id, dnac_jwt_token, catc_url)
        logging.info(f"File output {file_output}, Type:{type(file_output)}")
        command_output = glom(file_output[0], "commandResponses.SUCCESS")
    return command_output, len(command_output)


def parse_cdp_neighbor_output(query_config: str) -> dict:
    """
    Parses the 'show cdp neighbor' output string, extracting data into a DataFrame
    and the total count into a dictionary.

    Args:
        query_config (str): The multi-line string output from 'show cdp neighbor'.

    Returns:
        dict: A dictionary containing:
            'count' (int): The total number of CDP entries displayed.
            'data' (pd.DataFrame): A DataFrame with parsed CDP neighbor details.
    """
    cdp = {}
    total_cdp_entries = 0
    parsed_rows = []
    current_device_id = ""
    # Define column names explicitly
    column_names = [DEV_ID_TXT, INF, HOLD_TIME, CAPABILITY, PLATFORM, PORT_ID]

    # Define approximate column start positions based on the example header
    # "Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID"
    COL_RANGES = {
        DEV_ID_TXT: (0, 17),
        INF: (17, 33),
        HOLD_TIME: (33, 43),
        CAPABILITY: (43, 57),
        PLATFORM: (57, 67),
        PORT_ID: (67, None),  # To the end of the line
    }

    # Find the start and end of the main data block
    start_data_block_marker = DEV_ID_TXT
    end_data_block_marker = "Total cdp entries displayed :"

    start_idx = query_config.find(start_data_block_marker)
    end_idx = query_config.find(end_data_block_marker)
    logging.info(f"start_id: {start_idx} and end_id:{end_idx}")

    if start_idx == -1:
        raise ValueError(
            f"Could not find '{start_data_block_marker}' in the input string."
        )

    # Extract the relevant data string for parsing rows
    # This string starts from "Device ID" and goes up to (but not including) "Total cdp entries displayed"
    if end_idx != -1:
        data_string_to_parse = query_config[start_idx:end_idx].strip()
    else:
        # If "Total cdp entries displayed" is not found, parse until the end of the string
        data_string_to_parse = query_config[start_idx:].strip()
    logging.info(f"data_string_to_parse: {data_string_to_parse}")

    # Extract total cdp entries from the line containing the marker
    if end_idx != -1:
        logging.info(f"{len(end_data_block_marker)} {len(end_data_block_marker)}")
        cdp_count_index = end_idx + len(end_data_block_marker) + 1
        logging.info(f"{type(cdp_count_index)}")
        # Get the full line where the marker is found
        total_cdp_entries = query_config[cdp_count_index]

    # Split the extracted data string into lines
    lines_to_process = data_string_to_parse.splitlines()

    # The first line in data_string_to_parse is the header. We process lines AFTER it.
    # So, data_lines will be lines_to_process[1:]
    if not lines_to_process or len(lines_to_process) < 2:
        # Handle cases where there's no data or only a header
        df = pd.DataFrame(columns=column_names)
        cdp["count"] = total_cdp_entries
        cdp["data"] = df
        return cdp

    # Process each line after the header
    for line in lines_to_process[1:]:
        if not line.strip():  # Skip empty lines
            continue

        # Extract fields using the defined fixed widths
        device_id_field = line[
            COL_RANGES[DEV_ID_TXT][0] : COL_RANGES[DEV_ID_TXT][1]
        ].strip()
        local_intrfce_field = line[COL_RANGES[INF][0] : COL_RANGES[INF][1]].strip()
        holdtme_field = line[
            COL_RANGES[HOLD_TIME][0] : COL_RANGES[HOLD_TIME][1]
        ].strip()
        capability_field = line[
            COL_RANGES[CAPABILITY][0] : COL_RANGES[CAPABILITY][1]
        ].strip()
        platform_field = line[COL_RANGES[PLATFORM][0] : COL_RANGES[PLATFORM][1]].strip()
        port_id_field = line[COL_RANGES[PORT_ID][0] :].strip()

        # Update current_device_id if a new one is found on this line
        if device_id_field:
            current_device_id = device_id_field

        # Add a row to the parsed data only if interface details are present on this line.
        # This handles cases where Device ID is on its own line (e.g., "9800-ISSU.POD3.CSS.COM").
        if local_intrfce_field:
            parsed_rows.append(
                [
                    current_device_id,
                    local_intrfce_field,
                    holdtme_field,
                    capability_field,
                    platform_field,
                    port_id_field,
                ]
            )

    # Create the DataFrame
    df = pd.DataFrame(parsed_rows, columns=column_names)

    # Populate the cdp dictionary (as requested to keep unchanged)
    cdp["count"] = total_cdp_entries
    cdp["data"] = df

    return cdp
