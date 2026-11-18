# Data Model
`settings(key PRIMARY KEY,value TEXT)`: copy, logos, banners, links.
`products(id TEXT PRIMARY KEY,category CHECK(...),name,description,price_cents NULL,image_url,visible,sort_order,created_at)`.
`admin_auth(id=1,password_hash)`, `sessions(token_hash PRIMARY KEY,csrf_token,expires_at)`, `login_attempts(id,ip,at)`.
Arquivo original nunca sobrescrito por upload: nomes UUID sob `data/uploads/`; remoção do produto não apaga arquivos existentes (garante rollback manual, exige limpeza futura).
