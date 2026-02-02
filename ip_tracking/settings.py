pip install django-ratelimit
# settings.py

INSTALLED_APPS = [
    ...
    'ratelimit',
]
# settings.py

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# ip_tracking/views.py

from django.shortcuts import render
from ratelimit.decorators import ratelimit

# Anonymous users: 5 requests per minute (by IP)
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
# Authenticated users: 10 requests per minute (by user)
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def login_view(request):
    if request.method == 'POST':
        # Your login logic here
        pass

    return render(request, 'login.html')
