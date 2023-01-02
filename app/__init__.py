from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
import json
#import pymunk
from flask_cors import CORS
app = Flask(__name__)

#configure app
app.config['SECRET_KEY'] = 'xx'
app.config['SQLALCHEMY_DATABASE_URI'] =  "sqlite:///pilot.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

from . import views

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    #app.run()


#export FLASK_APP=__init__.py
#flask shell
#from app import db
#db.create_all()
#use gunicorn to run - https://exploreflask.com/en/latest/deployment.html
#gunicorn -w <num workers> <dir to folder containing init file>:app -b <host and port, prob 0.0.0.0:xxxx>
#then will be running at http://18.18.93.98:xxxx/<whatever url is, prob study>


#ssh tracey@18.18.93.98
#Server Account
#screen
#bash

#screen -ls
#screen -d to detach
#screen -r to reattach 
#ctra d to detach from screen

#to get data from database to json:
#sqlite-utils pilot.db "select * from trials" --json-cols > trials.json