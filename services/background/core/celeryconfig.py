from celery.schedules import crontab

beat_schedule = {
    "run-db-cleanup-every-hour": {
        "task": "src.tasks.cleanup.clean_database",
        "schedule": crontab(minute="*"),  # every hour
    },
}

broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/0"
timezone = "UTC"
beat_schedule = beat_schedule
