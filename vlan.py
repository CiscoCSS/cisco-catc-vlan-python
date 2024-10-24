#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Copyright (c) 2021 Cisco and/or its affiliates.

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

import logging
import urllib3
from datetime import datetime
from requests.auth import HTTPBasicAuth
from time import perf_counter as time
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
import dnac_api as dnac_api
import util as util
from dnac_config import DNAC_URL_REGION1, DNAC_PASS_REGION1, DNAC_USER_REGION1

urllib3.disable_warnings(InsecureRequestWarning)

DATEFORMAT = "%m-%d-%Y_%H%M%S.%f"


if __name__ == "__main__":
    status = True
    startTime = time()
    logging.basicConfig(
        # If you want to keep track in log then open this commented out application_run.log file
        filename="vlan_run_" + datetime.utcnow().strftime(DATEFORMAT)[:-3] + ".log",
        # Logging INFO, ERROR, DEBUG
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    dnac_auth1 = HTTPBasicAuth(DNAC_USER_REGION1, DNAC_PASS_REGION1)
    start = time()
    logging.info(start)
    bearer_token1 = dnac_api.get_dnac_jwt_token(dnac_auth1, DNAC_URL_REGION1)
    total = dnac_api.get_network_device_count(bearer_token1, DNAC_URL_REGION1)
    logging.info("Total number of Devices: {}".format(total))
    device_list = dnac_api.get_network_device_list(
        bearer_token1, DNAC_URL_REGION1, total
    )
    logging.info("Device_list: {}".format(device_list))
    vlan_list = dnac_api.get_device_vlan(bearer_token1, DNAC_URL_REGION1, device_list)

    util.build_report(vlan_list)
    dnac_api.logout(DNAC_URL_REGION1, bearer_token1)
    end = time()
    logging.info("Completed in: {} seconds.".format(end - start))
