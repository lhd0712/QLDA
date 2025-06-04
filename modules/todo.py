from flask import Blueprint, render_template, request, session, redirect, url_for
from modules.models import db, Todo, User
from datetime import date, datetime

todo_bp = Blueprint('todo', __name__)

@todo_bp.route('/todo', methods=['GET', 'POST'])
def todo():
    return redirect(url_for('todo.day_view'))

@todo_bp.route('/day')
def day_view():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    # Lấy ngày hiện tại hoặc ngày được chọn từ query string
    from flask import request
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            selected_date = date.today()
    else:
        selected_date = date.today()
    # Lọc event theo ngày bắt đầu (start_date)
    todos = Todo.query.filter_by(user_id=user.id, start_date=selected_date).all()
    popup = request.args.get('popup')
    return render_template('day.html', todos=todos, today=selected_date, popup=popup)

@todo_bp.route('/add-event', methods=['GET', 'POST'])
def add_event():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        title = request.form.get('title')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        reminder = request.form.get('reminder')
        repeat = request.form.get('repeat')
        tag = request.form.get('tag')
        location = request.form.get('location')
        description = request.form.get('description')
        # Validate required fields
        if not title or not start_date or not start_time:
            return render_template('addevent.html', message='Vui lòng nhập đầy đủ thông tin bắt buộc!')
        todo = Todo(
            task=title,
            user_id=user.id,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
            start_time=datetime.strptime(start_time, '%H:%M').time() if start_time else None,
            end_time=datetime.strptime(end_time, '%H:%M').time() if end_time else None,
            reminder=reminder,
            repeat=repeat,
            tag=tag,
            location=location,
            description=description
        )
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('todo.day_view', popup='1'))
    return render_template('addevent.html')
