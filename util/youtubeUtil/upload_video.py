import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =============================================================================
# CONFIGURATION
# =============================================================================
YOUTUBE_UTIL_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(YOUTUBE_UTIL_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(YOUTUBE_UTIL_DIR, "token.json")

# =============================================================================
# PLAYLIST CONFIGURATION
# =============================================================================
PLAYLIST_TITLE = "MksGlobalNews - Daily News"
PLAYLIST_DESCRIPTION = "Daily news compilations from MksGlobalNews."
PLAYLIST_PRIVACY = "public"

# =============================================================================
# YOUTUBE OAUTH SCOPE
# =============================================================================
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# =============================================================================
# AUTHENTICATION
# =============================================================================
def authenticate(client_secrets_file=CLIENT_SECRETS_FILE, token_file=TOKEN_FILE):
    """Authenticate with YouTube using OAuth 2.0."""
    print()
    print("=" * 80)
    print("YOUTUBE AUTHENTICATION")
    print("=" * 80)

    if not os.path.isfile(client_secrets_file):
        raise FileNotFoundError(
            "\nclient_secret.json was not found.\n\n"
            f"Expected location:\n{client_secrets_file}\n\n"
            "Please place client_secret.json in the same directory as this Python file."
        )

    credentials = None

    if os.path.isfile(token_file):
        print(f"Existing OAuth token found:\n{token_file}")
        try:
            credentials = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            print()
            print("⚠️ Existing token could not be loaded.")
            print(f"Reason: {e}")
            print("Starting new OAuth authentication.")
            credentials = None

    if credentials and credentials.expired and credentials.refresh_token:
        print("OAuth token has expired.")
        print("Refreshing OAuth token...")
        try:
            credentials.refresh(Request())
            print("✅ OAuth token refreshed successfully.")
        except Exception as e:
            print()
            print("⚠️ OAuth token refresh failed.")
            print(f"Reason: {e}")
            print("Starting new OAuth authentication.")
            credentials = None

    if credentials and credentials.valid:
        print("✅ Existing OAuth credentials are valid.")
    else:
        print()
        print("Starting new YouTube OAuth authentication...")
        print("Your browser should open automatically.")
        print()
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
        credentials = flow.run_local_server(port=0)
        print()
        print("✅ New YouTube OAuth authentication completed.")

    with open(token_file, "w", encoding="utf-8") as token:
        token.write(credentials.to_json())
    print(f"OAuth token saved to:\n{token_file}")
    print("✅ YouTube authentication successful.")
    return credentials

# =============================================================================
# CREATE YOUTUBE SERVICE
# =============================================================================
def create_youtube_service():
    credentials = authenticate()
    youtube = build("youtube", "v3", credentials=credentials)
    return youtube

# =============================================================================
# FIND EXISTING PLAYLIST
# =============================================================================
def find_playlist(youtube, playlist_title):
    """Search for a playlist by title and return its ID if found."""
    print()
    print("-" * 80)
    print("SEARCHING FOR PLAYLIST")
    print("-" * 80)
    print(f"Playlist title: {playlist_title}")

    next_page_token = None
    while True:
        response = youtube.playlists().list(
            part="snippet,status",
            mine=True,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for playlist in response.get("items", []):
            title = playlist.get("snippet", {}).get("title", "")
            playlist_id = playlist.get("id")
            if title == playlist_title:
                print()
                print("✅ Existing playlist found.")
                print(f"Playlist title: {title}")
                print(f"Playlist ID: {playlist_id}")
                return playlist_id

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    print()
    print("Playlist does not exist.")
    return None

# =============================================================================
# CREATE PLAYLIST
# =============================================================================
def create_playlist(youtube, playlist_title, playlist_description, privacy_status="public"):
    """Create a new YouTube playlist."""
    print()
    print("-" * 80)
    print("CREATING PLAYLIST")
    print("-" * 80)
    print(f"Title: {playlist_title}")
    print(f"Privacy: {privacy_status}")

    request_body = {
        "snippet": {
            "title": playlist_title,
            "description": playlist_description
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    try:
        response = youtube.playlists().insert(
            part="snippet,status",
            body=request_body
        ).execute()
    except Exception as e:
        print()
        print("❌ PLAYLIST CREATION FAILED")
        print(f"Exception type: {type(e).__name__}")
        print(f"Error:\n{e}")
        raise

    playlist_id = response["id"]
    print()
    print("✅ PLAYLIST CREATED")
    print(f"Playlist title: {playlist_title}")
    print(f"Playlist ID: {playlist_id}")
    print(f"Playlist URL: https://www.youtube.com/playlist?list={playlist_id}")
    return playlist_id

# =============================================================================
# GET OR CREATE PLAYLIST
# =============================================================================
def get_or_create_playlist(youtube):
    playlist_id = find_playlist(youtube, PLAYLIST_TITLE)
    if playlist_id:
        return playlist_id
    return create_playlist(youtube, PLAYLIST_TITLE, PLAYLIST_DESCRIPTION, PLAYLIST_PRIVACY)

# =============================================================================
# THUMBNAIL MIME TYPE
# =============================================================================
def get_thumbnail_mime_type(thumbnail_file):
    """Determine thumbnail MIME type."""
    extension = os.path.splitext(thumbnail_file)[1].lower()
    if extension == ".jpg":
        return "image/jpeg"
    if extension == ".jpeg":
        return "image/jpeg"
    if extension == ".png":
        return "image/png"
    raise ValueError(f"Unsupported thumbnail format: {extension}\nSupported formats: .jpg, .jpeg, .png")

# =============================================================================
# UPLOAD VIDEO
# =============================================================================
def upload_video(youtube, video_file, title, description="", tags=None, category_id="25", privacy_status="private"):
    """Upload a video to YouTube."""
    if not os.path.isfile(video_file):
        raise FileNotFoundError(f"Video file not found:\n{video_file}")
    if not title:
        raise ValueError("Video title cannot be empty.")

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    print()
    print("-" * 80)
    print("VIDEO UPLOAD")
    print("-" * 80)
    print(f"Video file:\n{video_file}")
    print(f"Title:\n{title}")
    print(f"Privacy:\n{privacy_status}")
    print()

    media_file = MediaFileUpload(video_file, chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media_file)

    response = None
    try:
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"Upload progress: {progress}%")
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ VIDEO UPLOAD FAILED")
        print("=" * 80)
        print(f"Exception type: {type(e).__name__}")
        print(f"Error:\n{e}")
        print("=" * 80)
        raise

    video_id = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    print()
    print("=" * 80)
    print("✅ VIDEO UPLOAD COMPLETED")
    print("=" * 80)
    print(f"Video ID: {video_id}")
    print(f"Video URL: {video_url}")
    print("=" * 80)

    return {"id": video_id, "url": video_url}

# =============================================================================
# UPLOAD THUMBNAIL
# =============================================================================
def upload_thumbnail(youtube, video_id, thumbnail_file):
    """Upload a custom thumbnail."""
    if not thumbnail_file:
        print("No thumbnail specified.")
        return False

    if not os.path.isfile(thumbnail_file):
        print()
        print("❌ Thumbnail file not found:")
        print(thumbnail_file)
        return False

    try:
        mime_type = get_thumbnail_mime_type(thumbnail_file)
    except ValueError as e:
        print()
        print(f"❌ {e}")
        return False

    size_mb = os.path.getsize(thumbnail_file) / (1024 * 1024)
    print()
    print("-" * 80)
    print("THUMBNAIL UPLOAD")
    print("-" * 80)
    print(f"Thumbnail:\n{thumbnail_file}")
    print(f"MIME type: {mime_type}")
    print(f"File size: {size_mb:.2f} MB")

    if size_mb > 50:
        print()
        print("❌ Thumbnail is larger than 50 MB.")
        return False

    thumbnail_media = MediaFileUpload(thumbnail_file, mimetype=mime_type, resumable=False)

    try:
        youtube.thumbnails().set(videoId=video_id, media_body=thumbnail_media).execute()
        print()
        print("✅ THUMBNAIL UPLOAD COMPLETED")
        return True
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ THUMBNAIL UPLOAD FAILED")
        print("=" * 80)
        print(f"Exception type: {type(e).__name__}")
        print(f"Error:\n{e}")
        print("=" * 80)
        return False

# =============================================================================
# ADD VIDEO TO PLAYLIST
# =============================================================================
def add_video_to_playlist(youtube, playlist_id, video_id):
    """Add a video to a YouTube playlist."""
    print()
    print("-" * 80)
    print("ADDING VIDEO TO PLAYLIST")
    print("-" * 80)
    print(f"Playlist ID: {playlist_id}")
    print(f"Video ID: {video_id}")

    request_body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
            }
        }
    }

    try:
        response = youtube.playlistItems().insert(part="snippet", body=request_body).execute()
        playlist_item_id = response.get("id")
        print()
        print("✅ VIDEO ADDED TO PLAYLIST")
        print(f"Playlist item ID: {playlist_item_id}")
        print(f"Playlist URL: https://www.youtube.com/playlist?list={playlist_id}")
        return True
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ADDING VIDEO TO PLAYLIST FAILED")
        print("=" * 80)
        print(f"Exception type: {type(e).__name__}")
        print(f"Error:\n{e}")
        print("=" * 80)
        return False

