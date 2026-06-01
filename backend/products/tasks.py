import time
from celery import shared_task

@shared_task
def dummy_background_task():
    print("Background task started")
    time.sleep(2)
    print("Background task finished")
    return "Done"
