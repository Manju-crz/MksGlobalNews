import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


YOUTUBE_UTIL_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(YOUTUBE_UTIL_DIR, "client_secret.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload"
]

VIDEO_FILE = os.path.join(YOUTUBE_UTIL_DIR, "my_video.mp4")
TOKEN_FILE = os.path.join(YOUTUBE_UTIL_DIR, "token.json")


def authenticate(client_secrets_file=CLIENT_SECRETS_FILE, token_file=TOKEN_FILE):
    """Authenticate with YouTube and reuse saved OAuth credentials when possible."""
    credentials = None

    if os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_file(token_file, SCOPES)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    elif not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file,
            SCOPES,
        )
        credentials = flow.run_local_server(port=0)

    with open(token_file, "w", encoding="utf-8") as token:
        token.write(credentials.to_json())

    return credentials


def upload_video(
    video_file,
    title,
    description="",
    tags=None,
    category_id="25",
    privacy_status="private",
    client_secrets_file=CLIENT_SECRETS_FILE,
    token_file=TOKEN_FILE,
):
    """Upload a video to YouTube and return its video ID and URL."""
    if not os.path.isfile(video_file):
        raise FileNotFoundError(f"Video file not found: {video_file}")
    if not title or not isinstance(title, str):
        raise ValueError("title must be a non-empty string")

    credentials = authenticate(client_secrets_file, token_file)

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
        }
    }

    media_file = MediaFileUpload(
        video_file,
        chunksize=-1,
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = request.execute()

    print("Upload successful!")
    print("Video ID:", response["id"])
    video_url = f"https://www.youtube.com/watch?v={response['id']}"
    print("URL:", video_url)
    return {"id": response["id"], "url": video_url}


if __name__ == "__main__":
    upload_video(
        video_file=VIDEO_FILE,
        title="My First Automated YouTube Video",
        description="Uploaded using YouTube Data API v3",
        tags=["automation", "youtube", "python"],
        privacy_status="private",
    )