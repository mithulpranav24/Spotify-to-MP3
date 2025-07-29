import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TRCK

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

if __name__ == "__main__":
    directory = r"C:\Users\Mithul\Music\Playlists"
    if os.path.isdir(directory):
        remove_mp3_tracknumber(directory)
    else:
        print("Invalid directory path")