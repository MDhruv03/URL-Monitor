#!/usr/bin/env python
"""
Quick script to check if migration 0006 has been applied.
Run this to verify the database state.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'url_monitor.settings')
django.setup()

from django.db import connection

def check_migration_status():
    """Check if migration 0006 is applied and verify column nullable status."""
    
    print("\n" + "="*60)
    print("MIGRATION STATUS CHECK")
    print("="*60 + "\n")
    
    # Check applied migrations
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM django_migrations 
            WHERE app = 'monitor' 
            ORDER BY applied DESC 
            LIMIT 5
        """)
        migrations = cursor.fetchall()
        
        print("Last 5 applied migrations:")
        for mig in migrations:
            print(f"  ✓ {mig[0]}")
        
        # Check if 0006 is applied
        cursor.execute("""
            SELECT COUNT(*) FROM django_migrations 
            WHERE app = 'monitor' AND name = '0006_alter_clickheatmap_url_alter_conversionfunnel_url_and_more'
        """)
        migration_applied = cursor.fetchone()[0] > 0
        
        print(f"\n{'✓' if migration_applied else '✗'} Migration 0006: {'APPLIED' if migration_applied else 'NOT APPLIED'}")
        
        # Check actual column constraints
        print("\n" + "-"*60)
        print("ACTUAL DATABASE SCHEMA:")
        print("-"*60 + "\n")
        
        cursor.execute("""
            SELECT 
                column_name, 
                is_nullable,
                data_type
            FROM information_schema.columns 
            WHERE table_name = 'monitor_performancemetric' 
            AND column_name = 'url_id'
        """)
        column_info = cursor.fetchone()
        
        if column_info:
            col_name, is_nullable, data_type = column_info
            print(f"Column: {col_name}")
            print(f"Type: {data_type}")
            print(f"Nullable: {is_nullable}")
            print(f"\nStatus: {'✓ FIXED' if is_nullable == 'YES' else '✗ STILL NOT NULL'}")
        else:
            print("⚠ Could not find url_id column")
    
    print("\n" + "="*60)
    
    if not migration_applied:
        print("\n⚠ ACTION REQUIRED:")
        print("Migration 0006 has NOT been applied yet!")
        print("\nFor LOCAL development:")
        print("  Run: python manage.py migrate")
        print("\nFor RENDER deployment:")
        print("  1. Check deployment logs")
        print("  2. Verify start.sh is running migrations")
        print("  3. May need to redeploy")
    elif column_info and column_info[1] == 'NO':
        print("\n⚠ ACTION REQUIRED:")
        print("Migration is recorded as applied but schema wasn't updated!")
        print("\nTry:")
        print("  python manage.py migrate --fake-initial")
        print("  python manage.py migrate monitor 0006 --fake")
        print("  python manage.py migrate monitor --run-syncdb")
    else:
        print("\n✓ ALL GOOD!")
        print("Migration applied and schema is correct.")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    check_migration_status()
