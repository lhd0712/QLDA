from flask import Blueprint, render_template, request, session, redirect, url_for
from modules.models import db, Todo, User
from datetime import date

todo_bp = Blueprint('todo', __name__)

@todo_bp.route('/todo', methods=['GET', 'POST'])
def todo():
    return redirect(url_for('todo.day_view'))

@todo_bp.route('/day')
def day_view():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    todos = Todo.query.filter_by(user_id=user.id).all()
    return render_template('day.html', todos=todos, today=date.today())
