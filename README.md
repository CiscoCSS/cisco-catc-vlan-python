# cisco-catc-vlan-python
**Catalyst Center Device Interface Query Report:**

**Use Case:** Query Catalyst Center devices for their assoicated vlans and generate csv report. Sequential execution.

**Solution:** A sequential query to Catalyst over it all it's devices and identify the one with it's associated vlan's and 
generate a csv report.

**Result:** Successful vlan query of DNA Center Devices in bulk sequentially in 5 seconds for 15 devices. Performance of the
script estimate: If any production enviroment has 2000 devices then it will execute (depending on your internet speed is
same as 5.53 seconds) in 12.29 minutes estimated. If internet speed is slower it will execute slower than estimated 
above, if faster it will execute faster. This script scales to generate report.

**Example:** vlan_run_0.993519977.log 2023-05-19 16:42:22.507 INFO: Print Network Device List 
{'device_total_count': 15, 'devices': [{'hostname': 'A...2C', 'role': 'ACCESS', 'reachability': 'Reachable', 'family': 
'Unified AP', 'platform': 'AIR-AP4800-B-K9', 'managementIpAddress': '172.x.x.x', 
'deviceId': '20e226ef-dfe5-4982-99be-5937b6bfec04'}... {'hostname': 'R...sspod2.com', 'role': 'BORDER ROUTER', 
'reachability': 'Reachable', 'family': 'Routers', 'platform': 'CSR1000V', 'managementIpAddress': '192.x.x.x', 
'deviceId': 'e4f45e71-bbf2-4bc8-97aa-1e2c4b7cb0de'}]} 2023-05-19 16:42:26.600 INFO: Completed in: 5.536824585 seconds.

**Pre-requisite:** 
Python 3.8+. If python is not installed, please follow: https://www.python.org/downloads/
▪ pip3 or pip installed. If pip3 is not installed, please follow instructions at: 
https://pip.pypa.io/en/stable/installing/virtualenv installed
▪ If virtualenv not installed already, install through bash$ pip3 install virtualenv. Follow this for further 
instructions: https://pypi.org/project/virtualenv/
▪ git installed ◦if git is not installed, please try referring: https://git-scm.com/downloads
Operating System: Linux based OS or windows or mac

**Setup:** 
▪python3 -m venv demoenv ▪source demo_env/bin/activate Run the command below with pip or pip3
▪pip install --upgrade pip
▪pip install -r requirements.txt or run make install on Makefile it will achieve the same.

**Installation:**
Git clone: git clone https://github.com/CiscoDevNet/cisco-catc-vlan-python.git
Go to your project folder
cd vlan
Set up a Python venv First make sure that you have Python 3 installed on your machine. We will then be using venv to create an isolated environment with only the necessary packages.
Install virtualenv via pip
pip install virtualenv
Create the venv
python3 -m venv venv
Activate your venv
source venv/bin/activate
Install dependencies: pip install -r requirements.txt or run make install on Makefile it will achieve the same.

**Usage:** 
Step I. Modify dnac_config.py file. Change the variables below per your environment.
DNAC_URL_REGION1 = '<<https://catalystcenteripaddress'>> Change this to your lab environment
DNAC_USER_REGION1 = '<<change this you username plain text>>'
DNAC_PASS_REGION1 = '<<change this your password plain text for same url region1>>'
LIMIT = 5    #you can change this 500 to scale up on how many devices it queries that api will accommodate, please check on your specific release and catalyst center api. 
WAIT_TIME = 60 * 60 #wait time modifiable per your requirements. First try with same.
DATEFORMAT = '%m-%d-%Y_%H%M%S.%f' 
REPORT_DIR = '<</absolute path to this vlan folder that holds the code base>>'
REPORT_NAME = "VlanReport" # You can modify name of the report

Step II. Run - python vlan.py and test, if it picks up all vlans and generates a csv file. Validate. 
You should see a VlanReport_timestamp.csv file and vlan_run_timestamp.log file gets generated. Check the log file and
csv file and validate output against your environment.

**Recommend:** Extensive testing in your lab against all scenarios. Check if it picks up all devices and it's associated. 