# =============================================================================
# UPLOAD SINGLE VIDEO (REUSABLE FUNCTION)
# =============================================================================
def upload_single_video(
    video_file,
    title,
    description="",
    tags=None,
    category_id="25",
    privacy_status="public",
    thumbnail_file=None,
    add_to_playlist=False,
    playlist_title="MksGlobalNews - Daily News",
    playlist_description="Daily news compilations from MksGlobalNews.",
    playlist_privacy="public"
):
    """
    Upload a single video with optional thumbnail and playlist addition.
    This function handles authentication internally and can be called from other files.

    Args:
        video_file: Path to the video file to upload
        title: Video title
        description: Video description (optional)
        tags: List of tags (optional)
        category_id: YouTube category ID (default: "25")
        privacy_status: Video privacy status (default: "public")
        thumbnail_file: Path to thumbnail image (optional)
        add_to_playlist: Whether to add video to playlist (default: False)
        playlist_title: Playlist title (default: "MksGlobalNews - Daily News")
        playlist_description: Playlist description (default)
        playlist_privacy: Playlist privacy status (default: "public")

    Returns:
        {
            "success": bool,
            "video_id": str or None,
            "url": str or None,
            "thumbnail_uploaded": bool,
            "playlist_added": bool,
            "error": str or None
        }
    """
    # Authenticate and create YouTube service
    youtube = create_youtube_service()

    # Get or create playlist if needed
    playlist_id = None
    if add_to_playlist:
        try:
            playlist_id = find_playlist(youtube, playlist_title)
            if not playlist_id:
                playlist_id = create_playlist(youtube, playlist_title, playlist_description, playlist_privacy)
        except Exception as e:
            print(f"Playlist operation failed: {e}")
            add_to_playlist = False

    # Upload video
    try:
        upload_result = upload_video(
            youtube=youtube,
            video_file=video_file,
            title=title,
            description=description,
            tags=tags,
            category_id=category_id,
            privacy_status=privacy_status
        )
    except Exception as e:
        return {
            "success": False,
            "video_id": None,
            "url": None,
            "thumbnail_uploaded": False,
            "playlist_added": False,
            "error": str(e)
        }

    video_id = upload_result["id"]
    video_url = upload_result["url"]

    # Upload thumbnail if provided
    thumbnail_uploaded = False
    if thumbnail_file:
        thumbnail_uploaded = upload_thumbnail(youtube=youtube, video_id=video_id, thumbnail_file=thumbnail_file)

    # Add to playlist if requested
    playlist_added = False
    if add_to_playlist and playlist_id:
        playlist_added = add_video_to_playlist(youtube=youtube, playlist_id=playlist_id, video_id=video_id)

    return {
        "success": True,
        "video_id": video_id,
        "url": video_url,
        "thumbnail_uploaded": thumbnail_uploaded,
        "playlist_added": playlist_added,
        "error": None
    }

