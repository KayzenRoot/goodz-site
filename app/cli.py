"""Local administrative bootstrap; never ship a default password."""
from __future__ import annotations
import argparse
import getpass
import os
from pathlib import Path
from .main import ROOT, init_db, connect, password_hash

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['set-password'])
    parser.add_argument('--data-dir', default=os.environ.get('GOODZ_DATA_DIR', str(ROOT / 'data')))
    args = parser.parse_args()
    first = getpass.getpass('Nova senha (mín. 12 caracteres): ')
    second = getpass.getpass('Repita a senha: ')
    if first != second:
        parser.error('As senhas não conferem.')
    try:
        encoded = password_hash(first)
    except ValueError as error:
        parser.error(str(error))
    db = Path(args.data_dir) / 'goodz.sqlite3'
    init_db(db)
    with connect(db) as c:
        c.execute('INSERT INTO admin_auth(id,password_hash) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET password_hash=excluded.password_hash', (encoded,))
        c.execute('DELETE FROM sessions')
    print('Senha configurada. Sessões anteriores encerradas.')

if __name__ == '__main__':
    main()
