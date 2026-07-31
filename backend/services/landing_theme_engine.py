import urllib.request
import urllib.parse
import json
import re

DEFAULT_ENTERPRISE_MODULES = [
    {
        "id": "pagos_online",
        "title": "Pasarela de Cobros Online Integrada",
        "desc": "Acepta MercadoPago, DLocal GO, tarjetas de débito/crédito y transferencias directo desde tu sitio.",
        "icon": "fa-credit-card",
        "tag": "Finanzas & Ventas"
    },
    {
        "id": "bot_whatsapp",
        "title": "Agente de IA 24/7 en WhatsApp",
        "desc": "Atención automática de consultas, cotizaciones y reservas vía WhatsApp incluso fuera de horario laboral.",
        "icon": "fa-robot",
        "tag": "Inteligencia Artificial"
    },
    {
        "id": "catalogo_ecommerce",
        "title": "Catálogo Interactivo con Carrito",
        "desc": "Muestra tu oferta de productos o servicios con precios, fotos, variaciones y pedidos directos.",
        "icon": "fa-shop",
        "tag": "Ventas Digitales"
    },
    {
        "id": "turnero_reservas",
        "title": "Motor de Reservas & Turnos Online",
        "desc": "Agendamiento automatizado sin solapamientos, sincronizado con calendarios y recordatorios por WhatsApp.",
        "icon": "fa-calendar-days",
        "tag": "Gestión Operativa"
    },
    {
        "id": "crm_analytics",
        "title": "CRM Integrado & Analítica de Leads",
        "desc": "Panel exclusivo de clientes para gestionar prospectos, historial de ventas y tasa de conversión.",
        "icon": "fa-chart-pie",
        "tag": "Gestión Comercial"
    },
    {
        "id": "dominio_ssl",
        "title": "Dominio Propio .COM + SSL Enterprise",
        "desc": "Infraestructura de servidor de alta velocidad CDN, certificado SSL y emails corporativos incluidos.",
        "icon": "fa-globe",
        "tag": "Infraestructura"
    }
]

