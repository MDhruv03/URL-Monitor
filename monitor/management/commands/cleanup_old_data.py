"""
Django management command to clean up old monitoring data.
Usage: python manage.py cleanup_old_data --days 90
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from monitor.models import URLStatus, Notification


class Command(BaseCommand):
    help = 'Clean up old monitoring data to save database space'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days of data to keep (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        self.stdout.write(
            self.style.WARNING(
                f"{'[DRY RUN] ' if dry_run else ''}Cleaning up data older than {days} days "
                f"(before {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')})"
            )
        )

        # Clean URLStatus records
        old_statuses = URLStatus.objects.filter(timestamp__lt=cutoff_date)
        status_count = old_statuses.count()
        if not dry_run:
            old_statuses.delete()
        self.stdout.write(
            self.style.SUCCESS(f"{'Would delete' if dry_run else 'Deleted'} {status_count} URL status records")
        )

        # Clean old read notifications
        old_notifications = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        )
        notif_count = old_notifications.count()
        if not dry_run:
            old_notifications.delete()
        self.stdout.write(
            self.style.SUCCESS(f"{'Would delete' if dry_run else 'Deleted'} {notif_count} read notifications")
        )

        total_deleted = status_count + notif_count
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'Would delete' if dry_run else 'Deleted'} a total of {total_deleted} records"
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("\nThis was a dry run. No data was actually deleted.")
            )
