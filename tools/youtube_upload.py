"""Vice Clips Publisher - YouTube upload flow (complete, runnable script).

This is the exact flow our internal tool uses to publish an approved Short to our own
channel (@vicedadepressao) with the YouTube Data API v3:

  1. OAuth 2.0 (installed app) with the scopes youtube.upload and youtube.readonly.
     The refresh token is stored privately and can be revoked at
     https://myaccount.google.com/permissions
  2. channels.list (mine=true) to confirm the connected channel.
  3. videos.insert with a resumable upload of the edited vertical video.

Requirements:  pip install google-auth-oauthlib google-api-python-client
Usage:         python youtube_upload.py client_secret.json video.mp4 "Title #shorts" "Description"
"""
import sys

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]


def main(client_secret: str, video: str, title: str, description: str) -> None:
    creds = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES).run_local_server(
        port=8765, access_type="offline", prompt="consent")
    youtube = build("youtube", "v3", credentials=creds)

    channel = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]
    print("Connected channel:", channel["snippet"]["title"], channel["snippet"].get("customUrl"))

    body = {
        "snippet": {"title": title[:100], "description": description[:5000], "categoryId": "20"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    request = youtube.videos().insert(
        part="snippet,status", body=body,
        media_body=MediaFileUpload(video, mimetype="video/mp4", resumable=True, chunksize=8 << 20))
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    print("Published:", f"https://youtube.com/shorts/{response['id']}",
          "| privacy:", response["status"]["privacyStatus"])


if __name__ == "__main__":
    main(*sys.argv[1:5])
