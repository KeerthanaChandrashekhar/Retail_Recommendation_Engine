const API = 'http://127.0.0.1:5000';

// ── SHARED DATA & HELPERS ────────────────────────────────────────────────────

const MOCK_PRICES = {
  home:60,decor:45,gift:35,kitchen:28,garden:22,fashion:55,other:40
};

const CAT_RULES = [
  [/candle|lamp|light|lantern|holder|cushion|pillow|curtain|mirror|frame|clock|blind|rug/i,'home','Home','🏡'],
  [/decor|ornament|vintage|retro|sign|vase|pot|urn|figurine|statue|plaque|wreath/i,'decor','Décor','🎨'],
  [/gift|card|wrap|ribbon|set|pack|bundle|hamper|box/i,'gift','Gifts','🎁'],
  [/mug|cup|tea|coffee|kitchen|tin|jar|bowl|plate|spoon|tray|jug|bottle|flask/i,'kitchen','Kitchen','☕'],
  [/garden|plant|flower|seed|herb|outdoor|watering|pot/i,'garden','Garden','🌿'],
  [/bag|purse|wallet|scarf|hat|jewel|bracelet|ring|soap|cream|lotion|perfume/i,'fashion','Style','👜'],
];

const WHY = [
  'Popular among similar customers',
  'Frequently bought together',
  'Matches your purchase history',
  'Trending in your segment',
  'Top pick for your profile',
  'Customers like you loved this',
  'High preference score',
  'Pairs well with past orders',
];

const SEED_ICONS = {
  home:['🕯️','🪞','🖼️','🛋️','🪴'],
  decor:['🏮','🧶','🎀','🪩','🫙'],
  gift:['🎁','🧸','🪄','🎊','✉️'],
  kitchen:['☕','🫖','🥄','🍶','🧺'],
  garden:['🌸','🌼','🪻','🌱','🌿'],
  fashion:['👜','🧴','💍','🧣','🪭'],
  other:['🛍️','📦','🌟','🏷️','🧩'],
};

function categorise(desc=''){
  for(const [re,key,label,icon] of CAT_RULES){
    if(re.test(desc)) return {key,label,icon};
  }
  return {key:'other',label:'General',icon:'🛍️'};
}

function seedIcon(id,cat){
  const arr=SEED_ICONS[cat]||SEED_ICONS.other;
  const h=String(id).split('').reduce((a,c)=>a+c.charCodeAt(0),0);
  return arr[h%arr.length];
}

function mockPrice(cat,id){
  const base=MOCK_PRICES[cat]||40;
  const h=String(id).split('').reduce((a,c)=>a+c.charCodeAt(0),0);
  return (base + (h%30) - 5).toFixed(2);
}

function confidence(score){
  if(score>=.70) return {label:'High match',color:'text-emerald-600 bg-emerald-50 border-emerald-200'};
  if(score>=.40) return {label:'Good match',color:'text-amber-600 bg-amber-50 border-amber-200'};
  return {label:'Fair match',color:'text-slate-500 bg-slate-100 border-slate-200'};
}

