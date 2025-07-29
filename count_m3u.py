import os

# Define the directory containing M3U playlists
base_dir = r"C:\Users\Mithul\Music\Backup\M3U Files"

# List of expected M3U files
playlist_files = [
    "2014+.m3u",
    "Mithul and his Moonlander.m3u",
    "Phonk.m3u",
    "Reels.m3u",
    "TN42.m3u",
    "Yallah.m3u"
]

# Function to count songs in an M3U file
def count_songs_in_m3u(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Count lines that are not comments or metadata (i.e., file paths)
            song_count = sum(1 for line in lines if line.strip() and not line.startswith("#"))
        return song_count
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

# Iterate through each playlist and count songs
for playlist in playlist_files:
    playlist_path = os.path.join(base_dir, playlist)
    if os.path.exists(playlist_path):
        song_count = count_songs_in_m3u(playlist_path)
        print(f"{playlist}: {song_count} songs")
    else:
        print(f"{playlist}: File not found")

print("Song count completed!")