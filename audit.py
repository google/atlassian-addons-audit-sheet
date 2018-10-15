#!/usr/local/bin/python3

# Copyright 2018 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import requests
import json
import re
import pygsheets
from pprint import pprint
import httplib2
http_client = httplib2.Http(timeout=100)
# import configuration file
import config_audit as config

from datetime import datetime, timezone
from time import strftime, localtime

timestamp = datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')

parser = argparse.ArgumentParser(description='Audit Atlassian Add-Ons.')
parser.add_argument('hosts', metavar='hosts', type=str, nargs='+',
                    help='Select target host(s): jira, confluence, stash, or all')

args = parser.parse_args()

# Shared details
user = config.jira_credentials['user']
password = config.jira_credentials['password']
headers = {'X-Atlassian-Token': 'nocheck'}
marketurl = 'https://marketplace.atlassian.com/'

# Google Sheets details
client = pygsheets.authorize(http_client=http_client)

sheet_url = config.google_sheet_url

ss = client.open_by_url(sheet_url)

targets = {}

possibletargets = {'Confluence': config.target_url['confluence'],
	'JIRA': config.target_url['jira'],
	'Stash': config.target_url['stash']}

for i in args.hosts:
	if i == 'jira':
		targets['JIRA'] = possibletargets['JIRA']

	if i == 'confluence':
		targets['Confluence'] = possibletargets['Confluence']

	if i == 'stash':
		targets['Stash'] = possibletargets['Stash']

	if i == 'all':
		targets = possibletargets

for worksheet, base_url in targets.items():
	
	sheet = ss.worksheet_by_title(worksheet)
	
	# Get all the plugins recorded in sheet, to be checked later for disabled plugins (diff against installed)
	sheetplugins = sheet.get_values(start=(2,2), end=(99,2), returnas='matrix', include_empty=False, include_all=False)

	recorded = []

	for sheetrow in sheetplugins:
		recorded.append(sheetrow[0])
	sheetkeys = recorded
	recorded = sorted(recorded)

	# Connect to Confluence, get the plugins
	plugins_url = base_url + 'rest/plugins/1.0/?os_authType=basic'
	
	r = requests.get(plugins_url, auth=(user, password), headers=headers)
	data = json.loads(r.text)
	allplugins = sorted(data["plugins"], key=lambda k: k['name'])
	
	# Iterate through the plugins

	installed = []

	for plugin in allplugins:
		if plugin["enabled"] and plugin["userInstalled"]:
			name = plugin["name"]
			description = plugin.get("description")
			current = plugin["version"]
			pluginkey = plugin["key"]

			installed.append(pluginkey)

			marketplacelink = marketurl + 'plugins/' + pluginkey + '/server/overview'
	
			expiry = 'N/A'
			sen = 'N/A'
	
	# Check if it is a Marketplace plugin
	
			addonslink = marketurl + "rest/2/addons/" + pluginkey 
			r = requests.get(addonslink)
	
			if r.status_code == 404:
				_2000 = _10000 = unlimited = latest = datacenter = "N/A"
	
			else:
				addon = json.loads(r.text)
				if "pricing" in addon["_links"]:
	
					r = requests.get(addonslink + "/pricing/server/live")
	
					if r.status_code == 404:
						_2000 = _10000 = unlimited = "N/A"
	
					else:
						pricedata = json.loads(r.text)
						_2000 = pricedata["items"][6]["amount"]
						_10000 = pricedata["items"][7]["amount"] 
						unlimited = pricedata["items"][7]["amount"]
	
	# Check current license expiration
	
					license_url = base_url + 'rest/plugins/1.0/' + pluginkey + '-key/license?os_authType=basic'
	
					r = requests.get(license_url, auth=(user, password), headers=headers)
	
					licensedata = json.loads(r.text)
	
					if "maintenanceExpiryDate" in licensedata:
						licensestamp = datetime.fromtimestamp(int(licensedata["maintenanceExpiryDate"]/1e3))
						expiry = licensestamp.strftime('%m/%d/%Y')

					if "supportEntitlementNumber" in licensedata:
						sen = licensedata["supportEntitlementNumber"]
	
				else:
					_2000 = _10000 = unlimited = "free"
	
				r = requests.get(addonslink + "/versions")
				versions = json.loads(r.text)
	
				for version in versions['_embedded']['versions']:
					if version['deployment']['server']:
						latest = version['name']
						datacenter = version['deployment']['dataCenter']
						break


			print(name)
			print("	" + description)
			print("	" + pluginkey)
			print("	" + current)
#			print("	" + latest)
#			print("	" + marketplacelink)
#			print("	" + str(_2000))
#			print("	" + str(_10000))
#			print("	" + str(unlimited))
			print("	" + expiry)

			if pluginkey in sheetkeys:
				row = sheetkeys.index(pluginkey) + 2

			else:
				sheet.insert_rows(1, number=1, values=None, inherit=False)
				sheetkeys.insert(0, pluginkey)
				row = 2

#				# Unstrikethrough if previously disabled - super slow
				# keycell[0].set_text_format('strikethrough', False) 
				# keycell[0].set_text_alignment('TOP', True) # for some reason set_text_format resets alignment

				# unstrikename = sheet.cell('A' + str(row))
				# unstrikename.set_text_format('strikethrough', False) 
				# unstrikename.set_text_alignment('TOP', True) 
	
			range = 'A' + str(row) + ':K' + str(row)
	
			hyperlink = '=HYPERLINK("' + marketplacelink + '", "' + name + '")'
	
			cell_list = [hyperlink]
			cell_list.append(pluginkey)
			cell_list.append(sen)
			cell_list.append(description)
			cell_list.append(str(current))
			cell_list.append(str(latest))
			cell_list.append(expiry)
			cell_list.append(_2000)
			cell_list.append(_10000)
			cell_list.append(unlimited)
			cell_list.append(datacenter)
			outer_cell = [cell_list]
	
			sheet.update_cells(crange=range, values=outer_cell)

	# Strikethrough disabled plugins

	disabled = list(set(recorded) - set(installed))

	print('Disabled:')
	pprint(disabled)

	for strikekey in disabled:
		strikerow = sheetkeys.index(strikekey) + 2
		strikecell = sheet.cell((strikerow,1))

		strikename = sheet.cell('A' + str(strikerow))
		strikename.set_text_format('strikethrough', True) 
		strikename.set_text_alignment('TOP', True) 

		if strikename.note == '':
			strikename.note = 'Disabled: ' + timestamp

	# Add a timestamp
	sheet.update_cell('A1', worksheet + ' Plugins Updated:\n' + timestamp)
