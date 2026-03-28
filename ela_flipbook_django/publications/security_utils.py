# publications/security_utils.py

import os
from django.utils import timezone
from datetime import timedelta
from .models import SecurityEvent, SecurityConfiguration, User
from .utils import send_single_email

def get_client_ip(request):
    """Extracts the client's IP address from the request."""
    if not request:
        return '0.0.0.0'
        
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip or '0.0.0.0'

def detect_anomalies(user, ip, event_type, request=None):
    """
    Checks for high-priority security anomalies:
    1. Brute force (too many failures from same IP or for same user).
    2. Login from a new IP for this user.
    """
    config = SecurityConfiguration.objects.first()
    if not config:
        config = SecurityConfiguration.objects.create()

    # 1. Brute Force Detection (Failed Logins)
    if event_type == 'login_failed':
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        # Count failures for this IP
        ip_failures = SecurityEvent.objects.filter(
            ip_address=ip,
            event_type='login_failed',
            timestamp__gte=one_hour_ago
        ).count()

        if ip_failures >= config.max_failed_attempts:
            # Trigger alert for brute force from IP
            send_critical_alert(
                f"Potential Brute Force from IP: {ip}",
                f"We detected {ip_failures} failed login attempts from IP {ip} in the last hour.",
                config.admin_email
            )
            return "brute_force_ip"

        # Count failures for this user (if provided)
        if user:
            user_failures = SecurityEvent.objects.filter(
                user=user,
                event_type='login_failed',
                timestamp__gte=one_hour_ago
            ).count()

            if user_failures >= config.max_failed_attempts:
                send_critical_alert(
                    f"Account Security Alert: {user.email}",
                    f"There have been {user_failures} failed login attempts for account {user.email} in the last hour.",
                    config.admin_email
                )
                return "brute_force_user"

    # 2. New IP Detection (Successful Login)
    if event_type == 'login_success' and user and config.alert_on_new_ip:
        # Check if this user has logged in from this IP before
        previous_login = SecurityEvent.objects.filter(
            user=user,
            ip_address=ip,
            event_type='login_success'
        ).exclude(timestamp=SecurityEvent.objects.filter(user=user, event_type='login_success').latest('timestamp').timestamp).exists()
        
        # Simplified: Just check if any previous success from this IP exists
        known_ip = SecurityEvent.objects.filter(
            user=user,
            ip_address=ip,
            event_type='login_success'
        ).count() > 1 # Current one is already saved if we call this after saving

        if not known_ip and SecurityEvent.objects.filter(user=user, event_type='login_success').count() > 1:
            # Send alert to the user about login from new IP
            send_security_notification_to_user(user, ip, request)
            return "new_ip"

    return None

def send_critical_alert(subject, message, recipient_email):
    """Sends a high-priority alert to the admin."""
    # We can use send_single_email or a direct mail call
    # Since send_single_email logs to EmailLog and requires a User object,
    # let's find a staff user or just use direct email if no user is provided.
    admin_user = User.objects.filter(email=recipient_email).first()
    
    if admin_user:
        context = {
            'alert_message': message,
            'timestamp': timezone.now(),
        }
        # We might need a specific template for security alerts
        # For now, let's just use a simple one if it exists or create it
        send_single_email(admin_user, f"[SECURITY ALERT] {subject}", 'publications/emails/security_alert.html', context, 'notification', force_manual=True)
    else:
        # Fallback to standard Django mail if no user object matches admin_email
        from django.core.mail import send_mail
        send_mail(
            f"[SECURITY ALERT] {subject}",
            message,
            os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@businessmatters.co.ke'),
            [recipient_email],
            fail_silently=True
        )

def send_security_notification_to_user(user, ip, request=None):
    """Notifies the user about a login from a new IP."""
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown Device') if request else 'Unknown Device'
    context = {
        'user': user,
        'ip_address': ip,
        'user_agent': user_agent,
        'timestamp': timezone.now(),
    }
    send_single_email(user, "New Login Detected", 'publications/emails/new_ip_login.html', context, 'notification')

def log_security_event(user, event_type, request, details=None):
    """Helper to log a security event and check for anomalies."""
    ip = get_client_ip(request)
    ua = request.META.get('HTTP_USER_AGENT', '') if request else 'Unknown'
    
    event = SecurityEvent.objects.create(
        user=user,
        event_type=event_type,
        ip_address=ip,
        user_agent=ua,
        details=details
    )
    
    # Check for anomalies
    anomaly = detect_anomalies(user, ip, event_type, request)
    if anomaly:
        event.details = event.details or {}
        event.details['anomaly_detected'] = anomaly
        event.save(update_fields=['details'])
    
    return event
