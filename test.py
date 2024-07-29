import json
import datetime

# Function to convert Unix timestamp to human-readable date
def convert_timestamp(timestamp):
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    return dt_object.strftime('%Y-%m-%d %H:%M:%S')

# Load the JSON data from the files
with open('following.json', 'r') as file:
    following_data = json.load(file)

with open('followers_1.json', 'r') as file:
    followers_data = json.load(file)

with open('pending_follow_requests.json', 'r') as file:
    pending_requests_data = json.load(file)

with open("follow_requests_you've_received.json", 'r') as file:
    received_requests_data = json.load(file)

# Extract the Instagram usernames from each file
# following_usernames = {entry['string_list_data'][0]['value'] for entry in following_data}

entries = following_data["relationships_following"]
following_usernames = {entry['string_list_data'][0]['value'] for entry in entries}

followers_usernames = {entry['string_list_data'][0]['value'] for entry in followers_data}

# pending_requests_usernames = {entry['string_list_data'][0]['value'] for entry in pending_requests_data}
entries = pending_requests_data["relationships_follow_requests_sent"]
pending_requests_usernames={entry['string_list_data'][0]['value'] for entry in entries}

# received_requests_usernames = {entry['string_list_data'][0]['value'] for entry in received_requests_data}
entries = received_requests_data["relationships_follow_requests_received"]
received_requests_usernames={entry['string_list_data'][0]['value'] for entry in entries}

# Find the usernames that are in following but not in followers
not_following_back = following_usernames - followers_usernames
print(not_following_back)
# Find the usernames that are in followers but not in following
unknown_followers = followers_usernames - following_usernames

# Extract the data for not following back
not_following_back_data = [
    {
        "value": entry['string_list_data'][0]['value'],
        "href": entry['string_list_data'][0]['href'],
        "timestamp": convert_timestamp(entry['string_list_data'][0]['timestamp'])
    }
    for entry in following_data["relationships_following"] if entry['string_list_data'][0]['value'] in not_following_back
]
print(not_following_back_data)
# Extract the data for unknown followers
unknown_followers_data = [
    {
        "value": entry['string_list_data'][0]['value'],
        "href": entry['string_list_data'][0]['href'],
        "timestamp": convert_timestamp(entry['string_list_data'][0]['timestamp'])
    }
    for entry in followers_data if entry['string_list_data'][0]['value'] in unknown_followers
]

# Extract the data for pending follow requests
pending_requests_data = [
    {
        "value": entry['string_list_data'][0]['value'],
        "href": entry['string_list_data'][0]['href'],
        "timestamp": convert_timestamp(entry['string_list_data'][0]['timestamp'])
    }
    for entry in pending_requests_data["relationships_follow_requests_sent"]
]

# Extract the data for received follow requests
received_requests_data = [
    {
        "value": entry['string_list_data'][0]['value'],
        "href": entry['string_list_data'][0]['href'],
        "timestamp": convert_timestamp(entry['string_list_data'][0]['timestamp'])
    }
    for entry in received_requests_data["relationships_follow_requests_received"]
]
# Prepare the summary data
summary_data = {
    "Total Followers": len(followers_usernames),
    "Total Following": len(following_usernames),
    "Total Not Following Back": len(not_following_back),
    "Not Following Back": not_following_back_data,
    "Total Unknown Followers": len(unknown_followers),
    "Unknown Followers": unknown_followers_data,
    "Total Pending Follow Requests": len(pending_requests_usernames),
    "Pending Follow Requests": pending_requests_data,
    "Total Received Follow Requests": len(received_requests_usernames),
    "Received Follow Requests": received_requests_data
}

# Save the result to a new JSON file
summary_filename = 'summary.json'
with open(summary_filename, 'w') as summary_file:
    json.dump(summary_data, summary_file, indent=2)

print(f"Summary written to {summary_filename}")