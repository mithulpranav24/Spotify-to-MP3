import csv
import os
from pathlib import Path

# Base directory for saving playlists
BASE_PATH = r"C:\Users\Mithul\Music\Playlists"


# Read playlists from CSV
def read_playlists_csv(csv_file):
    playlists = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            playlists.append(row)
    return playlists


# Prompt user to select playlists
def select_playlists(playlists):
    print("\nAvailable Playlists:")
    for i, playlist in enumerate(playlists, 1):
        print(f"{i}. {playlist['Name']}")
    selected = input("\nEnter the numbers of the playlists to download (e.g., 1,3,5): ")
    selected_indices = [int(i) - 1 for i in selected.split(',') if i.strip().isdigit()]
    return [playlists[i] for i in selected_indices if 0 <= i < len(playlists)]


# Open CMD to run spotDL download command
def download_playlist(playlist, base_path):
    # Create a valid folder name
    folder_name = "".join(c for c in playlist['Name'] if c.isalnum() or c in (' ', '_')).strip()
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Create spotDL command with only the playlist link and --overwrite skip
    command = f'spotdl download "{playlist['URL']}" --overwrite skip'

    # Command to open new CMD window
    cmd_command = f'start cmd /k "cd /d {folder_path} && {command}"'

    try:
        # Open new CMD window
        os.system(cmd_command)
        print(f"Started download for playlist '{playlist['Name']}' in {folder_path}")
    except Exception as e:
        print(f"Error starting download for playlist '{playlist['Name']}': {str(e)}")


def main():
    # Ensure base directory exists
    os.makedirs(BASE_PATH, exist_ok=True)

    # Read and select playlists
    playlists = read_playlists_csv('spotify_playlists.csv')
    if not playlists:
        print("No playlists found in spotify_playlists.csv")
        return

    selected_playlists = select_playlists(playlists)
    if not selected_playlists:
        print("No playlists selected")
        return

    # Download each selected playlist
    for playlist in selected_playlists:
        download_playlist(playlist, BASE_PATH)

    print("\nAll download commands initiated! Check CMD windows for progress.")


if __name__ == "__main__":
    main()