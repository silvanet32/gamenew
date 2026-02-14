# GameNew Séries (Flask)

Aplicação web para postagem de séries com:

- Login e cadastro de usuários
- Conta admin padrão
- Painel admin para adicionar, editar e apagar séries
- Painel de métodos de doação (ativar/desativar)
- Curtidas, comentários e contagem de visualizações por usuário
- Banco SQLite local

## Requisitos

- Python 3.10+

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executar

```bash
python app.py
```

Acesse: `http://127.0.0.1:5000`

## Admin padrão

- **Email:** `admin@gmail.com`
- **Senha:** `admin123`
