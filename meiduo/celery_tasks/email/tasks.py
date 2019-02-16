from celery_tasks.main import app


@app.task(name = 'send_email')
def send_email():
    print("11111")