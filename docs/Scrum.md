# Documentación Scrum - Backend de Login (FastAPI + MySQL)

Visión del producto
- Backend seguro y mantenible con registro y login de usuarios, roles “admin” y “user”, JWT y buenas prácticas.

Objetivo del Sprint 1
- Entregar backend funcional con autenticación/autorización por roles, endpoints protegidos y documentación en Swagger.

Épicas
- E1. Autenticación y Autorización: registro, login, JWT, roles, protección de endpoints.
- E2. Gestión de Usuarios: CRUD administrado, listado de usuarios por admin.
- E3. Seguridad y Cumplimiento: hashing, validación de entrada, configuración segura.
- E4. Infraestructura y Observabilidad: conexión MySQL, migraciones (futuras), logging básico.
- E5. Documentación y QA: documentación en /docs, pruebas, guías de uso y Postman.

Historias de Usuario (con criterios de aceptación y DoD)
- HU1 (3 pts): Como usuario, quiero registrarme para acceder a la plataforma.
  - CA:
    - Si envío email, full_name, password, role (opcional) al POST /auth/register y el email es único, se crea y devuelve datos sin password.
    - Password se almacena hasheado.
    - Si email existe, retorna 400 con detalle.
  - DoD:
    - Validaciones básicas (EmailStr, password mínimo).
    - Tests de éxito y duplicado.
    - Documentado en Swagger.

- HU2 (3 pts): Como usuario, quiero iniciar sesión para obtener un token JWT.
  - CA:
    - Envío username=email y password válidos al POST /auth/login (grant_type=password) y devuelve access_token tipo bearer.
    - Si credenciales inválidas, 401.
  - DoD:
    - Verificación de hash bcrypt.
    - Expiración de token configurada.
    - Documentado en Swagger.

- HU3 (2 pts): Como usuario autenticado, quiero ver mi perfil.
  - CA:
    - Con token válido, GET /users/me devuelve id, email, full_name, role.
    - Token inválido/expirado, 401.
  - DoD:
    - Dependencia get_current_user funcionando.
    - Documentado en Swagger.

- HU4 (3 pts): Como administrador, quiero listar usuarios.
  - CA:
    - Con token admin, GET /admin/users devuelve lista de usuarios.
    - Si no es admin, 403.
  - DoD:
    - Dependencia get_current_admin valida rol admin.
    - Documentado en Swagger.

- HU5 (3 pts): Como administrador, quiero crear usuarios con rol.
  - CA:
    - Con token admin, POST /admin/users crea usuario y devuelve datos.
    - Email duplicado, 400.
  - DoD:
    - Validaciones de entrada y rol.
    - Documentado en Swagger.

Historias Técnicas
- HT1 (2 pts): Conexión MySQL y creación automática de DB (.env: DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME).
- HT2 (2 pts): Modelo de datos y ORM (User y Enum de roles).
- HT3 (2 pts): Esquemas Pydantic y validación (EmailStr, UserRole).
- HT4 (3 pts): Seguridad: hashing bcrypt y JWT (.env: JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES).
- HT5 (2 pts): Dependencias de autorización (get_current_user/get_current_admin).
- HT6 (2 pts): CRUD de usuarios.
- HT7 (2 pts): Endpoints y arranque de app (register, login, me, admin/users).
- HT8 (1 pt): Dependencias y entorno virtual.

Definición de Listo (DoR)
- Historia clara, valor para usuario, CA definidos, dependencias identificadas, estimación y ejemplos request/response.

Definición de Hecho (DoD)
- Código implementado y revisado.
- Tests básicos en verde.
- Documentación en /docs actualizada.
- Sin errores en logs en flujo principal.
- Configuración por entorno validada (.env soportado).

Riesgos y supuestos
- Bcrypt en Windows: fijar versión compatible si es necesario.
- MySQL activo en XAMPP; ajustar variables si no es root sin contraseña.
- Migraciones no implementadas aún (siguiente sprint).

Backlog del Sprint (prioridad)
- P0: HU2, HU1, HT4, HT5, HT6, HU3
- P1: HU4, HU5, HT1, HT2, HT3, HT7
- P2: HT8, mejoras de DX, logging y manejo de errores

Day List (10 días)
- Día 1: Planificación, venv, dependencias.
- Día 2: MySQL y DB; modelos y esquemas.
- Día 3: /auth/register.
- Día 4: /auth/login + JWT.
- Día 5: Seguridad y /users/me.
- Día 6: Admin GET/POST /admin/users.
- Día 7: Tests básicos y correcciones.
- Día 8: Documentación /docs y Postman.
- Día 9: Hardening y revisión de logs.
- Día 10: Demo, retrospectiva y planificación.

Métricas sugeridas
- Velocidad (puntos por sprint), lead time, tasa de defectos, cobertura mínima de tests.

Entregables del Sprint 1
- Backend funcional con JWT y roles.
- Documentación interactiva en /docs.
- Usuario admin inicial.
- Guía de arranque y configuración.

---

# Documentación Scrum - Sprint 2: CRUD Administrador de Usuarios (búsqueda, filtros, paginación y ordenamiento)

Visión del producto (extensión)
- Ampliar la Gestión de Usuarios para que el administrador pueda ver, crear, actualizar y eliminar usuarios, con capacidades de búsqueda, filtros, paginación con total y ordenamiento configurable.

Objetivo del Sprint 2
- Entregar CRUD completo para administrador, con endpoints protegidos, respuesta paginada con total, búsqueda por email y nombre, filtro por rol, y ordenamiento por columnas.

