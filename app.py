from flask import Flask, render_template, request, jsonify
import json
import datetime
import os
import zipfile
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size for ZIP
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'json', 'zip'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_timestamp(timestamp):
    """Convert Unix timestamp to human-readable date"""
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    return dt_object.strftime('%Y-%m-%d %H:%M:%S')

def extract_json_from_zip(zip_file):
    """Extract required JSON files from Instagram ZIP archive"""
    try:
        # Read the ZIP file
        zip_data = zip_file.read()
        zip_buffer = io.BytesIO(zip_data)
        
        files = {}
        required_files = {
            'following': ['following.json'],
            'followers': ['followers_1.json', 'followers.json'],
            'pending': ['pending_follow_requests.json', 'recent_follow_requests.json'],
            'received': ['follow_requests_you\'ve_received.json', 'follow_requests_youve_received.json']
        }
        
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            # List all files in ZIP
            file_list = zip_ref.namelist()
            
            # Find the connections/followers_and_following folder
            target_folder = None
            for file_path in file_list:
                if 'connections/followers_and_following/' in file_path or 'connections\\followers_and_following\\' in file_path:
                    # Normalize path separators
                    normalized_path = file_path.replace('\\', '/')
                    parts = normalized_path.split('/')
                    
                    # Get the base folder path
                    if 'followers_and_following' in parts:
                        idx = parts.index('followers_and_following')
                        target_folder = '/'.join(parts[:idx+1]) + '/'
                        break
            
            if not target_folder:
                raise Exception("Could not find 'connections/followers_and_following/' folder in ZIP file. Make sure you uploaded the correct Instagram data archive.")
            
            # Extract required JSON files
            for key, possible_names in required_files.items():
                found = False
                for filename in possible_names:
                    # Try both forward and backward slashes
                    possible_paths = [
                        target_folder + filename,
                        target_folder.replace('/', '\\') + filename
                    ]
                    
                    for file_path in file_list:
                        normalized_file_path = file_path.replace('\\', '/')
                        if normalized_file_path.endswith(filename) and target_folder in normalized_file_path:
                            # Found the file!
                            json_data = zip_ref.read(file_path)
                            files[key] = io.BytesIO(json_data)
                            found = True
                            break
                    
                    if found:
                        break
                
                if not found:
                    # For optional files, create empty structure
                    if key == 'pending':
                        files[key] = io.BytesIO(b'{"relationships_follow_requests_sent": []}')
                    elif key == 'received':
                        files[key] = io.BytesIO(b'{"relationships_follow_requests_received": []}')
                    else:
                        raise Exception(f"Required file not found in ZIP: {' or '.join(possible_names)}")
        
        return files
        
    except zipfile.BadZipFile:
        raise Exception("Invalid ZIP file. Please upload a valid Instagram data archive.")
    except Exception as e:
        raise Exception(f"Error extracting ZIP file: {str(e)}")

