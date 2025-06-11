from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    fullname = db.Column(db.String(128), nullable=False)
    pincode = db.Column(db.String(32), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(32), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(16), nullable=True)
    email = db.Column(db.String(128), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('todos', lazy=True))
    # Thông tin chi tiết từng cột
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    reminder = db.Column(db.String(32), nullable=True)
    repeat = db.Column(db.String(32), nullable=True)
    tag = db.Column(db.String(64), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    time = db.Column(db.DateTime, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)