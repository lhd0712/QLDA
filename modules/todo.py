from flask import Blueprint, render_template, request, redirect, url_for, session
from modules.models import db, Todo, User
from datetime import date

todo_bp = Blueprint('todo', __name__)

@todo_bp.route('/day')
def day_view():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    todos = Todo.query.filter_by(user_id=user.id).all()
    return render_template('day.html', todos=todos, today=date.today())

todos = []

def require_login():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

@todo_bp.route('/todo', methods=['GET', 'POST'])
def todo():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        task = request.form.get('task')
        if task:
            todos.append({'task': task})
        return redirect(url_for('todo.todo'))
    return render_template('todo.html', todos=todos)

@todo_bp.route('/todo/edit/<int:idx>', methods=['GET', 'POST'])
def edit_event(idx):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    if idx < 0 or idx >= len(todos):
        return redirect(url_for('todo.todo'))
    if request.method == 'POST':
        todos[idx]['task'] = request.form.get('task')
        return redirect(url_for('todo.todo'))
    return render_template('edit_event.html', task=todos[idx]['task'], idx=idx)

@todo_bp.route('/todo/delete/<int:idx>')
def delete_event(idx):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    if 0 <= idx < len(todos):
        todos.pop(idx)
    return redirect(url_for('todo.todo'))
