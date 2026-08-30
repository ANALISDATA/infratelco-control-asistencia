# Power BI — INFRATELCO Control de Asistencia

**Estado: pendiente de construir con datos reales (Fase 4).** El diseño de base de datos
ya sigue, desde la Fase 1, la regla que Power BI necesita: **una fila de
`attendance_records` = una jornada de un empleado**, con columnas planas (latitud,
longitud, dirección, horas trabajadas) en vez de estructuras anidadas — ver
`documentation/database.md` y `documentation/technical-decisions.md`.

Este archivo se completará con instrucciones reales de conexión (vía el Excel exportado
en la Fase 4, o conexión directa a PostgreSQL) cuando esa fase esté construida y probada.
