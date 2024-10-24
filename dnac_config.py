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

#Please note using clear text username and password is not a good practice. This is only for demo purpose.
#Always use encryption and or Vault. Rely on your Business Security Policy. This is not secured.
#Please modify this file to run correctly pointing to sandbox or lab setup that you are using.
DNAC_URL_REGION1 = '<<https://catalystcenteripaddress>>' #Change this to your lab environment
DNAC_USER_REGION1 = '<<change this you username plain text>>'
DNAC_PASS_REGION1 = '<<change this your password plain text for same url region1>>'
LIMIT = 5    #you can change this 500 to scale up on how many devices it queries that api will accommodate
WAIT_TIME = 60 * 60 #wait time modifiable per your requirements. First try with same.
DATEFORMAT = '%m-%d-%Y_%H%M%S.%f'
REPORT_DIR = '<</absolute path to this vlan folder that holds the code base>>'
REPORT_NAME = "VlanReport"#You canmodify name of the report, if you do then please modify name of the log file vlan_run on vlan.py to match, if you like log file and report to have same name.
