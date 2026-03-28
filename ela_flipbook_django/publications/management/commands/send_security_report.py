from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from publications.models import SecurityEvent, SecurityConfiguration, User
from publications.security_utils import send_critical_alert

class Command(BaseCommand):
    help = 'Sends a daily security report to the admin.'

    def handle(self, *args, **options):
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        
        events = SecurityEvent.objects.filter(timestamp__gte=yesterday)
        
        if not events.exists():
            self.stdout.write(self.style.SUCCESS("No security events in the last 24 hours."))
            return

        total_count = events.count()
        success_count = events.filter(event_type='login_success').count()
        failed_count = events.filter(event_type='login_failed').count()
        anomalies = events.filter(details__has_key='anomaly_detected').count()
        
        top_ips = events.values('ip_address').annotate(count=Count('ip_address')).order_by('-count')[:5]
        
        report_msg = f"Security Summary for {yesterday.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}\n\n"
        report_msg += f"Total Events: {total_count}\n"
        report_msg += f"Successful Logins: {success_count}\n"
        report_msg += f"Failed Attempts: {failed_count}\n"
        report_msg += f"Anomalies Detected: {anomalies}\n\n"
        
        report_msg += "Top IP Addresses:\n"
        for ip in top_ips:
            report_msg += f"- {ip['ip_address']}: {ip['count']} events\n"
            
        config = SecurityConfiguration.objects.first()
        admin_email = config.admin_email if config else 'nigel2421@gmail.com'
        
        self.stdout.write(f"Sending security report to {admin_email}...")
        
        # Using a simple subject for the report
        send_critical_alert("Daily Security Report", report_msg, admin_email)
        
        self.stdout.write(self.style.SUCCESS("Security report sent successfully."))