# =============================================================================
# PROCESS ONE VIDEO
# =============================================================================
def process_video(youtube, playlist_id, video_data, index, total):
    """Upload one video, thumbnail and add it to playlist."""
    video_file = video_data["video_file"]
    title = video_data["title"]
    description = video_data.get("description", "")
    tags = video_data.get("tags", [])
    category_id = video_data.get("category_id", "25")
    privacy_status = video_data.get("privacy_status", "private")
    thumbnail_file = video_data.get("thumbnail_file")

    print()
    print("#" * 80)
    print(f"PROCESSING VIDEO {index}/{total}")
    print("#" * 80)
    print(f"Video:\n{video_file}")
    print(f"Title:\n{title}")
    print(f"Thumbnail:\n{thumbnail_file}")
    print(f"Playlist:\n{PLAYLIST_TITLE}")
    print(f"Privacy:\n{privacy_status}")

    if not os.path.isfile(video_file):
        print()
        print("❌ Video file not found.")
        return {
            "success": False,
            "video_id": None,
            "url": None,
            "thumbnail_uploaded": False,
            "playlist_added": False,
            "error": "Video file not found"
        }

    if thumbnail_file and not os.path.isfile(thumbnail_file):
        print()
        print("⚠️ Thumbnail file not found.")
        print("Video will still be uploaded.")
        thumbnail_file = None

    try:
        upload_result = upload_video(
            youtube=youtube,
            video_file=video_file,
            title=title,
            description=description,
            tags=tags,
            category_id=category_id,
            privacy_status=privacy_status
        )
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ VIDEO {index} FAILED")
        print("=" * 80)
        print(f"Error:\n{e}")
        print("=" * 80)
        return {
            "success": False,
            "video_id": None,
            "url": None,
            "thumbnail_uploaded": False,
            "playlist_added": False,
            "error": str(e)
        }

    video_id = upload_result["id"]
    video_url = upload_result["url"]

    thumbnail_uploaded = upload_thumbnail(youtube=youtube, video_id=video_id, thumbnail_file=thumbnail_file)
    playlist_added = add_video_to_playlist(youtube=youtube, playlist_id=playlist_id, video_id=video_id)

    print()
    print("=" * 80)
    print(f"VIDEO {index} FINAL RESULT")
    print("=" * 80)
    print("Video upload: ✅ SUCCESS")
    print(f"Video ID: {video_id}")
    print(f"Video URL: {video_url}")
    print(f"Thumbnail: {'✅ SUCCESS' if thumbnail_uploaded else '❌ FAILED'}")
    print(f"Playlist: {'✅ ADDED' if playlist_added else '❌ FAILED'}")
    print("=" * 80)

    return {
        "success": True,
        "video_id": video_id,
        "url": video_url,
        "thumbnail_uploaded": thumbnail_uploaded,
        "playlist_added": playlist_added,
        "error": None
    }

