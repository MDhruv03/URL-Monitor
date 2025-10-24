import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("Monitor tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'monitor_%'")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

print("\nMonitoredURL columns:")
cursor.execute('PRAGMA table_info(monitor_monitoredurl)')
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

conn.close()
