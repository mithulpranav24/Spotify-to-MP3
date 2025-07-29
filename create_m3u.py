import os
import shutil
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TRCK
import re

# Define directories
source_dir = r"C:\Users\Mithul\Music\Playlists"
base_dir = r"C:\Users\Mithul\Music\Backup"
android_base_dir = "/storage/emulated/0/Music"
m3u_dir = os.path.join(base_dir, "M3U Files")
pc_m3u_dir = r"C:\Users\Mithul\Music\M3U Files"

# Preliminary steps: Clear backup, copy playlists, and organize M3U files
# Delete everything in the backup directory
if os.path.exists(base_dir):
    shutil.rmtree(base_dir)
    print(f"Cleared backup directory: {base_dir}")

# Create backup directory
os.makedirs(base_dir, exist_ok=True)
print(f"Created backup directory: {base_dir}")

# Copy everything from Playlists to Backup
shutil.copytree(source_dir, base_dir, dirs_exist_ok=True)
print(f"Copied all contents from {source_dir} to {base_dir}")

# Create M3U Files and PC M3U directories
os.makedirs(m3u_dir, exist_ok=True)
os.makedirs(pc_m3u_dir, exist_ok=True)
print(f"Created directories: {m3u_dir} and {pc_m3u_dir}")

# Function to remove track numbers from MP3 metadata
def remove_mp3_tracknumber(directory):
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith('.mp3'):
                file_path = os.path.join(root, filename)
                try:
                    audio = MP3(file_path, ID3=ID3)
                    if 'TRCK' in audio.tags:
                        audio.tags.delall('TRCK')
                        audio.save()
                        print(f"Track number removed from: {filename}")
                    else:
                        print(f"No track number found in: {filename}")
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")

# Remove track numbers from MP3 files in backup directory
if os.path.isdir(base_dir):
    remove_mp3_tracknumber(base_dir)
else:
    print(f"Invalid directory path: {base_dir}")

# Define music folders
music_folders = [
    "2014+",
    "Mithul and his Moonlander",
    "Phonk",
    "Reels",
    "TN42",
    "Yallah",
    "0911",
    "Deduplicated"
]

# Create Deduplicated folder
dedup_dir = os.path.join(base_dir, "Deduplicated")
os.makedirs(dedup_dir, exist_ok=True)

# Supported audio file extension
audio_extensions = (".mp3",)

# Function to clean metadata for consistent comparison
def clean_string(s):
    if s:
        return re.sub(r'[^\w\s]', '', s).lower().strip()
    return ""

# Collect all audio files with metadata
all_songs = {}
for folder in music_folders:
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        continue
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(audio_extensions):
                full_path = os.path.join(root, file)
                try:
                    audio = MP3(full_path, ID3=ID3)
                    artist = clean_string(audio.get("TPE1", [""])[0])
                    title = clean_string(audio.get("TIT2", [""])[0])
                    duration = int(audio.info.length)
                    song_key = (artist, title) if artist and title else file.lower()
                    if song_key not in all_songs:
                        all_songs[song_key] = []
                    all_songs[song_key].append({
                        "path": full_path,
                        "folder": folder,
                        "artist": audio.get("TPE1", [""])[0],
                        "title": audio.get("TIT2", [""])[0],
                        "duration": duration
                    })
                except Exception as e:
                    print(f"Error reading {full_path}: {e}")
                    song_key = file.lower()
                    if song_key not in all_songs:
                        all_songs[song_key] = []
                    all_songs[song_key].append({
                        "path": full_path,
                        "folder": folder,
                        "artist": "",
                        "title": file,
                        "duration": 0
                    })

