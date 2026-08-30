# Arquitectura — INFRATELCO Control de Asistencia

## Visión general

```
frontend/app.py  ──►  st.navigation (enruta por rol)
        │
        ▼
frontend/pages/*.py  ──►  backend/services/*  ──►  backend/repositories/*  ──►  Supabase (PostgreSQL)
                                  │
                                  ▼
                          backend/services/audit  (toda acción administrativa)
```

- **frontend/**: pantallas Streamlit. No contienen lógica de negocio ni acceden a la base
  de datos directamente — solo llaman a `backend/services`.
- **backend/services/**: reglas de negocio (unicidad, permisos, auditoría). Cada carpeta es
  un dominio (`auth`, `employees`, `company`, `audit`; en fases siguientes: `attendance`,
  `geolocation`, `notifications`).
- **backend/repositories/**: única capa que habla con Supabase. Si el día de mañana se
  cambia de motor de base de datos, solo se tocan estos archivos.
- **backend/models/**: objetos tipados (`Employee`, `User`, `CompanySettings`, `Role`) que
  viajan entre capas en vez de diccionarios sueltos.
- **backend/utils/**: utilidades transversales sin lógica de negocio — hashing de
  contraseñas, zona horaria, cliente de base de datos.

## Por qué esta separación

Es el mismo motivo por el que el encargo original pide carpetas separadas (sección 2):
poder reemplazar o probar una pieza (por ejemplo, el proveedor de Reverse Geocoding en la
Fase 2) sin tocar la lógica de asistencia ni las pantallas.

## Enrutamiento y seguridad de pantallas

`frontend/app.py` es el único punto de entrada. Usa `st.navigation`/`st.Page` (no el
autodescubrimiento clásico de la carpeta `pages/`) para que **ninguna pantalla de
administrador sea alcanzable sin pasar primero por la verificación de sesión y de rol**
que está al principio de ese archivo. Ver `documentation/security.md`.

## Límite conocido de la Fase 1

La sesión de usuario vive en `st.session_state`, que depende de la conexión activa del
navegador con el servidor Streamlit. Si el usuario cierra la pestaña o recarga con F5,
Streamlit puede iniciar una sesión de navegador nueva y se pide iniciar sesión de nuevo.
No es un descuido: es una limitación conocida de Streamlit que se dejó documentada para
resolver más adelante (por ejemplo, con una cookie firmada) si el usuario lo pide.
