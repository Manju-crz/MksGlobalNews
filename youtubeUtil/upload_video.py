import os

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload"
]

VIDEO_FILE = "my_video.mp4"


def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        SCOPES
    )

    credentials = flow.run_local_server(
        port=0
    )

    return credentials


def upload_video():

    credentials = authenticate()

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    request_body = {
        "snippet": {
            "title": "My First Automated YouTube Video",
            "description": "Uploaded using YouTube Data API v3",
            "tags": [
                "automation",
                "youtube",
                "python"
            ],
            "categoryId": "25"
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media_file = MediaFileUpload(
        VIDEO_FILE,
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
    print(
        "URL:",
        f"https://www.youtube.com/watch?v={response['id']}"
    )


if __name__ == "__main__":
    upload_video()