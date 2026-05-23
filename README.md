
<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#1a1208">
<title>LuxHome – Sklad boshqaruvi</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">
<style>
  :root {
    --gold: #C9963A;
    --gold-light: #E8C97A;
    --dark: #0F0D08;
    --dark2: #1A1710;
    --dark3: #252118;
    --dark4: #312C22;
    --cream: #F5EDD8;
    --cream2: #EAE0C8;
    --text: #F0E6CE;
    --text-muted: #9A8E75;
    --red: #C94040;
    --green: #5A8C3A;
    --orange: #C97A30;
    --radius: 10px;
    --font-display: 'Cormorant Garamond', serif;
    --font-body: 'DM Sans', sans-serif;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: var(--font-body); background: var(--dark); color: var(--text); min-height: 100vh; }
  nav {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 1.5rem; height: 58px;
    background: var(--dark2);
    border-bottom: 1px solid #2e2918;
    position: sticky; top: 0; z-index: 50;
  }
  .logo { font-family: var(--font-display); font-size: 22px; font-weight: 600; color: var(--cream); letter-spacing: 3px; }
  .logo span { color: var(--gold); }
  .nav-links { display: flex; gap: 4px; }
  .nav-btn { background: transparent; border: none; font-family: var(--font-body); font-size: 13px; color: var(--text-muted); padding: 7px 16px; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
  .nav-btn:hover { color: var(--text); background: var(--dark3); }
  .nav-btn.active { color: var(--gold); background: rgba(201,150,58,0.12); }
  .page { display: none; padding: 1.25rem; max-width: 960px; margin: 0 auto; }
  .page.active { display: block; }
  .stats-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 1.25rem; }
  @media(max-width:600px){ .stats-row { grid-template-columns: repeat(2,1fr); } }
  .stat { background: var(--dark2); border: 1px solid #2e2918; border-radius: var(--radius); padding: 1rem; text-align: center; }
  .stat .n { font-family: var(--font-display); font-size: 28px; color: var(--gold); font-weight: 500; }
  .stat .l { font-size: 11px; color: var(--text-muted); margin-top: 3px; letter-spacing: 0.5px; }
  .toolbar { display: flex; gap: 8px; margin-bottom: 1rem; flex-wrap: wrap; }
  .toolbar input, .toolbar select { font-family: var(--font-body); font-size: 13px; padding: 8px 12px; background: var(--dark2); color: var(--text); border: 1px solid #2e2918; border-radius: 8px; outline: none; transition: border-color 0.2s; }
  .toolbar input { flex: 1; min-width: 160px; }
  .toolbar input:focus, .toolbar select:focus { border-color: var(--gold); }
  .toolbar select option { background: var(--dark2); }
  .btn-add { background: var(--gold); color: var(--dark); border: none; border-radius: 8px; padding: 8px 18px; font-size: 13px; font-weight: 500; font-family: var(--font-body); cursor: pointer; transition: background 0.2s; white-space: nowrap; }
  .btn-add:hover { background: var(--gold-light); }
  .tbl-wrap { border: 1px solid #2e2918; border-radius: var(--radius); overflow: hidden; overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; min-width: 520px; }
  thead { background: var(--dark3); }
  th { padding: 10px 14px; text-align: left; font-size: 11px; font-weight: 500; color: var(--text-muted); letter-spacing: 0.8px; text-transform: uppercase; }
  td { padding: 11px 14px; color: var(--text); border-top: 1px solid #1e1c13; }
  tr:hover td { background: rgba(255,255,255,0.02); }
  .badge { display: inline-block; font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 20px; }
  .ok  { background: rgba(90,140,58,0.18); color: #8BC462; border: 1px solid rgba(90,140,58,0.3); }
  .low { background: rgba(201,122,48,0.18); color: #E09850; border: 1px solid rgba(201,122,48,0.3); }
  .out { background: rgba(201,64,64,0.18); color: #E07070; border: 1px solid rgba(201,64,64,0.3); }
  .action-btn { background: transparent; border: 1px solid #2e2918; border-radius: 7px; padding: 5px 10px; font-size: 12px; cursor: pointer; color: var(--text-muted); font-family: var(--font-body); margin-left: 4px; transition: all 0.15s; }
  .action-btn:hover { border-color: var(--gold); color: var(--gold); }
  .action-btn.del:hover { border-color: var(--red); color: #E07070; }
  .empty { text-align: center; padding: 2.5rem; color: var(--text-muted); font-size: 13px; }
  .overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.65); display: flex; align-items: center; justify-content: center; z-index: 200; padding: 1rem; }
  .modal { background: var(--dark2); border: 1px solid #3a3320; border-radius: 14px; padding: 1.75rem; width: 100%; max-width: 360px; animation: popIn 0.18s ease; }
  @keyframes popIn { from { transform: scale(0.94); opacity: 0; } to { transform: scale(1); opacity: 1; } }
  .modal h3 { font-family: var(--font-display); font-size: 20px; color: var(--cream); margin-bottom: 1.25rem; font-weight: 500; }
  .field { margin-bottom: 1rem; }
  .field label { display: block; font-size: 11px; color: var(--text-muted); letter-spacing: 0.5px; margin-bottom: 5px; text-transform: uppercase; }
  .field input, .field select { width: 100%; font-family: var(--font-body); font-size: 14px; padding: 9px 12px; background: var(--dark3); color: var(--text); border: 1px solid #2e2918; border-radius: 8px; outline: none; transition: border-color 0.2s; }
  .field input:focus, .field select:focus { border-color: var(--gold); }
  .field select option { background: var(--dark3); }
  .modal-btns { display: flex; gap: 8px; margin-top: 1.25rem; }
  .btn-save { flex: 1; background: var(--gold); color: var(--dark); border: none; border-radius: 8px; padding: 10px; font-size: 13px; font-weight: 500; font-family: var(--font-body); cursor: pointer; transition: background 0.2s; }
  .btn-save:hover { background: var(--gold-light); }
  .btn-cancel { flex: 1; background: transparent; color: var(--text-muted); border: 1px solid #2e2918; border-radius: 8px; padding: 10px; font-size: 13px; font-family: var(--font-body); cursor: pointer; transition: all 0.2s; }
  .btn-cancel:hover { color: var(--text); border-color: var(--text-muted); }
  .price-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); gap: 14px; }
  .price-card { background: var(--dark2); border: 1px solid #2e2918; border-radius: 14px; padding: 1.5rem; display: flex; flex-direction: column; gap: 10px; }
  .price-card.featured { border-color: var(--gold); }
  .price-card label { font-size: 11px; color: var(--text-muted); letter-spacing: 0.5px; text-transform: uppercase; display: block; margin-bottom: 3px; }
  .price-card input, .price-card textarea { width: 100%; font-family: var(--font-body); font-size: 13px; padding: 7px 10px; background: var(--dark3); color: var(--text); border: 1px solid #2e2918; border-radius: 7px; outline: none; transition: border-color 0.2s; }
  .price-card input:focus, .price-card textarea:focus { border-color: var(--gold); }
  .price-card input.big { font-size: 20px; font-weight: 500; color: var(--gold); }
  .price-card textarea { resize: vertical; min-height: 90px; line-height: 1.6; }
  .featured-toggle { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-muted); cursor: pointer; }
  .featured-toggle input[type=checkbox] { accent-color: var(--gold); width: 15px; height: 15px; }
  .pop-badge { display: inline-block; background: rgba(201,150,58,0.18); color: var(--gold); font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 20px; border: 1px solid rgba(201,150,58,0.3); }
  .section-label { font-size: 11px; font-weight: 500; letter-spacing: 1px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 1rem; }
  .save-hint { font-size: 12px; color: var(--text-muted); text-align: center; margin-top: 1rem; display: flex; align-items: center; justify-content: center; gap: 6px; }
  @media(max-width:480px){ nav { padding: 0 1rem; } .logo { font-size: 18px; } .nav-btn { padding: 6px 10px; font-size: 12px; } .page { padding: 1rem; } .modal { padding: 1.25rem; } }
</style>
</head>
<body>
<nav>
  <div class="logo">LUX<span>HOME</span></div>
  <div class="nav-links">
    <button class="nav-btn active" onclick="showPage('mahsulot',this)"><i class="ti ti-package"></i> Mahsulotlar</button>
    <button class="nav-btn" onclick="showPage('narx',this)"><i class="ti ti-tag"></i> Narxlar</button>
  </div>
</nav>
<div id="mahsulot" class="page active">
  <div class="stats-row" id="statsRow"></div>
  <div class="toolbar">
    <input type="text" id="searchInput" placeholder="Mahsulot qidirish..." oninput="renderTable()">
    <select id="filterCat" onchange="renderTable()"><option value="">Barcha kategoriyalar</option></select>
    <button class="btn-add" onclick="openModal()"><i class="ti ti-plus"></i> Qo'shish</button>
  </div>
  <div class="tbl-wrap">
    <table>
      <thead><tr><th>Nomi</th><th>Kategoriya</th><th>Miqdor</th><th>Narx</th><th>Holat</th><th>Amallar</th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
</div>
<div id="narx" class="page">
  <div class="section-label">Tariflarni o'zingiz tahrirlang</div>
  <div class="price-grid" id="priceGrid"></div>
  <div class="save-hint"><i class="ti ti-info-circle"></i> Matn kiritilgach avtomatik saqlanadi</div>
</div>
<div class="overlay" id="overlay" style="display:none" onclick="overlayClick(event)">
  <div class="modal">
    <h3 id="modalTitle">Yangi mahsulot</h3>
    <div class="field"><label>Nomi</label><input id="fName" placeholder="Mahsulot nomini kiriting"></div>
    <div class="field"><label>Kategoriya</label>
      <select id="fCat"><option>Mebel</option><option>Yorug'lik</option><option>Pardalar</option><option>Dekor</option><option>Oshxona</option><option>Boshqa</option></select>
    </div>
    <div class="field"><label>Miqdor (dona)</label><input id="fQty" type="number" min="0" placeholder="0"></div>
    <div class="field"><label>Narx (so'm)</label><input id="fPrice" type="number" min="0" placeholder="0"></div>
    <div class="modal-btns">
      <button class="btn-cancel" onclick="closeModal()">Bekor</button>
      <button class="btn-save" onclick="saveProduct()">Saqlash</button>
    </div>
  </div>
</div>
<script>
var STORAGE_KEY='luxhome_products',PLANS_KEY='luxhome_plans';
var defaultProducts=[{id:1,name:'Sofa Milano',cat:'Mebel',qty:12,price:4500000},{id:2,name:'Devor chiroq LED',cat:"Yorug'lik",qty:4,price:280000},{id:3,name:"Ipak parda Beige",cat:'Pardalar',qty:0,price:750000},{id:4,name:'Gul vazasi Marmur',cat:'Dekor',qty:27,price:320000}];
var defaultPlans=[{name:"Boshlang'ich",price:'',desc:'Kichik ombor uchun',features:"500 ta mahsulot\n1 foydalanuvchi\nHisobotlar\nEmail yordam",featured:false},{name:'Professional',price:'',desc:"O'rta hajm uchun",features:"Cheksiz mahsulot\n5 foydalanuvchi\nKengaytirilgan hisobot\nBarcode skaneri\nPrioritet yordam",featured:true},{name:'Korporativ',price:'',desc:'Yirik tarmoqlar uchun',features:"Cheksiz hamma narsa\nCheksiz foydalanuvchi\nAPI integratsiya\nMaxsus dizayn\n24/7 yordam",featured:false}];
function load(k,d){try{var v=localStorage.getItem(k);return v?JSON.parse(v):d;}catch(e){return d;}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v));}catch(e){}}
var products=load(STORAGE_KEY,defaultProducts),plans=load(PLANS_KEY,defaultPlans),editId=null;
function fmt(n){return Number(n).toLocaleString('uz-UZ')+" so'm";}
function status(q){if(q===0)return'<span class="badge out">Tugagan</span>';if(q<=5)return'<span class="badge low">Kam qoldi</span>';return'<span class="badge ok">Yetarli</span>';}
function renderStats(){var t=products.length,l=products.filter(p=>p.qty>0&&p.qty<=5).length,o=products.filter(p=>p.qty===0).length,c=[...new Set(products.map(p=>p.cat))].length;document.getElementById('statsRow').innerHTML='<div class="stat"><div class="n">'+t+'</div><div class="l">Jami mahsulot</div></div><div class="stat"><div class="n">'+c+'</div><div class="l">Kategoriyalar</div></div><div class="stat"><div class="n">'+l+'</div><div class="l">Kam qolgan</div></div><div class="stat"><div class="n">'+o+'</div><div class="l">Tugagan</div></div>';}
function renderCatFilter(){var sel=document.getElementById('filterCat'),cur=sel.value,cats=[...new Set(products.map(p=>p.cat))];sel.innerHTML='<option value="">Barcha kategoriyalar</option>'+cats.map(c=>'<option'+(c===cur?' selected':'')+'>'+c+'</option>').join('');}
function renderTable(){var q=document.getElementById('searchInput').value.toLowerCase(),cat=document.getElementById('filterCat').value,rows=products.filter(p=>(!q||p.name.toLowerCase().includes(q))&&(!cat||p.cat===cat)),tb=document.getElementById('tbody');if(!rows.length){tb.innerHTML='<tr><td colspan="6" class="empty">Mahsulot topilmadi</td></tr>';return;}tb.innerHTML=rows.map(p=>'<tr><td><strong>'+p.name+'</strong></td><td>'+p.cat+'</td><td>'+p.qty+' dona</td><td>'+fmt(p.price)+'</td><td>'+status(p.qty)+'</td><td><button class="action-btn" onclick="openModal('+p.id+')">Tahrir</button><button class="action-btn del" onclick="deleteProduct('+p.id+')">O\'chir</button></td></tr>').join('');}
function openModal(id){editId=id||null;document.getElementById('modalTitle').textContent=id?'Mahsulotni tahrirlash':'Yangi mahsulot';if(id){var p=products.find(x=>x.id===id);document.getElementById('fName').value=p.name;document.getElementById('fCat').value=p.cat;document.getElementById('fQty').value=p.qty;document.getElementById('fPrice').value=p.price;}else{document.getElementById('fName').value='';document.getElementById('fQty').value='';document.getElementById('fPrice').value='';}document.getElementById('overlay').style.display='flex';setTimeout(()=>document.getElementById('fName').focus(),100);}
function closeModal(){document.getElementById('overlay').style.display='none';}
function overlayClick(e){if(e.target===document.getElementById('overlay'))closeModal();}
function saveProduct(){var name=document.getElementById('fName').value.trim(),cat=document.getElementById('fCat').value,qty=parseInt(document.getElementById('fQty').value)||0,price=parseInt(document.getElementById('fPrice').value)||0;if(!name){document.getElementById('fName').focus();return;}if(editId){var p=products.find(x=>x.id===editId);p.name=name;p.cat=cat;p.qty=qty;p.price=price;}else{products.push({id:Date.now(),name,cat,qty,price});}save(STORAGE_KEY,products);closeModal();renderStats();renderCatFilter();renderTable();}
function deleteProduct(id){if(!confirm("O'chirishni tasdiqlaysizmi?"))return;products=products.filter(p=>p.id!==id);save(STORAGE_KEY,products);renderStats();renderCatFilter();renderTable();}
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeModal();if(e.key==='Enter'&&document.getElementById('overlay').style.display==='flex')saveProduct();});
function renderPrices(){document.getElementById('priceGrid').innerHTML=plans.map((pl,i)=>'<div class="price-card'+(pl.featured?' featured':'')+'">'+( pl.featured?'<div class="pop-badge">Eng mashhur</div>':'')+'<div><label>Tarif nomi</label><input value="'+esc(pl.name)+'" placeholder="Tarif nomi" oninput="plans['+i+'].name=this.value;savePlans()"></div><div><label>Narx</label><input class="big" value="'+esc(pl.price)+'" placeholder="Masalan: 79,000 so\'m" oninput="plans['+i+'].price=this.value;savePlans()"></div><div><label>Tavsif</label><input value="'+esc(pl.desc)+'" placeholder="Kim uchun?" oninput="plans['+i+'].desc=this.value;savePlans()"></div><div><label>Xususiyatlar (yangi qatorda)</label><textarea oninput="plans['+i+'].features=this.value;savePlans()">'+esc(pl.features)+'</textarea></div><label class="featured-toggle"><input type="checkbox" '+(pl.featured?'checked':'')+' onchange="plans['+i+'].featured=this.checked;savePlans();renderPrices()"> Eng mashhur</label></div>').join('');}
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function savePlans(){save(PLANS_KEY,plans);}
function showPage(id,btn){document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));document.getElementById(id).classList.add('active');btn.classList.add('active');if(id==='narx')renderPrices();}
renderStats();renderCatFilter();renderTable();
</script>
</body>
</html>
