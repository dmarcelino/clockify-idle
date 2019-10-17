import calendar
import configparser
from datetime import datetime
from datetime import timezone
import json
import os
import requests


config = configparser.ConfigParser()
config.read('config.ini')

if not config['clockify.me'].get('APIKey'):
    config['clockify.me']['APIKey'] = os.environ['CLOCKIFY_KEY']

API_KEY = config['clockify.me']['APIKey']
API_BASE = config['clockify.me']['APIBaseEndpoint']
NOW = datetime.now(timezone.utc)
# OUT_FILE = 'clockify_time-entries.json'


def get_headers(api_key):
    if not api_key:
        api_key = API_KEY
    return {
        "content-type": "application/json",
        "X-Api-Key": api_key,
    }


def get_workspaces(workspace_id=None):
    url = "{}{}".format(API_BASE, "/workspaces")
    headers = get_headers(API_KEY)
    response = requests.get(url, headers=headers)
    response_json = response.json()
    # print(json.dumps(response_json, indent=2, sort_keys=True))
    return response_json


def _set_from_config(time_entry, time_entry_key, config_key):
    config_value = config['time_entry'].get(config_key)
    if (config_value):
        time_entry[time_entry_key] = config_value


def get_new_time_entry():
    time_entry = {
        "start": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "billable": "true",
        # "description": "Writing documentation",
        # "projectId": "5b1667790cb8797321f3d664",
        # "taskId": "5b1e6b160cb8793dd93ec120",
        # "end": "2018-06-12T13:50:14.000Z",
        # "tagIds": [
        #  "5a7c5d2db079870147fra234"
        # ],
    }
    _set_from_config(time_entry, 'projectId', 'DefaultProjectId')
    _set_from_config(time_entry, 'billable', 'DefaultBillable')
    _set_from_config(time_entry, 'description', 'DefaultDescription')

    return time_entry


def send_time_entry(time_entry, entry_id=None):
    # check CACHE first
    workspaces = get_workspaces()
    workspace_id = workspaces[0]['id']
    headers = get_headers(API_KEY)

    url = "{}{}".format(API_BASE, "/workspaces/{}/time-entries".format(workspace_id))
    if entry_id:
        url = "{}/{}".format(url, entry_id)
        response = requests.put(url, json=time_entry, headers=headers)
    else:
        response = requests.post(url, json=time_entry, headers=headers)
    response_json = response.json()

    if response.status_code < 200 or response.status_code >= 300:
        print('ERROR while sending time entry, code: {}.'.format(response.status_code))
        print(json.dumps(response_json, indent=2, sort_keys=True))

    return response_json


# Helper method to get a range of datetimes representing beginning and end of month
def _get_month_datetime_range(month=NOW.month, year=NOW.year):
    start = datetime(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    last_day = calendar.monthrange(year, month)
    end = datetime(year=year, month=month, day=last_day[1],
                   hour=23, minute=59, second=59, microsecond=999, tzinfo=timezone.utc)
    return start, end


# Helper method to get the time entries for a given month
def get_time_entries(month=NOW.month, year=NOW.year):
    # try:
    #     with open(OUT_FILE) as json_file:
    #         response_json = json.load(json_file)
    # except FileNotFoundError:

    workspaces = get_workspaces()
    workspace_id = workspaces[0]['id']
    user_id = workspaces[0]['memberships'][0]['userId']
    # print("{}, {}".format(workspace_id, user_id))

    # 2nd request
    url = "{}{}".format(API_BASE,
                        "/workspaces/{workspace_id}/user/{user_id}/time-entries".format(workspace_id=workspace_id,
                                                                                        user_id=user_id))

    start, end = _get_month_datetime_range(month, year)
    params = {
        "start": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "hydrated": True,
    }
    headers = get_headers(API_KEY)

    response = requests.get(url, params=params, headers=headers)
    response_json = response.json()
    # print(json.dumps(response_json, indent=2, sort_keys=True))
    # with open(OUT_FILE, 'w') as outfile:
    #   json.dump(response_json, outfile)

    return response_json
