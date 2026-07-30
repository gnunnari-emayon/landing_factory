# Contexto y Arquitectura del Proyecto: Nicho Landing Factory & CRM

## 📋 Resumen Ejecutivo
**Nicho Landing Factory & CRM** es una plataforma desarrollada para **Emayon Forge** orientada a la generación automatizada de landing pages personalizadas por nicho comercial, integrada con un CRM de gestión comercial.

El diferencial clave del sistema es su **Mecanismo de Fallback Inteligente por Rubro**: cuando una llamada a modelos de IA (OpenAI/Gemini) falla o no está disponible, la plataforma analiza semánticamente el nombre comercial y el rubro mediante expresiones regulares y diccionarios de palabras clave para asignar automáticamente una categoría visual optima.

---

## 🏗️ Estructura del Proyecto y Capas (Estándar Emayon Forge)

```
landing_factory/
├── backend/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuración central (Pydantic/EnvVars, credenciales CRM, puerto, DB)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Dataclasses y esquemas DTO (LandingRequest, LandingResponse)
│   ├── services/
│   │   ├── __init__.py
│   │   └── generator.py     # Motor de generación, palabras clave por nicho e inferencia por rubro
│   ├── routers/
│   │   ├── __init__.py
│   │   └── api.py           # Funciones de control HTTP y autenticación
│   └── main.py              # Aplicación FastAPI, montaje estático y plantillas Jinja2
├── frontend/
│   ├── css/
│   │   └── main.css         # Estilos globales, variables CSS por nicho y componentes UI
│   ├── js/
│   │   └── main.js          # Captura de eventos e interacción cliente
│   ├── scss/                # Fuentes SCSS pre-compiladas
│   └── templates/
│       ├── base.html        # Layout maestro
│       ├── index.html       # Landing comercial pública
│       ├── admin/
│       │   └── dashboard.html # Dashboard CRM para usuario DEV
│       └── partials/        # Componentes header y footer
├── tests/
│   └── test_generator.py    # Suite de pruebas unitarias con unittest
├── docs/
│   └── architecture.md      # Especificación modular
├── README.md
├── package.json
└── requirements.txt
```

---

## ⚙️ Componentes Principales y Lógica de Negocio

### 1. Motor de Inferencia por Rubro (`backend/services/generator.py`)
Soporta 9 categorías visuales principales mediante palabras clave predefinidas:
- `gastronomia`: café, bar, restaurante, pizzería, sushi, heladería, etc.
- `automotriz`: taller, mecánico, auto, lubricentro, repuestos, etc.
- `salud_belleza`: clínica, odontología, médica, estética, spa, peluquería, etc.
- `retail`: tienda, boutique, ropa, calzado, bazar, etc.
- `logistica`: fletes, transporte, mudanzas, envíos, distribuidora.
- `tecnologia`: software, sistemas, tech, app, ciberseguridad, nube.
- `servicios_hogar`: plomería, electricidad, pintura, refrigeración.
- `educacion`: instituto, academia, colegio, cursos, tutoría.
- `inmobiliaria`: propiedades, alquileres, bienes raíces.
- *Default Fallback*: `corporativo` (utilizado si no coincide ninguna palabra clave).

### 2. Endpoints y Controladores (`backend/main.py`)
- `GET /`: Landing page pública de presentación.
- `GET /admin/dashboard`: Panel de administración CRM para usuarios DEV.
- `POST /api/generate`: Endpoint API para procesar solicitudes de generación de landing page.

---

## 🔍 Análisis del Objeto Cliente Actual vs. Requerimientos para Demo Mejorada

### Objeto Cliente Actual (`LandingRequest` / `LandingResponse`)
Actualmente, el objeto cliente está limitado a datos de clasificación:
```python
class LandingRequest:
    nombre_negocio: str
    rubro: str

class LandingResponse:
    nombre_negocio: str
    rubro: str
    categoria_visual: str
    status: str = "success"
    fallback_aplicado: bool = False
```

### Diagnóstico de Limitaciones para la Demo:
1. **Falta de Contenido Generado de la Landing**: No se generan secciones como Hero (título, subtítulo), propuesta de valor, lista de servicios/productos destacados, llamado a la acción (CTA) ni testimonios.
2. **Falta de Datos de Contacto y Branding**: No almacena teléfono/WhatsApp, email, dirección, horario comercial ni paleta de colores personalizada.
3. **Ausencia de Vista Previa Dinámica / Plantilla de Landing**: El CRM en `/admin/dashboard` no permite visualizar la landing page interactiva generada para un cliente específico.
4. **CRM Simulado Sin Persistencia Dinámica**: El endpoint `/api/generate` no guarda en base de datos ni interactúa con la tabla del frontend en tiempo real.

---

## 🚀 Oportunidades para la Demo Mejorada
Para desplegar una **demo impactante (WOW factor)** que convenza a potenciales clientes o stakeholders, el objeto cliente debe expandirse para incluir:
- **Estructura de Landing Completa**: Título impactante, subtítulo, 3 servicios/productos destacados, propuesta de valor, botón de conversión a WhatsApp/Formulario.
- **Visualizador Interactivo de Landing**: Posibilidad de ver la landing page renderizada en tiempo real según la categoría visual asignada (`gastronomia`, `automotriz`, `salud_belleza`, etc.) con temas de color adaptativos.
- **Gestión CRM Integrada**: Formulario funcional que inserte en vivo el nuevo cliente en la lista interactiva, permitiendo filtrar por rubro, ver su estado comercial y previzualizar la landing generada en un modal o nueva pestaña.
