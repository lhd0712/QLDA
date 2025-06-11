# run_notification_cron.py
from modules.models import db, User
from modules.notification import create_event_notifications_for_user
from app import app

def run_all():
    with app.app_context():
        for user in User.query.all():
            create_event_notifications_for_user(user.id)

if __name__ == '__main__':
    run_all()
