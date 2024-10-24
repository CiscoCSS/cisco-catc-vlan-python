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

import os
import pandas as pd
from datetime import datetime
from dnac_config import REPORT_DIR, REPORT_NAME


DATEFORMAT = "%m-%d-%Y_%H%M%S.%f"


def build_report(result):
    """
    This function creates a report on result
    :param: device_vlan list
    :return:
    """
    current = datetime.utcnow().strftime(DATEFORMAT)[:-3]
    query_report = REPORT_DIR + os.sep + REPORT_NAME + "_" + current + ".csv"
    list_to_csv(result, query_report)


def list_to_csv(data, filename):
    """
    This function covnerts list to csv file
    :param data: data
    :param filename: full path csv filename
    :return: no return value
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
