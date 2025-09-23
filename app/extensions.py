from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# initialize the app
app = Flask(__name__)

#set up database conn
# app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:admin@localhost:5432/flask_api'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://myduka_user:Admin123@172.17.0.1/:5432/myduka_api'


#basedir = os.path.abspath(os.path.dirname(__file__))
#print("basedir-----",basedir)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'flask_api.db')





# disable events tracks object changes
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

app.config['SQLALCHEMY_ECHO'] = True

#bind sqlalchemy to our flask application
db=SQLAlchemy(app)

app.config["JWT_SECRET_KEY"] = "MyKey@123"
CORS(app, resources={r"/*": {"origins": "*"}})

#set up the database connection
# CREATE USER myDuka_user WITH PASSWORD 'admin';
# GRANT CONNECT ON DATABASE myDuka_api TO myDuka_user;

#CREATE USER myDuka_user WITH PASSWORD 'admin';
#GRANT ALL PRIVILEGES ON DATABASE flask_api TO myDuka_user;