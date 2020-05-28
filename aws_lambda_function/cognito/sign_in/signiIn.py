from __future__ import print_function
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json
import uuid
import pymongo

 
# COGNITO CONFIGURATION
USER_POOL_ID = ''
CLIENT_ID = ''
CLIENT_SECRET = ''

ERROR = 0
SUCCESS = 1
USER_EXISTS = 2

client = None

def get_secret_hash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'), 
        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2
    
def sign_up(username, password):
    try:
        resp = client.sign_up(
            ClientId=CLIENT_ID,
            SecretHash=get_secret_hash(username),
            Username=username,
            Password=password)
        print(resp)
    except client.exceptions.UsernameExistsException as e:
        return USER_EXISTS
    except Exception as e:
        print(e)
        return ERROR
    return SUCCESS

def lambda_handler(event, context):
    global client
    if client == None:
        client = boto3.client('cognito-idp')

    print(event)
    body = event
    username = body['username']
    password = body['password']
    is_new = "false"
    user_id = str(uuid.uuid4())
    signed_up = sign_up(username, password)
    if signed_up == ERROR:
        return {'status': 'fail', 'msg': 'failed to sign up'}
    if signed_up == USER_EXISTS:
        return {'status': 'fail', 'msg': 'username already exist'}
    if signed_up == SUCCESS:
        is_new = "true"
        
        #scrittura su mongo
        myclient = pymongo.MongoClient("mongodb://admin:<password>@mycluster0-shard-00-00-wikeo.mongodb.net:27017,mycluster0-shard-00-01-wikeo.mongodb.net:27017,mycluster0-shard-00-02-wikeo.mongodb.net:27017/test?ssl=true&replicaSet=MyCluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
        mydb = myclient["tedx_users"]
        mycol = mydb["users"]
        mydict = { "id_user": user_id, "username": username }
        mycol.insert_one(mydict)
        
        return {'status': 'success', 'user_id': user_id, 'description': 'user successfully signed up'}