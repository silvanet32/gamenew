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

## Método para baixar dependências

```bash
./scripts/install_deps.sh
```

Esse comando:
- cria `.venv` (se não existir)
- ativa o ambiente virtual
- instala os pacotes do `requirements.txt`

## Método para iniciar

```bash
./scripts/start.sh
```

Esse comando ativa `.venv` e inicia a aplicação Flask.

Acesse: `http://127.0.0.1:5000`

## Admin padrão

- **Email:** `admin@gmail.com`
- **Senha:** `admin123`