# Resolve duplicates and map paths (keep one copy on disk)
final_paths = {}
for song_key, instances in all_songs.items():
    if len(instances) == 1:
        final_paths[song_key] = instances[0]
    else:
        # Check if any instance is in "Mithul and his Moonlander"
        mithul_instance = next((inst for inst in instances if inst["folder"] == "Mithul and his Moonlander"), None)
        if mithul_instance:
            final_paths[song_key] = mithul_instance
            # Delete duplicates from other folders
            for inst in instances:
                if inst["folder"] != "Mithul and his Moonlander":
                    try:
                        os.remove(inst["path"])
                        print(f"Deleted duplicate: {inst['path']}")
                    except Exception as e:
                        print(f"Error deleting {inst['path']}: {e}")
        else:
            # Keep one instance in Deduplicated folder
            first_instance = instances[0]
            new_path = os.path.join(dedup_dir, os.path.basename(first_instance["path"]))
            try:
                shutil.move(first_instance["path"], new_path)
                print(f"Moved to Deduplicated: {new_path}")
                final_paths[song_key] = {
                    "path": new_path,
                    "folder": "Deduplicated",
                    "artist": first_instance["artist"],
                    "title": first_instance["title"],
                    "duration": first_instance["duration"]
                }
                # Delete other duplicates
                for inst in instances[1:]:
                    try:
                        os.remove(inst["path"])
                        print(f"Deleted duplicate: {inst['path']}")
                    except Exception as e:
                        print(f"Error deleting {inst['path']}: {e}")
            except Exception as e:
                print(f"Error moving {first_instance['path']}: {e}")
                final_paths[song_key] = first_instance

# Create separate M3U playlists for each folder (excluding Deduplicated) for both Android and PC
playlist_summary = []
for folder in music_folders[:-1]:  # Skip Deduplicated
    # Use exact folder name for Mithul and his Moonlander, replace spaces with underscores for others
    output_filename = folder if folder == "Mithul and his Moonlander" else folder.replace(" ", "_")

    # Android playlist
    android_output_file = os.path.join(m3u_dir, f"{output_filename}.m3u")
    android_song_count = 0
    with open(android_output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for song_key, instances in all_songs.items():
            for inst in instances:
                if inst["folder"] == folder:
                    song = final_paths.get(song_key, inst)
                    if song["artist"] and song["title"]:
                        f.write(f"#EXTINF:{song['duration']},{song['artist']} - {song['title']}\n")
                    else:
                        f.write(f"#EXTINF:{song['duration']},{song['title']}\n")
                    android_path = song["path"].replace(base_dir, android_base_dir).replace("\\", "/")
                    f.write(f"{android_path}\n")
                    android_song_count += 1
    print(f"Created Android playlist: {android_output_file} with {android_song_count} songs")
    playlist_summary.append({"Playlist Name": output_filename, "Number of Songs": android_song_count})

    # PC playlist
    pc_output_file = os.path.join(pc_m3u_dir, f"{output_filename}_PC.m3u")
    pc_song_count = 0
    with open(pc_output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for song_key, instances in all_songs.items():
            for inst in instances:
                if inst["folder"] == folder:
                    song = final_paths.get(song_key, inst)
                    if song["artist"] and song["title"]:
                        f.write(f"#EXTINF:{song['duration']},{song['artist']} - {song['title']}\n")
                    else:
                        f.write(f"#EXTINF:{song['duration']},{song['title']}\n")
                    f.write(f"{song['path']}\n")
                    pc_song_count += 1
    print(f"Created PC playlist: {pc_output_file} with {pc_song_count} songs")

# Move M3U files to appropriate directories
for file in os.listdir(base_dir):
    if file.lower().endswith(".m3u"):
        file_path = os.path.join(base_dir, file)
        if file.endswith("_PC.m3u"):
            shutil.move(file_path, os.path.join(pc_m3u_dir, file))
            print(f"Moved PC playlist: {file} to {pc_m3u_dir}")
        else:
            shutil.move(file_path, os.path.join(m3u_dir, file))
            print(f"Moved Android playlist: {file} to {m3u_dir}")

# Print playlist summary table
print("\nPlaylist Summary:")
print("-" * 40)
print(f"{'Playlist Name':<25} | {'Number of Songs':<15}")
print("-" * 40)
for playlist in playlist_summary:
    print(f"{playlist['Playlist Name']:<25} | {playlist['Number of Songs']:<15}")
print("-" * 40)

print("All operations completed successfully!")