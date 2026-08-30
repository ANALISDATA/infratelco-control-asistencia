# INFRATELCO — Control de Asistencia

Sistema empresarial de control de asistencia, ingreso, salida y geolocalización para
**INFRATELCO — Ingeniería Eléctrica e Infraestructura**.

> **Estado actual: Fase 1 completada** (estructura, base de datos, autenticación, roles,
> gestión de empleados, configuración, auditoría). El registro de ingreso/salida con
> geolocalización todavía **no existe** — es la Fase 2. Ver el detalle de qué funciona
> hoy y qué falta al final de este archivo y en `documentation/`.

## Requisitos

- Python 3.11 o superior.
- Una cuenta gratuita de [Supabase](https://supabase.com) (base de datos).

## Instalación (primera vez)

1. **Crear el proyecto en Supabase** (gratis): [supabase.com](https://supabase.com) →
   *New project*. Guarda la contraseña de la base de datos en un lugar seguro.

2. **Configurar las credenciales de la app:**
   - Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml`.
   - En Supabase: *Project Settings → API* → copia *Project URL* y la clave
     **service_role** (no la `anon/public`) y pégalas en `secrets.toml`.

3. **Instalar dependencias y crear las tablas:**
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python Conectar_Supabase.py
   ```
   Si dice que faltan las tablas, copia el SQL que imprime en pantalla, pégalo en
   Supabase → *SQL Editor* → *New query* → *Run*, y vuelve a correr el comando.

4. **Crear el primer administrador:**
   ```
   python Crear_Administrador.py
   ```
   Pide correo y una contraseña temporal (mínimo 8 caracteres, con letras y números).

5. **Abrir la app:**
   ```
   streamlit run frontend/app.py
   ```
   O, en Windows, doble clic en **`▶ ABRIR LA APP.bat`** (crea el entorno automáticamente
   la primera vez).

## Primer ingreso

- Entra con el correo del administrador que creaste en el paso 4. La app pedirá cambiar
  la contraseña temporal antes de continuar — es obligatorio (regla de seguridad).
- Desde **Empleados**, crea al resto del personal. Cada empleado necesita un correo (se
  usa para su cuenta de acceso; puede iniciar sesión con ese correo **o** con su cédula).
  Al crearlo, la app muestra una contraseña temporal **una sola vez** — entrégasela al
  empleado en persona o por un canal seguro (todavía no se envía por correo/WhatsApp
  automáticamente, ver `documentation/notifications.md`).
- En **Configuración**, completa NIT, dirección, teléfono y correo corporativos (se
  dejaron vacíos a propósito: no existían en la carpeta de trabajo y no se inventaron).

## Qué funciona hoy (Fase 1) — probado

- Login por cédula o correo, con bloqueo tras 5 intentos fallidos.
- Cambio de contraseña obligatorio en el primer ingreso.
- Gestión de empleados: crear, editar, activar/desactivar, cédula y correo únicos.
- Configuración de empresa (horario, tolerancia, geolocalización, WhatsApp admin).
- Auditoría inmutable de toda acción administrativa.
- Identidad visual real de INFRATELCO (logo y colores tomados del logo original).

32 pruebas automáticas pasan (`python -m pytest tests/ -v`), incluyendo una prueba que
ejecuta la aplicación completa (framework oficial `AppTest` de Streamlit) y pruebas de
los flujos de login/bloqueo y creación de empleados contra una base de datos simulada.
**No se ha probado todavía contra un proyecto de Supabase real** porque no había
credenciales configuradas — hazlo siguiendo los pasos de instalación de arriba y avísame
si algo falla.

## Qué falta (fases siguientes, ver `documentation/technical-decisions.md`)

- **Fase 2**: registro de ingreso/salida, geolocalización, Reverse Geocoding, horarios,
  puntualidad, dashboard con indicadores del día.
- **Fase 3**: justificaciones, correcciones administrativas, histórico con filtros.
- **Fase 4**: Excel corporativo, Power BI.
- **Fase 5**: WhatsApp, email, resumen diario.

## Ejecutar las pruebas

```
.venv\Scripts\activate
python -m pytest tests/ -v
```

## Estructura del proyecto

Ver `documentation/architecture.md`.
