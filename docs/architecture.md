# Arquitectura del Sistema: Nicho Landing Factory & CRM

Este proyecto sigue la arquitectura empresarial modular de Emayon Forge (basada en el estándar de `organizacion-fem`).

## Estrategia de Capas (SOLID)

- **`backend/core/`**: Configuración centralizada, variables de entorno y utilidades transversales.
- **`backend/models/`**: Definición de esquemas de datos, DTOs y modelos declarativos.
- **`backend/services/`**: Lógica de negocio (algoritmos de inferencia, llamadas a IA, integraciones).
- **`backend/routers/`**: Controladores delgados HTTP y endpoints de API.
- **`frontend/`**: Plantillas HTML, estilos SCSS/CSS y scripts del cliente para el CRM.
- **`tests/`**: Suite automatizada de pruebas unitarias e integración.
- **`docs/`**: Documentación técnica del repositorio.
