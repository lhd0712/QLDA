function showTab(tab) {
  document.getElementById('tab-info').style.display = (tab === 'info') ? '' : 'none';
  document.getElementById('tab-account').style.display = (tab === 'account') ? '' : 'none';
  document.getElementById('tab-info-btn').classList.toggle('active', tab === 'info');
  document.getElementById('tab-account-btn').classList.toggle('active', tab === 'account');
  localStorage.setItem('profileTab', tab);
}
window.onload = function() {
  var tab = "{{ active_tab if active_tab else '' }}" || localStorage.getItem('profileTab') || 'info';
  showTab(tab);
};