THEMES_POR_CATEGORIA = {
    "gastronomia": {
        "bg": "#0c0908",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(245, 158, 11, 0.15)",
        "border_hover": "rgba(245, 158, 11, 0.35)",
        "glow": "rgba(245, 158, 11, 0.12)",
        "glow_secondary": "rgba(234, 88, 12, 0.06)",
        "accent": "#f59e0b",
        "accent_gradient": "from-amber-300 via-orange-400 to-amber-500",
        "font_display": "'Playfair Display', serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Gastronomía & Carta Digital",
        "cta_text": "Reservar Mesa / Pedir Ahora",
        "hours": "Lunes a Domingos: 11:30 - 00:30 hs",
        "features": [
            {"title": "Platos de Autor & Especialidades", "desc": "Carta variada elaborada con ingredientes seleccionados y recetas exclusivas del chef.", "icon": "fa-utensils", "tag": "Gastronomía"},
            {"title": "Carta Digital QR & Take Away", "desc": "Menú dinámico actualizable en tiempo real para consulta rápida y pedidos express.", "icon": "fa-qrcode", "tag": "Experiencia"},
            {"title": "Reservas de Mesa Garantizadas", "desc": "Asignación ágil de ubicaciones para almuerzos, cenas y celebraciones especiales.", "icon": "fa-chair", "tag": "Reservas"},
            {"title": "Catering & Eventos Privados", "desc": "Servicio integral de comida y banquetes adaptado a reuniones corporativas y sociales.", "icon": "fa-champagne-glasses", "tag": "Eventos"},
            {"title": "Envíos Express a Domicilio", "desc": "Despacho directo con empaquetado térmico para conservar la máxima frescura.", "icon": "fa-motorcycle", "tag": "Delivery"},
            {"title": "Promociones & Menú Ejecutivo", "desc": "Opciones especiales de mediodía y promociones en combos familiares.", "icon": "fa-tags", "tag": "Beneficios"}
        ],
        "news": [
            {"title": "Lanzamiento de nuestra Carta de Estación", "date": "Noticia Reciente", "snippet": "Incorporamos nuevas opciones gourmet y maridajes seleccionados para esta temporada.", "read_time": "2 min"},
            {"title": "Protocolo de Calidad & Frescura Certificada", "date": "Novedades del Sector", "snippet": "Conoce nuestro proceso de selección de ingredientes de proveedores locales.", "read_time": "3 min"},
            {"title": "Noche de Maridaje & Menú Pasos", "date": "Próximo Evento", "snippet": "Una experiencia culinaria única diseñada por nuestro equipo gastronómico.", "read_time": "2 min"}
        ],
        "reviews": [
            {"name": "Mariana Gómez", "comment": "Excelente atención y la calidad de la comida es insuperable. Un ambiente super cálido.", "rating": 5, "city": "Google Maps"},
            {"name": "Carlos Rodríguez", "comment": "El servicio de reservas funcionó perfecto. Los platos llegaron a tiempo y riquísimos.", "rating": 5, "city": "Cliente Verificado"},
            {"name": "Sofía Rossi", "comment": "Mi lugar favorito en la ciudad. Súper recomendable la carta digital y las sugerencias.", "rating": 5, "city": "Google Reviews"}
        ]
    },
    "automotriz": {
        "bg": "#070a12",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(59, 130, 246, 0.15)",
        "border_hover": "rgba(59, 130, 246, 0.35)",
        "glow": "rgba(59, 130, 246, 0.14)",
        "glow_secondary": "rgba(14, 165, 233, 0.06)",
        "accent": "#3b82f6",
        "accent_gradient": "from-blue-400 via-sky-400 to-indigo-400",
        "font_display": "'Oswald', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Taller Mecánico & Servicios Automotor",
        "cta_text": "Solicitar Turno en Taller",
        "hours": "Lunes a Viernes: 08:00 - 18:30 | Sábados: 08:00 - 13:00 hs",
        "features": [
            {"title": "Diagnóstico Computarizado Multimarca", "desc": "Escaneo electrónico avanzado de motor, frenos ABS, airbag y módulos de control.", "icon": "fa-microchip", "tag": "Tecnología"},
            {"title": "Mantenimiento Preventivo & Service", "desc": "Cambio de aceite, filtros, bujías y fluidos siguiendo especificaciones de fábrica.", "icon": "fa-wrench", "tag": "Service"},
            {"title": "Frenos, Suspensión & Tren Delantero", "desc": "Revisión integral y reemplazo de amortiguadores, discos, pastillas y cazoletas.", "icon": "fa-dharmachakra", "tag": "Seguridad"},
            {"title": "Mecánica Ligera & Pesada", "desc": "Reparaciones complejas de motor, embrague, transmisión y tapa de cilindros.", "icon": "fa-gears", "tag": "Especialistas"},
            {"title": "Repuestos Originales Garantizados", "desc": "Utilizamos componentes con garantía de fábrica para asegurar durabilidad.", "icon": "fa-shield-halved", "tag": "Garantía"},
            {"title": "Revisión Pre-Viaje Express", "desc": "Chequeo completo de 25 puntos críticos antes de salir a la ruta.", "icon": "fa-car-side", "tag": "Revisión"}
        ],
        "news": [
            {"title": "Importancia del Diagnóstico Escaneado Preventivo", "date": "Nota Técnica", "snippet": "Prevenir averías complejas mediante el escaneo a tiempo ahorra costos futuros.", "read_time": "3 min"},
            {"title": "Guía de Mantenimiento de Frenos y Suspensión", "date": "Consejos del Experto", "snippet": "Signos de desgaste que indican la necesidad de revisar tus pastillas y amortiguadores.", "read_time": "4 min"},
            {"title": "Nuevas Herramientas Computarizadas de Taller", "date": "Equipamiento", "snippet": "Incorporamos escáneres de última generación para vehículos de todas las marcas.", "read_time": "2 min"}
        ],
        "reviews": [
            {"name": "Ignacio Peralta", "comment": "Muy profesionales. Me explicaron el diagnóstico detallado antes de hacer el trabajo.", "rating": 5, "city": "Google Maps"},
            {"name": "Lucía Benítez", "comment": "El auto quedó impecable. El presupuesto fue claro y cumplieron con los tiempos.", "rating": 5, "city": "Cliente Verificado"},
            {"name": "Esteban Morales", "comment": "Excelente atención en taller. Altamente recomendables por la honestidad y rapidez.", "rating": 5, "city": "Google Reviews"}
        ]
    },
    "salud_belleza": {
        "bg": "#060f14",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(14, 165, 233, 0.15)",
        "border_hover": "rgba(14, 165, 233, 0.35)",
        "glow": "rgba(14, 165, 233, 0.12)",
        "glow_secondary": "rgba(20, 184, 166, 0.06)",
        "accent": "#0ea5e9",
        "accent_gradient": "from-sky-300 via-teal-300 to-cyan-400",
        "font_display": "'Outfit', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Centro de Salud & Bienestar",
        "cta_text": "Agendar Consulta Directa",
        "hours": "Lunes a Sábados: 09:00 - 20:00 hs",
        "features": [
            {"title": "Tratamientos Personalizados", "desc": "Evaluación previa diagnóstica para diseñar protocolos a medida según tu necesidad.", "icon": "fa-user-doctor", "tag": "Atención"},
            {"title": "Equipamiento de Alta Tecnología", "desc": "Procedimientos seguros utilizando aparatos modernos y certificados.", "icon": "fa-sparkles", "tag": "Innovación"},
            {"title": "Estética Facial & Corporal", "desc": "Rejuvenecimiento, limpieza profunda, dermoabrasión y moldeado corporal.", "icon": "fa-hand-holding-heart", "tag": "Estética"},
            {"title": "Salud Integral & Especialistas", "desc": "Equipo multidisciplinario comprometido con tu bienestar y seguridad.", "icon": "fa-heart-pulse", "tag": "Salud"},
            {"title": "Turnos Flexibles sin Esperas", "desc": "Sistema de agendamiento organizado para garantizar tu comodidad.", "icon": "fa-calendar-check", "tag": "Turnos"},
            {"title": "Ambiente Relax & Confort", "desc": "Espacios privados diseñados para brindar tranquilidad y privacidad.", "icon": "fa-spa", "tag": "Bienestar"}
        ],
        "news": [
            {"title": "Nuevos Tratamientos Faciales de Temporada", "date": "Novedades Salud", "snippet": "Descubre las técnicas más efectivas para mantener la piel hidratada y radiante.", "read_time": "3 min"},
            {"title": "Beneficios de la Atención Multidisciplinaria", "date": "Artículos de Salud", "snippet": "La combinación de estética y salud médica para resultados duraderos.", "read_time": "4 min"},
            {"title": "Cuidado Preventivo & Hábitos Saludables", "date": "Recomendaciones", "snippet": "Pequeños cambios cotidianos para potenciar los resultados de tus tratamientos.", "read_time": "2 min"}
        ],
        "reviews": [
            {"name": "Valeria Maidana", "comment": "Increíble la atención. Me sentí super cuidada desde la primera consulta.", "rating": 5, "city": "Google Maps"},
            {"name": "Claudia Fernández", "comment": "Los resultados superaron mis expectativas. Los profesionales son de primer nivel.", "rating": 5, "city": "Cliente Verificado"},
            {"name": "Camila Suárez", "comment": "Instalaciones limpias, modernas y puntualidad absoluta con los turnos.", "rating": 5, "city": "Google Reviews"}
        ]
    },
    "inmobiliaria": {
        "bg": "#0a0c10",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(234, 179, 8, 0.15)",
        "border_hover": "rgba(234, 179, 8, 0.35)",
        "glow": "rgba(234, 179, 8, 0.12)",
        "glow_secondary": "rgba(217, 119, 6, 0.06)",
        "accent": "#eab308",
        "accent_gradient": "from-amber-200 via-yellow-400 to-amber-500",
        "font_display": "'Cormorant Garamond', serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Bienes Raíces & Inversiones",
        "cta_text": "Consultar Propiedades",
        "hours": "Lunes a Viernes: 09:00 - 18:00 | Sábados: 09:30 - 13:00 hs",
        "features": [
            {"title": "Venta & Alquiler de Inmuebles", "desc": "Catálogo selecto de casas, departamentos, terrenos y locales comerciales.", "icon": "fa-building", "tag": "Propiedades"},
            {"title": "Tasaciones Profesionales de Mercado", "desc": "Evaluación precisa fundada en oferta real y métricas del sector inmobiliario.", "icon": "fa-chart-line", "tag": "Valuaciones"},
            {"title": "Asesoramiento Legal & Notarial", "desc": "Acompañamiento transparente en la confección de contratos y escrituración.", "icon": "fa-scale-balanced", "tag": "Legal"},
            {"title": "Desarrollos en Pozo & Inversiones", "desc": "Oportunidades de inversión en emprendimientos de alto potencial de plusvalía.", "icon": "fa-city", "tag": "Inversión"},
            {"title": "Administración de Alquileres", "desc": "Gestión integral de cobros, mantenimiento y atención de inquilinos.", "icon": "fa-key", "tag": "Gestión"},
            {"title": "Tours Virtuales & Asesoría Personal", "desc": "Visitas guiadas presenciales y contenido multimedia de alta resolución.", "icon": "fa-camera-retro", "tag": "Experiencia"}
        ],
        "news": [
            {"title": "Oportunidades de Inversión Inmobiliaria 2026", "date": "Análisis Inmobiliario", "snippet": "Zonas de mayor crecimiento y rentabilidad proyectada en el mercado local.", "read_time": "4 min"},
            {"title": "Guía Paso a Paso para la Compra de tu Primer Inmueble", "date": "Consejos Legales", "snippet": "Requisitos, documentación y claves para una operación segura y transparente.", "read_time": "5 min"},
            {"title": "Tendencias en Arquitectura Residencial Urbana", "date": "Novedades del Sector", "snippet": "Diseño funcional, sostenibilidad y eficiencia energética en nuevas propiedades.", "read_time": "3 min"}
        ],
        "reviews": [
            {"name": "Roberto Soria", "comment": "Vendieron mi propiedad en tiempo récord. La transparencia y el trato excelente.", "rating": 5, "city": "Google Maps"},
            {"name": "Gisela Maidana", "comment": "Nos asesoraron en todo el proceso de alquiler. Súper responsables y profesionales.", "rating": 5, "city": "Cliente Verificado"},
            {"name": "Marcelo Paz", "comment": "Gente honesta y con un conocimiento impecable del mercado inmobiliario.", "rating": 5, "city": "Google Reviews"}
        ]
    },
    "tecnologia": {
        "bg": "#090a16",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(99, 102, 241, 0.15)",
        "border_hover": "rgba(99, 102, 241, 0.35)",
        "glow": "rgba(99, 102, 241, 0.14)",
        "glow_secondary": "rgba(168, 85, 247, 0.06)",
        "accent": "#6366f1",
        "accent_gradient": "from-indigo-300 via-purple-400 to-sky-400",
        "font_display": "'Space Grotesk', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Soluciones Digitales & Tecnología",
        "cta_text": "Solicitar Propuesta Tech",
        "hours": "Lunes a Viernes: 09:00 - 18:00 hs (Atención Guardias 24/7)",
        "features": [
            {"title": "Desarrollo Web & Apps a Medida", "desc": "Plataformas digitales rápidas, responsivas y enfocadas en conversión.", "icon": "fa-code", "tag": "Desarrollo"},
            {"title": "Ciberseguridad & Protección de Datos", "desc": "Auditorías de seguridad, encriptación y blindaje contra amenazas.", "icon": "fa-shield-halved", "tag": "Seguridad"},
            {"title": "Infraestructura Nube & Servidores", "desc": "Migración y optimización en la nube para garantizar máxima disponibilidad.", "icon": "fa-server", "tag": "Cloud"},
            {"title": "Integraciones API & Automatización", "desc": "Conexión de sistemas, CRM, facturación y procesamiento automático.", "icon": "fa-diagram-project", "tag": "Sistemas"},
            {"title": "Soporte Técnico Especializado", "desc": "Asistencia técnica continua y resolución ágil de incidencias.", "icon": "fa-headset", "tag": "Soporte"},
            {"title": "Consultoría IT & Transformación", "desc": "Asesoramiento estratégico para digitalizar procesos clave de tu empresa.", "icon": "fa-lightbulb", "tag": "Estrategia"}
        ],
        "news": [
            {"title": "Inteligencia Artificial Aplicada a los Negocios", "date": "Tech Insights", "snippet": "Cómo la automatización con IA está aumentando la rentabilidad en empresas.", "read_time": "3 min"},
            {"title": "Buenas Prácticas de Ciberseguridad Corporativa", "date": "Seguridad Digital", "snippet": "Estrategias para proteger la información confidencial de tu organización.", "read_time": "4 min"},
            {"title": "Arquitecturas Cloud Escalables para PYMEs", "date": "Infraestructura", "snippet": "Ventajas de migrar servidores tradicionales a entornos cloud de alta eficiencia.", "read_time": "3 min"}
        ],
        "reviews": [
            {"name": "Federico Albarracín", "comment": "Desarrollaron nuestro sistema a medida con una calidad y rapidez increíble.", "rating": 5, "city": "Google Maps"},
            {"name": "Paula Domínguez", "comment": "Excelente soporte técnico. Resolvieron nuestro problema en el acto.", "rating": 5, "city": "Cliente Verificado"},
            {"name": "Hernán Romero", "comment": "Un equipo brillante. Lograron automatizar nuestros procesos comerciales al 100%.", "rating": 5, "city": "Google Reviews"}
        ]
    },
    "retail": {
        "bg": "#0d0914",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(236, 72, 153, 0.15)",
        "border_hover": "rgba(236, 72, 153, 0.35)",
        "glow": "rgba(236, 72, 153, 0.12)",
        "glow_secondary": "rgba(244, 63, 94, 0.06)",
        "accent": "#ec4899",
        "accent_gradient": "from-pink-300 via-rose-400 to-purple-400",
        "font_display": "'Outfit', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Comercio & Indumentaria",
        "cta_text": "Ver Catálogo / Comprar",
        "hours": "Lunes a Sábados: 09:00 - 20:30 hs",
        "features": [
            {"title": "Catálogo de Productos Actualizado", "desc": "Amplia selección de artículos con control de stock y fotos detalladas.", "icon": "fa-bag-shopping", "tag": "Productos"},
            {"title": "Venta Directa & Envíos Rápidos", "desc": "Despacho ágil a domicilio con opciones de pago contra entrega o tarjetas.", "icon": "fa-truck-fast", "tag": "Envíos"},
            {"title": "Atención & Asesoramiento Personalizado", "desc": "Recomendaciones a la medida para ayudarte a elegir el producto perfecto.", "icon": "fa-comments", "tag": "Atención"},
            {"title": "Garantía & Cambios Simples", "desc": "Política clara de cambios para comprar con total tranquilidad.", "icon": "fa-rotate-left", "tag": "Confianza"},
            {"title": "Ofertas & Descuentos Exclusivos", "desc": "Precios especiales en combos, fechas clave y promociones de temporada.", "icon": "fa-percent", "tag": "Promos"},
            {"title": "Múltiples Medios de Pago", "desc": "Pagos seguros en cuotas con débito, crédito y transferencias.", "icon": "fa-wallet", "tag": "Pagos"}
        ],
        "news": [
            {"title": "Nueva Colección & Tendencias de Temporada", "date": "Moda & Estilo", "snippet": "Descubre las últimas novedades y estilos que llegaron al local esta semana.", "read_time": "2 min"},
            {"title": "Guía para Elegir el Talle o Tamaño Perfecto", "date": "Consejos Útiles", "snippet": "Tips sencillos para asegurar que tu compra online calce justo como deseas.", "read_time": "3 min"},
            {"title": "Beneficios de Comprar Directo en el Negocio", "date": "Novedades Local", "snippet": "Atención personalizada, asesoramiento y descuentos exclusivos presenciales.", "read_time": "2 min"}
        ],
        "reviews": [
            {"name": "Camila Mansilla", "comment": "La ropa es hermosa y de excelente calidad. El envío llegó al día siguiente.", "rating": 5, "city": "Google Maps"},
            {"name": "Luciana Vega", "comment": "Atención muy amable por WhatsApp. Me ayudaron a elegir el talle exacto.", "rating": 5, "city": "Cliente Verificado"},
            {"name": "Gabriel Torres", "comment": "Excelente experiencia de compra. Todo muy prolijo y super recomendable.", "rating": 5, "city": "Google Reviews"}
        ]
    },
    "logistica": {
        "bg": "#090d12",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(16, 185, 129, 0.15)",
        "border_hover": "rgba(16, 185, 129, 0.35)",
        "glow": "rgba(16, 185, 129, 0.12)",
        "glow_secondary": "rgba(6, 182, 212, 0.06)",
        "accent": "#10b981",
        "accent_gradient": "from-emerald-300 via-teal-400 to-cyan-400",
        "font_display": "'Space Grotesk', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Logística & Transporte Express",
        "cta_text": "Cotizar Envío / Flete",
        "hours": "Lunes a Sábados: 07:30 - 19:30 hs",
        "features": [
            {"title": "Fletes & Mudanzas Urbanas", "desc": "Traslado seguro de cargas, mobiliario y paquetería con personal capacitado.", "icon": "fa-truck-ramp-box", "tag": "Transporte"},
            {"title": "Monitoreo & Seguimiento en Tiempo Real", "desc": "Control satelital de flotas para garantizar el arribo seguro a destino.", "icon": "fa-location-crosshairs", "tag": "Seguridad"},
            {"title": "Puntualidad & Tiempos Garantizados", "desc": "Compromiso estricto con los horarios acordados de carga y descarga.", "icon": "fa-clock", "tag": "Puntualidad"},
            {"title": "Cotización Inmediata sin Sorpresas", "desc": "Presupuestos claros calculados según volumen, peso y distancia.", "icon": "fa-calculator", "tag": "Cotización"},
            {"title": "Distribución Corporativa B2B", "desc": "Servicio diario para comercios, fábricas y distribuidores regionales.", "icon": "fa-boxes-stacked", "tag": "B2B"},
            {"title": "Embalaje Protegido & Carga Segura", "desc": "Protección especial para mercadería delicada durante el trayecto.", "icon": "fa-box-open", "tag": "Protección"}
        ],
        "news": [
            {"title": "Optimización de Rutas para Envíos Rápidos", "date": "Logística Moderna", "snippet": "Cómo reducimos tiempos de viaje y costos de transporte para nuestros clientes.", "read_time": "3 min"},
            {"title": "Claves para Planificar una Mudanza Exitosa", "date": "Guía Práctica", "snippet": "Consejos de embalaje y organización para un traslado rápido y seguro.", "read_time": "4 min"},
            {"title": "Modernización de Flotas & Seguridad Vial", "date": "Novedades Empresa", "snippet": "Incorporamos nuevas unidades equipadas para mayor capacidad de carga.", "read_time": "2 min"}
        ],
        "reviews": [
            {"name": "Martín Carrizo", "comment": "Hicimos la mudanza de la oficina y fueron extremadamente cuidadosos y puntuales.", "rating": 5, "city": "Google Maps"},
            {"name": "Clara Echeverría", "comment": "Los fletes son super confiables. Cotizaron al toque por WhatsApp y cumplieron.", "rating": 5, "city": "Cliente Verificado"},
            {"name": "Gonzalo Blanco", "comment": "Excelente servicio de distribución para nuestro negocio. 100% recomendable.", "rating": 5, "city": "Google Reviews"}
        ]
    },
    "servicios_hogar": {
        "bg": "#0a0c0e",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(249, 115, 22, 0.15)",
        "border_hover": "rgba(249, 115, 22, 0.35)",
        "glow": "rgba(249, 115, 22, 0.12)",
        "glow_secondary": "rgba(234, 179, 8, 0.06)",
        "accent": "#f97316",
        "accent_gradient": "from-orange-300 via-amber-400 to-orange-500",
        "font_display": "'Plus Jakarta Sans', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap",
        "badge": "Servicios Especializados para el Hogar",
        "cta_text": "Solicitar Servicio Técnico",
        "hours": "Atención Urgencias 24/7 | Regular: 08:00 - 20:00 hs",
        "features": [
            {"title": "Atención Rápida de Urgencias", "desc": "Respuesta inmediata para resolver problemas críticos en tu domicilio.", "icon": "fa-bolt", "tag": "Urgencias"},
            {"title": "Personal Calificado & Idóneo", "desc": "Técnicos especialistas con experiencia comprobada en cada especialidad.", "icon": "fa-screwdriver-wrench", "tag": "Técnicos"},
            {"title": "Presupuestos Transparentes", "desc": "Evaluación detallada de costos antes de iniciar cualquier reparación.", "icon": "fa-clipboard-check", "tag": "Presupuesto"},
            {"title": "Garantía Escrita de Trabajo", "desc": "Respaldamos cada intervención realizada para tu total tranquilidad.", "icon": "fa-shield-halved", "tag": "Garantía"},
            {"title": "Mantenimiento & Reformas", "desc": "Servicios de pintura, plomería, electricidad, gas y aire acondicionado.", "icon": "fa-house-gear", "tag": "Hogar"},
            {"title": "Materiales de Primera Calidad", "desc": "Trabajamos exclusivamente con insumos y repuestos homologados.", "icon": "fa-hammer", "tag": "Calidad"}
        ],
        "news": [
            {"title": "Consejos para Prevenir Averías Domésticas", "date": "Consejos Útiles", "snippet": "Mantenimiento preventivo sencillo para evitar sorpresas en cañerías y cables.", "read_time": "3 min"},
            {"title": "Mantenimiento de Aires Acondicionados en Verano", "date": "Servicio Técnico", "snippet": "Limpieza de filtros y carga de gas para optimizar el consumo de energía.", "read_time": "3 min"},
            {"title": "Cómo Detectar Fugas o Sobrecargas a Tiempo", "date": "Seguridad Hogar", "snippet": "Señales de alerta que indican cuándo contactar a un especialista matriculado.", "read_time": "4 min"}
        ],
        "reviews": [
            {"name": "Hernán Bravo", "comment": "Vinieron un domingo por una urgencia de plomería y lo solucionaron en 1 hora.", "rating": 5, "city": "Google Maps"},
            {"name": "Lorena Basualdo", "comment": "Super prolijos para trabajar. Hicieron la instalación eléctrica impecable.", "rating": 5, "city": "Cliente Verificado"},
            {"name": "Diego Peralta", "comment": "Honestidad y rapidez. Pasaron presupuesto antes de tocar nada y cobraron lo justo.", "rating": 5, "city": "Google Reviews"}
        ]
    },
    "educacion": {
        "bg": "#090a14",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(139, 92, 246, 0.15)",
        "border_hover": "rgba(139, 92, 246, 0.35)",
        "glow": "rgba(139, 92, 246, 0.12)",
        "glow_secondary": "rgba(99, 102, 241, 0.06)",
        "accent": "#8b5cf6",
        "accent_gradient": "from-violet-300 via-purple-400 to-indigo-400",
        "font_display": "'Outfit', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Formación & Educación Profesional",
        "cta_text": "Inscribirse / Solicitar Info",
        "hours": "Lunes a Viernes: 08:00 - 21:00 | Sábados: 09:00 - 14:00 hs",
        "features": [
            {"title": "Cursos & Programas Prácticos", "desc": "Capacitaciones enfocadas en habilidades aplicables al campo laboral.", "icon": "fa-graduation-cap", "tag": "Formación"},
            {"title": "Modalidad Presencial & Virtual", "desc": "Aulas interactivas y campus online adaptados a tus horarios.", "icon": "fa-laptop-code", "tag": "Modalidad"},
            {"title": "Docentes Experimentados", "desc": "Profesionales activos en la industria que comparten conocimiento real.", "icon": "fa-chalkboard-user", "tag": "Docentes"},
            {"title": "Certificación & Respaldo", "desc": "Acreditaciones que potencian tu currículum y perfil profesional.", "icon": "fa-certificate", "tag": "Certificados"},
            {"title": "Bolsa de Empleo & Pasantías", "desc": "Conexión directa con empresas e instituciones del sector.", "icon": "fa-briefcase", "tag": "Insertabilidad"},
            {"title": "Tutorías & Seguimiento Individual", "desc": "Acompañamiento pedagógico constante durante todo tu trayecto.", "icon": "fa-user-graduate", "tag": "Tutoría"}
        ],
        "news": [
            {"title": "Apertura de Inscripciones para Cursos 2026", "date": "Novedades Académicas", "snippet": "Conoce los nuevos programas de capacitación diseñados para este año.", "read_time": "3 min"},
            {"title": "Habilidades Profesionales Más Demandadas", "date": "Mercado Laboral", "snippet": "Análisis de las competencias más requeridas por empresas de la región.", "read_time": "4 min"},
            {"title": "Talleres & Workshops Gratuitos de Orientación", "date": "Eventos", "snippet": "Participa de nuestras charlas abiertas y descubre tu vocación profesional.", "read_time": "2 min"}
        ],
        "reviews": [
            {"name": "Andrea Cabrera", "comment": "Excelente la calidad del curso. Los profesores explican genial y con casos reales.", "rating": 5, "city": "Google Maps"},
            {"name": "Matías Ferreyra", "comment": "El campus virtual funciona bárbaro y el material de estudio es muy completo.", "rating": 5, "city": "Cliente Verificado"},
            {"name": "Natalia Ponce", "comment": "Gracias a la capacitación pude conseguir mi primer trabajo en el rubro.", "rating": 5, "city": "Google Reviews"}
        ]
    },
    "corporativo": {
        "bg": "#080b11",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(99, 102, 241, 0.15)",
        "border_hover": "rgba(99, 102, 241, 0.35)",
        "glow": "rgba(99, 102, 241, 0.12)",
        "glow_secondary": "rgba(59, 130, 246, 0.06)",
        "accent": "#6366f1",
        "accent_gradient": "from-indigo-300 via-blue-400 to-sky-400",
        "font_display": "'Plus Jakarta Sans', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap",
        "badge": "Servicios Profesionales & Comerciales",
        "cta_text": "Contactar con la Empresa",
        "hours": "Lunes a Viernes: 09:00 - 18:00 hs",
        "features": [
            {"title": "Excelencia & Calidad de Servicio", "desc": "Procesos estandarizados enfocados en superar las expectativas de cada cliente.", "icon": "fa-award", "tag": "Calidad"},
            {"title": "Atención Inmediata & Personalizada", "desc": "Respuesta ágil por múltiples canales directos de comunicación.", "icon": "fa-clock", "tag": "Atención"},
            {"title": "Trayectoria & Confianza Comprobada", "desc": "Años de experiencia respaldando la satisfacción de nuestra clientela.", "icon": "fa-thumbs-up", "tag": "Experiencia"},
            {"title": "Soluciones Integrales a Medida", "desc": "Propuestas adaptadas a las demandas específicas de tu proyecto.", "icon": "fa-sliders", "tag": "Soluciones"},
            {"title": "Asesoría Comercial Especializada", "desc": "Orientación experta para maximizar resultados y eficiencia de costos.", "icon": "fa-handshake", "tag": "Asesoría"},
            {"title": "Compromiso & Garantía Total", "desc": "Cumplimiento garantizado de plazos, acuerdos y condiciones comerciales.", "icon": "fa-shield-check", "tag": "Compromiso"}
        ],
        "news": [
            {"title": "Renovación de Infraestructura & Servicios", "date": "Novedades Empresa", "snippet": "Optimizamos nuestros procesos para brindar una atención aún más rápida.", "read_time": "2 min"},
            {"title": "Tendencias del Sector & Claves de Crecimiento", "date": "Visión Comercial", "snippet": "Cómo adaptarse a las nuevas exigencias del mercado manteniendo alta calidad.", "read_time": "3 min"},
            {"title": "Compromiso con la Satisfacción del Cliente", "date": "Cultura Corporativa", "snippet": "Nuestra filosofía centrada en construir relaciones de largo plazo.", "read_time": "2 min"}
        ],
        "reviews": [
            {"name": "Gonzalo Méndez", "comment": "Una empresa seria y súper responsable. La atención al cliente es impecable.", "rating": 5, "city": "Google Maps"},
            {"name": "Patricia Luna", "comment": "Muy satisfechos con el servicio recibido. Cumplieron con absolutamente todo.", "rating": 5, "city": "Cliente Verificado"},
            {"name": "Javier Bustos", "comment": "Gente honesta y profesional. Los recomendamos sin ninguna duda.", "rating": 5, "city": "Google Reviews"}
        ]
    }
}

