from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv()

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes),"utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64, 
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    
    json_result = json.loads(result.content)
    token = json_result.get("access_token")
    return token
    
def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}
    
def search_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    
    query_url = url + query
    result = get(query_url, headers=headers)
    json_results = json.loads(result.content)["artists"]["items"]
    if len(json_results) == 0:
        print("No artist found")
        return none
    
    return json_results[0]

def songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers = headers)
    json_results = json.loads(result.content)["tracks"]
    return json_results
    
def audio_feature(token, track_ids):
    url = "https://api.spotify.com/v1/audio-features"
    headers = get_auth_header(token)
    params = {"ids": ",".join(track_ids)}
    results = get(url, headers = headers, params=params)
    json_results = json.loads(results.content)["audio_features"]
    return json_results
    
token = get_token()
fav_artist = input("Enter your favorite artist/band: ")
result = search_artist(token, fav_artist) #specifies our artist name
artist_id = (result["id"]) #retrieves the id value within dictionary 
songs = songs_by_artist(token, artist_id) 

track_ids = [song["id"] for song in songs] #extract track ids from songs
features = audio_feature(token, track_ids)

#create a dictionary to store the information
data = {
    "artist_name": result["name"],
    "top_tracks": []
}

#loop through each song
for i, feature in enumerate(features):
    title = songs[i]["name"]
    track_info = {
        "title": title,
        "danceability": feature["danceability"],
        "energy": feature["energy"],
        "acousticness": feature["acousticness"]
    }
    data["top_tracks"].append(track_info)

#calculate and add average scores
dance_avg = sum(track["danceability"] for track in data["top_tracks"]) / len(data["top_tracks"])
energy_avg = sum(track["energy"] for track in data["top_tracks"]) / len(data["top_tracks"])
acoustic_avg = sum(track["acousticness"] for track in data["top_tracks"]) / len(data["top_tracks"])

data["average_scores"] = {
    "danceability": round(dance_avg, 2),
    "energy": round(energy_avg, 2),
    "acousticness": round(acoustic_avg, 2)}

print(json.dumps(data, indent=1))