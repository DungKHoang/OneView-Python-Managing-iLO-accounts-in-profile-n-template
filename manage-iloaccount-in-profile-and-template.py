# ---------------------------------------------------------------------------------------------------------------------------
# Copyright 2018 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from pprint import pprint
import json
import copy
import csv
import requests
from requests.auth import AuthBase

import os
from os import sys
import requests
import re

#from config_loader import try_load_from_file
#from configloader import ConfigLoader

from hpOneView.exceptions import HPOneViewException
from hpOneView.oneview_client import OneViewClient

TABSPACE        = "    "
COMMA           = ','
CR              = '\n'
CRLF            = '\r\n'
IC_OFFSET       = 3         # Used to calculate bay number from InterconnectBaySet
                            # InterconnectBaySet = 1 ---> Bay 1  and Bay 4
                            # InterconnectBaySet = 2 ---> Bay 1  and Bay 5
                            # InterconnectBaySet = 3 ---> Bay 1  and Bay 6



def add_iLO_account(PROFILE):
    ####      iLO region
    PROFILE.update(managementProcessor            = dict())
    PROFILE['managementProcessor'].update(manageMp                       = True)
    PROFILE['managementProcessor'].update(mpSettings =  [])




    account               = dict()
    account.update(userName     = 'user1')
    account.update(displayName  = 'user1_display_name')
    account.update(password     = 'P@ssword1')
    account.update(userConfigPriv = True)
    account.update(remoteConsolePriv = True)
    account.update(virtualMediaPriv = True)
    account.update(virtualPowerAndResetPriv = True)
    account.update(loginPriv = True)
    account.update(iLOConfigPriv = True)
    account.update(hostBIOSConfigPriv = True)
    account.update(hostNICConfigPriv = True)
    account.update(hostStorageConfigPriv = True)


    mpSettings_element    = dict()
    mpSettings_element.update(settingType = 'LocalAccounts')
    mpSettings_element.update(args         = dict())
    mpSettings_element['args'].update(localAccounts  = [])
    mpSettings_element['args']['localAccounts'].append(account)


    PROFILE['managementProcessor']['mpSettings'].append(mpSettings_element)

    return PROFILE




CONFIG = {
    "api_version": 1000,
    "ip": "192.168.1.51",
    "credentials": {
        "userName": "administrator",
        "password": "password"
    }
}



config_file = '/home/dung/configFiles/oneview_config.json'
with open(config_file) as json_data:
    config = json.load(json_data)
oneview_client = OneViewClient(config)

oneview_client = OneViewClient(CONFIG)

spt_name                                    = 'AA-spt-iLO'
#===================Attributes for server-profile-templates AA-spt-iLO ========================
PROFILE                                      = dict()
PROFILE.update(name                          = spt_name)
PROFILE.update(type                          = 'ServerProfileTemplateV6')
PROFILE.update(affinity                      = 'Bay')
PROFILE.update(hideUnusedFlexNics            = True)


sht                                          = oneview_client.server_hardware_types.get_by_uri('/rest/server-hardware-types/7D886C43-03ED-4A76-B3BA-7F0096B79E89')
PROFILE.update(serverHardwareTypeUri         = '/rest/server-hardware-types/7D886C43-03ED-4A76-B3BA-7F0096B79E89')
eg_uri                                       = oneview_client.enclosure_groups.get_by('name', 'EG 3 frames')[0]['uri']
PROFILE.update(enclosureGroupUri             = eg_uri)
add_iLO_account(PROFILE)

# ---------------------------------------
#  Creating server-profile-templates ---> AA-spt-iLO
# Remove commnent oif you want to create a new template
#spt      = oneview_client.server_profile_templates.create(PROFILE)

# ---------------------------------------
# Update spt to add iLO account
# X-API-version muste be 1000 ( OV 4.20)
spt                                          = oneview_client.server_profile_templates.get_by_name(spt_name) 
PROFILE                                      = spt.data.copy()
add_iLO_account(PROFILE)

spt_update                                   =  spt.update(PROFILE)
print(json.dumps(PROFILE, indent=4))

# ---------------------------------------
# Update sp to add iLO account
# X-API-version muste be 1000 ( OV 4.20)

sp_name                                     = 'AA-sp-iLO'
sp                                          =   oneview_client.server_profiles.get_by_name(sp_name) 
PROFILE                                     = sp.data.copy()
add_iLO_account(PROFILE)

sp_update                                   =  sp.update(PROFILE)
print(json.dumps(PROFILE, indent=4))

