(function(){
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function store(k,v){try{localStorage.setItem(k,v);}catch(e){}}
  function load(k){try{return localStorage.getItem(k);}catch(e){return null;}}

  var mains = {en: document.querySelector('main[lang="en"]'), ar: document.querySelector('main[lang="ar"]')};
  var langBtns = Array.prototype.slice.call(document.querySelectorAll('.lang button'));

  function pickInitial(){
    var u = new URLSearchParams(location.search).get('lang');
    if(u==='ar'||u==='en') return u;
    var s = load('shabakah-lang');
    if(s==='ar'||s==='en') return s;
    return (navigator.language||'').toLowerCase().indexOf('ar')===0 ? 'ar' : 'en';
  }

  function setLang(lang){
    if(lang!=='ar') lang='en';
    document.documentElement.lang = lang;
    document.documentElement.dir = lang==='ar' ? 'rtl' : 'ltr';
    mains.en.hidden = lang!=='en';
    mains.ar.hidden = lang!=='ar';
    langBtns.forEach(function(b){b.setAttribute('aria-pressed', String(b.getAttribute('data-lang')===lang));});
    document.querySelectorAll('nav a[data-nav]').forEach(function(a){
      var key = a.getAttribute('data-nav');
      a.setAttribute('href', '#' + key + (lang==='ar' ? '-ar' : ''));
      a.textContent = a.getAttribute(lang==='ar' ? 'data-ar' : 'data-en');
    });
    store('shabakah-lang', lang);
  }
  langBtns.forEach(function(b){ b.addEventListener('click', function(){ setLang(b.getAttribute('data-lang')); }); });

  // The lab map: each port is a tab that shows its service.
  document.querySelectorAll('[data-map]').forEach(function(map){
    var tabs = Array.prototype.slice.call(map.querySelectorAll('.port'));
    var panels = Array.prototype.slice.call(map.querySelectorAll('.pdetail'));
    function show(tab, focus){
      tabs.forEach(function(t){
        var on = t===tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
      });
      panels.forEach(function(p){
        var on = p.id === tab.getAttribute('aria-controls');
        p.hidden = !on;
        if(on && !reduce){ p.classList.remove('swap'); void p.offsetWidth; p.classList.add('swap'); }
      });
      if(focus) tab.focus();
    }
    tabs.forEach(function(t, i){
      t.addEventListener('click', function(){ show(t, false); });
      t.addEventListener('keydown', function(ev){
        var step = {ArrowRight:1, ArrowDown:1, ArrowLeft:-1, ArrowUp:-1}[ev.key];
        if(ev.key==='Home') step = -i; else if(ev.key==='End') step = tabs.length-1-i;
        if(step===undefined) return;
        ev.preventDefault();
        show(tabs[(i + step + tabs.length) % tabs.length], true);
      });
    });
    show(tabs[0], false);
  });

  // Screenshot gallery
  var CAPS = {
    en:{menu:"The guide greets you when you SSH in and remembers your progress.",
        lesson:"Each lesson shows the objective, the material, and a challenge to check.",
        ctf:"The flag board tracks the flags you have found and your score.",
        achievements:"Badges unlock as you clear lessons and capture flags.",
        targets:"See at a glance which practice services are up.",
        cheat:"A cheat sheet of the exact commands, one keypress away."},
    ar:{menu:"يستقبلك المرشد فور دخولك ويتذكّر أين وصلت.",
        lesson:"يعرض كل درس هدفه ومادته وتمرينا يُصحّح لك.",
        ctf:"تتابع في لوحة التحديات ما كشفته من رموز ومجموع نقاطك.",
        achievements:"تكسب الشارات كلما أتممت دروسا وكشفت رموزا سرية.",
        targets:"تعرف بلمحة أي خدمات التدريب تعمل الآن.",
        cheat:"ورقة بأهم الأوامر على بُعد ضغطة واحدة."}
  };
  ['en','ar'].forEach(function(lang){
    var scope = mains[lang];
    var tabs = scope.querySelectorAll('.shot-tabs button');
    var img = scope.querySelector('.shot-stage img');
    var cap = scope.querySelector('.shot-cap');
    tabs.forEach(function(tab){
      tab.addEventListener('click', function(){
        var key = tab.getAttribute('data-shot');
        tabs.forEach(function(t){ t.setAttribute('aria-selected', String(t===tab)); });
        if(!reduce){ img.style.opacity = '0'; img.onload = function(){ img.style.opacity = '1'; }; }
        img.src = (lang==='ar' ? 'screenshots/ar/' : 'screenshots/') + key + '.png';
        img.alt = tab.textContent;
        cap.textContent = CAPS[lang][key];
      });
    });
  });

  // Copy buttons
  document.querySelectorAll('.copybtn').forEach(function(btn){
    btn.addEventListener('click', function(){
      var pre = document.getElementById(btn.getAttribute('data-copy'));
      if(!pre) return;
      var label = btn.textContent;
      var done = function(){ btn.textContent = document.documentElement.lang==='ar' ? 'نُسخ' : 'Copied'; setTimeout(function(){ btn.textContent = label; }, 1400); };
      if(navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(pre.textContent).then(done, done); }
    });
  });

  setLang(pickInitial());
})();
