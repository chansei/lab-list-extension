from __future__ import print_function

import base64
import email
import os.path
import re

import dateutil.parser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# 二段階認証のメールにフィルタでラベル付与して、そのラベルを基にメール検索
LABEL_ID = "Label_8448835002496324100"


def decode(encoded):  # 複合化
    decoded = base64.urlsafe_b64decode(encoded).decode()
    return decoded

def gmail_get_messages_body(service, labelIdsValue):  # メール本文の取得
    mailBody = []
    messages = service.users().messages()
    msg_list = messages.list(
        userId='me', labelIds=labelIdsValue, maxResults=1).execute()
    for msg in msg_list['messages']:
        date = gmail_get_messages_body_date(messages, msg)
        topid = msg['id']
        msg = messages.get(userId='me', id=topid).execute()

        if (msg["payload"]["body"]["size"] != 0):
            mailBody.append(date+"<br>"+decode(msg["payload"]["body"]["data"]))
        else:
            # メールによっては"parts"属性の中に本文がある場合もある
            mailBody.append(
                date+"<br>"+decode(msg["payload"]["parts"][0]["body"]["data"]))
    return mailBody


def gmail_get_messages_body_date(messages, msg):  # 受信日時の取得
    msg_id = msg['id']
    m = messages.get(userId='me', id=msg_id, format='raw').execute()
    raw = base64.urlsafe_b64decode(m['raw'])
    eml = email.message_from_bytes(raw)
    date = dateutil.parser.parse(eml.get('Date')).strftime("%Y-%m-%d_%H-%M-%S")
    return date

def get_auth_key():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    mails = gmail_get_messages_body(service, LABEL_ID)

    return mails[0][57:65]  # 正規表現で動かそうとしたけど上手くいかないのでとりあえず絶対位置指定

if __name__ == '__main__':
    get_auth_key()
