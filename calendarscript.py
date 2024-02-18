import os
import tkinter as tk
import threading
import http.server
import socketserver
import webbrowser
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

PORT = 8005
HTML_FILE = 'calendar.html'
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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def fetch_events(calendar_service):
    # Set the time range to include events for the next 24 hours
    now = datetime.utcnow()
    start_time = now.isoformat() + 'Z'  # 'Z' indicates UTC time
    end_time = (now + timedelta(days=1)).isoformat() + 'Z'

    # Fetch events from Google Calendar
    events_result = calendar_service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_time,
                                                   singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def format_events_for_fullcalendar(events):
    formatted_events = []
    for event in events:
        formatted_event = {
            'title': event['summary'],
            'start': event['start'].get('dateTime', event['start'].get('date')),
            'end': event['end'].get('dateTime', event['end'].get('date')),
        }
        formatted_events.append(formatted_event)
    return formatted_events

def start_http_server():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("HTTP server started at port", PORT)
        httpd.serve_forever()

def display_calendar():
    webbrowser.open(f'http://localhost:{PORT}/{HTML_FILE}')

def display_tasks(events):
    # Display events/tasks using Tkinter
    root = tk.Tk()
    root.title("Today's Tasks")
    for event in events:
        label = tk.Label(root, text=event['title'], font=('Helvetica', 12), fg='blue', padx=10, pady=5)
        label.pack()
    root.mainloop()

def main():
    # Authenticate with Google Calendar
    calendar_service = authenticate_google_calendar()

    # Fetch events from Google Calendar
    events = fetch_events(calendar_service)

    # Format events for FullCalendar
    formatted_events = format_events_for_fullcalendar(events)

    # Start the HTTP server in a separate thread
    http_server_thread = threading.Thread(target=start_http_server)
    http_server_thread.start()

    # Display FullCalendar in the default web browser
    display_calendar()

    # Display tasks in Tkinter
    display_tasks(formatted_events)

if __name__ == "__main__":
    main()
