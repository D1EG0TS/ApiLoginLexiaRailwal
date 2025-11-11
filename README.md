# ApiLogin (FastAPI + MySQL)

Backend de autenticación con registro y login de usuarios, roles “admin” y “user”, JWT y protección de endpoints. Incluye documentación Scrum y una colección de Postman.

## Stack
- FastAPI, Uvicorn
- SQLAlchemy (MySQL con PyMySQL)
- Pydantic, python-jose (JWT)
- passlib[bcrypt]

## Estructura
```
ApiLogin/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── deps.py
│   ├── database.py
│   └── security.py
├── docs/
│   ├── Scrum.md
│   └── ApiLogin.postman_collection.json
└── requirements.txt
```

## Configuración y arranque
1) Asegúrate de tener MySQL activo (XAMPP) y accesible.
2) Crea/activa entorno virtual:
- PowerShell:
  - `./.venv/Scripts/Activate.ps1`
- CMD:
  - `./.venv/Scripts/activate.bat`
3) Instala dependencias si fuera necesario:
- `pip install -r requirements.txt`
4) Arranca el servidor:
- `./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

Swagger UI:
- http://127.0.0.1:8000/docs

## Variables de entorno (opcional)
Crea un archivo `.env` si deseas personalizar la configuración:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASS=
DB_NAME=login_api
JWT_SECRET=pon_un_secret_seguro
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Endpoints
- POST /auth/register
  - Body JSON: { email, full_name, password, role? }
  - Crea usuario (si email único) y devuelve datos sin password.
- POST /auth/login
  - Body form (x-www-form-urlencoded): username, password, grant_type=password.
  - Devuelve access_token (bearer).
- GET /users/me
  - Header: Authorization: Bearer <token>.
  - Devuelve perfil del usuario autenticado.
- GET /admin/users
  - Header: Authorization: Bearer <token> (rol admin).
  - Lista de usuarios.
- POST /admin/users
  - Header: Authorization: Bearer <token> (rol admin).
  - Body JSON: { email, full_name, password, role }.

## Documentación Scrum y Postman
- Documentación Scrum: `docs/Scrum.md`
- Colección Postman: `docs/ApiLogin.postman_collection.json`
  - Importa en Postman.
  - Ejecuta "Auth - Login" con `admin@example.com` / `Admin123!` para obtener el token.
  - La colección guarda el token en la variable `{{token}}` y lo usa en los endpoints protegidos.

## Notas de seguridad
- Passwords se guardan hasheados con bcrypt.
- El token JWT debe usar un `JWT_SECRET` fuerte y mantenerse fuera del repo.
- Revisa tiempos de expiración del token según necesidades.

## Resolución de problemas
- Falta email-validator: `pip install pydantic[email]` o `pip install email-validator`.
- Falta python-multipart (para login form): `pip install python-multipart`.
- Bcrypt en Windows: si hay errores, prueba una versión compatible o reinstala `bcrypt` y `cffi`.
- MySQL no disponible: verifica XAMPP/MySQL y credenciales (.env).

## Próximos pasos
- Añadir tests básicos (unitarios) para seguridad y endpoints críticos.
- Migraciones (Alembic) y logging más granular.
- Integración con frontend.