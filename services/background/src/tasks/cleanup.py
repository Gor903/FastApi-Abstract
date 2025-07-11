from core import celery_app


@celery_app.task
def clean_database():
    print("🧹 Cleaning up database...")
