from flask import (
    Flask,
    request,
    url_for,
)
from tiniyo.voice_response import VoiceResponse
from helper import tiniyoml

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
    selected_option = request.form['Digits']
    option_actions = {'1': "tablebooking",
                      '2': "loyalitypoint",
                      '3': "otherquery"}

    if selected_option in option_actions:
        if int(selected_option) == 1:
            response = _tablereservation()
            return tiniyoml(response)
        elif int(selected_option) == 2:
            response = _loyality_point()
            return tiniyoml(response)
        elif int(selected_option) == 3:
            response = _forotherquery()
            return tiniyoml(response)
    else:
        return _redirect_welcome()


def _loyality_point(response):
    response.say("To get to _loyality_point, please visit our website",voice="alice", language="en-GB")
    response.hangup()
    return response


def _tablereservation(response):
    with response.gather(
        numDigits=1, action=url_for('/ivr/reservation_day'), method="POST"
    ) as g:
        g.say("Press 1 for today " +
              "Press 2 for tomorrow " +
              "To go back to the main menu " +
              " press the star key.",
              voice="alice", language="en-GB", loop=3)

    return response

def _tableservationtime_today(response):
    with response.gather(
        numDigits=1, action=url_for('/ivr/tableservationtimetoday'), method="POST"
    ) as g:
        g.say("Press 1 for breakfast, press 2 for lunch, press 3 for dinner" ,voice="alice", language="en-GB", loop=3)
    return response

def _tableservationtime_tomorrow(response):
    with response.gather(
        numDigits=1, action=url_for('/ivr/tableservationtimetomorrow'), method="POST"
    ) as g:
        g.say("Press 1 for breakfast, press 2 for lunch, press 3 for dinner" ,voice="alice", language="en-GB", loop=3)
    return response


def _forotherquery(response):
    response.dial('xxxxxxxxx',timeout=30,ring_tone='https://tiniyo.s3-ap-southeast-1.amazonaws.com/public/KolkataMixtapeWelcome.mp3',action=url_for('/forotherqueryCB'))
    return tiniyoml(response)


@app.route('/ivr/tableservationtimetomorrow', methods=['POST'])
def reservation_time_tomorrow():
    selected_option = request.form['Digits']
    option_actions = {'1': "breakfast",
                      '2': "lunch",
                      '3': "dinner"}

    if selected_option in option_actions:
        if int(selected_option) == 1:
            response = reservation_time_today()
            return tiniyoml(response)
        elif int(selected_option) == 2:
            response = reservation_time_tomorrow()
            return tiniyoml(response)

@app.route('/ivr/tableservationtimetoday', methods=['POST'])
def reservation_time_today():
    selected_option = request.form['Digits']
    option_actions = {'1': "breakfast",
                      '2': "lunch",
                      '3': "dinner"}

    if selected_option in option_actions:
        if int(selected_option) == 1:
            response=reservation_time_today()
            return tiniyoml(response)
        elif int(selected_option) == 2:
            response=reservation_time_tomorrow()
            return tiniyoml(response)

@app.route('/ivr/reservation_day', methods=['POST'])
def reservation_day():
    selected_option = request.form['Digits']
    option_actions = {'1': "today",
                      '2': "tomorrow",
                      '*': "welcome"}

    if selected_option in option_actions:
        if int(selected_option) == 1:
            response = reservation_time_today()
            return tiniyoml(response)
        elif int(selected_option) == 2:
            response = reservation_time_tomorrow()
            return tiniyoml(response)

    return _redirect_welcome()

def _redirect_welcome():
    response = VoiceResponse()
    response.say("Returning to the main menu", voice="alice", language="en-GB")
    response.redirect(url_for('welcome'))

    return tiniyoml(response)

if __name__ == '__main__':
    app.run()