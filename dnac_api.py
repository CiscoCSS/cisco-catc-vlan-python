"""

Copyright (c) 2018 Cisco and/or its affiliates.

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
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import json
import logging
import requests
import urllib3
from dnac_config import LIMIT
from math import ceil
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings
RESPONSE_KEY = "response"
DATA_JSON = "application/json"
RESPONSE_CODE = "Response code: {}"
RESPONSE_IN_JSON = "Response in JSON: {}"


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
        logging.errorrint(err)
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
    region_url = url + f"/dna/intent/api/v1/network-device"
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
        # network-device api does not have a rate limit, sharing rate limit handling with you. This is useful when
        # API's are restricted with rate_limit, slide 13 has an example of Automation Workshopv1.0.pdf
        # if devices_response.status_code == 429:
        # time.sleep(WAIT_TIME)
        # get_inventory(url, offset, token, total, device_list)
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


def get_device_interface(auth_token, url, did):
    """
    This function gets device interface
    :param auth_token: DNAC authentication token
    :param url: DNAC region url
    :param did: device id
    :return:
    """
    device_interface = []
    logging.info(f"did: {did}, type(did):{type(did)}")
    region_url = url + f"/dna/intent/api/v1/network-device/{did}/vlan"
    header = {"content-type": DATA_JSON, "x-auth-token": auth_token}

    try:
        id_response = requests.get(region_url, headers=header, verify=False)
        logging.info(RESPONSE_CODE.format(id_response.status_code))
        logging.info(RESPONSE_IN_JSON.format(json.dumps(id_response.json(), indent=4)))
        if id_response.status_code == 200:
            device_json = id_response.json()
            for item in device_json.get("response"):
                device = {}
                device["interfaceName"] = item.get("interfaceName")
                device_interface.append(device)
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
    return device_interface


def get_device_vlan(token, dnac_url_region, dev_list):
    """
    This function gets vlan for all devices
    :param token: DNAC authentication token
    :param dnac_url_region: dnac region url
    :param dev_list: device list
    :return: device vlan list
    """
    data = {}
    device_vlan = []
    logging.info(f"{type(dev_list)} dev_list:{dev_list}")
    for item in dev_list:
        device_id = item.get("deviceId")
        management_ip = item.get("managementIpAddress")
        hostname = item.get("hostname")
        if "unknown" not in device_id:
            vlan = get_device_interface(token, dnac_url_region, device_id)
            data = item
            data["vlan"] = vlan
            device_vlan.append(data)
    logging.info(f"device_vlan:{device_vlan}, size: {len(device_vlan)}")
    return device_vlan


def logout(dnac_url, dnac_jwt_token):
    """
    Logout from DNAC
    :param dnac_url: dnac url
    :param dnac_jwt_token: token
    :return:
    """
    headers = {"content-type": "application/json", "x-auth-token": dnac_jwt_token}
    url = dnac_url + "/logout?nocache"
    response = requests.get(url, headers=headers, verify=False)
    if response.ok:
        logging.info("logout")
