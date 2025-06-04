from flask import Blueprint, render_template, request, session, redirect, url_for

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    # Giả sử dữ liệu user lưu trong auth.users
    from modules.auth import users
    username = session['username']
    user = users.get(username)
    if request.method == 'POST':
        user['fullname'] = request.form['fullname']
        return render_template('profile.html', user=user, message='Cập nhật thành công!')
    return render_template('profile.html', user=user)
