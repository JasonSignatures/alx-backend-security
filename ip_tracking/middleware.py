from .models import, BlockedIP, RequestLog
import logging
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django_ip_geolocation.backends import IPGeolocationAPI

class RequestLoggingMiddleware:
    """
    Middleware that logs the IP address, timestamp, and path of each incoming request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the IP address of the client
        ip_address = self.get_client_ip(request)
        path = request.path
        timestamp = timezone.now()

        # Log request details to database
        RequestLog.objects.create(ip_address=ip_address, path=path, timestamp=timestamp)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """
        Returns the real client IP address, even if behind a proxy.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geo_backend = IPGeolocationAPI()  # or get via settings

    def __call__(self, request):
        ip_address = self.get_client_ip(request)

        # block check
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Access Denied: Your IP has been blocked.")

        path = request.path

        # caching key
        cache_key = f"geoip_{ip_address}"
        geo_data = cache.get(cache_key)
        if not geo_data:
            try:
                result = self.geo_backend.get_details(ip_address)
                country = result.get('country_name') or result.get('country')
                city = result.get('city')
            except Exception as e:
                logging.warning(f"Geo lookup failed for {ip_address}: {e}")
                country = None
                city = None
            geo_data = {'country': country, 'city': city}
            # cache for 24 hours
            cache.set(cache_key, geo_data, 24 * 3600)

        else:
            country = geo_data.get('country')
            city = geo_data.get('city')

        # log the request
        RequestLog.objects.create(
            ip_address=ip_address,
            path=path,
            country=country,
            city=city,
            timestamp=timezone.now()
        )

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
