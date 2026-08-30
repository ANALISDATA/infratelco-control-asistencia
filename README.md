# INFRATELCO — Control de Asistencia

Sistema empresarial de control de asistencia, ingreso, salida y geolocalización para
**INFRATELCO — Ingeniería Eléctrica e Infraestructura**.

> **Estado actual: Fases 1 y 2 completadas** (estructura, base de datos, autenticación,
> roles, empleados, configuración, auditoría, horarios, y el registro de ingreso/salida
> con geolocalización y Reverse Geocoding). Desplegada y funcionando en Streamlit
> Community Cloud. Ver el detalle de qué funciona hoy y qué falta al final de este
> archivo y en `documentation/`.

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

## Qué funciona hoy — probado

**Fase 1:**
- Login por cédula o correo, con bloqueo tras 5 intentos fallidos, sesión persistente
  (empleados no tienen que volver a loguearse cada día — 30 días; administradores 12h).
- Cambio de contraseña obligatorio en el primer ingreso.
- Gestión de empleados: crear, editar, activar/desactivar, cédula y correo únicos.
- Configuración de empresa (horario, tolerancia, geolocalización, WhatsApp admin).
- Auditoría inmutable de toda acción administrativa.
- Identidad visual real de INFRATELCO (logo y colores tomados del logo original).

**Fase 2:**
- Registro de ingreso/salida con geolocalización real (GPS del navegador) y dirección
  legible por Reverse Geocoding (Nominatim) — ver `documentation/geolocation.md`.
- Hora oficial siempre del servidor, nunca del celular del empleado.
- Puntualidad calculada según el horario asignado al empleado (o el predeterminado de
  la empresa si no tiene uno asignado), con tolerancia configurable.
- Horarios: crear/editar horarios con hora de entrada/salida y tolerancia por día de
  la semana, y asignarlos a cada empleado.
- Bloqueo de doble ingreso, doble salida, y salida sin ingreso.
- Cálculo automático de horas trabajadas.
- Dashboard con indicadores reales del día (ingresos, puntuales, tarde, no marcaron,
  sin salida) y gráficos de barras profesionales.
- Pantalla "Asistencia del día" para el administrador, con direcciones y coordenadas.

43 pruebas automáticas pasan (`python -m pytest tests/ -v`), incluyendo una prueba que
ejecuta la aplicación completa (framework oficial `AppTest` de Streamlit). El ciclo
completo de ingreso/salida, cálculo de horas, y los indicadores del dashboard ya se
probaron **contra la base de datos real** (no solo simulada) — ver
`documentation/geolocation.md` para el detalle de qué se probó y qué falta.

**No probado todavía:** el diálogo real del navegador pidiendo permiso de ubicación en
un celular real (no hay forma de simular eso desde aquí) — es lo primero que deberías
probar tú en la app ya desplegada.

## Qué falta (fases siguientes, ver `documentation/technical-decisions.md`)

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
