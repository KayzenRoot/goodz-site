'use strict';
const $ = id => document.getElementById(id);
let csrf = '', settings = {}, products = [], editing = null;
async function api(url, {method='GET', data, file} = {}) {
  const headers = {}; if (csrf) headers['X-CSRF-Token'] = csrf;
  let body;
  if (file) { const form = new FormData(); form.append('file', file); body = form; }
  else if (data !== undefined) { headers['Content-Type']='application/json'; body=JSON.stringify(data); }
  const res = await fetch(url, {method,headers,body,credentials:'same-origin'});
  let payload; try { payload=await res.json(); } catch { payload={}; }
  if (!res.ok) throw new Error(typeof payload.detail === 'string' ? payload.detail : `Erro HTTP ${res.status}`);
  return payload;
}
function toast(message, error=false) {const el=$('status');el.textContent=message;el.classList.toggle('error',error);el.hidden=false;window.scrollTo({top:0,behavior:'smooth'});}
function activate() {$('login-screen').hidden=true;$('dashboard').hidden=false;}
function setView(name){ document.querySelectorAll('.panel').forEach(el=>el.hidden=el.id!==`tab-${name}`); document.querySelectorAll('[data-tab]').forEach(el=>el.classList.toggle('active',el.dataset.tab===name));$('status').hidden=true; }
function fill() { document.querySelectorAll('[data-setting]').forEach(el=>el.value=settings[el.dataset.setting]||'');document.querySelectorAll('[data-preview]').forEach(el=>el.src=settings[el.dataset.preview]||''); }
async function reload() {const state=await api('/api/admin/state'); csrf=state.csrf;settings=state.settings;products=state.products;activate();fill();renderProducts();}
async function saveSetting(values) {const reply=await api('/api/admin/settings',{method:'PUT',data:{values}});settings=reply.settings;fill();toast('Alterações salvas com sucesso.');}
async function sendImage(file) {return (await api('/api/admin/upload',{method:'POST',file})).url;}
function textNode(tag,value,className=''){const el=document.createElement(tag); el.textContent=value; if(className)el.className=className; return el;}
function renderProducts(){ const list=$('admin-products');list.replaceChildren();if(!products.length){list.append(textNode('p','Nenhum produto cadastrado ainda.'));return;}
  products.forEach(p=>{
    const row=textNode('div','', 'product-entry'); const img=p.image_url?document.createElement('img'):textNode('div','', 'no-img');if(p.image_url){img.src=p.image_url;img.alt=p.name;}row.append(img);
    const info=document.createElement('div');info.append(textNode('h3',p.name),textNode('p',`${p.category==='pastelaria'?'Pastelaria':'Dogueria'} • ${p.visible?'Visível':'Oculto'}${p.price_cents!==null?' • '+(p.price_cents/100).toLocaleString('pt-BR',{style:'currency',currency:'BRL'}):''}`));
    const edit=textNode('button','Editar');edit.type='button';edit.addEventListener('click',()=>{editing=p.id;$('p-category').value=p.category;$('p-name').value=p.name;$('p-desc').value=p.description;$('p-price').value=p.price_cents!==null?(p.price_cents/100).toFixed(2).replace('.',','):'';$('p-visible').checked=p.visible;$('p-order').value=p.sort_order;$('p-file').value='';$('p-preview').src=p.image_url||'';$('p-preview').hidden=!p.image_url;$('product-form-title').textContent='Editar produto';$('product-form').scrollIntoView({behavior:'smooth',block:'center'});});
    const del=textNode('button','Excluir','delete');del.type='button';del.addEventListener('click',async()=>{if(!confirm(`Excluir "${p.name}"?`))return;try{await api(`/api/admin/products/${encodeURIComponent(p.id)}`,{method:'DELETE'});await reload();toast('Produto excluído.');}catch(e){toast(e.message,true);}});
    info.append(edit,del);row.append(info);list.append(row);
  });
}
function resetProduct() {editing=null;$('product-form').reset();$('p-visible').checked=true;$('p-order').value='0';$('p-preview').hidden=true;$('p-preview').removeAttribute('src');$('product-form-title').textContent='Adicionar produto';}
document.querySelectorAll('[data-tab]').forEach(btn=>btn.addEventListener('click',()=>setView(btn.dataset.tab)));
$('login-form').addEventListener('submit',async(e)=>{e.preventDefault();$('login-error').hidden=true;try{const data=await api('/api/admin/login',{method:'POST',data:{password:$('password').value}});csrf=data.csrf;$('password').value='';await reload();}catch(err){$('login-error').hidden=false;$('login-error').textContent=err.message;}});
document.querySelectorAll('[data-file]').forEach(input=>input.addEventListener('change',async()=>{const file=input.files[0];if(!file)return;input.disabled=true;try{const path=await sendImage(file);await saveSetting({[input.dataset.file]:path});}catch(err){toast(err.message,true);}finally{input.disabled=false;input.value='';}}));
document.querySelectorAll('[data-settings-form]').forEach(form=>form.addEventListener('submit',async(e)=>{e.preventDefault();const values={};form.querySelectorAll('[data-setting]').forEach(el=>values[el.dataset.setting]=el.value.trim());try{await saveSetting(values);}catch(err){toast(err.message,true);}}));
$('p-file').addEventListener('change',()=>{const file=$('p-file').files[0];if(file){const url=URL.createObjectURL(file);$('p-preview').src=url;$('p-preview').hidden=false;$('p-preview').onload=()=>URL.revokeObjectURL(url);}});
$('product-form').addEventListener('submit',async(e)=>{e.preventDefault();$('product-save').disabled=true;try{
  const raw=$('p-price').value.trim();let price_cents=null;if(raw){if(!/^\d{1,6}([,.]\d{1,2})?$/.test(raw))throw new Error('Preço inválido. Use 19,90.');price_cents=Math.round(Number(raw.replace(',','.'))*100);}
  const previous=products.find(p=>p.id===editing);let url=previous?.image_url||'';if($('p-file').files[0])url=await sendImage($('p-file').files[0]);
  const data={category:$('p-category').value,name:$('p-name').value,description:$('p-desc').value,price_cents,image_url:url,visible:$('p-visible').checked,sort_order:Number($('p-order').value||0)};
  await api(editing?`/api/admin/products/${encodeURIComponent(editing)}`:'/api/admin/products',{method:editing?'PUT':'POST',data});resetProduct();await reload();toast('Produto salvo com sucesso.');
}catch(err){toast(err.message,true);}finally{$('product-save').disabled=false;}});
$('product-cancel').addEventListener('click',resetProduct);
$('logout').addEventListener('click',async()=>{try{await api('/api/admin/logout',{method:'POST'});}finally{csrf='';$('dashboard').hidden=true;$('login-screen').hidden=false;$('password').value='';}});
$('password-form').addEventListener('submit',async(e)=>{e.preventDefault();try{await api('/api/admin/password',{method:'POST',data:{current_password:$('current-pass').value,new_password:$('new-pass').value}});csrf='';$('dashboard').hidden=true;$('login-screen').hidden=false;$('password-form').reset();$('login-error').hidden=false;$('login-error').textContent='Senha atualizada. Faça login novamente.';}catch(err){toast(err.message,true);}});
reload().catch(()=>{ $('login-screen').hidden=false;$('dashboard').hidden=true; });
