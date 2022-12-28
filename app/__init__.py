from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xx'
app.config['SQLALCHEMY_DATABASE_URI'] =  "sqlite:///pilot.db"  #config.get('SQLALCHEMY_DATABASE_URI') #make local db for testing
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)
from . import views
if __name__ == '__main__':
    app.run()


#fl
#flask shell
#export ..
#db.create_all()
#flask run -h 0.0.0.0 -p 1717

#export FLASK_APP=__init__
#flask run

#ssh tracey@18.18.93.98
#Server Account
#bash
#screen -ls
#screen -d to detach
#screen -r to reattach 
#ctra d to detach from screen

#to run locally, url in views and experiment should be "/"
#to run on server, url = '/study' or whatever
#li125-172.members.linode.com


#to get data from database to json:
#sqlite-utils pilot.db "select * from trials" --json-cols > trials.json