from flask import render_template, request, make_response, session
from . import app, db
from .models import Subject, Trial
import datetime
import json
from .game import update_game, init_game
from .generate_trials import get_trial_info

# Views
# converts function output to an http response to be displayed by a client
#responds to web request from this url:

url_str = ""
#url_str = "/study"

@app.route(url_str + '/get_trial', methods=['GET'])
def get_trial():
    imd = request.args
    trial_data = imd.to_dict(flat=False)
    return get_trial_info(trial_data["trial_type"])

@app.route(url_str + '/init_trial', methods=['POST'])
def init_trial():
    data = request.get_json(force=True)
    init_game(data)
    return "all good mate"

@app.route(url_str + '/callback', methods=['GET'])
def get_update():
    imd = request.args
    user_data = imd.to_dict(flat=False)
    return update_game(user_data)


@app.route(url_str + '/', methods=['GET', 'POST'])
def experiment():
    if request.method == 'GET':
        #renders experiment on screen
        #return render_template('index.html', posts=posts)
        #init game here?
        return render_template('experiment.html')
    if request.method == 'POST':
        #sometimes we want to collect data, othertimes we want to collect info about user actions in the game
        #in our plugin, we will record if they press left or whatever and send this info somehow - just need to specify url
        #want to also return pygame game state (ball pos, tool pos, success, what else?)
        #or, can we do this without doing render template? can we just store the var in the html file?

        dd = request.get_json(force=True)['data']
        #subject information
        if dd['exp_phase'] == 'subject_info':
            print('recording subject data')
            ret = Subject( subject_id= str(dd['subject_id']),
                           comments = str(dd['comments']),
                           comments_rt = str(dd['comments_rt']),
                           prog_bg = str(dd['prog_bg']),
                           math_bg = str(dd['math_bg']),
                           bg_comments = str(dd['bg_comments']),
                           completion_code = str(dd['completion_code']),
                           age= str(dd['age']),
                           gender= str(dd['gender']),
                           nationality= str(dd['nationality']),
                           country= str(dd['country']),
                           student= str(dd['student']),
                           language= str(dd['language']),
                           education= str(dd['education']))
        #trial response
        else:
            print('recording trial data')
            ret = Trial( row_id = str(dd['subject_id']) + str(dd['func_idx']),
                           confidence = str(dd['confidence']),
                           confidence_rt = str(dd['confidence_rt']),
                           complexity = str(dd['complexity']),
                           complexity_rt = str(dd['complexity_rt']),
                           true_x = str(dd['true_x']),
                           true_y = str(dd['true_y']),
                           response_x = str(dd['response_x']),
                           response_y = str(dd['response_y']),
                           rts = str(dd['rts']),
                           func = str(dd['func']),
                           func_idx = str(dd['func_idx']))

        db.session.add(ret)
        db.session.commit()
        return make_response("", 200)