# GameNew Séries (Flask + Frontend Integrado)

Agora backend e frontend podem rodar na **mesma página/URL** via Flask.

## URL única

- `http://127.0.0.1:5000/app`

> O frontend é servido pelo próprio Flask a partir de `frontend/dist`.

## Requisitos

- Python 3.10+
- Node.js 18+

## Windows (mais fácil)

1. Instalar dependências:
   ```bat
   install_deps.bat
   ```
2. Gerar build do frontend:
   ```bat
   build_frontend.bat
   ```
3. Iniciar tudo em URL única:
   ```bat
   start_site.bat
   ```

Ou use tudo em sequência:

```bat
run_site.bat
```

## Linux/macOS

1. Instalar dependências:
   ```bash
   ./scripts/install_deps.sh
   ```
2. Build do frontend:
   ```bash
   ./scripts/build_frontend.sh
   ```
3. Iniciar backend (serve /app na mesma origem):
   ```bash
   ./scripts/start.sh
   ```

## Notas

- Se `http://127.0.0.1:5000/app` mostrar aviso de build, rode o build do frontend primeiro.
- Em produção, mantenha a mesma estratégia: Flask servindo o `frontend/dist`.

## Admin padrão

- **Email:** `admin@gmail.com`
- **Senha:** `admin123`
