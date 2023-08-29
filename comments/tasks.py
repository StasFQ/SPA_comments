import requests
from celery import shared_task
from django.core.mail import send_mail as django_send_mail


@shared_task
def send_mail(subject, text, email):
    django_send_mail(subject, text, email, ['admin@example.com'])


@shared_task
def get_jwt_token():
    url = 'http://web:8000/api/api/token/'
    data = {
        'username': 'admin',
        'password': 'admin'
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token = response.json().get("access")
        get_comment_count(token)
    return None


#Примерная таска, не имеет особой логики
@shared_task
def get_comment_count(jwt_token):
    headers = {
        'Authorization': f'Bearer {jwt_token}'
    }
    url = 'http://web:8000/api/comments/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        comments = response.json()
        comment_count = len(comments)
        return comment_count
    return None
