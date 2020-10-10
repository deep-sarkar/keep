from .token_service import generate_token
from django.contrib.sites.shortcuts import get_current_site
from fundoo.settings import EMAIL_HOST_USER
from django_short_url.views import get_surl
from django_short_url.models import ShortURL
from util import static_data
from django.template.loader import render_to_string
from account.task import send_fundoo_mail

def send_account_activation_mail(request):
    username             = request.data.get('username')
    email                = request.data.get('email')
    password             = request.data.get('password')
    payload = {
        'username':username,
        'password':password
    }
    token       = generate_token(payload)
    surl        = get_surl(str(token)) 
    final_url   = surl.split('/')
    curren_site = get_current_site(request)
    domain      = curren_site.domain
    subject     = static_data.ACCOUNT_ACTIVATION_SUBJECT
    msg = render_to_string(
            'account/account_activation.html',
            {
                'username': username, 
                'domain': domain,
                'surl': final_url[2],
            })
    send_fundoo_mail.delay(subject, msg, [email])

def send_forgot_password_mail(request, username):
    email = request.data.get('email')
    payload = {
                'username': username,
                }
    token = generate_token(payload)
    current_site = get_current_site(request)
    domain_name = current_site.domain
    surl = get_surl(str(token))
    final_url = surl.split("/")
    mail_subject = static_data.PASSWORD_RESET_MESSAGE
    msg = render_to_string(
        'account/forgot_password.html',
        {
            'username': username, 
            'domain': domain_name,
            'surl': final_url[2],
            })         
    send_fundoo_mail.delay(mail_subject, msg, [email])