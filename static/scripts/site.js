'use strict';
const byId = id => document.getElementById(id);
const setText = (id, value) => { if (byId(id) && value !== undefined) byId(id).textContent = value; };
const setImage = (id, src) => { if (byId(id) && /^\/(assets|uploads)\/[\w./-]+$/.test(src || '')) byId(id).src = src; };
const labelLinks = [ ['instagram_url', 'Instagram'], ['tiktok_url', 'TikTok'], ['whatsapp_url', 'WhatsApp'] ];
let products = [], selected = 'todos';
function renderProducts() {
  const target = byId('product-grid'); target.replaceChildren();
  const items = products.filter(p => p.visible && (selected === 'todos' || p.category === selected));
  if (!items.length) {
    const empty = document.createElement('div'); empty.className = 'empty-products';
    empty.textContent = 'Nossa seleção está sendo preparada. Volte em breve para descobrir os destaques GOODZ.';
    target.append(empty); return;
  }
  items.forEach(p => {
    const card = document.createElement('article'); card.className = 'product-card';
    if (p.image_url) {
      const img = document.createElement('img'); img.src = p.image_url; img.alt = `Foto de ${p.name}`; img.loading = 'lazy'; card.append(img);
    } else {
      const placeholder = document.createElement('div'); placeholder.className = 'product-placeholder'; placeholder.textContent = p.category === 'pastelaria' ? '✦ PASTELARIA' : '✦ DOGUERIA'; card.append(placeholder);
    }
    const body = document.createElement('div'); body.className = 'product-body';
    const label = document.createElement('span'); label.className = 'product-type'; label.textContent = `GOODZ ${p.category.toUpperCase()}`;
    const title = document.createElement('h3'); title.textContent = p.name;
    const desc = document.createElement('p'); desc.textContent = p.description;
    body.append(label, title, desc);
    if (p.price_cents !== null) {
      const price = document.createElement('strong'); price.className = 'price'; price.textContent = (p.price_cents/100).toLocaleString('pt-BR',{style:'currency',currency:'BRL'}); body.append(price);
    }
    card.append(body); target.append(card);
  });
}
function applyLink(id, emptyId, url) {
  const a = byId(id), fallback = byId(emptyId);
  if (!a || !fallback) return;
  if (url && /^https?:\/\//i.test(url)) { a.href = url; a.classList.remove('hide'); fallback.classList.add('hide'); }
  else { a.removeAttribute('href'); a.classList.add('hide'); fallback.classList.remove('hide'); }
}
async function boot() {
  byId('year').textContent = new Date().getFullYear();
  try {
    const res = await fetch('/api/site'); if (!res.ok) throw new Error('Falha ao carregar o conteúdo');
    const {settings:s, products:items} = await res.json();
    [ ['hero-heading','hero_title'], ['hero-desc','hero_description'], ['pastelaria-title','pastelaria_title'], ['pastelaria-desc','pastelaria_description'], ['dogueria-title','dogueria_title'], ['dogueria-desc','dogueria_description'], ['about-text','about_text'], ['address-text','address_text'] ].forEach(([id,k]) => setText(id,s[k]));
    [ ['nav-logo','logo_goodz'], ['footer-logo','logo_goodz'], ['about-logo','logo_goodz'], ['hero-image','hero_image'], ['pastelaria-logo','logo_pastelaria'], ['dogueria-logo','logo_dogueria'], ['pastelaria-image','pastelaria_image'], ['dogueria-image','dogueria_image'] ].forEach(([id,k]) => setImage(id,s[k]));
    applyLink('ifood-link','ifood-wait',s.ifood_url); applyLink('food99-link','food99-wait',s.food99_url);
    const social = byId('social-links'); social.replaceChildren();
    labelLinks.forEach(([key,name]) => { if (s[key] && /^https?:\/\//i.test(s[key])) {const a = document.createElement('a'); a.textContent = name + ' ↗'; a.href=s[key]; a.target='_blank'; a.rel='noopener noreferrer'; social.append(a);} });
    products=items; renderProducts();
  } catch(error) { console.error('GOODZ:', error.message); }
}
document.querySelectorAll('[data-filter]').forEach(b=> b.addEventListener('click', () => {
  selected = b.dataset.filter; document.querySelectorAll('[data-filter]').forEach(x => x.classList.toggle('active', x === b)); renderProducts();
}));
boot();
