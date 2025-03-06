from flask import Flask, jsonify, render_template, request, send_file
import requests
import re
import json
from datetime import datetime, timedelta, timezone
from io import BytesIO
import os

app = Flask(__name__)

token_file = 'token_data.json'
announcement_cache = None
announcement_cache_time = None
apikey = None

# Load token from file or set to None if it doesn't exist or is expired
def load_token():
    global token, apikey
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            data = json.load(f)
            token_date = datetime.fromisoformat(data['date'])
            if datetime.utcnow() - token_date < timedelta(days=1):
                token = data['token']
                apikey = data['apikey']
            else:
                token = None
                apikey = None
    else:
        token = None
        apikey = None
    if(token == None or apikey==None):
        retrieve_token_and_apikey()
    print(token,apikey)

# Save token and date to a file
def save_token(token, apikey):
    with open(token_file, 'w') as f:
        json.dump({
            'token': token,
            'apikey': apikey,
            'date': datetime.utcnow().isoformat()
        }, f)

# Fetch announcements from API with caching and image filtering
def fetch_announcements():
    global token
    global apikey
    
    global announcement_cache, announcement_cache_time

    # Check if announcements are cached and within 15 minutes
    if announcement_cache and announcement_cache_time and \
       (datetime.utcnow() - announcement_cache_time < timedelta(minutes=15)):
        return announcement_cache

    load_token() #update if too old too.

    print(token,apikey)

    
    # If no valid token and API key, retrieve them
    if token is None or apikey is None:
        retrieve_token_and_apikey()
    

    # Request announcements from API
    if token != None and apikey!=None:
        two_weeks_ago = (datetime.utcnow() - timedelta(weeks=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        announcements_api_url = f"https://api.binderly.app/rest/v1/school_announcements?select=id%2Cbody%2Cbody2%2Calt_text%2Cimgs%2Cschool_id%2Cdistrict_id%2Cschool_id_list%2Cpost_date%2Cbgcolor%2Ctextcolor%2Cstart_at%2Cend_at%2Clink%2Clink_title%2Clink2%2Clink2_title%2Cimg2%2Cimg2_title&status=eq.3&or=%28school_id.eq.63%2C+district_id.eq.3%29&start_at=lte.{now}&end_at=gte.{two_weeks_ago}&order=start_at.desc%2Cupdated_at.desc"
        headers = {
            'Authorization': f"Bearer {token}",
            'apikey': apikey
        }

        response = requests.get(announcements_api_url, headers=headers)
        if response.status_code == 200:
            announcements = response.json()

            # Filter out announcements without images and print each announcement
            filtered_announcements = []

            now2 = datetime.utcnow().replace(tzinfo=timezone.utc)  # Make UTC time offset-aware
            filtered_announcements = []

            for announcement in announcements:
                try:
                    # Parse start_at and end_at as offset-aware datetimes
                    start_at = datetime.fromisoformat(announcement['start_at'])
                    end_at = datetime.fromisoformat(announcement['end_at'])

                    # Check if the current time falls within the range and imgs exists
                    if start_at <= now2 <= end_at and announcement.get("imgs"):
                        filtered_announcements.append(announcement)
                except Exception as e:
                    print(f"Error processing announcement: {announcement}, Error: {e}")
            # Cache announcements and update cache time
            announcement_cache = filtered_announcements
            announcement_cache_time = datetime.utcnow()

            if(filtered_announcements == {}):
                filtered_announcements.append(
                    {'id': 7957, 'body': 'No announcements.', 'body2': None, 'alt_text': None, 'imgs': [], 'school_id': 63, 'district_id': None, 'school_id_list': None, 'post_date': '', 'bgcolor': 'FFFFFF', 'textcolor': '282828', 'start_at': '', 'end_at': '', 'link': None, 'link_title': None, 'link2': None, 'link2_title': None, 'img2': None, 'img2_title': None}
                    )
            return filtered_announcements

    return []

# Retrieve token and apikey
def retrieve_token_and_apikey():
    global token, apikey

    #Temp prob?
    f = open('raw_creds.txt','r')
    l = f.readlines()
    f.close()
    eml = l[0].replace('\n','') #uh I think .strip is better,
    pwd = l[1].replace('\n','')

    print('ret toke')
    announcements_url = "https://binderly.app/content/announcements"
    announcements_response = requests.get(announcements_url)

    print(announcements_response)

    js_file_match = re.search(r'src="(main\.[a-zA-Z0-9]+\.js)"', announcements_response.text)
    
    if js_file_match:
        js_file_url = "https://binderly.app/" + js_file_match.group(1)
        js_response = requests.get(js_file_url)
        supabase_key_match = re.search(r'supabaseKey:"([a-zA-Z0-9-_.]+)"', js_response.text)

        print('aaa')
        
        if supabase_key_match:
            supabase_key = supabase_key_match.group(1)
            print('bb') #debugging stuffs
            
            token_url = "https://api.binderly.app/auth/v1/token?grant_type=password"
            payload = {
                "email": eml,#"", #I usually have it HARD coded, but idk
                "gotrue_meta_security": {},
                "password": pwd,#"" #I usually have it HARD coded, but idk
            }
            headers = {
                'apikey': supabase_key
            }

            print('c')
            
            response = requests.post(token_url, headers=headers, json=payload)
            token_response = response.json()


            print('done')
            if 'access_token' in token_response:
                token = token_response['access_token']
                apikey = supabase_key
                save_token(token, apikey)
    else:
        print('false')

# Route to fetch announcements
@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    announcements = fetch_announcements()
    return jsonify(announcements)

# Route to fetch images with authorization
@app.route('/image/<path:image_path>', methods=['GET'])
def get_image(image_path):
    if token and apikey:
        image_url = f"https://api.binderly.app/storage/v1/object/announcement-images/{image_path}"
        headers = {
            'Authorization': f"Bearer {token}",
            'apikey': apikey
        }
        image_response = requests.get(image_url, headers=headers)
        if image_response.status_code == 200:
            return send_file(BytesIO(image_response.content), mimetype=image_response.headers['Content-Type'])
        else:
            return f"Error loading image: {image_response.status_code}", image_response.status_code
    else:
        return "Error: Token or API key missing"

# Route to render announcements on a webpage
@app.route('/')
def index():
    announcements = fetch_announcements()
    return render_template('index.html', announcements=announcements)

if __name__ == '__main__':
    load_token()
    app.run(host='0.0.0.0', port=5014, debug=False)
