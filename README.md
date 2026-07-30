# Nicho Landing Factory & CRM

Plataforma de generación automática de landing pages por nicho con CRM de gestión comercial para Emayon Forge.

## 🚀 Características
- **Fallback Inteligente por Rubro**: Asignación automática de categorías visuales (`gastronomia`, `automotriz`, `salud_belleza`, `retail`, `logistica`, `tecnologia`, etc.) mediante la función `inferir_categoria_por_rubro` cuando falla o no responde la IA.
- **Autenticación CRM**: Acceso controlado para usuarios de desarrollo (`DEV`).
- **Arquitectura Multiusuario VPS**: Configurado para permisos compartidos de equipo (`developers`).

## 🛠️ Instalación y Uso Local

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/gnunnari-emayon/landing_factory.git
   cd landing_factory
   ```

2. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   ```

3. Ejecutar las pruebas unitarias:
   ```bash
   python test_generator.py
   ```

4. Iniciar el servidor CRM:
   ```bash
   python app.py
   ```

## 🌲 Estrategia de Ramas
- `main`: Rama de producción desplegada en `https://crm.emayonforge.com/`.
- `develop`: Rama de integración para desarrollo continuo del equipo.