function esc(s){
  return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function storeProduct(rec){
  const {key,label,icon}=categorise(rec.description||'');
  const price=mockPrice(key,rec.item_id||'x');
  const obj={...rec,cat:key,catLabel:label,catIcon:icon,price,emoji:seedIcon(rec.item_id,key)};
  sessionStorage.setItem('shopai_product',JSON.stringify(obj));
}

function authRoute(){
  const uid=localStorage.getItem('shopai_uid')||'';
  return uid.toUpperCase().startsWith('R');
}

// ── TRENDING MOCK DATA ────────────────────────────────────────────────────────

const TRENDING = [
  {item_id:'85123A',description:'WHITE HANGING HEART T-LIGHT HOLDER',score:.92,price:'14.95'},
  {item_id:'22423', description:'REGENCY CAKESTAND 3 TIER',            score:.89,price:'24.95'},
  {item_id:'47566', description:'PARTY BUNTING',                       score:.85,price:'9.99'},
  {item_id:'84879', description:'ASSORTED COLOUR BIRD ORNAMENT',       score:.81,price:'6.50'},
  {item_id:'21232', description:'STRAWBERRY CERAMIC TRINKET BOX',      score:.78,price:'11.25'},
  {item_id:'22720', description:'SET OF 3 CAKE TINS PANTRY DESIGN',    score:.76,price:'18.50'},
  {item_id:'21977', description:'PACK OF 60 PINK PAISLEY CAKE CASES',  score:.74,price:'3.95'},
  {item_id:'84991', description:'60 TEATIME FAIRY CAKE CASES',         score:.71,price:'3.50'},
];

// ── SHARED NAV RENDERER ───────────────────────────────────────────────────────

function renderNav(activePage){
  const isRetailer=authRoute();
  const uid=localStorage.getItem('shopai_uid')||'';
  const links=[
    {href:'index.html',label:'Home',id:'home'},
    {href:'dashboard.html',label:'Dashboard',id:'dashboard'},
  ];
  return `
  <nav class="sticky top-0 z-50 bg-white border-b border-stone-200 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-14">
      <a href="index.html" class="flex items-center gap-2 font-bold text-lg tracking-tight text-stone-900">
        <span class="w-6 h-6 rounded-md bg-terracotta flex items-center justify-center text-white text-xs font-black">S</span>
        shopAI
      </a>
      <div class="hidden sm:flex items-center gap-1">
        ${links.map(l=>`
          <a href="${l.href}" class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors
            ${activePage===l.id
              ? 'bg-stone-100 text-stone-900'
              : 'text-stone-500 hover:text-stone-900 hover:bg-stone-50'}">
            ${l.label}
          </a>`).join('')}
      </div>
      <div class="flex items-center gap-3">
        ${uid
          ? `<span class="text-xs text-stone-400 hidden sm:block">ID: <span class="text-stone-700 font-medium">${esc(uid)}</span></span>
             <button onclick="logout()" class="text-xs text-stone-400 hover:text-terracotta transition-colors">Sign out</button>`
          : `<a href="index.html#login" class="text-sm text-stone-500 hover:text-stone-900 transition-colors">Login</a>`
        }
        <div class="w-8 h-8 rounded-full bg-stone-100 flex items-center justify-center text-stone-500 text-sm font-medium">
          ${uid ? esc(String(uid).charAt(0).toUpperCase()) : '?'}
        </div>
      </div>
    </div>
  </nav>`;
}

function logout(){
  localStorage.removeItem('shopai_uid');
  window.location.href='index.html';
}

// ── PRODUCT CARD (home + product similar) ────────────────────────────────────

function productCard(rec, i=0, clickable=true){
  const {key,label}=categorise(rec.description||'');
  const conf=confidence(rec.score||0);
  const price=rec.price||mockPrice(key,rec.item_id||'x');
  const emoji=rec.emoji||seedIcon(rec.item_id,key);
  const pct=Math.round((rec.score||0)*100);
  const why=WHY[i%WHY.length];

  const thumbBg={
    home:'bg-stone-100',decor:'bg-purple-50',gift:'bg-rose-50',
    kitchen:'bg-amber-50',garden:'bg-green-50',fashion:'bg-pink-50',other:'bg-slate-100'
  }[key]||'bg-slate-100';

  const clickHandler=clickable
    ? `onclick="(function(){storeProduct(${JSON.stringify(JSON.stringify(rec)).slice(1,-1).replace(/'/g,"\\'")});window.location='product.html';})()" style="cursor:pointer"`
    :'';

  // store properly via data attr to avoid escaping hell
  return `
  <div class="product-card bg-white rounded-2xl border border-stone-200 overflow-hidden shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200"
       style="animation:fadeUp .3s ease both;animation-delay:${(i*.05).toFixed(2)}s"
       data-rec='${esc(JSON.stringify({...rec,cat:key,catLabel:label,price,emoji}))}'
       ${clickable?'onclick="openProduct(this)" style="cursor:pointer"':''}
  >
    <div class="relative ${thumbBg} h-36 flex items-center justify-center text-5xl select-none">
      ${emoji}
      <span class="absolute top-2 right-2 text-[10px] font-semibold px-2 py-0.5 rounded-full border ${conf.color}">${conf.label}</span>
    </div>
    <div class="p-4">
      <span class="inline-block text-[9px] tracking-widest uppercase font-bold text-stone-400 mb-1">${label}</span>
      <p class="text-sm font-semibold text-stone-800 leading-snug line-clamp-2 mb-2">${esc(rec.description||'Unknown Product')}</p>
      <div class="flex items-center justify-between mb-3">
        <span class="text-base font-bold text-terracotta">£${price}</span>
        <span class="text-xs text-stone-400 font-mono">${pct}% match</span>
      </div>
      <div class="w-full bg-stone-100 rounded-full h-1 mb-3">
        <div class="bg-terracotta h-1 rounded-full transition-all duration-500" style="width:${pct}%"></div>
      </div>
      <p class="text-[11px] text-stone-400 italic mb-3">✦ ${why}</p>
      <button onclick="event.stopPropagation();addToCart('${esc(String(rec.item_id))}','${esc(rec.description||'')}','${price}')"
        class="w-full py-2 rounded-xl text-sm font-semibold bg-stone-900 text-white hover:bg-terracotta transition-colors duration-200">
        Add to Cart
      </button>
    </div>
  </div>`;
}

function openProduct(el){
  try{
    const rec=JSON.parse(el.dataset.rec);
    storeProduct(rec);
    window.location.href='product.html';
  }catch(e){console.error(e);}
}

// ── CART ─────────────────────────────────────────────────────────────────────

function addToCart(id,name,price){
  let cart=JSON.parse(localStorage.getItem('shopai_cart')||'[]');
  const ex=cart.find(x=>x.id===id);
  if(ex){ex.qty++;}else{cart.push({id,name,price,qty:1});}
  localStorage.setItem('shopai_cart',JSON.stringify(cart));
  updateCartBadge();
  showToast(`Added to cart!`);
}

function updateCartBadge(){
  const cart=JSON.parse(localStorage.getItem('shopai_cart')||'[]');
  const total=cart.reduce((a,x)=>a+x.qty,0);
  document.querySelectorAll('.cart-badge').forEach(el=>{
    el.textContent=total;
    el.classList.toggle('hidden',total===0);
  });
}

function showToast(msg){
  const t=document.createElement('div');
  t.className='fixed bottom-6 left-1/2 -translate-x-1/2 bg-stone-900 text-white text-sm px-5 py-3 rounded-xl shadow-xl z-50 transition-all';
  t.textContent=msg;
  document.body.appendChild(t);
  setTimeout(()=>{t.style.opacity='0';setTimeout(()=>t.remove(),400);},2200);
}

window.addEventListener('DOMContentLoaded',updateCartBadge);

// ============================================================
// EMAIL RECOMMENDATION FEATURE
// ============================================================

function sendRecommendations(userId) {
  if (!userId) {
    showEmailResult('error', 'Please enter a Customer ID.');
    return;
  }

  const btn   = document.getElementById('send-btn');
  const icon  = document.getElementById('send-btn-icon');
  const label = document.getElementById('send-btn-label');

  if (btn) {
    btn.disabled = true;
    btn.classList.add('opacity-70','cursor-not-allowed');
    icon.textContent  = '⏳';
    label.textContent = 'Sending…';
  }

  fetch(`${API}/send_recommendations/${encodeURIComponent(userId)}`)
    .then(res => res.json())
    .then(data => {

      if (data.status) {
        showEmailResult(
          'success',
          `✅ ${data.status} — sent to <strong>${data.sent_to}</strong> with ${data.num_products} product picks.`
        );
      } 
      else {
        showEmailResult('error', `⚠️ ${data.error || 'Unknown error'}`);
      }

    })
    .catch(() => {
      showEmailResult(
        'error',
        '⚠️ Could not reach Flask API. Make sure <code>python app.py</code> is running.'
      );
    })
    .finally(() => {

      if (btn) {
        btn.disabled = false;
        btn.classList.remove('opacity-70','cursor-not-allowed');
        icon.textContent  = '📧';
        label.textContent = 'Send Recommendations';
      }

    });
}

function showEmailResult(type, html) {

  const el = document.getElementById('email-result');

  if (!el) {
    alert(html.replace(/<[^>]+>/g,''));
    return;
  }

  const styles = {
    success:'bg-emerald-50 border border-emerald-200 text-emerald-800',
    error:'bg-red-50 border border-red-200 text-red-700'
  };

  el.className = `mt-4 rounded-xl px-4 py-3 text-sm ${styles[type] || styles.error}`;
  el.innerHTML = html;
  el.classList.remove('hidden');

  clearTimeout(el._hideTimer);
  el._hideTimer = setTimeout(() => el.classList.add('hidden'),6000);
}
