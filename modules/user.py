from flask import Blueprint, render_template, request, session, redirect, url_for
from modules.models import User, db
import os

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        active_tab = None
        # Xử lý upload avatar (nếu có)
        if 'avatar' in request.files and request.files['avatar'].filename:
            avatar = request.files['avatar']
            from werkzeug.utils import secure_filename
            filename = secure_filename(f"{user.username}.png")
            avatar_path = os.path.join('static', 'avatar')
            os.makedirs(avatar_path, exist_ok=True)
            avatar.save(os.path.join(avatar_path, filename))
            return render_template('profile.html', user=user, message='Cập nhật ảnh đại diện thành công!', active_tab='info', error=False, os=os)
        # Đổi mật khẩu
        if request.form.get('change_password'):
            new_password = request.form.get('new_password')
            re_password = request.form.get('re_password')
            active_tab = 'account'
            message = None
            error = None
            if (not new_password and not re_password):
                message = 'Vui lòng nhập mật khẩu mới và xác nhận!'
                error = True
            elif not new_password or not re_password:
                message = 'Vui lòng nhập đầy đủ cả hai trường mật khẩu!'
                error = True
            elif new_password != re_password:
                message = 'Mật khẩu không khớp!'
                error = True
            else:
                from werkzeug.security import generate_password_hash
                user.password = generate_password_hash(new_password)
                db.session.commit()
                message = 'Đổi mật khẩu thành công!'
                error = False
            return render_template('profile.html', user=user, message=message, error=error, active_tab=active_tab, os=os, show_account_msg=True)
        # Đổi pincode
        if request.form.get('change_pincode'):
            new_pincode = request.form.get('new_pincode')
            re_pincode = request.form.get('re_pincode')
            active_tab = 'account'
            message = None
            error = None
            if (not new_pincode and not re_pincode):
                message = 'Vui lòng nhập pincode mới và xác nhận!'
                error = True
            elif not new_pincode or not re_pincode:
                message = 'Vui lòng nhập đầy đủ cả hai trường pincode!'
                error = True
            elif new_pincode != re_pincode:
                message = 'Pincode không khớp!'
                error = True
            else:
                user.pincode = new_pincode
                db.session.commit()
                message = 'Đổi pincode thành công!'
                error = False
            return render_template('profile.html', user=user, message=message, error=error, active_tab=active_tab, os=os, show_account_msg=True)
        # Cập nhật thông tin người dùng
        user.fullname = request.form.get('fullname', user.fullname)
        user.dob = request.form.get('dob') or None
        user.phone = request.form.get('phone', user.phone)
        user.address = request.form.get('address', user.address)
        user.gender = request.form.get('gender', user.gender)
        user.email = request.form.get('email', user.email)
        if user.dob:
            try:
                from datetime import datetime
                user.dob = datetime.strptime(user.dob, '%Y-%m-%d').date()
            except Exception:
                pass
        db.session.commit()
        return render_template('profile.html', user=user, message='Cập nhật thành công!', error=False, active_tab='info', os=os)
    return render_template('profile.html', user=user, active_tab='info', os=os)