# =============================================================================
# MAIN (BATCH UPLOAD)
# =============================================================================
def main():
    videos_to_upload = [
        {
            "video_file": r"C:\DATA\VS_Code_Notes\MksGlobalNews\dumps\generated_videos\2026_09_20_01_32_Group1.mp4",
            "title": "MksGlobalNews - Group 1 Compilation",
            "description": "First compilation of news stories from multiple sources",
            "tags": ["news", "India News", "World News", "MksGlobalNews"],
            "category_id": "25",
            "privacy_status": "public",
            "thumbnail_file": r"C:\DATA\VS_Code_Notes\MksGlobalNews\dumps\generated_images\2026_09_20_01_32_4.png"
        },
        {
            "video_file": r"C:\DATA\VS_Code_Notes\MksGlobalNews\dumps\generated_videos\2026_09_20_01_32_Group2.mp4",
            "title": "MksGlobalNews - Group 2 Compilation",
            "description": "Second compilation of news stories from multiple sources",
            "tags": ["news", "India News", "World News", "MksGlobalNews"],
            "category_id": "25",
            "privacy_status": "public",
            "thumbnail_file": r"C:\DATA\VS_Code_Notes\MksGlobalNews\dumps\generated_images\2026_09_20_01_32_5.png"
        }
    ]

    print()
    print("=" * 80)
    print("MksGlobalNews - YouTube Batch Upload")
    print("=" * 80)
    print(f"Total videos: {len(videos_to_upload)}")
    print(f"Target playlist: {PLAYLIST_TITLE}")
    print(f"Playlist privacy: {PLAYLIST_PRIVACY}")
    print("=" * 80)

    try:
        youtube = create_youtube_service()
    except Exception as e:
        print(f"Error:\n{e}")
        sys.exit(1)

    try:
        playlist_id = get_or_create_playlist(youtube)
    except Exception as e:
        print(f"Error:\n{e}")
        sys.exit(1)

    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    print()
    print("=" * 80)
    print("TARGET PLAYLIST READY")
    print("=" * 80)
    print(f"Playlist: {PLAYLIST_TITLE}")
    print(f"Playlist ID: {playlist_id}")
    print(f"Playlist URL: {playlist_url}")
    print("=" * 80)

    results = []
    total_videos = len(videos_to_upload)

    for index, video_data in enumerate(videos_to_upload, start=1):
        result = upload_single_video(
            video_file=video_data["video_file"],
            title=video_data["title"],
            description=video_data.get("description", ""),
            tags=video_data.get("tags", []),
            category_id=video_data.get("category_id", "25"),
            privacy_status=video_data.get("privacy_status", "public"),
            thumbnail_file=video_data.get("thumbnail_file"),
            add_to_playlist=True,
            playlist_title=PLAYLIST_TITLE,
            playlist_description=PLAYLIST_DESCRIPTION,
            playlist_privacy=PLAYLIST_PRIVACY
        )
        results.append(result)

    print()
    print("=" * 80)
    print("FINAL BATCH UPLOAD SUMMARY")
    print("=" * 80)

    successful_videos = 0
    successful_thumbnails = 0
    successful_playlist_additions = 0

    for index, result in enumerate(results, start=1):
        print()
        print(f"VIDEO {index}")
        print("-" * 40)
        if result["success"]:
            successful_videos += 1
            print("Video upload: ✅ SUCCESS")
            print(f"Video ID: {result['video_id']}")
            print(f"URL: {result['url']}")
            if result["thumbnail_uploaded"]:
                successful_thumbnails += 1
                print("Thumbnail: ✅ SUCCESS")
            else:
                print("Thumbnail: ❌ FAILED")
            if result["playlist_added"]:
                successful_playlist_additions += 1
                print("Playlist: ✅ ADDED")
            else:
                print("Playlist: ❌ FAILED")
        else:
            print("Video upload: ❌ FAILED")
            if result.get("error"):
                print(f"Error: {result['error']}")

    print()
    print("=" * 80)
    print("FINAL COUNTS")
    print("=" * 80)
    print(f"Videos uploaded: {successful_videos}/{total_videos}")
    print(f"Thumbnails uploaded: {successful_thumbnails}/{total_videos}")
    print(f"Videos added to playlist: {successful_playlist_additions}/{total_videos}")
    print()
    print(f"Playlist: {PLAYLIST_TITLE}")
    print(playlist_url)
    print("=" * 80)
    print()
    print("Batch upload process completed.")

if __name__ == "__main__":
    main()
