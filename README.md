# GameNew Séries (Flask + React/Vite)

Projeto com backend Flask e nova interface React + Vite (estilo React-bites).

## Funcionalidades

- Login e cadastro de usuários (backend Flask)
- Conta admin padrão
- Painel admin para adicionar, editar e apagar séries
- Painel de métodos de doação (ativar/desativar)
- Curtidas, comentários e contagem de visualizações por usuário
- Interface moderna em React + Vite na pasta `frontend/`

## Requisitos

- Python 3.10+
- Node.js 18+

## Método fácil no Windows (.bat)

Para instalar dependências e iniciar backend + frontend automaticamente:

```bat
run_site.bat
```

O script faz tudo:
- cria/ativa `.venv`
- instala dependências Python (`requirements.txt`)
- instala dependências do frontend (`npm install`)
- inicia Flask e Vite em janelas separadas

## Método para baixar dependências

```bash
./scripts/install_deps.sh
```

Esse comando instala:
- backend (`requirements.txt` com `.venv`)
- frontend (`frontend/package.json`)

## Método para iniciar o backend (Flask)

```bash
./scripts/start.sh
```

Acesse: `http://127.0.0.1:5000`

## Método para iniciar a interface React + Vite

```bash
./scripts/start_frontend.sh
```

Acesse: `http://127.0.0.1:5173`

## Admin padrão

- **Email:** `admin@gmail.com`
- **Senha:** `admin123`
