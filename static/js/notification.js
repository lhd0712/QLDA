// notification.js - handle notification UI and API for day/week views

let lastNotificationCount = 0;
let notificationSound = null;

async function fetchNotifications(showPopup = false) {
    try {
        const res = await fetch('/api/notifications');
        const data = await res.json();
        if (data.success) {
            updateNotificationUI(data.notifications, showPopup);
        }
    } catch (e) {
        // ignore
    }
}

function playNotificationSound() {
    // Always create a new Audio object to avoid browser autoplay policy issues
    try {
        const audio = new Audio('/static/sound/notification.mp3');
        audio.volume = 1.0;
        audio.play().catch(() => {});
    } catch (e) {}
}

function updateNotificationUI(notifications, showPopup = false) {
    const badge = document.getElementById('notification-badge');
    const list = document.getElementById('notification-list');
    const popup = document.getElementById('notification-popup');
    if (!badge || !list) return;
    // Đếm số noti chưa đọc và còn hiệu lực (event chưa kết thúc)
    const now = new Date();
    const unreadCount = notifications.filter(n => !n.is_read && new Date(n.time.replace(' ', 'T')) >= now).length;
    if (unreadCount > 0) {
        badge.style.display = '';
        badge.textContent = unreadCount;
    } else {
        badge.style.display = 'none';
    }
    list.innerHTML = notifications.map((n, idx) => `
        <li style="padding:12px 16px;border-bottom:1px solid #f0f0f0;cursor:pointer;${n.is_read ? 'color:#888;background:#fff;' : 'background:#e6f0ff;'}" data-notif-id="${n.id}" tabindex="0">
            <div style="font-weight:bold;">${n.title}</div>
            <div style="font-size:13px;color:#666;">${n.time}${window.SHOW_NOTIFICATION_DESCRIPTION && n.description ? ' - ' + n.description : ''}</div>
        </li>
    `).join('');
    // Gán sự kiện click cho từng thông báo
    Array.from(list.children).forEach((li, idx) => {
        li.onclick = async function() {
            const notifId = li.getAttribute('data-notif-id');
            await fetch('/api/notifications/mark-read', {method: 'POST'});
            // Không ẩn hết, chỉ cập nhật lại trạng thái đã đọc
            fetchNotifications();
            if (popup) popup.style.display = 'none';
            // Scroll tới event-block nếu có trên trang
            const eventBlock = document.querySelector(`.event-block[onclick*='/edit-event/${notifId}']`);
            if (eventBlock) {
                eventBlock.scrollIntoView({behavior: 'smooth', block: 'center'});
                eventBlock.classList.add('search-highlight');
                setTimeout(() => eventBlock.classList.remove('search-highlight'), 1200);
            }
        };
        li.onkeydown = function(e) {
            if (e.key === 'Enter') li.onclick();
        };
    });
    // Chỉ hiện popup và phát âm thanh nếu có noti chưa đọc mới
    const newUnread = unreadCount > lastNotificationCount;
    if (showPopup && newUnread) {
        if (popup) popup.style.display = '';
        playNotificationSound();
    }
    lastNotificationCount = unreadCount;
}

document.addEventListener('DOMContentLoaded', function() {
    const bell = document.getElementById('notification-bell');
    const popup = document.getElementById('notification-popup');
    const markRead = document.getElementById('notification-mark-read');
    if (!bell || !popup) return;
    bell.addEventListener('click', function(e) {
        e.stopPropagation();
        if (popup.style.display === 'none' || !popup.style.display) {
            fetchNotifications();
            popup.style.display = '';
        } else {
            popup.style.display = 'none';
        }
    });
    document.addEventListener('click', function(e) {
        if (!popup.contains(e.target) && e.target !== bell && !bell.contains(e.target)) {
            popup.style.display = 'none';
        }
    });
    if (markRead) {
        markRead.addEventListener('click', async function() {
            await fetch('/api/notifications/mark-read', {method: 'POST'});
            updateNotificationUI([]);
        });
    }
});

// Poll for notifications every 3 seconds, show popup and sound if có thông báo mới
document.addEventListener('DOMContentLoaded', function() {
    setInterval(() => fetchNotifications(true), 3000); // 3 giây kiểm tra 1 lần
    // Lần đầu vào trang cũng kiểm tra luôn
    fetchNotifications(true);
});
