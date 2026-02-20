import os
import pickle
import httplib2
from google_auth_httplib2 import AuthorizedHttp
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Die Berechtigung, die du zum Hochladen benötigst
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    credentials = None
    # Token-Datei speichert deine Kanal-Wahl (so musst du dich nur 1x einloggen)
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If the stored token can't be refreshed (revoked/expired), force a new login.
    # Refresh proactively so we don't discover invalid_grant mid-upload.
    if credentials and getattr(credentials, "refresh_token", None):
        try:
            credentials.refresh(Request())
        except RefreshError:
            credentials = None
            try:
                os.remove("token.pickle")
            except OSError:
                pass

    # Wenn kein gültiges Token da ist, starte den Login-Prozess
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'OAuth.json', SCOPES)
        credentials = flow.run_local_server(port=8080)
        # Hier wählst du im Browser den Ziel-Kanal aus!
        # Speichere das Token für die nächsten 113 Videos
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    # Increase HTTP timeouts for large/resumable uploads.
    http = AuthorizedHttp(credentials, http=httplib2.Http(timeout=600))
    return build('youtube', 'v3', http=http)

# Dienst erstellen
youtube = get_authenticated_service()
