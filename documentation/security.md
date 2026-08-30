# Seguridad — INFRATELCO Control de Asistencia

## Contraseñas

- Hasheadas con **bcrypt** (`backend/utils/security.py`). Nunca se guarda ni se muestra
  una contraseña en texto plano — ni en base de datos, ni en logs, ni en pantalla (salvo
  la contraseña *temporal* que se le muestra una única vez al administrador al crear un
  empleado, para que se la entregue en persona; ver `documentation/technical-decisions.md`).
- Política mínima: 8 caracteres, al menos una letra y un número (`validar_fortaleza`).
- Cambio de contraseña obligatorio en el primer acceso y cada vez que un administrador
  restablece la clave de otro usuario (`must_change_password`).

## Sesiones

- Token aleatorio de 32 bytes (`secrets.token_urlsafe`), del cual solo se guarda su
  **hash SHA-256** en la tabla `sessions` — igual que con las contraseñas, si alguien
  lee la base de datos no puede reusar una sesión activa.
- Expiran a las `SESSION_TTL_HOURS` horas (`backend/config.py`), configurable sin tocar
  lógica de negocio.
- `cerrar_sesion()` revoca el token inmediatamente (no espera a que expire).

## Bloqueo por intentos fallidos

- Tras `MAX_FAILED_LOGIN_ATTEMPTS` (5) intentos fallidos seguidos, la cuenta se bloquea
  `LOGIN_LOCKOUT_MINUTES` (15) minutos. Se resetea a 0 en el siguiente login exitoso.
- El mensaje de error de login es **el mismo** exista o no el usuario, y sea la cédula/correo
  o la contraseña lo incorrecto (`MENSAJE_CREDENCIALES_INVALIDAS`) — evita que alguien
  pueda usar el formulario de login para averiguar qué cédulas existen en el sistema.

## Roles y acceso horizontal

- Dos roles (`admin`, `employee`) definidos en la tabla `roles` y en `backend/models.Role`.
- El enrutamiento en `frontend/app.py` decide qué páginas existen según el rol — un
  empleado nunca recibe siquiera las páginas de administrador en su navegación.
- Un empleado ve sus propios datos a través de `usuario.employee_id` — nunca recibe un ID
  de empleado que pueda manipular para ver a otra persona (eso se refuerza en la Fase 2,
  cuando el empleado empiece a consultar sus propios registros de asistencia).

## Auditoría

- `backend/services/audit/audit_service.py` es el único punto desde el que se escribe en
  `audit_logs`. Se registra en cada login exitoso, login fallido, cambio de contraseña,
  creación/edición/activación/desactivación de empleado y cambio de configuración.
- La tabla no tiene función de actualizar ni de borrar expuesta desde la aplicación
  (`audit_repository.py` solo define `registrar` y `listar`) — es inmutable para
  cualquier usuario, incluido el administrador, desde la interfaz.

## Pendiente para fases siguientes (documentado, no implementado todavía)

- **CSRF / rate limiting a nivel de red**: Streamlit no expone endpoints HTTP propios
  para formularios (todo corre sobre WebSocket de la propia sesión), por lo que el CSRF
  clásico de formularios web no aplica de la misma forma; se revisará si en una fase
  posterior se agrega una API HTTP separada (por ejemplo, para un webhook de WhatsApp).
- **HTTPS en producción**: lo provee la plataforma de despliegue (Streamlit Community
  Cloud sirve todo por HTTPS de forma nativa); si se despliega en un servidor propio,
  debe documentarse en `documentation/deployment.md` (Fase 4/5).
- **Rotación/expiración de tokens de recuperación de contraseña**: el backend ya soporta
  `password_resets` con expiración de `PASSWORD_RESET_TTL_MINUTES`, pero el flujo de
  autoservicio "olvidé mi contraseña" por correo requiere un proveedor de email conectado
  (Fase 5). Mientras tanto, el reseteo lo hace un administrador desde la app
  (`auth_service.restablecer_password_administrador`).
