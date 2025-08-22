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
__copyright__ = "Copyright (c) {{current_year}} Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import datetime
import logging
import re
import urllib3
from requests.auth import HTTPBasicAuth
from time import perf_counter as time
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
import catc_api as catc_api
from dnac_config import (
    BAD_REQUEST,
    COMMAND,
    DATE_FORMAT,
    DNAC_URL_REGION1,
    DNAC_PASS_REGION1,
    DNAC_USER_REGION1
)

urllib3.disable_warnings(InsecureRequestWarning)


def get_query_list(device_list, token, catc_region, query_list):
    """
    This function check all devices for config query lines
    :param device_list: all devices in DNA Center inventory
    :param token: authentication token
    :param catc_region: DNA Center Region
    :return: list of devices where config query lines were present
    """
    for item in device_list:
        query = {}
        logging.info("item {}".format(item))
        pattern_pid = re.compile("[A]{1}[I]{1}[R]{1}")
        logging.info("pattern_pid {}".format(pattern_pid))
        if item["platform"]:
            output_platform = pattern_pid.findall(item["platform"])
            logging.info(
                "output_platform {} len output platform {}".format(
                    output_platform, len(output_platform)
                )
            )
            if len(output_platform) == 1 and output_platform[0] == "AIR":
                logging.info("AIROS")
                AIROS = True
                IOSXE = False
            else:
                IOSXE = True
                AIROS = False
            logging.info("Reachable: {}".format(item["reachability"]))
            logging.info("Iosxe: {}".format(IOSXE))
            if (
                item["reachability"] == "Reachable"
                and IOSXE
                #and item["family"] == "Wireless Controller" # Filtering by wireless controller
            ):
                query_config, query_length = catc_api.get_output_command_runner(
                    COMMAND, item["deviceId"], token, catc_region
                )
                logging.info(
                    f"Device Running Config {query_config}, Type:{type(query_config)}, Length: {query_length}"
                )
                if query_length >= 1:
                    logging.info(f"{query_config[COMMAND]}")
                if (
                    query_config == ""
                    or BAD_REQUEST in query_config
                    or len(query_config) == len(COMMAND) + 1
                ):
                    logging.error("{} does not contain data".format(query_config))
                else:
                    if query_length >= 1:
                        logging.info(
                            f"RESULT: {query_config[COMMAND]}, TYPE OF RESULT:{type(query_config[COMMAND])}"
                        )
                    query["username"] = DNAC_USER_REGION1
                    query["config_query"] = COMMAND
                    if query_length >= 1:
                        logging.info(f"{query_config[COMMAND]}")
                        query["result"] = catc_api.parse_cdp_neighbor_output(
                            query_config[COMMAND]
                        )
                    query["hostname"] = item["hostname"]
                    query["reachabilityStatus"] = item["reachability"]
                    query["family"] = item["family"]
                    query["platform"] = item["platform"]
                    query["managementIpAddress"] = item["managementIpAddress"]
                    query_list.append(query)
    return query_list


if __name__ == "__main__":
    status = True
    query_list = []
    startTime = time()
    logging.basicConfig(
        # If you want to keep track in log then open this commented out application_run.log file
        filename=f"cdp_run_{datetime.datetime.now().strftime(DATE_FORMAT)[:-3]}.log",
        # Logging INFO, ERROR, DEBUG
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    dnac_auth1 = HTTPBasicAuth(DNAC_USER_REGION1, DNAC_PASS_REGION1)
    start = time()
    logging.info(start)
    bearer_token1 = catc_api.get_dnac_jwt_token(dnac_auth1, DNAC_URL_REGION1)
    total = catc_api.get_network_device_count(bearer_token1, DNAC_URL_REGION1)
    logging.info("Total number of Devices: {}".format(total))
    device_list = catc_api.get_network_device_list(
        bearer_token1, DNAC_URL_REGION1, total
    )
    logging.info("Device_list: {}".format(device_list))
    end = time()
    total_time = end - start
    logging.info(f"Completed in: {total_time} seconds.")
    q_list = get_query_list(device_list, bearer_token1, DNAC_URL_REGION1, query_list)
    logging.info("Query list: {}".format(q_list))
    # Iterate through each entry in the query_list
    for i, query_entry in enumerate(query_list):
        logging.info(
            f"{i + 1}. Hostname: {query_entry['hostname']}) - IP: {query_entry['managementIpAddress']}\n"
        )
        if "result" in query_entry and "data" in query_entry["result"]:
            cdp_dataframe = query_entry["result"]["data"]
            logging.info(cdp_dataframe[["Device ID", "Local Intrfce", "Port ID"]])
            logging.info("-" * 30)
    finish = time()
    complete_time = finish - start
    command_runner_time = finish - end
    logging.info(
        f"Full run completed in: {complete_time} seconds and command_runner_time {command_runner_time}"
    )
