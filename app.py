from flask import Flask, redirect, url_for, session
from config import Config
from flask_migrate import Migrate
from modules.models import db
from modules.auth import auth_bp
from modules.todo import todo_bp
from modules.user import user_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(auth_bp)
app.register_blueprint(todo_bp)
app.register_blueprint(user_bp)

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('todo.day_view'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
