from .token_service import generate_token
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from fundoo.settings import EMAIL_HOST_USER
from django_short_url.views import get_surl
from django_short_url.models import ShortURL
from util import static_data
from django.template.loader import render_to_string

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
    send_mail(subject, msg, EMAIL_HOST_USER,
                    [email], fail_silently=False)