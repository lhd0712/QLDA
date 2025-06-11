from flask import Blueprint, jsonify, request, session
from modules.models import db, Todo, User, Notification
from datetime import datetime, timedelta

notification_bp = Blueprint('notification', __name__)

# Lấy danh sách thông báo cho user hiện tại
def get_notifications_for_user(user_id, include_read=True):
    now = datetime.now()
    # Lấy tất cả noti (đã đọc và chưa đọc), chỉ ẩn popup với noti đã đọc
    query = Notification.query.filter_by(user_id=user_id).order_by(Notification.time.desc())
    notifications = query.all()
    result = []
    for n in notifications:
        # Chỉ hiển thị noti cho event chưa kết thúc hoặc đã đọc (lịch sử)
        if n.time >= now or n.is_read:
            result.append({
                'id': n.todo_id or n.id,
                'title': n.title,
                'time': n.time.strftime('%Y-%m-%d %H:%M'),
                'reminder': '',
                'description': n.description or '',
                'is_read': n.is_read
            })
    return result

@notification_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    notifications = get_notifications_for_user(user.id, include_read=True)
    return jsonify({'success': True, 'notifications': notifications})

# Đánh dấu đã đọc (tạm thời không lưu DB, chỉ trả về thành công)
@notification_bp.route('/api/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    Notification.query.filter_by(user_id=user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})

# Hàm tiện ích: Tạo notification khi có event sắp diễn ra
# Gọi hàm này khi tạo/sửa event hoặc chạy định kỳ

def create_event_notifications_for_user(user_id):
    now = datetime.now()
    todos = Todo.query.filter_by(user_id=user_id).all()
    for todo in todos:
        if todo.reminder and todo.reminder != 'none' and todo.start_time and todo.start_date:
            # Xử lý lặp lại: tạo notification cho mỗi lần lặp nếu đến thời gian
            repeat_type = todo.repeat or 'none'
            repeat_dates = []
            if repeat_type == 'none':
                repeat_dates = [todo.start_date]
            else:
                # Tạo danh sách ngày lặp từ start_date đến end_date hoặc 7 ngày tới
                max_days = 7  # chỉ tạo noti cho 7 ngày tới để tránh quá tải
                d = todo.start_date
                end = todo.end_date or (now.date() + timedelta(days=max_days))
                while d <= end and (d - now.date()).days <= max_days:
                    if repeat_type == 'daily':
                        repeat_dates.append(d)
                        d += timedelta(days=1)
                    elif repeat_type == 'weekly':
                        repeat_dates.append(d)
                        d += timedelta(weeks=1)
                    elif repeat_type == 'monthly':
                        repeat_dates.append(d)
                        # Lặp tháng: tăng tháng, giữ ngày
                        month = d.month + 1
                        year = d.year + (month - 1) // 12
                        month = (month - 1) % 12 + 1
                        try:
                            d = d.replace(year=year, month=month)
                        except:
                            break
                    elif repeat_type == 'yearly':
                        repeat_dates.append(d)
                        try:
                            d = d.replace(year=d.year + 1)
                        except:
                            break
                    else:
                        break
            for d in repeat_dates:
                event_datetime = datetime.combine(d, todo.start_time)
                try:
                    minutes_before = int(todo.reminder)
                except Exception:
                    minutes_before = 0
                notify_time = event_datetime - timedelta(minutes=minutes_before)
                # Nếu chưa có notification cho lần lặp này và thời gian hợp lệ
                exists = Notification.query.filter_by(user_id=user_id, todo_id=todo.id, time=event_datetime).first()
                if not exists and now <= event_datetime and now >= notify_time:
                    n = Notification(
                        user_id=user_id,
                        todo_id=todo.id,
                        title=todo.task,
                        description=todo.description,
                        time=event_datetime,
                        is_read=False
                    )
                    db.session.add(n)
    db.session.commit()
