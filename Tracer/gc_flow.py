# Standard Library
from os import path, getenv
from sys import argv
import io
import csv

# Google API
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload



def downParseSheet(id):
    """
    Downloads a Google Sheet and returns as CSV

    Parameters:
    id: id of file
    creds: creds used to sign in to Google API
    """

    # When I wrote this, only God and I knew how it worked. Now, only God knows!
    request = drive_service.files().export_media(fileId=id, mimeType='text/csv')
    fh = io.BytesIO()

    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()

    txt = io.StringIO(fh.getvalue().decode('UTF-8'))
    
    return [row for row in csv.reader(txt, delimiter=',')]


def pplToCSV(ppl):
    fh = io.StringIO()
    writer = csv.writer(fh)
    writer.writerow(["Name", "Email"])
    writer.writerows([[p['name'], p['email']] for p in ppl])

    mem = io.BytesIO()
    mem.write(fh.getvalue().encode())
    mem.seek(0)
    fh.close()
    return mem

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/classroom.profile.emails',
    'https://www.googleapis.com/auth/classroom.announcements.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    ]

gc_service = None
drive_service = None

def gAPI_init(dir):
    global gc_service, drive_service

    creds = None
    token_path = dir + "token.json"
    credentials_path = dir + "credentials.json"

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run (comment this out for App Engine!)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    gc_service = build('classroom', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

def getTarget(email):
    # https://developers.google.com/classroom/reference/rest/v1/userProfiles#UserProfile
    target = gc_service.userProfiles().get(userId=email).execute()
    return target
    
def getCourses(target):
    result = gc_service.courses().list(teacherId=target['id']).execute().get('courses', [])
    result += gc_service.courses().list(studentId=target['id']).execute().get('courses', [])
    for i in result:
        i["ignored"] = False
    return result

def getPeople(target, courses, seatingChart=True):
    ppl_list = []
    for course in courses:
        # parse seating chart if available
        if seatingChart and (sheet := next((announcement['materials'][0]['driveFile']['driveFile'] for announcement in gc_service.courses().announcements().list(courseId=course['id']).execute().get('announcements', []) if announcement['text'] == getenv("SEATING_CHART_TITLE")), None)) is not None: # sorry for whoever has to maintain this
            chart = downParseSheet(sheet['id'])
            table = ""
            for row in chart:
                if row[0] == target['name']['fullName']:
                    table = row[2]
                    break
            
            ppl_list += [{'name': row[0], 'email': row[1]} for row in chart if row[2] == table and row[1] != target['emailAddress']]
        # enumerate through all courses, pulling teachers and students
        else:
            teachers = gc_service.courses().teachers().list(courseId=course['id']).execute().get('teachers', [])
            for teacher in teachers:
                tmp = {
                    'userId': teacher['userId'],
                    'email': teacher['profile']['emailAddress'],
                    'name': teacher['profile']['name']['fullName'],
                    'isTeacher': True
                }
                if tmp not in ppl_list and tmp['email'] != target['emailAddress']:
                    ppl_list.append(tmp)

            students = gc_service.courses().students().list(courseId=course['id']).execute().get('students', [])
            for student in students:
                tmp = {
                    'userId': student['userId'],
                    'email': student['profile']['emailAddress'],
                    'name': student['profile']['name']['fullName'],
                    'isTeacher': False
                }
                if tmp not in ppl_list and tmp['email'] != target['emailAddress']:
                    ppl_list.append(tmp)

    return ppl_list


def main(args):
    gAPI_init(args[2]) # same directory
    person = getTarget(args[1])
    courses = getCourses(person)
    
    print('Courses:')
    for num, course in enumerate(courses):
        print(f"{num+1}. {course['name']}")
    exclude = input("Please type the numbers of any courses you would like to exclude separated by spaces.").split()

    new = []
    for num, course in enumerate(courses):
        if str(num+1) not in exclude:
            new += [course]

    for num, course in enumerate(new):
        print(f"{num+1}. {course['name']}")

    ppl_list = getPeople(person, new)
    with open(f"traced_contacts ({person['name']['givenName']}).csv", 'w') as f:
        f.write(pplToCSV(ppl_list).getbuffer())

if __name__ == '__main__':
    if len(argv) != 3:
        raise ValueError("Please pass in only the email of the trace and directory of tokens")
    main(argv)