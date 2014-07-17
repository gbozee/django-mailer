import httplib2
from apiclient.discovery import build

import base64

ME = 'me'


class Bunch(object):
    def __init__(self, *args, **kwargs):
        self.__dict__ = kwargs
        self.pk = self.id

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name, m2m=True, related_objects=True,
                                         related_m2m=True, virtual=True)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)

class Thread(Bunch):
    def __unicode__(self):
        return self.id


class Message(Bunch):
    pass


def _get_gmail_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)


def _make_message(msg):
    body = ''.join(base64.urlsafe_b64decode(p['body']['data'].encode('utf-8')) for p in msg['payload']['parts'])
    sender = [h['value'] for h in msg['payload']['headers'] if h['name'] == 'From'][0]
    receiver = [h['value'] for h in msg['payload']['headers'] if h['name'] == 'To'][0]
    return Message(
        id=msg['id'],
        receiver=receiver,
        sender=sender,
        body=body
    )


def get_messages_by_thread_id(credentials, thread_id):
    gmail = _get_gmail_service(credentials)
    thread = gmail.users().threads().get(
        userId=ME,
        id=thread_id
    ).execute()

    return map(_make_message, thread['messages'])


def get_all_threads(credentials):
    gmail = _get_gmail_service(credentials)
    threads = gmail.users().threads().list(
        userId=ME,
    ).execute()['threads']
    return tuple(Thread(id=t['id'], number_of_messages=None) for t in threads)


def get_thread_by_id(credentials, thread_id):
    gmail = _get_gmail_service(credentials)
    thread = gmail.users().threads().get(
        userId=ME,
        id=thread_id
    ).execute()
    return Thread(
        id=thread['id'],
        number_of_messages=len(thread['messages'])
    )


def get_message_by_id(credentials, message_id):
    gmail = _get_gmail_service(credentials)
    message = gmail.users().messages().get(
        userId=ME,
        id=message_id
    ).execute()
    return _make_message(message)