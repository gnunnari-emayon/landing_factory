# 🚀 Nicho Landing Factory & CRM — Multi-Proyecto Emayon Forge

Plataforma integral de generación automática de landing pages por nicho, CRM de gestión comercial, prospección B2B y arquitectura multi-servidor desacoplada para **Emayon Forge**.

---

## 🏛️ Arquitectura del Sistema (3 Proyectos Independientes)

El repositorio aloja **3 proyectos/servidores independientes** diseñados para ejecutarse en diferentes puertos locales, lo que permite desarrollo desacoplado, testing y aislamiento de bases de datos.

| Proyecto | Archivo "Cerebro" (Main Entry Point) | Puerto por Defecto | Base de Datos | Propósito Principal |
| :--- | :--- | :--- | :--- | :--- |
| **1. Nicho Landing (Padre)** | [`backend/main.py`](file:///Users/fgabrielbustos/Documents/Apps/emayon/nicho_landing_factory/backend/main.py) | **`8000`** *(o 8010)* | `crm_factory.db` / `factory_local.db` | Generador de Landings por Nicho, CRM Comercial, Prospector Google Maps y Motor de Inferencia por Rubro. |
| **2. Agencia Standalone** | [`agencia_standalone/standalone_server.py`](file:///Users/fgabrielbustos/Documents/Apps/emayon/nicho_landing_factory/agencia_standalone/standalone_server.py) | **`8005`** | Mocks / SQLite | Entorno aislado de desarrollo para la **Agencia CMS**, gestión de clientes, campañas y Focus Group con IA. |
| **3. Neumáticos Standalone** | [`neumaticos_standalone/standalone_server.py`](file:///Users/fgabrielbustos/Documents/Apps/emayon/nicho_landing_factory/neumaticos_standalone/standalone_server.py) | **`8011`** *(o 8000)* | `neumaticos_standalone.db` | ERP / POS / Taller AutoCentro, cotizador de neumáticos, turnero online, recepción y caja diaria. |

> [!NOTE]
> En la carpeta [`app/main.py`](file:///Users/fgabrielbustos/Documents/Apps/emayon/nicho_landing_factory/app/main.py) reside la versión monolítica extendida previa que registra todos los routers de la plataforma. Para el flujo de trabajo actual, el punto de entrada activo del Padre es `backend/main.py`.

---

## 🛠️ Instalación y Configuración Inicial

### 1. Clonar el repositorio y entrar al directorio:
```bash
git clone https://github.com/gnunnari-emayon/landing_factory.git
cd landing_factory
```

### 2. Crear y activar entorno virtual Python:
```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/macOS
# venv\Scripts\activate   # En Windows
```

### 3. Instalar dependencias backend y frontend:
```bash
pip install -r requirements.txt
npm install
```

### 4. Configurar variables de entorno:
```bash
cp .env.example .env
```
*(Editar `.env` inyectando credenciales de Google Places, DeepSeek, MercadoPago, etc.)*

---

## 🚀 Comandos de Ejecución Local (3 Servidores)

Puedes iniciar cada servidor de manera independiente en terminales separadas:

### 1️⃣ Proyecto Padre (Nicho Landing Factory & CRM) — Puerto 8000
```bash
npm run dev
# O ejecutando directamente uvicorn:
uvicorn backend.main:app --reload --port 8000
```
* 🌐 **Dashboard CRM**: `http://localhost:8000/`
* 🗺️ **Prospector Maps B2B**: `http://localhost:8000/prospector`
* 📑 **Swagger API Docs**: `http://localhost:8000/docs`

### 2️⃣ Agencia CMS Standalone — Puerto 8005
```bash
uvicorn agencia_standalone.standalone_server:app --reload --port 8005
```
* 🌐 **Agencia CMS**: `http://localhost:8005/agenciacms.html` o `http://localhost:8005/`
* 📑 **Swagger API Docs**: `http://localhost:8005/docs`
* 📘 Documentación detallada en [`agencia_standalone/AUDIT_AND_GUIDE.md`](file:///Users/fgabrielbustos/Documents/Apps/emayon/nicho_landing_factory/agencia_standalone/AUDIT_AND_GUIDE.md).

### 3️⃣ Neumáticos & AutoCentro Standalone — Puerto 8011
```bash
python -m uvicorn neumaticos_standalone.standalone_server:app --port 8011 --reload
```
* 🌐 **Portal AutoCentro**: `http://127.0.0.1:8011/`
* 🛒 **Cotizador & Tienda**: `http://127.0.0.1:8011/cotizador`
* 📅 **Turnero Online**: `http://127.0.0.1:8011/turnos`
* 🔐 **Login Admin**: `http://127.0.0.1:8011/login`
* 📘 Documentación detallada en [`neumaticos_standalone/AUDIT_AND_GUIDE_NEUMATICOS.md`](file:///Users/fgabrielbustos/Documents/Apps/emayon/nicho_landing_factory/neumaticos_standalone/AUDIT_AND_GUIDE_NEUMATICOS.md).

---

## ✨ Características Principales

- **Fallback Inteligente por Rubro**: Asignación automática de categorías visuales (`gastronomia`, `automotriz`, `salud_belleza`, `retail`, `logistica`, `tecnologia`, etc.) mediante `inferir_categoria_por_rubro` ante fallas de llamadas a IA.
- **Prospector Google Maps B2B**: Scraping, geolocalización, enriquecimiento de teléfonos por código de país e importación masiva de prospectos.
- **Entorno Standalone desacoplado**: Permite probar interfaces complejas (React SPA / Jinja2) con datos *mock* y logins simplificados sin afectar el servidor padre.
- **Diseño SCSS Modular**: Estilos compilados con Sass siguiendo la [Guía de Desarrollo Visual](file:///Users/fgabrielbustos/Documents/Apps/emayon/nicho_landing_factory/docs/guia_desarrollo_visual.md).

---

## 📁 Estructura del Repositorio

```text
landing_factory/
├── backend/                        # LÓGICA CORE Y SERVIDOR PADRE
│   ├── main.py                     # [CEREBRO PADRE] Entry Point principal (Puerto 8000)
│   ├── core/                       # Configuración y conexión DB
│   ├── models/                     # Modelos ORM ProspectoB2BModel
│   ├── services/                   # Motor de inferencia, generador landing, prospección
│   └── routers/                    # Endpoints HTTP
├── agencia_standalone/             # MÓDULO INDEPENDIENTE AGENCIA CMS
│   ├── standalone_server.py        # [CEREBRO AGENCIA] Entry Point Standalone (Puerto 8005)
│   ├── templates/                  # Frontend agenciacms.html / agencia_services.html
│   ├── routers/                    # Endpoints de agencia
│   └── AUDIT_AND_GUIDE.md          # Guía de auditoría y uso de Agencia
├── neumaticos_standalone/          # MÓDULO INDEPENDIENTE NEUMÁTICOS & AUTOCENTRO
│   ├── standalone_server.py        # [CEREBRO NEUMÁTICOS] Entry Point Standalone (Puerto 8011)
│   ├── models.py                   # Modelos ORM ERP/Taller/Caja
│   ├── routers/                    # POS, taller, cotizador, cuentas corrientes
│   └── AUDIT_AND_GUIDE_NEUMATICOS.md # Guía de uso de AutoCentro
├── app/                            # Monolito backend extendido (Legacy/Integración)
│   └── main.py                     # Entry Point del monolito completo
├── frontend/                       # Vistas HTML, CSS compilado y SCSS
├── docs/                           # Documentación de arquitectura y guías visuales
├── package.json                    # Scripts npm (Sass y dev uvicorn)
└── requirements.txt                # Dependencias Python
```

---

## 🌲 Estrategia de Ramas

- **`main`**: Rama de producción desplegada en [crm.emayonforge.com](https://crm.emayonforge.com/).
- **`develop`**: Rama de integración para desarrollo continuo del equipo.
