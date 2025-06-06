from flask import Blueprint, render_template, request, session, redirect, url_for
from modules.models import db, Todo, User
from datetime import date, datetime, timedelta
from datetime import date as dt_date
import calendar
import os
from copy import copy

todo_bp = Blueprint('todo', __name__)

# Danh sách tag mặc định
DEFAULT_TAGS = ['work', 'personal', 'meeting', 'study', 'family', 'health', 'travel', 'finance', 'shopping', 'other']

@todo_bp.route('/todo', methods=['GET', 'POST'])
def todo():
    return redirect(url_for('todo.day_view'))

@todo_bp.route('/day')
def day_view():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    # Lấy ngày hiện tại hoặc ngày được chọn từ query string
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            selected_date = date.today()
    else:
        selected_date = date.today()
    todos = Todo.query.filter_by(user_id=user.id).all()  # lấy tất cả để xử lý repeat
    def is_event_on_date(todo, d):
        if not todo.start_date:
            return False
        if todo.repeat == 'daily':
            if todo.end_date and d > todo.end_date:
                return False
            return d >= todo.start_date
        elif todo.repeat == 'weekly':
            if todo.end_date and d > todo.end_date:
                return False
            days_diff = (d - todo.start_date).days
            return d >= todo.start_date and days_diff % 7 == 0 and days_diff >= 0
        elif todo.repeat == 'monthly':
            if todo.end_date and d > todo.end_date:
                return False
            months_diff = (d.year - todo.start_date.year) * 12 + (d.month - todo.start_date.month)
            return d >= todo.start_date and d.day == todo.start_date.day and months_diff >= 0
        elif todo.repeat == 'yearly':
            if todo.end_date and d > todo.end_date:
                return False
            years_diff = d.year - todo.start_date.year
            return d >= todo.start_date and d.day == todo.start_date.day and d.month == todo.start_date.month and years_diff >= 0
        else:
            return todo.start_date == d
    # Lọc event cho ngày được chọn (clone object để không ghi đè start_time/end_time)
    todos_today = []
    for todo in todos:
        if is_event_on_date(todo, selected_date):
            t = copy(todo)
            if t.start_time:
                t.start_time = datetime.combine(selected_date, t.start_time)
            if t.end_time:
                t.end_time = datetime.combine(selected_date, t.end_time)
            todos_today.append(t)
    # Lấy event ngày mai (bao gồm lặp, clone object)
    tomorrow = selected_date + timedelta(days=1)
    todos_tomorrow = []
    for todo in todos:
        if is_event_on_date(todo, tomorrow):
            t = copy(todo)
            if t.start_time:
                t.start_time = datetime.combine(tomorrow, t.start_time)
            if t.end_time:
                t.end_time = datetime.combine(tomorrow, t.end_time)
            todos_tomorrow.append(t)
    # Lấy danh sách tag duy nhất (từ DB và mặc định, loại trùng, loại rỗng)
    all_tags = db.session.query(Todo.tag).filter(Todo.user_id==user.id, Todo.tag!=None, Todo.tag!='').distinct().all()
    tag_list = list({t[0] for t in all_tags if t[0]})
    tag_list = sorted(set(DEFAULT_TAGS) | set(tag_list))
    # --- Xử lý overlap chuẩn: interval partitioning (kiểm tra với tất cả event trong cột) ---
    todos_sorted = sorted(todos_today, key=lambda t: (t.start_time or datetime.min, t.end_time or datetime.max))
    columns = []  # Mỗi phần tử là list các event trong 1 cột
    event_columns = {}
    for todo in todos_sorted:
        placed = False
        for col_idx, col in enumerate(columns):
            if all(
                (not e.start_time or not e.end_time or not todo.start_time or not todo.end_time) or
                (e.end_time <= todo.start_time or todo.end_time <= e.start_time)
                for e in col
            ):
                col.append(todo)
                event_columns[todo] = col_idx
                placed = True
                break
        if not placed:
            columns.append([todo])
            event_columns[todo] = len(columns) - 1
    total_columns = len(columns) if columns else 1
    events = []
    for col_idx, col in enumerate(columns):
        for todo in sorted(col, key=lambda t: (t.start_time or datetime.min, t.end_time or datetime.max)):
            events.append({'todo': todo, 'column': col_idx, 'total_columns': total_columns})

    popup = request.args.get('popup')
    return render_template('day.html', todos=todos_today, today=selected_date, popup=popup, events=events, todos_tomorrow=todos_tomorrow, tag_list=tag_list, user=user, os=os)

@todo_bp.route('/add-event', methods=['GET', 'POST'])
def add_event():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    # Lấy danh sách tag duy nhất (từ DB và mặc định, loại trùng, loại rỗng)
    all_tags = db.session.query(Todo.tag).filter(Todo.user_id==user.id, Todo.tag!=None, Todo.tag!='').distinct().all()
    tag_list = list({t[0] for t in all_tags if t[0]})
    tag_list = sorted(set(DEFAULT_TAGS) | set(tag_list))
    if request.method == 'POST':
        title = request.form.get('title')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        reminder = request.form.get('reminder')
        repeat = request.form.get('repeat')
        tag = request.form.get('tag')
        # Không cho phép thêm tag mới bằng text nữa
        if tag == '__new__':
            tag = None
        # Validate required fields
        if not title or not start_date or not start_time:
            return render_template('addevent.html', message='Vui lòng nhập đầy đủ thông tin bắt buộc!', tag_list=tag_list)
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
            location=request.form.get('location'),
            description=request.form.get('description')
        )
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('todo.day_view', popup='1'))
    return render_template('addevent.html', tag_list=tag_list)

