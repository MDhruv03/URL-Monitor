"""
Django management command to clean up data for deleted URLs
Usage: python manage.py cleanup_deleted_urls
"""
from django.core.management.base import BaseCommand
from monitor.models import (
    URLStatus, PageView, ClickHeatmap,
    MouseMovement, PerformanceMetric,
    Alert, Notification, MonitoredURL
)


class Command(BaseCommand):
    help = 'Clean up all data associated with deleted (is_active=False) URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write(
            self.style.WARNING(
                f"{'[DRY RUN] ' if dry_run else ''}Cleaning up data for deleted URLs..."
            )
        )

        # Get all inactive URLs
        inactive_urls = MonitoredURL.objects.filter(is_active=False)
        inactive_count = inactive_urls.count()
        
        if inactive_count == 0:
            self.stdout.write(self.style.SUCCESS("No deleted URLs found. Nothing to clean up."))
            return

        self.stdout.write(f"Found {inactive_count} deleted URL(s)")

        total_deleted = 0

        # Clean URLStatus
        url_statuses = URLStatus.objects.filter(url__is_active=False)
        status_count = url_statuses.count()
        if not dry_run and status_count > 0:
            url_statuses.delete()
        total_deleted += status_count
        self.stdout.write(
            self.style.SUCCESS(f"{'Would delete' if dry_run else 'Deleted'} {status_count} URL status records")
        )

        # Clean PageViews
        pageviews = PageView.objects.filter(url__is_active=False)
        pageview_count = pageviews.count()
        if not dry_run and pageview_count > 0:
            pageviews.delete()
        total_deleted += pageview_count
        self.stdout.write(
            self.style.SUCCESS(f"{'Would delete' if dry_run else 'Deleted'} {pageview_count} pageview records")
        )

        # Clean ClickHeatmaps
        clicks = ClickHeatmap.objects.filter(url__is_active=False)
        click_count = clicks.count()
        if not dry_run and click_count > 0:
            clicks.delete()
        total_deleted += click_count
        self.stdout.write(
            self.style.SUCCESS(f"{'Would delete' if dry_run else 'Deleted'} {click_count} click heatmap records")
        )

        # Clean MouseMovements
        movements = MouseMovement.objects.filter(url__is_active=False)
        movement_count = movements.count()
        if not dry_run and movement_count > 0:
            movements.delete()
        total_deleted += movement_count
        self.stdout.write(
            self.style.SUCCESS(f"{'Would delete' if dry_run else 'Deleted'} {movement_count} mouse movement records")
        )

        # Clean PerformanceMetrics
        perf_metrics = PerformanceMetric.objects.filter(url__is_active=False)
        perf_count = perf_metrics.count()
        if not dry_run and perf_count > 0:
            perf_metrics.delete()
        total_deleted += perf_count
        self.stdout.write(
            self.style.SUCCESS(f"{'Would delete' if dry_run else 'Deleted'} {perf_count} performance metric records")
        )

        # Clean Alerts
        alerts = Alert.objects.filter(url__is_active=False)
        alert_count = alerts.count()
        if not dry_run and alert_count > 0:
            alerts.delete()
        total_deleted += alert_count
        self.stdout.write(
            self.style.SUCCESS(f"{'Would delete' if dry_run else 'Deleted'} {alert_count} alert records")
        )

        # Clean Notifications related to deleted URLs
        notifications = Notification.objects.filter(url_status__url__is_active=False)
        notif_count = notifications.count()
        if not dry_run and notif_count > 0:
            notifications.delete()
        total_deleted += notif_count
        self.stdout.write(
            self.style.SUCCESS(f"{'Would delete' if dry_run else 'Deleted'} {notif_count} notification records")
        )

        # Finally, delete the inactive URL records themselves
        if not dry_run and inactive_count > 0:
            for url in inactive_urls:
                self.stdout.write(f"  Deleting URL: {url.name} ({url.url})")
            inactive_urls.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'Would delete' if dry_run else 'Deleted'} {inactive_count} URL records and {total_deleted} associated data records"
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("\nThis was a dry run. No data was actually deleted.")
            )
            self.stdout.write(
                self.style.WARNING("Run without --dry-run to actually delete the data.")
            )
