#!/usr/bin/env python
"""
Combined Celery Worker + Beat Launcher
Runs both worker and beat in a single process for Render free tier
"""
import os
import sys
from multiprocessing import Process

def start_worker():
    """Start Celery worker"""
    os.system('celery -A url_monitor worker --loglevel=info')

def start_beat():
    """Start Celery beat scheduler"""
    os.system('celery -A url_monitor beat --loglevel=info')

if __name__ == '__main__':
    print("Starting combined Celery worker + beat...")
    
    # Start beat in separate process
    beat_process = Process(target=start_beat)
    beat_process.start()
    
    # Start worker in main process (blocks)
    try:
        start_worker()
    except KeyboardInterrupt:
        print("Shutting down...")
        beat_process.terminate()
        beat_process.join()
        sys.exit(0)
