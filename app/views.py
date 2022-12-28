from flask import render_template, request, make_response, session
from . import app, db
from .models import Subject, Trial
import datetime
import json


# Views
# converts function output to an http response to be displayed by a clienr
#responds to web request from this url:
#@app.route('/study', methods=['GET', 'POST'])
@app.route('/callback', methods=['GET', 'POST'])
def get_update():
    return {"x":"heyyyy buddy"}
    #return update_game(request.args.get('user_data'))

@app.route('/', methods=['GET', 'POST'])
def experiment():
    if request.method == 'GET':
        #renders experiment on screen
        #to get the desired game state information, must return from pymunk - each time we step, either download, or just call from here!
        #return render_template('index.html', posts=posts)
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