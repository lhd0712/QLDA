from flask import Flask, redirect, url_for, session
from config import Config
from flask_migrate import Migrate
from modules.models import db
from modules.auth import auth_bp
from modules.todo import todo_bp
from modules.user import user_bp
from modules.notification import notification_bp
import threading
import time

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(auth_bp)
app.register_blueprint(todo_bp)
app.register_blueprint(user_bp)
app.register_blueprint(notification_bp)

def start_notification_cron():
    def cron_job():
        while True:
            with app.app_context():
                from modules.models import User
                from modules.notification import create_event_notifications_for_user
                for user in User.query.all():
                    create_event_notifications_for_user(user.id)
            time.sleep(60)  # mỗi 60 giây
    t = threading.Thread(target=cron_job, daemon=True)
    t.start()

start_notification_cron()

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('todo.day_view'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
