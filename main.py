from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.fields.html5 import DateField
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import sendgrid
import os
from sendgrid.helpers.mail import *
cred = credentials.Certificate('bennettra-f6176-39124368e57f.json')
firebase_admin.initialize_app(cred)

todaydate = datetime.datetime.today().strftime('%Y-%m-%d')

db = firestore.client()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bennettsecret'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    form = LoginForm()

    if form.validate_on_submit():
        return dbpush(form.nameClub.data,form.nameEvent.data,form.nameHall.data,form.eventDate.data,form.eventTime.data,form.eventDetails.data)
    return render_template('form.html', form=form)

def dbpush(nameClub,nameEvent,nameHall,eventDate,eventTime,eventDetails):

    doc = db.collection(str(eventDate)).document(nameEvent)
    doc.set({
    'Club': nameClub,
    'Event': nameEvent,
    'Venue': nameHall,
    'Date': str(eventDate),
    'Time': eventTime,
    'Details': eventDetails
    })

    sg = sendgrid.SendGridAPIClient(apikey='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')
    from_email = Email("hellohitesh123@sendgrid.com")
    to_email = Email("ip5314@bennett.edu.in")
    subject = nameEvent+" at Bennett"
    mailtext = nameClub+" is hosting "+ nameEvent+" on "+str(eventDate)+" at "+eventTime+", venue: "+nameHall+". Details of the event: "+eventDetails+". Looking forward to seeing you there."
    content = Content("text/plain", mailtext)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)



    return render_template('success.html')


class LoginForm(FlaskForm):

    nameClub = StringField('Club Name')
    nameEvent = StringField('Name of Event')
    nameHall = StringField('Name of Hall')
    eventDate = DateField('Date of Event')
    eventTime = StringField('Time')
    eventDetails = StringField('Event Details')

class DateViewForm(FlaskForm):
    pickdate = DateField("Choose date")

@app.route('/dateview', methods=['GET', 'POST'])
def dateview():
    dateform = DateViewForm()
    if dateform.validate_on_submit():
        return display(str(dateform.pickdate.data))
    return render_template('dateview.html', form = dateform)



@app.route('/display', methods=['GET', 'POST'])
def display(date_events = todaydate):
    dates_ref = db.collection(date_events)
    events = dates_ref.get()
    events1 = dates_ref.get()
    empty = True
    for d in events:
        if d:
            empty = False
            break

    if(empty):
        return render_template('display.html', eventdata = 'empty')
    else:
        return render_template('display.html', eventdata = events1)




    return render_template('display.html', eventdata = events)

if __name__ == '__main__':
    app.run(debug=True)
