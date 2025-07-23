import os
import requests
from dotenv import load_dotenv
import json
from collections import defaultdict
import datetime
from nanoleafapi import Nanoleaf, NanoleafDigitalTwin
import time

load_dotenv()

API_KEY = os.getenv('BUNGIE_API_KEY')
MEMBERSHIP_TYPE = os.getenv('MEMBERSHIP_TYPE', 3)  # Default to 3 (Steam)
MEMBERSHIP_ID = os.getenv('MEMBERSHIP_ID')
CHARACTER_ID = os.getenv('CHARACTER_ID')

HEADERS = {
    'X-API-Key': API_KEY
}

BASE_URL = 'https://www.bungie.net/Platform/Destiny2'

nanoleaf_ip = os.getenv("NANOLEAF_IP") # Replace with the Nanoleaf's IP
auth_token = os.getenv("NANOLEAF_API_KEY")  # Replace with your actual token or leave as None to generate a new one
#############################################################################################
#                                        METHODS                                            #
#############################################################################################
def get_user_info(bungie_id):
    url = f"{BASE_URL}/User/GetBungieNetUserById/{bungie_id}/"
    print(url)
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def get_membership():
    url = f"{BASE_URL}/SearchDestinyPlayer/{MEMBERSHIP_TYPE}/{MEMBERSHIP_ID}/"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def get_profile():
    url = f"{BASE_URL}/{MEMBERSHIP_TYPE}/Profile/{MEMBERSHIP_ID}/?components=100,200"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def get_character(character_id):
    url = f"{BASE_URL}/{MEMBERSHIP_TYPE}/Profile/{MEMBERSHIP_ID}/Character/{character_id}/?components=200,205"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def get_loadout(character_id):
    url = f"{BASE_URL}/{MEMBERSHIP_TYPE}/Profile/{MEMBERSHIP_ID}/Character/{character_id}/?components=205"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def get_subclass(character_id):
    url = f"{BASE_URL}/{MEMBERSHIP_TYPE}/Profile/{MEMBERSHIP_ID}/Character/{character_id}/?components=205"
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    subclass = None
    try:
        equipment = data['Response']['equipment']['data']['items']
        for item in equipment:
            # Destiny 2 subclasses have bucketHash 3284755031
            if item.get('bucketHash') == 3284755031:
                subclass = item
                break
    except (KeyError, TypeError):
        pass
    return subclass

def get_item(item_hash):
    url = f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/{item_hash}/"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

def get_sublcass_info(char_id):
    subclass_name = get_item(get_subclass(char_id)['itemHash'])['Response']['displayProperties']['name']
    subclass_color = get_item(get_subclass(char_id)['itemHash'])['Response']['backgroundColor']
    return {"subclass_name": subclass_name, "subclass_color": subclass_color}

def set_subclass_color(target_color):
    if nl.set_color(target_color):
        print(f"Nanoleaf lights successfully set to RGB: {target_color}")
    else:
        print("Failed to set Nanoleaf lights color.")
    if nl.set_brightness(100):
        print(f"Nanoleaf lights successfully set to RGB: 100")
    else:
        print("Failed to set Nanoleaf lights color.")


if __name__ == "__main__":
    while True:
        char_list = get_profile()['Response']['characters']['data'].keys()
        
        guardian_dict = {}
        for i, guardian in enumerate(char_list):
            curr_char = get_character(guardian)
            last_played = curr_char['Response']['character']['data']['dateLastPlayed']
            g_class = ""
            if i ==0:
                g_class = 'Titan'
            elif i ==1:
                g_class = "Hunter"
            else:
                g_class = "Warlock"
        
            curr_subclass = get_sublcass_info(guardian)
            guardian_dict[g_class] = {"subclass": curr_subclass['subclass_name'], "lastPlayed": last_played, "isActiveGuardian":False, "color": curr_subclass['subclass_color']} 
        
            # print(f"{g_class}:\n  -Subclass: {curr_subclass}\n  -Last Played: {last_played}")
        
        titan_time = datetime.datetime.strptime(guardian_dict['Titan']['lastPlayed'][:-1], "%Y-%m-%dT%H:%M:%S")
        warlock_time = datetime.datetime.strptime(guardian_dict['Warlock']['lastPlayed'][:-1], "%Y-%m-%dT%H:%M:%S")
        hunter_time = datetime.datetime.strptime(guardian_dict['Hunter']['lastPlayed'][:-1], "%Y-%m-%dT%H:%M:%S")
        titan_delta_time = datetime.datetime.now() - titan_time
        warlock_delta_time = datetime.datetime.now() - warlock_time
        hunter_delta_time = datetime.datetime.now() - hunter_time
        
        if titan_delta_time < warlock_delta_time and titan_delta_time < hunter_delta_time:
            guardian_dict['Titan']['isActiveGuardian'] = True
            guardian_dict['Warlock']['isActiveGuardian'] = False
            guardian_dict['Hunter']['isActiveGuardian'] = False
        elif warlock_delta_time < titan_delta_time and warlock_delta_time < hunter_delta_time:
            guardian_dict['Titan']['isActiveGuardian'] = False
            guardian_dict['Warlock']['isActiveGuardian'] = True
            guardian_dict['Hunter']['isActiveGuardian'] = False
        elif hunter_delta_time < titan_delta_time and hunter_delta_time < warlock_delta_time:
            guardian_dict['Titan']['isActiveGuardian'] = False
            guardian_dict['Warlock']['isActiveGuardian'] = False
            guardian_dict['Hunter']['isActiveGuardian'] = True
        
        for k,v in guardian_dict.items():
            if v['isActiveGuardian'] == True:
                print(v['color'])
                target_color = (v['color']['red'], v['color']['green'], v['color']['blue'])
                set_subclass_color(target_color)

        time.sleep(10)