def process_instagram_data(files):
    """Process Instagram JSON files and generate summary"""
    try:
        # Load all JSON files
        following_data = json.loads(files['following'].read())
        followers_data = json.loads(files['followers'].read())
        pending_requests_data = json.loads(files['pending'].read())
        received_requests_data = json.loads(files['received'].read())
        
        # Extract Instagram usernames from each file
        following_entries = following_data["relationships_following"]
        
        # Handle different formats for following.json
        # New format has username in 'title', older format has it in string_list_data[0]['value']
        following_usernames = set()
        following_dict = {}  # Store username -> entry mapping for later use
        
        for entry in following_entries:
            if 'title' in entry and entry['title']:
                # New format: username in title field
                username = entry['title']
                following_usernames.add(username)
                following_dict[username] = entry
            elif 'string_list_data' in entry and len(entry['string_list_data']) > 0:
                # Old format: username in string_list_data
                if 'value' in entry['string_list_data'][0]:
                    username = entry['string_list_data'][0]['value']
                    following_usernames.add(username)
                    following_dict[username] = entry
        
        followers_usernames = {entry['string_list_data'][0]['value'] for entry in followers_data if 'string_list_data' in entry and len(entry['string_list_data']) > 0 and 'value' in entry['string_list_data'][0]}
        
        # Handle pending requests - might have different key names
        if "relationships_follow_requests_sent" in pending_requests_data:
            pending_entries = pending_requests_data["relationships_follow_requests_sent"]
        elif "relationships_permanent_follow_requests" in pending_requests_data:
            pending_entries = pending_requests_data["relationships_permanent_follow_requests"]
        else:
            pending_entries = []
        
        pending_requests_usernames = {entry['string_list_data'][0]['value'] for entry in pending_entries if 'string_list_data' in entry and len(entry['string_list_data']) > 0 and 'value' in entry['string_list_data'][0]}
        
        received_entries = received_requests_data["relationships_follow_requests_received"]
        received_requests_usernames = {entry['string_list_data'][0]['value'] for entry in received_entries if 'string_list_data' in entry and len(entry['string_list_data']) > 0 and 'value' in entry['string_list_data'][0]}
        
        # Find usernames that are in following but not in followers
        not_following_back = following_usernames - followers_usernames
        
        # Find usernames that are in followers but not in following
        unknown_followers = followers_usernames - following_usernames
        
        # Extract data for not following back
        not_following_back_data = []
        for username in not_following_back:
            entry = following_dict.get(username)
            if entry:
                # Handle both formats
                if 'title' in entry and entry['title']:
                    # New format
                    href = entry['string_list_data'][0]['href'] if 'string_list_data' in entry and len(entry['string_list_data']) > 0 else f"https://www.instagram.com/{username}"
                    timestamp = entry['string_list_data'][0]['timestamp'] if 'string_list_data' in entry and len(entry['string_list_data']) > 0 and 'timestamp' in entry['string_list_data'][0] else 0
                    not_following_back_data.append({
                        "value": username,
                        "href": href,
                        "timestamp": convert_timestamp(timestamp) if timestamp else "Unknown"
                    })
                else:
                    # Old format
                    not_following_back_data.append({
                        "value": entry['string_list_data'][0]['value'],
                        "href": entry['string_list_data'][0]['href'],
                        "timestamp": convert_timestamp(entry['string_list_data'][0]['timestamp'])
                    })
        
        # Sort by username
        not_following_back_data.sort(key=lambda x: x['value'].lower())
        
        # Extract data for unknown followers
        unknown_followers_data = []
        for entry in followers_data:
            if 'string_list_data' in entry and len(entry['string_list_data']) > 0:
                if 'value' in entry['string_list_data'][0]:
                    username = entry['string_list_data'][0]['value']
                    if username in unknown_followers:
                        unknown_followers_data.append({
                            "value": username,
                            "href": entry['string_list_data'][0].get('href', f"https://www.instagram.com/{username}"),
                            "timestamp": convert_timestamp(entry['string_list_data'][0]['timestamp']) if 'timestamp' in entry['string_list_data'][0] else "Unknown"
                        })
        
        unknown_followers_data.sort(key=lambda x: x['value'].lower())
        
        # Extract data for pending follow requests
        pending_requests_list = []
        for entry in pending_entries:
            if 'string_list_data' in entry and len(entry['string_list_data']) > 0:
                if 'value' in entry['string_list_data'][0]:
                    username = entry['string_list_data'][0]['value']
                    pending_requests_list.append({
                        "value": username,
                        "href": entry['string_list_data'][0].get('href', f"https://www.instagram.com/{username}"),
                        "timestamp": convert_timestamp(entry['string_list_data'][0]['timestamp']) if 'timestamp' in entry['string_list_data'][0] else "Unknown"
                    })
        
        pending_requests_list.sort(key=lambda x: x['value'].lower())
        
        # Extract data for received follow requests
        received_requests_list = []
        for entry in received_entries:
            if 'string_list_data' in entry and len(entry['string_list_data']) > 0:
                if 'value' in entry['string_list_data'][0]:
                    username = entry['string_list_data'][0]['value']
                    received_requests_list.append({
                        "value": username,
                        "href": entry['string_list_data'][0].get('href', f"https://www.instagram.com/{username}"),
                        "timestamp": convert_timestamp(entry['string_list_data'][0]['timestamp']) if 'timestamp' in entry['string_list_data'][0] else "Unknown"
                    })
        
        received_requests_list.sort(key=lambda x: x['value'].lower())
        
        # Prepare summary data
        summary_data = {
            "Total Followers": len(followers_usernames),
            "Total Following": len(following_usernames),
            "Total Not Following Back": len(not_following_back),
            "Not Following Back": not_following_back_data,
            "Total Unknown Followers": len(unknown_followers),
            "Unknown Followers": unknown_followers_data,
            "Total Pending Follow Requests": len(pending_requests_usernames),
            "Pending Follow Requests": pending_requests_list,
            "Total Received Follow Requests": len(received_requests_usernames),
            "Received Follow Requests": received_requests_list
        }
        
        return summary_data
    
    except Exception as e:
        raise Exception(f"Error processing Instagram data: {str(e)}")

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and process Instagram data"""
    try:
        # Check if a ZIP file was uploaded
        if 'zipfile' in request.files and request.files['zipfile'].filename != '':
            zip_file = request.files['zipfile']
            
            if not allowed_file(zip_file.filename):
                return jsonify({'error': 'Please upload a ZIP file'}), 400
            
            # Extract JSON files from ZIP
            files = extract_json_from_zip(zip_file)
            
        else:
            # Check if all required individual files are present
            required_files = ['following', 'followers', 'pending', 'received']
            if not all(file in request.files for file in required_files):
                return jsonify({'error': 'Please upload either a ZIP file or all four JSON files'}), 400
            
            files = {}
            for file_key in required_files:
                file = request.files[file_key]
                if file.filename == '':
                    return jsonify({'error': f'{file_key} file is empty'}), 400
                if not allowed_file(file.filename):
                    return jsonify({'error': f'{file_key} must be a JSON file'}), 400
                files[file_key] = file
        
        # Process the data
        summary = process_instagram_data(files)
        
        return jsonify(summary), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
