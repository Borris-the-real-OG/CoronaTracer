from os import getenv

from flask import render_template, request, Flask
from flask.helpers import send_file, url_for
from werkzeug.utils import redirect

from googleapiclient import errors

import Tracer.gc_flow as GC
import Tracer.emailing as Email

class State:
    def __init__(self):
        self.profile = None
        self.courses = []
        self.ppl_list = []
        self.message = None

props = State()
isAuth = False
app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for("apper"))


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/app', methods=['GET', 'POST'])
def apper():
    global props, isAuth

    if isAuth is False:
        GC.gAPI_init("Tracer/")
        isAuth = True
    else:
        if request.method == 'POST':
            if (email := request.form.get('userEmail')) is not None and (props.profile is None or email != props.profile.get('emailAddress')):
                props = State()
                try:
                    props.profile = GC.getTarget(request.form['userEmail'])
                except errors.HttpError as e:
                    props.message = {
                        'title': "Invalid email",
                        'description': "The Google Classroom API failed to process the email you provided. Make sure you have permission to view this user's courses and that this user is in your domain.",
                        'stackTrace': e
                    }
                else:
                    props.courses = GC.getCourses(props.profile)
            elif request.form.get('course-phase') is not None:
                ignored = []

                for _, item in enumerate(request.form):
                    if item[-6:] == "ignore":
                        ignored += [item[:-7]]
                for c in props.courses:
                    c['ignored'] = (c['id'] in ignored)

                props.ppl_list = GC.getPeople(props.profile, [i for i in props.courses if i.get('ignored') is False], seatingChart=(not request.form.get("noSeating")))
            elif (subject := request.form.get('emailSubject')) is not None and props.ppl_list:
                if (body := request.form.get('emailBody')) is None: #or body[:48] == "Don't modify this if you want the default email.":
                    with open("Tracer/base_email.html", 'r') as f:
                        body = f.read()
                try:
                    Email.sendEmails([p['email'] for p in props.ppl_list] + ([extra] if (extra := request.form.get('extraEmail')) else []), subject, body)
                except Exception as e:
                    props.message = {
                        'title': "Failed to email contacts",
                        'description': "Check email configuration and make sure the environment script has been run and try again.",
                        'stackTrace': e
                    }
                else:
                    props.message = {
                        'title': "Email successful",
                        'description': f"Successfully emailed {len(props.ppl_list)} contacts from {getenv('SENDER_EMAIL')}.",
                        'good': True
                    }
            elif (fh := request.form.get('exportName')) is not None:
                try:
                    return send_file(GC.pplToCSV(props.ppl_list), as_attachment=True, attachment_filename=fh, mimetype="text/csv")
                except Exception as e:
                    props.message = {
                        'title': "Failed to download file",
                        'description': "This is probably a server side problem... Sorry!",
                        'stackTrace': e
                    }
    tmp = render_template('app.html', props=props)
    props.message = None
    return tmp

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)