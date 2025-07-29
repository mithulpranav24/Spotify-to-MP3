import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv

# Set up authentication
scope = "playlist-read-private playlist-read-collaborative"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='667e8bd0ed034a18979447d86bc141f7',
                                              client_secret='2b41bbd8faab442d9c47b459b47d9bb7',
                                              redirect_uri='http://127.0.0.1:5000/callback',
                                              scope=scope))

# Get current user's playlists
playlists = []
results = sp.current_user_playlists(limit=50)
playlists.extend(results['items'])

# Handle pagination if you have more than 50 playlists
while results['next']:
    results = sp.next(results)
    playlists.extend(results['items'])

# Extract playlist names, URLs, and URIs
playlist_data = []
for playlist in playlists:
    playlist_data.append({
        'Name': playlist['name'],
        'URL': playlist['external_urls']['spotify'],
        'URI': playlist['uri']
    })

# Save to CSV
with open('spotify_playlists.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Name', 'URL', 'URI'])
    writer.writeheader()
    writer.writerows(playlist_data)

print("Playlists exported to spotify_playlists.csv")