@todo_bp.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    todo = Todo.query.filter_by(id=event_id, user_id=user.id).first()
    if not todo:
        return redirect(url_for('todo.day_view'))
    # Lấy danh sách tag duy nhất (từ DB và mặc định, loại trùng, loại rỗng)
    all_tags = db.session.query(Todo.tag).filter(Todo.user_id==user.id, Todo.tag!=None, Todo.tag!='').distinct().all()
    tag_list = list({t[0] for t in all_tags if t[0]})
    tag_list = sorted(set(DEFAULT_TAGS) | set(tag_list))
    if request.method == 'POST':
        todo.task = request.form.get('title')
        todo.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date() if request.form.get('start_date') else None
        todo.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None
        # Xử lý lỗi khi input time có thể là 'HH:MM' hoặc 'HH:MM:SS'
        def parse_time(val):
            if not val:
                return None
            try:
                return datetime.strptime(val, '%H:%M').time()
            except ValueError:
                return datetime.strptime(val, '%H:%M:%S').time()
        todo.start_time = parse_time(request.form.get('start_time'))
        todo.end_time = parse_time(request.form.get('end_time'))
        todo.reminder = request.form.get('reminder')
        todo.repeat = request.form.get('repeat')
        todo.tag = request.form.get('tag')
        todo.location = request.form.get('location')
        todo.description = request.form.get('description')
        db.session.commit()
        return redirect(url_for('todo.day_view', popup='1'))
    return render_template('edit_event.html', todo=todo, tag_list=tag_list)

def get_week_days(selected_date):
    # Trả về list 7 ngày (datetime.date) của tuần chứa selected_date, bắt đầu từ thứ 2
    weekday = selected_date.weekday()  # 0=Mon
    monday = selected_date - timedelta(days=weekday)
    return [monday + timedelta(days=i) for i in range(7)]

@todo_bp.route('/week')
def week_view():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    # Lấy ngày hiện tại hoặc ngày được chọn từ query string
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            selected_date = date.today()
    else:
        selected_date = date.today()
    # Xử lý chuyển tuần
    week_offset = int(request.args.get('week_offset', 0))
    selected_date = selected_date + timedelta(weeks=week_offset)
    week_days = get_week_days(selected_date)
    # Lấy tất cả event của user để xử lý repeat
    todos = Todo.query.filter_by(user_id=user.id).all()
    events_by_day = {}
    events_in_week = []
    def is_event_on_date(todo, d):
        if not todo.start_date:
            return False
        if todo.repeat == 'daily':
            if todo.end_date and d > todo.end_date:
                return False
            return d >= todo.start_date
        elif todo.repeat == 'weekly':
            if todo.end_date and d > todo.end_date:
                return False
            days_diff = (d - todo.start_date).days
            return d >= todo.start_date and days_diff % 7 == 0 and days_diff >= 0
        elif todo.repeat == 'monthly':
            if todo.end_date and d > todo.end_date:
                return False
            months_diff = (d.year - todo.start_date.year) * 12 + (d.month - todo.start_date.month)
            return d >= todo.start_date and d.day == todo.start_date.day and months_diff >= 0
        elif todo.repeat == 'yearly':
            if todo.end_date and d > todo.end_date:
                return False
            years_diff = d.year - todo.start_date.year
            return d >= todo.start_date and d.day == todo.start_date.day and d.month == todo.start_date.month and years_diff >= 0
        else:
            return todo.start_date == d
    for d in week_days:
        # Lấy event cho ngày d (bao gồm lặp)
        todos_day = []
        for todo in todos:
            if is_event_on_date(todo, d):
                # Clone event để không ghi đè start_time/end_time gốc
                t = copy(todo)
                if t.start_time:
                    t.start_time = datetime.combine(d, t.start_time)
                if t.end_time:
                    t.end_time = datetime.combine(d, t.end_time)
                todos_day.append(t)
        events_in_week.extend(todos_day)
        # --- Xử lý overlap chuẩn: interval partitioning (kiểm tra với tất cả event trong cột) ---
        todos_sorted = sorted(todos_day, key=lambda t: (t.start_time or datetime.min, t.end_time or datetime.max))
        columns = []
        event_columns = {}
        for todo in todos_sorted:
            placed = False
            for col_idx, col in enumerate(columns):
                if all(
                    (not e.start_time or not e.end_time or not todo.start_time or not todo.end_time) or
                    (e.end_time <= todo.start_time or todo.end_time <= e.start_time)
                    for e in col
                ):
                    col.append(todo)
                    event_columns[todo] = col_idx
                    placed = True
                    break
            if not placed:
                columns.append([todo])
                event_columns[todo] = len(columns) - 1
        total_columns = len(columns) if columns else 1
        events = []
        for col_idx, col in enumerate(columns):
            for todo in sorted(col, key=lambda t: (t.start_time or datetime.min, t.end_time or datetime.max)):
                events.append({'todo': todo, 'column': col_idx, 'total_columns': total_columns})
        events_by_day[d.isoformat()] = events
    week_range = f"{week_days[0].strftime('%d/%m/%Y')} - {week_days[-1].strftime('%d/%m/%Y')}"
    return render_template('week.html', week_days=week_days, events_by_day=events_by_day, week_range=week_range, selected_date=selected_date, events_in_week=events_in_week, user=user, os=os)

@todo_bp.route('/delete-event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    todo = Todo.query.filter_by(id=event_id, user_id=user.id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
    return redirect(url_for('todo.day_view'))
