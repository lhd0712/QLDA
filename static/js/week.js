// Debounce function to optimize performance
function debounce(func, wait) {
	let timeout;
	return function executedFunction(...args) {
		const later = () => {
			clearTimeout(timeout);
			func(...args);
		};
		clearTimeout(timeout);
		timeout = setTimeout(later, wait);
	};
}
function normalizeText(str) {
	return (str || '').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '');
}
// Filter events in week view
const filterEvents = debounce(function() {
	const keyword = normalizeText(document.getElementById('eventSearchInput').value.trim());
	const suggestionBox = document.getElementById('search-suggestion-box');
	let matches = [];
	document.querySelectorAll('.event-block').forEach((item, idx) => {
		const title = normalizeText(item.querySelector('.event-title').textContent);
		const tag = normalizeText(item.getAttribute('data-tag') || '');
		const timeSpan = item.querySelector('.event-time');
		const time = timeSpan ? timeSpan.textContent.trim() : '';
		if (keyword && (title.includes(keyword) || tag.includes(keyword))) {
			matches.push({
				title: item.querySelector('.event-title').textContent,
				time: time,
				tag: tag,
				element: item
			});
		}
	});
	matches.sort((a, b) => {
		const timeA = a.time ? a.time.split('-')[0].trim() : '23:59';
		const timeB = b.time ? b.time.split('-')[0].trim() : '23:59';
		return timeA.localeCompare(timeB);
	});
	if (keyword && matches.length > 0) {
		let html = matches.slice(0, 10).map((match, idx) => `
			<div class="search-suggestion-item" data-idx="${idx}" style="padding:6px 18px; cursor:pointer; font-size:15px; color:#0B41FF; border-bottom:1px solid #F0F0F0; display:flex; justify-content:space-between; align-items:center;" tabindex="0">
				<span>${match.title} ${match.tag ? `<span style=\"color:#666;font-size:13px;margin-left:8px;\">#${match.tag}</span>` : ''}</span>
				${match.time ? `<span style=\"color:#666;font-size:13px;margin-left:12px;\">${match.time}</span>` : ''}
			</div>
		`).join('');
		suggestionBox.innerHTML = html;
		suggestionBox.style.display = '';
		Array.from(suggestionBox.children).forEach((child, idx) => {
			child.onclick = () => selectSuggestion(idx);
			child.onkeydown = e => {
				if (e.key === 'Enter') selectSuggestion(idx);
			};
		});
		highlightSuggestion(-1);
	} else if (keyword) {
		suggestionBox.innerHTML = `<div style=\"padding:6px 18px; font-size:15px; color:#666;\">Không tìm thấy sự kiện nào</div>`;
		suggestionBox.style.display = '';
	} else {
		suggestionBox.style.display = 'none';
	}
}, 300);
function selectSuggestion(idx) {
	const suggestionBox = document.getElementById('search-suggestion-box');
	const keyword = normalizeText(document.getElementById('eventSearchInput').value.trim());
	let matches = [];
	document.querySelectorAll('.event-block').forEach((item) => {
		const title = normalizeText(item.querySelector('.event-title').textContent);
		const tag = normalizeText(item.getAttribute('data-tag') || '');
		if (keyword && (title.includes(keyword) || tag.includes(keyword))) {
			matches.push(item);
		}
	});
	if (matches[idx]) {
		const el = matches[idx];
		el.scrollIntoView({ behavior: 'smooth', block: 'center' });
		el.classList.add('search-highlight');
		setTimeout(() => el.classList.remove('search-highlight'), 1200);
		suggestionBox.style.display = 'none';
		document.getElementById('eventSearchInput').blur();
	}
}
let currentSuggestion = -1;
function highlightSuggestion(idx) {
	const suggestionBox = document.getElementById('search-suggestion-box');
	Array.from(suggestionBox.children).forEach((child, i) => {
		child.style.background = i === idx ? '#e6f0ff' : '';
	});
	currentSuggestion = idx;
}
// Calendar logic for week view
const calendar = document.getElementById('calendar');
const calendarMonth = document.getElementById('calendarMonth');
const prevMonthBtn = document.getElementById('prevMonth');
const nextMonthBtn = document.getElementById('nextMonth');
let today = new Date();
let currentMonth = today.getMonth();
let currentYear = today.getFullYear();
let selectedDate = null;
function renderCalendar(month, year, selectedDateStr = null) {
	const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
	calendarMonth.textContent = monthNames[month] + ' ' + year;
	const firstDay = new Date(year, month, 1);
	const lastDay = new Date(year, month + 1, 0);
	let html = '';
	html += '<thead><tr>';
	const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
	for (let d of days) html += `<th style="color:#888;font-size:12px;">${d}</th>`;
	html += '</tr></thead><tbody>';
	let startDay = (firstDay.getDay() + 6) % 7;
	let day = 1;
	for (let i = 0; i < 6; i++) {
		html += '<tr>';
		for (let j = 0; j < 7; j++) {
			if (i === 0 && j < startDay) {
				html += '<td></td>';
			} else if (day > lastDay.getDate()) {
				html += '<td></td>';
			} else {
				const dateObj = new Date(year, month, day);
				const thisDateStr = `${year}-${month+1}-${day}`;
				const isSelected = selectedDateStr === thisDateStr;
				const isToday = dateObj.getDate() === today.getDate() && dateObj.getMonth() === today.getMonth() && dateObj.getFullYear() === today.getFullYear();
				const isHighlight = isSelected ? 'selected' : '';
				const bgColor = isSelected ? '#0B41FF' : (isToday ? '#F5F5F5' : '#F5F5F5');
				const color = isSelected ? '#fff' : '#333';
				html += `<td class="${isHighlight}" style="padding:4px;"><button class="calendar-day" data-date="${thisDateStr}" style="width:28px;height:28px;border-radius:50%;border:none;background:${bgColor};color:${color};font-weight:bold;cursor:pointer;">${day}</button></td>`;
				day++;
			}
		}
		html += '</tr>';
		if (day > lastDay.getDate()) break;
	}
	html += '</tbody>';
	calendar.innerHTML = html;
	document.querySelectorAll('.calendar-day').forEach(btn => {
		btn.onclick = function() {
			const dateStr = this.getAttribute('data-date');
			window.location.href = '/week?date=' + dateStr;
		};
	});
}
window.onload = function() {
	const params = new URLSearchParams(window.location.search);
	let dateStr = params.get('date');
	let defaultDate;
	if (dateStr) {
		const [y, m, d] = dateStr.split('-').map(Number);
		defaultDate = new Date(y, m - 1, d);
		selectedDate = dateStr;
	} else {
		defaultDate = new Date(currentYear, currentMonth, today.getDate());
		selectedDate = `${defaultDate.getFullYear()}-${defaultDate.getMonth()+1}-${defaultDate.getDate()}`;
	}
	renderCalendar(defaultDate.getMonth(), defaultDate.getFullYear(), selectedDate);
	const weekTitle = document.getElementById('weekTitle');
	if (weekTitle) {
		const weekStart = new Date(defaultDate);
		weekStart.setDate(defaultDate.getDate() - defaultDate.getDay() + 1);
		const weekEnd = new Date(weekStart);
		weekEnd.setDate(weekStart.getDate() + 6);
		const startStr = `${String(weekStart.getDate()).padStart(2, '0')}/${String(weekStart.getMonth()+1).padStart(2, '0')}/${weekStart.getFullYear()}`;
		const endStr = `${String(weekEnd.getDate()).padStart(2, '0')}/${String(weekEnd.getMonth()+1).padStart(2, '0')}/${weekEnd.getFullYear()}`;
		weekTitle.textContent = `${startStr} - ${endStr}`;
	}
	currentMonth = defaultDate.getMonth();
	currentYear = defaultDate.getFullYear();
};
prevMonthBtn.onclick = function() {
	currentMonth--;
	if (currentMonth < 0) {
		currentMonth = 11;
		currentYear--;
	}
	renderCalendar(currentMonth, currentYear, selectedDate);
};
nextMonthBtn.onclick = function() {
	currentMonth++;
	if (currentMonth > 11) {
		currentMonth = 0;
		currentYear++;
	}
	renderCalendar(currentMonth, currentYear, selectedDate);
};
const searchInput = document.getElementById('eventSearchInput');
const suggestionBox = document.getElementById('search-suggestion-box');
searchInput.addEventListener('input', filterEvents);
searchInput.addEventListener('focus', () => {
	if (suggestionBox.innerHTML) suggestionBox.style.display = '';
});
searchInput.addEventListener('keydown', e => {
	const items = Array.from(suggestionBox.children);
	if (!items.length || suggestionBox.style.display === 'none') return;
	if (e.key === 'ArrowDown') {
		e.preventDefault();
		let next = (currentSuggestion + 1) % items.length;
		highlightSuggestion(next);
		items[next].scrollIntoView({ block: 'nearest' });
	} else if (e.key === 'ArrowUp') {
		e.preventDefault();
		let prev = (currentSuggestion - 1 + items.length) % items.length;
		highlightSuggestion(prev);
		items[prev].scrollIntoView({ block: 'nearest' });
	} else if (e.key === 'Enter') {
		if (currentSuggestion >= 0) {
			selectSuggestion(currentSuggestion);
			e.preventDefault();
		}
	} else if (e.key === 'Escape') {
		suggestionBox.style.display = 'none';
		currentSuggestion = -1;
		searchInput.blur();
	}
});
document.addEventListener('click', e => {
	if (!searchInput.contains(e.target) && !suggestionBox.contains(e.target)) {
		suggestionBox.style.display = 'none';
		currentSuggestion = -1;
	}
});
function goToCurrentWeek() {
	const today = new Date();
	const dateStr = `${today.getFullYear()}-${today.getMonth()+1}-${today.getDate()}`;
	window.location.href = '/week?date=' + dateStr;
}