def obtener_contexto_web_empresa(nombre: str, ciudad: str):
    """
    Extrae información real disponible en internet (DuckDuckGo / OSM)
    para alimentar la landing page con datos fidedignos del negocio.
    """
    ciudad_clean = ciudad.split(",")[0].strip()
    query = f"{nombre} {ciudad_clean}"
    
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}&kl=ar-es"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9"
    }
    
    resumen_encontrado = None
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            snippets = re.findall(r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
            for snip in snippets:
                clean_snip = re.sub(r'<[^>]+>', '', snip).strip()
                if len(clean_snip) > 30 and not any(bad in clean_snip.lower() for bad in ["duckduckgo", "wikipedia", "busco"]):
                    resumen_encontrado = clean_snip
                    break
    except Exception:
        pass

    return {
        "resumen_web": resumen_encontrado or f"Empresa referente en {ciudad_clean}, enfocada en brindar atención de excelencia y soluciones a medida."
    }

def obtener_theme_config(categoria: str) -> dict:
    """Devuelve la configuración estética y de contenidos armónica del rubro."""
    cat_clean = categoria.lower().strip() if categoria else "corporativo"
    theme = THEMES_POR_CATEGORIA.get(cat_clean, THEMES_POR_CATEGORIA["corporativo"]).copy()
    theme["enterprise_modules"] = DEFAULT_ENTERPRISE_MODULES
    return theme
