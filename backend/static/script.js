/* ═══════════════════════════════════════════════════════
   FinRisk — Global Script
   • PWA Service Worker registration
   • Notification Bell system
   • Loan pending timer
   • Toast system (shared)
   • Mobile sidebar (shared)
   • Legacy login/register stubs (kept for compat)
═══════════════════════════════════════════════════════ */

/* ── PWA SERVICE WORKER ─────────────────────────────── */
if('serviceWorker' in navigator){
  window.addEventListener('load', function(){
    navigator.serviceWorker.register('/static/sw.js')
      .then(function(reg){ console.log('SW registered:', reg.scope); })
      .catch(function(err){ console.log('SW error:', err); });
  });
}

/* ── TOAST SYSTEM ───────────────────────────────────── */
(function(){
  function ensureContainer(){
    let c = document.getElementById('toastContainer');
    if(!c){
      c = document.createElement('div');
      c.id = 'toastContainer';
      document.body.appendChild(c);
    }
    return c;
  }
  window.showToast = function(msg, type){
    type = type || 'info';
    let icons = {success:'✅', error:'❌', info:'ℹ', warn:'⚠'};
    let t = document.createElement('div');
    t.className = 'toast ' + type;
    t.innerHTML = '<span>'+(icons[type]||'')+'</span><span>'+msg+'</span>';
    ensureContainer().appendChild(t);
    setTimeout(function(){
      t.classList.add('fade-out');
      setTimeout(function(){ if(t.parentNode) t.parentNode.removeChild(t); }, 300);
    }, 3000);
  };
})();

/* ── MOBILE SIDEBAR ─────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function(){
  let sidebar = document.querySelector('.sidebar');
  if(!sidebar) return;
  if(document.querySelector('.hamburger')) return; // already added
  let btn = document.createElement('button');
  btn.className = 'hamburger';
  btn.innerHTML = '☰';
  btn.setAttribute('aria-label','Open menu');
  document.body.appendChild(btn);
  let overlay = document.createElement('div');
  overlay.className = 'sidebar-overlay';
  document.body.appendChild(overlay);
  btn.addEventListener('click', function(){
    sidebar.classList.toggle('open');
    overlay.classList.toggle('open');
  });
  overlay.addEventListener('click', function(){
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
  });
});

/* ── NOTIFICATION BELL ──────────────────────────────── */
/* Injects a bell icon into .topbar and manages unread count */
(function(){
  let _unread = 0;
  let _msgs   = [];

  function ensureBell(){
    let topbar = document.querySelector('.topbar');
    if(!topbar || document.getElementById('notifBell')) return;

    let bell = document.createElement('div');
    bell.id = 'notifBell';
    bell.innerHTML = `
      <button id="notifBtn" onclick="window._notifToggle()" aria-label="Notifications">
        🔔<span id="notifBadge" style="display:none">0</span>
      </button>
      <div id="notifDropdown" style="display:none">
        <div id="notifHeader">
          <span>Notifications</span>
          <button onclick="window._notifClear()" style="background:none;border:none;color:#bfa980;font-size:12px;cursor:pointer;font-family:DM Mono,monospace;">Clear all</button>
        </div>
        <div id="notifList"><div id="notifEmpty">No notifications yet</div></div>
      </div>`;
    topbar.appendChild(bell);
  }

  window._notifToggle = function(){
    let d = document.getElementById('notifDropdown');
    if(!d) return;
    d.style.display = d.style.display === 'none' ? 'block' : 'none';
    // mark as read
    _unread = 0;
    let badge = document.getElementById('notifBadge');
    if(badge){ badge.style.display = 'none'; badge.innerText = '0'; }
  };

  window._notifClear = function(){
    _msgs = [];
    _unread = 0;
    let list = document.getElementById('notifList');
    if(list) list.innerHTML = '<div id="notifEmpty">No notifications yet</div>';
    let badge = document.getElementById('notifBadge');
    if(badge){ badge.style.display = 'none'; badge.innerText = '0'; }
  };

  window.addNotification = function(msg, type){
    ensureBell();
    type = type || 'info';
    _msgs.unshift({ msg: msg, type: type, time: new Date() });
    if(_msgs.length > 20) _msgs.pop();
    _unread++;

    let badge = document.getElementById('notifBadge');
    if(badge){
      badge.style.display = 'inline-block';
      badge.innerText = _unread > 9 ? '9+' : _unread;
    }

    let list = document.getElementById('notifList');
    if(list){
      let empty = document.getElementById('notifEmpty');
      if(empty) empty.remove();
      let item = document.createElement('div');
      item.className = 'notif-item notif-' + type;
      let icons = {success:'✅',error:'❌',warn:'⚠',info:'ℹ'};
      item.innerHTML = '<span class="ni-icon">'+(icons[type]||'ℹ')+'</span>' +
        '<span class="ni-msg">'+msg+'</span>' +
        '<span class="ni-time">'+_fmtTime(new Date())+'</span>';
      list.insertBefore(item, list.firstChild);
    }
  };

  function _fmtTime(d){
    return d.getHours().toString().padStart(2,'0')+':'+d.getMinutes().toString().padStart(2,'0');
  }

  document.addEventListener('DOMContentLoaded', ensureBell);
})();

/* ── LOAN PENDING TIMER ─────────────────────────────── */
/* Call startLoanTimer(dateString) with the created_at date of the loan */
window.startLoanTimer = function(dateStr){
  let el = document.getElementById('loanPendingTimer');
  if(!el || !dateStr) return;
  function update(){
    let now  = new Date();
    let then = new Date(dateStr);
    let diff = Math.floor((now - then) / 1000);
    if(diff < 0){ el.innerText = 'Just now'; return; }
    let d = Math.floor(diff/86400);
    let h = Math.floor((diff%86400)/3600);
    let m = Math.floor((diff%3600)/60);
    if(d>0)      el.innerText = d+'d '+h+'h '+m+'m pending';
    else if(h>0) el.innerText = h+'h '+m+'m pending';
    else         el.innerText = m+'m pending';
  }
  update();
  setInterval(update, 60000);
};

/* ── LEGACY STUBS (kept so old references don't break) ─ */
function registerUser(){}
function loginUser(){}
function loadDashboard(){}
function goToLoan(){}
function calculateLoan(){}
function loadCharts(){}
