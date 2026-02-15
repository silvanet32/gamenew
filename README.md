# GameNew Séries (Flask + React/Vite)

Projeto com backend Flask e interface React + Vite.

## Requisitos

- Python 3.10+
- Node.js 18+

## Windows (sem trabalho manual)

Use estes arquivos `.bat` na raiz do projeto:

1. **Instalar dependências**
   ```bat
   install_deps.bat
   ```
2. **Iniciar o site** (backend + frontend em janelas separadas)
   ```bat
   start_site.bat
   ```
3. **Tudo em um comando**
   ```bat
   run_site.bat
   ```

### O que foi corrigido

- O instalador agora usa `python -m pip` (mais estável no Windows).
- O script de instalação não fecha sem mostrar mensagem final (`pause`).
- O start abre backend e frontend em janelas separadas com `cmd /k`, então se der erro a janela fica aberta para você ver.

## Linux/macOS

### Instalar dependências

```bash
./scripts/install_deps.sh
```

### Iniciar backend

```bash
./scripts/start.sh
```

### Iniciar frontend

```bash
./scripts/start_frontend.sh
```

## Endereços

- Backend: `http://127.0.0.1:5000`
- Frontend: `http://127.0.0.1:5173`

## Admin padrão

- **Email:** `admin@gmail.com`
- **Senha:** `admin123`
