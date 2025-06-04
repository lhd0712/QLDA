from flask import Blueprint, render_template, request, redirect, url_for, session
from modules.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('todo.todo'))
        else:
            return render_template('login.html', error='Sai thông tin đăng nhập!')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        pincode = request.form['pincode']
        password = request.form['password']
        repassword = request.form['repassword']
        if password != repassword:
            return render_template('register.html', error='Mật khẩu nhập lại không khớp!')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Tên đăng nhập đã tồn tại!')
        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw, fullname=fullname, pincode=pincode)
        db.session.add(user)
        db.session.commit()
        return render_template('login.html', error=None, message='Đăng ký thành công! Vui lòng đăng nhập.')
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        pincode = request.form['pincode']
        new_password = request.form['new_password']
        repassword = request.form['repassword']
        user = User.query.filter_by(username=username, pincode=pincode).first()
        if not user:
            return render_template('forgot_password.html', error='Sai username hoặc pincode!')
        if new_password != repassword:
            return render_template('forgot_password.html', error='Mật khẩu nhập lại không khớp!')
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return render_template('login.html', error=None, message='Đặt lại mật khẩu thành công! Vui lòng đăng nhập.')
    return render_template('forgot_password.html')
