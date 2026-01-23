from django.shortcuts import render
from django.http import HttpResponse
from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.views import View

# Example function-based view
@ratelimit(key='ip', rate='5/m', block=True)  # anonymous users
def anonymous_login_view(request):
    return HttpResponse("Anonymous login attempt allowed.")

# Example class-based view (for authenticated users)
@method_decorator(ratelimit(key='user', rate='10/m', block=True), name='dispatch')
class SecureLoginView(View):
    def get(self, request):
        return HttpResponse("Authenticated login page.")
