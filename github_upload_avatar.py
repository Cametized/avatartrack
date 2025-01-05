import requests
import time

ROBLOX_USER_ID = 'PUT YOUR USE HEREEE'
DISCORD_WEBHOOK_URL = 'PUT YOUR WEBHOOK HEREEE'

ROBLOX_AVATAR_API_URL = f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=7554529574&size=150x150&format=Png&isCircular=false'

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_current_avatar_url():
    response = requests.get(ROBLOX_AVATAR_API_URL, headers=HEADERS)
    data = response.json()
    
    if response.status_code == 200 and data.get('data'):
        return data['data'][0]['imageUrl']
    else:
        print(f"Error fetching avatar: {data}")
        return None

# Function to send a message to Discord
def send_discord_webhook(old_avatar_url, new_avatar_url):
    embed = {
        "title": "Roblox Avatar Change Detected!",
        "description": f"User's avatar has changed.",
        "color": 15258703,
        "fields": [
            {"name": "Old Avatar", "value": f"[View Old Avatar]({old_avatar_url})"},
            {"name": "New Avatar", "value": f"[View New Avatar]({new_avatar_url})"}
        ],
        "thumbnail": {
            "url": new_avatar_url
        }
    }

    data = {
        "content": "An avatar change was detected!",
        "embeds": [embed]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    
    if response.status_code == 204:
        print("Notification sent successfully.")
    else:
        print(f"Error sending webhook: {response.status_code}, {response.text}")

def track_avatar_changes(interval=60):
    previous_avatar_url = get_current_avatar_url()
    
    if not previous_avatar_url:
        print("Unable to fetch the initial avatar. Exiting.")
        return
    
    print("this is totally spyware that gives me his logins and not the avatar tracker")

    while True:
        time.sleep(interval)
        current_avatar_url = get_current_avatar_url()
        
        if not current_avatar_url:
            print("Error fetching current avatar. Retrying...")
            continue

        if current_avatar_url != previous_avatar_url:
            print(f"Avatar changed: {current_avatar_url}")
            send_discord_webhook(previous_avatar_url, current_avatar_url)
            previous_avatar_url = current_avatar_url
        else:
            print("No changes detected.")

# Start tracking
track_avatar_changes(interval=5)  # Check every 60 seconds
