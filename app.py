from flask import (
    Flask,
    request,
    url_for,
)
from tiniyo.voice_response import VoiceResponse
from helper import tiniyoml
from config import *

app = Flask(__name__)

@app.route('/ivr/welcome', methods=['GET','POST'])
def welcome():
    response = VoiceResponse()
    with response.gather(
        num_digits=1, action=url_for('welcomeCB',_scheme='http',_external=True), method="POST"
    ) as g:
        g.say(message="Thanks for calling Kolkata Mix Tape E T Phone Home Service. " +
              "Please press 1 for Table reservation." +
              "Press 2 for your loyality point." +
              "Press 2 for any other query.", loop=3)
    return tiniyoml(response)

@app.route('/ivr/welcomeCB', methods=['POST'])
def welcomeCB():
    app.logger.error("DTMFGathertime response = %s" % request.get_json())
    digit = None
    if request.get_json() is not None:
        if 'Digits' in request.get_json():
            selected_option = request.json.get('Digits')
    #selected_option = request.form['Digits']
    app.logger.error("welcomeCB digit received = %s" % selected_option)
    option_actions = {'1': "tablebooking",
                      '2': "loyalitypoint",
                      '3': "otherquery"}

    if selected_option in option_actions:
        if int(selected_option) == 1:
            response = _tablereservation()
            return tiniyoml(response)
        elif int(selected_option) == 2:
            response = _loyality_point(request.json.get('From'))
            return tiniyoml(response)
        elif int(selected_option) == 3:
            response = _forotherquery()
            return tiniyoml(response)
    else:
        return _redirect_welcome()

def _tablereservation():
    response = VoiceResponse()
    with response.gather(
        numDigits=1, action=url_for('reservation_day',_scheme='http',_external=True), method="POST"
    ) as g:
        g.say("Press 1 for today " +
              "Press 2 for tomorrow " +
              "To go back to the main menu " +
              " press the star key.",
              voice="alice", language="en-GB", loop=3)

    return response


def _loyality_point(customer_number):
    response = VoiceResponse()
    req_body = {'customer_key': customer_key, 'merchant_id': merchant_id, 'customer_mobile': customer_number}
    my_headers = {'x-api-key' : x_api_key,'Content-Type':'application/json','Accept':'application/json'}
    custresp = requests.get(customer_check_url,headers=my_headers,data=req_body)
    if (response.status_code == 200):
        response.say("Your loyality points are "+response.json().response.details.currentpoints,voice="alice", language="en-GB")
        # Code here will only run if the request is successful
    else:
        response.say("To get to _loyality_point, please visit our website",voice="alice", language="en-GB")
    response.hangup()
    return response


def _tableservationtime_today():
    response = VoiceResponse()
    with response.gather(
        numDigits=1, action=url_for('tableservationtimetoday',_scheme='http',_external=True), method="POST"
    ) as g:
        g.say("Press 1 for breakfast, press 2 for lunch, press 3 for dinner" ,voice="alice", language="en-GB", loop=3)
    return response

def _tableservationtime_tomorrow():
    response = VoiceResponse()
    with response.gather(
        numDigits=1, action=url_for('tableservationtimetomorrow',_scheme='http',_external=True), method="POST"
    ) as g:
        g.say("Press 1 for breakfast, press 2 for lunch, press 3 for dinner" ,voice="alice", language="en-GB", loop=3)
    return response


def _forotherquery():
    response = VoiceResponse()
    response.dial(reception_number,timeout=30,action=url_for('receptionCB',_scheme='http',_external=True), method="POST")
    return response

@app.route('/ivr/receptionCB', methods=['GET','POST'])
def receptionCB():
    response = VoiceResponse()
    response.dial(manager_number, timeout=30,action=url_for('managerCB',_scheme='http',_external=True), method="POST")
    return response

@app.route('/ivr/managerCB', methods=['GET','POST'])
def managerCB():
    response = VoiceResponse()
    response.dial(owner_number, timeout=30,action=url_for('managerCB',_scheme='http',_external=True), method="POST")
    return response

@app.route('/ivr/ownerCB', methods=['GET','POST'])
def ownerCB():
    client = Client(auth_id, auth_secret)
    # Send SMS to owner and manager. 
    message = client.messages.create(
                              body='Missed Call for the customer ' + request.form.get('From'),
                              from_=sender_id,
                              to=manager_number
                          )
    message = client.messages.create(
                            body='Missed Call for the customer : '+request.form.get('From'),
                            from_=sender_id,
                            to=owner_number
                        )
    return


@app.route('/ivr/tableservationtimetomorrow', methods=['POST'])
def tableservationtimetomorrow():
    #selected_option = request.form['Digits']
    app.logger.error("tableservationtimetomorrow response = %s" % request.get_json())
    digit = None
    if request.get_json() is not None:
        if 'Digits' in request.get_json():
            selected_option = request.json.get('Digits')
    # selected_option = request.form['Digits']
    app.logger.error("tableservationtimetomorrow digit received = %s" % selected_option)
    option_actions = {'1': "breakfast",
                      '2': "lunch",
                      '3': "dinner"}

    print("Table is booked for tomorrow for %s" % option_actions[selected_option])
    ###SEND SMS https://github.com/tiniyo/tiniyo-python
    return _redirect_confirmation("Tomorrow "+option_actions[selected_option], request.form.get("From"))

@app.route('/ivr/tableservationtimetoday', methods=['POST'])
def tableservationtimetoday():
    app.logger.error("tableservationtimetoday response = %s" % request.get_json())
    digit = None
    if request.get_json() is not None:
        if 'Digits' in request.get_json():
            selected_option = request.json.get('Digits')
    # selected_option = request.form['Digits']
    app.logger.error("tableservationtimetoday digit received = %s" % selected_option)
    option_actions = {'1': "breakfast",
                      '2': "lunch",
                      '3': "dinner"}
    print("Table is booked for today for %s" % option_actions[selected_option])
    ###SEND SMS https://github.com/tiniyo/tiniyo-python
    return _redirect_confirmation("Today "+option_actions[selected_option], request.form.get("From"))


@app.route('/ivr/reservation_day', methods=['POST'])
def reservation_day():
    app.logger.error("reservation_day response = %s" % request.get_json())
    digit = None
    if request.get_json() is not None:
        if 'Digits' in request.get_json():
            selected_option = request.json.get('Digits')
    # selected_option = request.form['Digits']
    app.logger.error("reservation_day digit received = %s" % selected_option)
    option_actions = {'1': "today",
                      '2': "tomorrow",
                      '*': "welcome"}

    if selected_option in option_actions:
        if int(selected_option) == 1:
            response = _tableservationtime_today()
            return tiniyoml(response)
        elif int(selected_option) == 2:
            response = _tableservationtime_tomorrow()
            return tiniyoml(response)
    return _redirect_welcome()


def _redirect_welcome():
    response = VoiceResponse()
    response.say("No Digit received. Returning to the main menu", voice="alice", language="en-GB")
    response.redirect(url_for('welcome',_scheme='http',_external=True) )

    return tiniyoml(response)

def _redirect_confirmation(time, customer_number):
    response = VoiceResponse()
    response.say("Your reservation is successfully booked for "+time+". You will received sms shortly", voice="alice", language="en-GB")
    response.say("Good Bye", voice="alice", language="en-GB")
    
    client = Client(auth_id, auth_secret)
    # Send SMS to customer of confirmation. 
    message = client.messages.create(
                              body="Your reservation is successfully booked for "+ time +".",
                              from_=sender_id,
                              to=customer_number
                          )
    return tiniyoml(response)


if __name__ == '__main__':
    app.run()