Épicas
- E2 (ampliada). Gestión de Usuarios avanzada: lectura, actualización, eliminación, búsqueda, filtros, paginación, ordenamiento.
- E6. Infraestructura de acceso: configuración CORS por entorno y servidor accesible desde la red local (0.0.0.0).

Historias de Usuario (con criterios de aceptación y DoD)
- HU6 (3 pts): Como administrador, quiero actualizar usuarios.
  - CA:
    - Con token admin, PUT /admin/users/{user_id} acepta body parcial { email?, full_name?, password?, role? }.
    - Si se envía password, el backend actualiza usando hash bcrypt y devuelve el usuario actualizado sin password.
    - Si el email ya existe en otro usuario, retorna 400 con detalle.
    - Si el usuario no existe, 404.
  - DoD:
    - Validación de entrada y unicidad de email.
    - Tests de éxito, duplicado de email y usuario inexistente.
    - Documentado en Swagger.

- HU7 (2 pts): Como administrador, quiero eliminar usuarios.
  - CA:
    - Con token admin, DELETE /admin/users/{user_id} elimina y devuelve 204.
    - Si el usuario no existe, 404.
  - DoD:
    - Confirmación de borrado en Postman/Swagger.
    - Manejo correcto de errores y protección de endpoint.

- HU8 (3 pts): Como administrador, quiero listar usuarios con búsqueda, filtros y orden.
  - CA:
    - GET /admin/users acepta q (email parcial), full_name (nombre parcial), role (admin|user), limit, offset, sortBy (id|email|full_name|role), sortOrder (asc|desc).
    - Devuelve lista de usuarios (UserOut) ordenados según sortBy/sortOrder; por defecto sortBy=id, sortOrder=asc.
    - Solo accesible con rol admin (403 si no).
  - DoD:
    - Filtros aplicados en la capa de datos.
    - Tests de filtros, orden y paginación.

- HU9 (3 pts): Como administrador, quiero listado paginado con total.
  - CA:
    - GET /admin/users/paged devuelve { items: UserOut[], total: number } con los mismos filtros y ordenamiento.
    - limit/offset determinan la página; total permite calcular páginas.
  - DoD:
    - Consistencia entre items y total.
    - Documentado en Swagger y colección Postman.

- HU10 (2 pts): Como administrador/front, quiero que el backend permita orígenes configurables y acceso por IP LAN.
  - CA:
    - CORS_ORIGINS configurable en .env; servidor escuchando en 0.0.0.0:8000.
    - Cambios en .env requieren reinicio del servidor.
  - DoD:
    - Variables de entorno documentadas.
    - Verificación de CORS y acceso cruzado.

Historias Técnicas
- HT9 (2 pts): Extender list_users (app/crud.py) para aceptar q, full_name, role, limit, offset, sort_by, sort_order, con mapeo seguro de columnas y orden por defecto id asc.
- HT10 (2 pts): Implementar count_users (app/crud.py) aplicando los mismos filtros para calcular el total con SQLAlchemy func.count.
- HT11 (2 pts): Añadir esquema UsersPaged (app/schemas.py) con items y total; incluir created_at en UserOut.
- HT12 (3 pts): Implementar get_user, update_user y delete_user (app/crud.py) con hashing de password y verificación de unicidad de email.
- HT13 (3 pts): Añadir endpoints GET/PUT/DELETE /admin/users/{user_id} (app/main.py), protegidos con get_current_admin; manejo de 404/400.
- HT14 (2 pts): Configuración CORS desde .env y arranque del servidor en 0.0.0.0 para acceso desde la red local.

Definición de Listo (DoR)
- Historias con CA claros incluyendo filtros/orden/paginación.
- Dependencias identificadas (JWT, roles, DB, CORS).
- Estimación y ejemplos de requests.

Definición de Hecho (DoD)
- Código implementado y revisado (CRUD admin, paginación, ordenamiento, filtros).
- Tests básicos en verde.
- Documentación en /docs actualizada.
- Postman actualizado con ejemplos.
- CORS y arranque en 0.0.0.0 validados.

Riesgos y supuestos
- Desajustes de CORS entre frontend y backend.
- Filtros con LIKE pueden requerir índices en email/full_name para alto volumen.
- Rol admin requerido; manejo correcto de 403.

Backlog del Sprint (prioridad)
- P0: HU6, HU7, HU8, HU9, HT9, HT10, HT11, HT12, HT13
- P1: HU10, HT14
- P2: Mejora de DX, logging y validaciones adicionales

Day List (10 días)
- Día 1: Diseñar esquemas (UserUpdate, UsersPaged) y actualizar UserOut con created_at.
- Día 2: Implementar funciones CRUD (get_user, update_user, delete_user) en app/crud.py.
- Día 3: Añadir endpoints admin GET/PUT/DELETE /admin/users/{user_id} en app/main.py.
- Día 4: Extender list_users con búsqueda, filtros y ordenamiento; pruebas.
- Día 5: Implementar count_users y endpoint /admin/users/paged.
- Día 6: Configurar CORS_ORIGINS en .env y host 0.0.0.0; verificación en LAN.
- Día 7: QA: pruebas end-to-end con Postman y /docs.
- Día 8: Hardening: mensajes de error, validaciones, manejo de límites.
- Día 9: Revisión de performance y posibles índices en DB.
- Día 10: Demo y retrospectiva.

Métricas sugeridas
- Latencia de endpoints de listado y total.
- Tasa de errores (4xx/5xx) por historia.
- Cobertura mínima de tests.

Entregables del Sprint 2
- CRUD admin completo (GET/POST/PUT/DELETE).
- Listado con filtros/orden y endpoint paginado con total.
- Esquemas actualizados (UserOut con created_at, UsersPaged).
- Configuración CORS y guía de arranque para acceso por IP LAN.