**Cisco Sample Code License, Version 1.1**
These terms govern this Cisco Systems, Inc. (“Cisco”), example or demo source code and its associated documentation (together, the “Sample Code”). By downloading, copying, modifying, compiling, or redistributing the Sample Code, you accept and agree to be bound by the following terms and conditions (the “License”). If you are accepting the License on behalf of an entity, you represent that you have the authority to do so (either you or the entity, “you”). Sample Code is not supported by Cisco TAC and is not tested for quality or performance. This is your only license to the Sample Code and all rights not expressly granted are reserved.

1. LICENSE GRANT: Subject to the terms and conditions of this License, Cisco hereby grants to you a perpetual, worldwide, non-exclusive, non-transferable, non-sublicensable, royalty-free license to copy and modify the Sample Code in source code form, and compile and redistribute the Sample Code in binary/object code or other executable forms, in whole or in part, solely for use with Cisco products and services. For interpreted languages like Java and Python, the executable form of the software may include source code and compilation is not required.

2. CONDITIONS: You shall not use the Sample Code independent of, or to replicate or compete with, a Cisco product or service. Cisco products and services are licensed under their own separate terms and you shall not use the Sample Code in any way that violates or is inconsistent with those terms (for more information, please visit: www.cisco.com/go/terms ).

3. OWNERSHIP: Cisco retains sole and exclusive ownership of the Sample Code, including all intellectual property rights therein, except with respect to any third-party material that may be used in or by the Sample Code. Any such third-party material is licensed under its own separate terms (such as an open source license) and all use must be in full accordance with the applicable license. This License does not grant you permission to use any trade names, trademarks, service marks, or product names of Cisco. If you provide any feedback to Cisco regarding the Sample Code, you agree that Cisco, its partners, and its customers shall be free to use and incorporate such feedback into the Sample Code, and Cisco products and services, for any purpose, and without restriction, payment, or additional consideration of any kind. If you initiate or participate in any litigation against Cisco, its partners, or its customers (including cross-claims and counter-claims) alleging that the Sample Code and/or its use infringe any patent, copyright, or other intellectual property right, then all rights granted to you under this License shall terminate immediately without notice.

4. LIMITATION OF LIABILITY: CISCO SHALL HAVE NO LIABILITY IN CONNECTION WITH OR RELATING TO THIS LICENSE OR USE OF THE SAMPLE CODE, FOR DAMAGES OF ANY KIND, INCLUDING BUT NOT LIMITED TO DIRECT, INCIDENTAL, AND CONSEQUENTIAL DAMAGES, OR FOR ANY LOSS OF USE, DATA, INFORMATION, PROFITS, BUSINESS, OR GOODWILL, HOWEVER CAUSED, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/CiscoCSS/cisco-catc-vlan-python)

6. DISCLAIMER OF WARRANTY: SAMPLE CODE IS INTENDED FOR EXAMPLE PURPOSES ONLY AND IS PROVIDED BY CISCO “AS IS” WITH ALL FAULTS AND WITHOUT WARRANTY OR SUPPORT OF ANY KIND. TO THE MAXIMUM EXTENT PERMITTED BY LAW, ALL EXPRESS AND IMPLIED CONDITIONS, REPRESENTATIONS, AND WARRANTIES INCLUDING, WITHOUT LIMITATION, ANY IMPLIED WARRANTY OR CONDITION OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, SATISFACTORY QUALITY, NON-INTERFERENCE, AND ACCURACY, ARE HEREBY EXCLUDED AND EXPRESSLY DISCLAIMED BY CISCO. CISCO DOES NOT WARRANT THAT THE SAMPLE CODE IS SUITABLE FOR PRODUCTION OR COMMERCIAL USE, WILL OPERATE PROPERLY, IS ACCURATE OR COMPLETE, OR IS WITHOUT ERROR OR DEFECT.

7. GENERAL: This License shall be governed by and interpreted in accordance with the laws of the State of California, excluding its conflict of laws provisions. You agree to comply with all applicable United States export laws, rules, and regulations. If any provision of this License is judged illegal, invalid, or otherwise unenforceable, that provision shall be severed and the rest of the License shall remain in full force and effect. No failure by Cisco to enforce any of its rights related to the Sample Code or to a breach of this License in a particular situation will act as a waiver of such rights. In the event of any inconsistencies with any other terms, this License shall take precedence.

Last updated January 26, 2018vlan. Modify code to fit your environment. 
