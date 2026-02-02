from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_suspicious_ips():
    """Flag IPs with >100 requests/hour or accessing sensitive paths"""
    one_hour_ago = timezone.now() - timedelta(hours=1)
    sensitive_paths = ['/admin', '/login']

    # Aggregate IPs with request count > 100
    from django.db.models import Count
    heavy_users = (
        RequestLog.objects.filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(request_count=Count('id'))
        .filter(request_count__gt=100)
    )

    # Save suspicious activity
    for entry in heavy_users:
        ip = entry['ip_address']
        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            defaults={'reason': 'Excessive requests (>100/hour)'}
        )

    # Check sensitive path access
    for path in sensitive_paths:
        logs = RequestLog.objects.filter(path__icontains=path, timestamp__gte=one_hour_ago)
        for log in logs:
            SuspiciousIP.objects.get_or_create(
                ip_address=log.ip_address,
                defaults={'reason': f'Accessed sensitive path: {path}'}
            )
