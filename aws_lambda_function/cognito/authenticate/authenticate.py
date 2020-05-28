from __future__ import print_function
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json
import uuid
 
# COGNITO CONFIGURATION
USER_POOL_ID = ''
CLIENT_ID = ''
CLIENT_SECRET = ''


client = None

def get_secret_hash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'), 
        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2
    
    
def initiate_auth(username, password):
    try:
        resp = client.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'SECRET_HASH': get_secret_hash(username),
                'PASSWORD': password
            },
            ClientMetadata={
                'username': username,
                'password': password
            })
    except client.exceptions.NotAuthorizedException as e:
        return None, "The username or password is incorrect"
    except Exception as e:
        print(e)
        return None, "Unknown error"
    return resp, None

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
    resp, msg = initiate_auth(username, password)
    if msg != None:
        return {'status': 'fail', 'msg': msg}
    id_token = resp['AuthenticationResult']['IdToken']
    print('id token: ' + id_token)
    return {'status': 'success', 'id_token': id_token, 'user_id': user_id, 'is_new': is_new}