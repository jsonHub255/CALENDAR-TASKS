import tkinter as tk
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define scopes and token file
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE = 'token.json'


def authenticate_google_calendar():
    creds = None
    # Load token from file if it exists
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    except Exception as e:
        print(f"Error loading token: {e}")

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def get_events(calendar_service):
    # Set the time range to include events for the next 24 hours
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    start_time = now.isoformat() + 'Z'  # 'Z' indicates UTC time
    end_time = (now + timedelta(days=1)).isoformat() + 'Z'

    events_result = calendar_service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_time,
                                                   singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


def display_tasks():
    # Authenticate with Google Calendar
    calendar_service = authenticate_google_calendar()

    # Get events/tasks for today
    events = get_events(calendar_service)

    # Display events/tasks using Tkinter
    root = tk.Tk()
    root.title("Today's Tasks")

    for event in events:
        label = tk.Label(root, text=event['summary'], font=('Helvetica', 12), fg='blue', padx=10, pady=5)
        label.pack()

    root.mainloop()


if __name__ == "__main__":
    display_tasks()
