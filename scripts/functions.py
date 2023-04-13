import pyrebase
import json
# from urllib.error import HTTPError
from requests.exceptions import HTTPError
import re

import firebase_admin
from firebase_admin import auth as firebase_admin_auth
from firebase_admin import credentials as firebase_admin_credentials
from firebase_admin import db as firebase_admin_db
from firebase_admin import storage as firebase_admin_storage

# TODO: REVIEW 
#-----------these lines to be reviewed
config_file = open("./config.json")
config = json.load(config_file)
config_file.close()

creds_file = open("./creds.json")
creds = json.load(creds_file)
creds_file.close()

dbURL_file = open("./dbURL.json")
dbURL = json.load(dbURL_file)
dbURL_file.close()


pyrFirebase = pyrebase.initialize_app(config)
pyrAuth = pyrFirebase.auth()

cred = firebase_admin_credentials.Certificate(creds)
fbAdmin = firebase_admin.initialize_app(cred, dbURL)

#firebase = pyrebase.initialize_app("./key.json")

def login(email, password):
    # global auth
    try:
        return pyrAuth.sign_in_with_email_and_password(email, password)
    except Exception as e :
        return False

def sign_up(email, password,displayName):
    result=[False,"no user"]
    try:
        user = pyrAuth.create_user_with_email_and_password(email,password)
        # user. add data to user like account type and uid ...etc
        result[0]=True
        # print(user)
        result[1]=user["email"]
        if (email.split('@')[1].split(".")[0]=="admin"):
            # print(user["localId"])
            ref = firebase_admin_db.reference('/')
            ref.child("users").child(user["localId"]).child("displayName").set(displayName.split("_")[0])
            ref.child("users").child(user["localId"]).child("email").set(email)
            ref.child("users").child(user["localId"]).child("rank").set(displayName.split("_")[1])
            # print(user)
        return result
    except Exception as e:
        #had to work like this because I couldn't parse HTTPError type and I don't have time to look for a way
        
        # err_str = str(e)
        # err_str = err_str.split('"message": "')[1]
        # err_str = err_str.split('",')[0]

        #--alt solution
        # err_str = err_str.replace(str(e.errno),"")

        #--------- jaqee's solution -----------
        err_str = str(e)
        err_str = re.sub(r'\[.*\] ','',err_str)
        err_str = json.loads(err_str)

        print(err_str["error"]["errors"][0]["message"])

        result[0]=False
        result[1]=err_str["error"]["errors"][0]["message"]
        
        return result
    
def delete_user(email):
    try : 
        user = firebase_admin_auth.get_user_by_email(email)
        # print(user.__dict__["_data"]["localId"])
        firebase_admin_auth.delete_user(user.uid)
        #TODO: delete child DATA in Realtime DB
        if(email.split('@')[1].split(".")[0]=="admin"):
            ref = firebase_admin_db.reference('/')
            ref.child("users").child(user.uid).delete()
        return "deleted user : " + user.email
        # return "done"
    except Exception as e:
        print(e)
        return False

def get_data(uid):
    res=["dName","rnk"]
    ref = firebase_admin_db.reference('/')
    res[0]=ref.child("users").child(uid).child("displayName").get()
    res[1]=ref.child("users").child(uid).child("rank").get()
    return res