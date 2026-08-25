"""
app/routes/simulation_scenarios.py
6 simulaciones inmersivas:
  - 3 de Ingeniería Social (is_001, is_002, is_003)
  - 3 de Redes (net_001, net_002, net_003)

Cada escenario tiene pasos (stages) con decisiones y consecuencias.
"""

SOCIAL_ENGINEERING_SCENARIOS = [
    {
        "id": "is_001",
        "module": "social",
        "title": "El técnico de IT",
        "location": "Oficina — Bogotá",
        "description": "Es lunes por la mañana. Recibes una llamada inesperada.",
        "risk": "alto",
        "thumbnail": "📞",
        "stages": [
            {
                "id": "call_intro",
                "type": "phone_call",
                "caller": "Soporte Técnico — Ext. 4821",
                "avatar": "🧑‍💻",
                "transcript": [
                    {"role": "caller", "text": "Buenos días, le habla Carlos Méndez del departamento de soporte técnico. Estamos haciendo una actualización de seguridad urgente en todos los equipos de la empresa."},
                    {"role": "caller", "text": "Necesito que me confirme sus credenciales de acceso al sistema para verificar que su cuenta quede correctamente migrada antes de las 12 del mediodía, de lo contrario perderá acceso a sus archivos."},
                ],
                "choices": [
                    {"id": "give_creds",  "label": "Darle las credenciales — es urgente", "risk": "alto",  "icon": "ti-shield-off"},
                    {"id": "ask_verify",  "label": "Pedirle que se identifique primero",  "risk": "bajo",   "icon": "ti-id"},
                    {"id": "hang_up",     "label": "Colgar y llamar a IT directamente",   "risk": "bajo",   "icon": "ti-phone-off"},
                    {"id": "give_partial","label": "Dar solo el usuario, no la clave",    "risk": "medio",  "icon": "ti-alert-triangle"},
                ],
                "correct": "hang_up",
                "consequence_bad": "El atacante ahora tiene acceso completo a tu cuenta corporativa. En los siguientes 20 minutos accede a tus correos, documentos y transfiere $4.2M desde la cuenta de la empresa.",
                "consequence_good": "Correcto. Llamas al número oficial de IT y confirmas: nadie del equipo hizo esa llamada. Era un ataque de vishing. El número era falso.",
            },
            {
                "id": "followup_email",
                "type": "email",
                "sender": "it-soporte@empresa-col.net",
                "subject": "URGENTE: Completa la verificación de seguridad",
                "body": "Como acordamos por teléfono, necesitamos que hagas clic en el siguiente enlace para completar la migración de tu cuenta antes de las 12:00 m.",
                "link_text": "https://portal-empresa.com/seguridad/verificar",
                "link_real": "http://empresa-col.net.phish.ru/steal",
                "transcript": [],
                "choices": [
                    {"id": "click_link",   "label": "Hacer clic en el enlace",             "risk": "alto", "icon": "ti-link"},
                    {"id": "hover_check",  "label": "Revisar la URL real antes de hacer clic", "risk": "bajo","icon": "ti-eye"},
                    {"id": "report_phish", "label": "Reportar el correo como phishing",    "risk": "bajo", "icon": "ti-flag"},
                ],
                "correct": "report_phish",
                "consequence_bad": "El enlace instala un keylogger silencioso. Todo lo que escribas desde ahora es enviado al atacante en tiempo real.",
                "consequence_good": "Excelente. El dominio del remitente era 'empresa-col.net' — no el dominio oficial. El enlace apuntaba a un servidor en Rusia.",
            }
        ]
    },
    {
        "id": "is_002",
        "module": "social",
        "title": "El USB abandonado",
        "location": "Parqueadero — Edificio corporativo",
        "description": "Llegas al trabajo y encuentras algo en el piso.",
        "risk": "alto",
        "thumbnail": "💾",
        "stages": [
            {
                "id": "find_usb",
                "type": "scene",
                "scene_text": "Mientras caminas hacia el ascensor del edificio, ves un USB en el piso. Tiene una etiqueta que dice: 'NÓMINAS Q3 — CONFIDENCIAL'. No hay nadie más en el parqueadero.",
                "transcript": [],
                "choices": [
                    {"id": "plug_in",        "label": "Conectarlo a tu PC para ver qué tiene",         "risk": "alto",  "icon": "ti-plug"},
                    {"id": "plug_personal",  "label": "Conectarlo a mi celular personal",              "risk": "alto",  "icon": "ti-device-mobile"},
                    {"id": "take_to_it",     "label": "Entregarlo a seguridad sin conectarlo",         "risk": "bajo",  "icon": "ti-shield-check"},
                    {"id": "leave_it",       "label": "Dejarlo en el piso — no es mi problema",       "risk": "medio", "icon": "ti-arrow-left"},
                ],
                "correct": "take_to_it",
                "consequence_bad": "El USB ejecuta automáticamente un script al conectarse. En 8 segundos instala un troyano de acceso remoto. El atacante ahora tiene control total de tu equipo.",
                "consequence_good": "Correcto. El equipo de seguridad analiza el USB: contenía un AutoRun malicioso diseñado para infectar el primer equipo donde se conectara. La trampa era deliberada.",
            },
            {
                "id": "colleague_pressure",
                "type": "conversation",
                "speaker": "Tu compañero Andrés",
                "avatar": "👨‍💼",
                "transcript": [
                    {"role": "speaker", "text": "¡Oye! Vi que encontraste ese USB. Yo lo conecté en mi laptop hace un momento para ver qué tenía. Creo que son los datos de nómina del trimestre anterior."},
                    {"role": "speaker", "text": "¿Tú lo conectaste también? Deberías hacerlo, todos necesitan ver esto."},
                ],
                "choices": [
                    {"id": "follow_colleague","label": "Si Andrés lo hizo, entonces está bien",   "risk": "alto",  "icon": "ti-users"},
                    {"id": "warn_colleague",  "label": "Advertir a Andrés y escalar a seguridad", "risk": "bajo",  "icon": "ti-alert"},
                    {"id": "ignore",          "label": "Ignorar y conectarlo yo también",         "risk": "alto",  "icon": "ti-eye-off"},
                ],
                "correct": "warn_colleague",
                "consequence_bad": "La presión social funcionó. Conectas el USB. El malware se propaga ahora a tu equipo. Dos máquinas infectadas en el mismo edificio.",
                "consequence_good": "Correcto. La presión de grupo es una táctica clásica. Andrés tampoco lo conectó — era parte de la prueba. Reportas el incidente a tiempo.",
            }
        ]
    },
    {
        "id": "is_003",
        "module": "social",
        "title": "El mensaje de WhatsApp",
        "location": "Tu teléfono — Cualquier lugar",
        "description": "Recibes un mensaje de un número desconocido.",
        "risk": "medio",
        "thumbnail": "💬",
        "stages": [
            {
                "id": "whatsapp_msg",
                "type": "chat_message",
                "sender": "+57 320 *** 4821",
                "avatar": "👤",
                "transcript": [
                    {"role": "sender", "text": "Hola! Soy tu jefe, el Dr. Ramírez. Estoy en una reunión y no puedo llamar."},
                    {"role": "sender", "text": "Necesito que hagas una transferencia urgente de $2.800.000 a este número de cuenta antes de las 3pm. Te explico todo después. Es para cerrar un contrato importante."},
                    {"role": "sender", "text": "Cuenta: 456-789-123 Bancolombia. Es MUY urgente."},
                ],
                "choices": [
                    {"id": "transfer",      "label": "Hacer la transferencia — el jefe lo pide", "risk": "alto",  "icon": "ti-credit-card"},
                    {"id": "call_boss",     "label": "Llamar al número REAL de mi jefe a verificar", "risk": "bajo","icon": "ti-phone"},
                    {"id": "ask_account",   "label": "Pedir más detalles por WhatsApp",          "risk": "medio", "icon": "ti-message"},
                    {"id": "ignore_msg",    "label": "Ignorar el mensaje",                        "risk": "medio", "icon": "ti-eye-off"},
                ],
                "correct": "call_boss",
                "consequence_bad": "Haces la transferencia. Minutos después llamas a tu jefe real y descubres que él no envió ningún mensaje. El dinero ya fue retirado. Es irrecuperable.",
                "consequence_good": "Tu jefe contesta y confirma que él no mandó ningún mensaje. Era un número clonado. CEO Fraud — el atacante había obtenido el nombre de tu jefe de LinkedIn.",
            },
            {
                "id": "fake_link",
                "type": "chat_message",
                "sender": "+57 320 *** 4821",
                "avatar": "👤",
                "transcript": [
                    {"role": "sender", "text": "Entiendo, disculpa la confusión 😅 Mira, al menos revisa este documento con los detalles del contrato del que te hablé:"},
                    {"role": "sender", "text": "https://docs-google.com-contrato2024.tk/ver"},
                ],
                "choices": [
                    {"id": "open_link",    "label": "Abrir el enlace — parece de Google Docs", "risk": "alto", "icon": "ti-link"},
                    {"id": "check_domain", "label": "Revisar el dominio — algo no cuadra",     "risk": "bajo", "icon": "ti-zoom-in"},
                    {"id": "block",        "label": "Bloquear el número y reportar",           "risk": "bajo", "icon": "ti-ban"},
                ],
                "correct": "block",
                "consequence_bad": "El enlace abre una página que imita Google Docs y pide tus credenciales de Google. Las ingresas. Tu cuenta de Gmail es comprometida en segundos.",
                "consequence_good": "Correcto. 'docs-google.com-contrato2024.tk' — el dominio real es '.tk', no google.com. El 'google.com' era parte del subdominio para engañar a simple vista.",
            }
        ]
    }
]

NETWORK_SCENARIOS = [
    {
        "id": "net_001",
        "module": "networks",
        "title": "WiFi gratis en el aeropuerto",
        "location": "Aeropuerto El Dorado — Bogotá",
        "description": "Tienes 2 horas de espera. Necesitas hacer una transacción bancaria.",
        "risk": "alto",
        "thumbnail": "✈️",
        "stages": [
            {
                "id": "airport_wifi",
                "type": "wifi_scan",
                "available_networks": [
                    {"ssid": "Aeropuerto_ElDorado_FREE",  "signal": 4, "lock": False, "safe": False, "note": "Sin contraseña — cualquiera puede unirse"},
                    {"ssid": "ElDorado_Oficial_5G",        "signal": 3, "lock": True,  "safe": True,  "note": "Red oficial del aeropuerto — requiere código del tiquete"},
                    {"ssid": "FREE_WIFI_VIP_LOUNGE",       "signal": 5, "lock": False, "safe": False, "note": "Red falsa creada por atacante — Evil Twin"},
                    {"ssid": "Tigo_4G_Hotspot_Personal",  "signal": 2, "lock": True,  "safe": True,  "note": "Tu propio hotspot móvil"},
                ],
                "transcript": [],
                "choices": [
                    {"id": "connect_free",    "label": "Conectarme a 'Aeropuerto_ElDorado_FREE'",  "risk": "alto",  "icon": "ti-wifi"},
                    {"id": "connect_vip",     "label": "Conectarme a 'FREE_WIFI_VIP_LOUNGE'",      "risk": "alto",  "icon": "ti-wifi"},
                    {"id": "connect_official","label": "Buscar la red oficial con contraseña",     "risk": "bajo",  "icon": "ti-lock"},
                    {"id": "use_mobile",      "label": "Usar mis datos móviles",                   "risk": "bajo",  "icon": "ti-signal-4g"},
                ],
                "correct": "use_mobile",
                "consequence_bad": "Te conectas. En la misma red hay un atacante ejecutando un ataque Man-in-the-Middle. Todo tu tráfico pasa por su laptop antes de llegar a internet.",
                "consequence_good": "Correcto. Tus datos móviles crean un canal cifrado directo a la red celular — sin intermediarios. Ningún atacante en el aeropuerto puede interceptarte.",
            },
            {
                "id": "mitm_attack",
                "type": "attack_visualization",
                "attack_type": "man_in_the_middle",
                "scene_text": "Decidiste conectarte a la red pública. Ahora vas a ver exactamente qué puede ver el atacante.",
                "captured_data": [
                    {"type": "credencial", "data": "usuario: juan.garcia@empresa.com",   "site": "webmail corporativo"},
                    {"type": "credencial", "data": "contraseña: ******* (capturada)",    "site": "webmail corporativo"},
                    {"type": "cookie",     "data": "SESSION_TOKEN=eyJhbGci...",          "site": "banco en línea"},
                    {"type": "datos",      "data": "Número tarjeta: 4532-XXXX-XXXX-8821","site": "tienda online"},
                ],
                "transcript": [],
                "choices": [
                    {"id": "disconnect",    "label": "Desconectarme inmediatamente",               "risk": "bajo",  "icon": "ti-wifi-off"},
                    {"id": "use_https",     "label": "Solo usar sitios con HTTPS — eso protege",  "risk": "medio", "icon": "ti-lock"},
                    {"id": "continue",      "label": "Continuar — no tengo nada importante",      "risk": "alto",  "icon": "ti-arrow-right"},
                ],
                "correct": "disconnect",
                "consequence_bad": "HTTPS cifra el contenido, pero en una red pública el atacante puede hacer SSL stripping — degradar la conexión a HTTP sin que notes diferencia visual.",
                "consequence_good": "Bien. Pero el daño puede ya estar hecho. La lección: nunca realizar transacciones sensibles en redes públicas, independientemente del candado HTTPS.",
            }
        ]
    },
    {
        "id": "net_002",
        "module": "networks",
        "title": "La red WiFi del vecino",
        "location": "Tu apartamento — Medellín",
        "description": "Tu internet falló. Ves que el WiFi del vecino no tiene contraseña.",
        "risk": "medio",
        "thumbnail": "🏠",
        "stages": [
            {
                "id": "neighbor_wifi",
                "type": "scene",
                "scene_text": "Son las 10pm, tienes que entregar un trabajo. Tu router falló. Ves la red 'NETLIFE_TORRES_5G' sin candado. Tu vecino de siempre, el señor Torres, seguro no tiene problema.",
                "transcript": [],
                "choices": [
                    {"id": "connect_use",   "label": "Conectarme y usar su red tranquilamente",  "risk": "alto",  "icon": "ti-wifi"},
                    {"id": "connect_ask",   "label": "Tocar su puerta y pedir permiso primero",  "risk": "bajo",  "icon": "ti-door"},
                    {"id": "use_mobile",    "label": "Usar datos móviles aunque sea más lento",  "risk": "bajo",  "icon": "ti-device-mobile"},
                    {"id": "wait",          "label": "Esperar a que el internet se recupere",    "risk": "bajo",  "icon": "ti-clock"},
                ],
                "correct": "use_mobile",
                "consequence_bad": "Acceder sin permiso a una red ajena es un delito en Colombia (Ley 1273). Pero además, el router del vecino puede tener configuración insegura — exponiéndote a otros en esa red.",
                "consequence_good": "Correcto. Aunque parece inofensivo, conectarse sin permiso es ilegal. Usar datos móviles protege tanto tu privacidad como la del vecino.",
            },
            {
                "id": "router_exposure",
                "type": "attack_visualization",
                "attack_type": "network_scan",
                "scene_text": "Imagina que te conectaste. Esto es lo que un atacante básico podría ver en esa red en menos de 2 minutos con herramientas gratuitas:",
                "captured_data": [
                    {"type": "dispositivo", "data": "iPhone 14 — Juan Torres",            "site": "192.168.1.2"},
                    {"type": "dispositivo", "data": "Smart TV Samsung — sin cifrado",     "site": "192.168.1.3"},
                    {"type": "dispositivo", "data": "Laptop HP — Windows 11",             "site": "192.168.1.4"},
                    {"type": "trafico",     "data": "DNS queries sin cifrar — historial completo de sitios visitados", "site": "todos los dispositivos"},
                ],
                "transcript": [],
                "choices": [
                    {"id": "understand",    "label": "Entendido — nunca más sin VPN en redes ajenas", "risk": "bajo", "icon": "ti-check"},
                    {"id": "ignore",        "label": "No me importa, no tengo nada que ocultar",      "risk": "alto", "icon": "ti-eye-off"},
                ],
                "correct": "understand",
                "consequence_bad": "'No tengo nada que ocultar' es una falacia. Tu historial de navegación, dispositivos y comportamiento son valiosos para atacantes y vendedores de datos.",
                "consequence_good": "Exacto. En cualquier red que no controles, una VPN cifra todo tu tráfico antes de salir al router — haciéndolo ilegible para cualquier interceptor.",
            }
        ]
    },
    {
        "id": "net_003",
        "module": "networks",
        "title": "Puerto abierto en la empresa",
        "location": "Empresa — Sistema remoto",
        "description": "Eres el administrador. Alguien configuró mal el servidor.",
        "risk": "alto",
        "thumbnail": "🖥️",
        "stages": [
            {
                "id": "port_scan_alert",
                "type": "terminal",
                "scene_text": "Recibes una alerta del sistema de monitoreo. Alguien está escaneando los puertos de tu servidor.",
                "terminal_output": [
                    "ALERTA DE SEGURIDAD — 14:23:07",
                    "IP origen: 185.220.101.47 (TOR exit node)",
                    "Escaneando puertos: 22, 23, 80, 443, 3389, 8080...",
                    "Puerto 3389 (RDP) — ABIERTO y EXPUESTO a internet",
                    "Puerto 22 (SSH) — ABIERTO, contraseña por defecto detectada",
                    "Intentos de login: admin/admin, root/root, administrator/123456",
                ],
                "transcript": [],
                "choices": [
                    {"id": "close_ports",   "label": "Cerrar puertos 3389 y 22 al exterior inmediatamente", "risk": "bajo",  "icon": "ti-lock"},
                    {"id": "block_ip",      "label": "Solo bloquear esa IP específica",                     "risk": "medio", "icon": "ti-ban"},
                    {"id": "monitor",       "label": "Solo monitorear — puede ser un falso positivo",       "risk": "alto",  "icon": "ti-eye"},
                    {"id": "do_nothing",    "label": "No hacer nada — el firewall lo manejará",             "risk": "alto",  "icon": "ti-circle"},
                ],
                "correct": "close_ports",
                "consequence_bad": "El escaneo era una prueba. 4 minutos después, un segundo atacante desde otra IP logra acceso por el puerto RDP con credenciales por defecto. El servidor es comprometido.",
                "consequence_good": "Correcto. Bloquear una IP no basta — hay miles de IPs de ataque. La solución es cerrar puertos innecesarios y usar VPN para acceso remoto.",
            },
            {
                "id": "breach_consequence",
                "type": "terminal",
                "scene_text": "Simulación: el servidor fue comprometido. Esto es lo que ocurre en las siguientes 48 horas:",
                "terminal_output": [
                    "Hora 0:00 — Atacante obtiene acceso como Administrador",
                    "Hora 0:15 — Descarga toda la base de datos de clientes (14.800 registros)",
                    "Hora 2:30 — Instala ransomware en modo silencioso",
                    "Hora 24:00 — Ransomware se activa: todos los archivos cifrados",
                    "Hora 24:01 — Nota de rescate: $85.000 USD en Bitcoin",
                    "Hora 48:00 — Datos de clientes publicados en foro de hackers",
                ],
                "transcript": [],
                "choices": [
                    {"id": "learn_harden",  "label": "Aprender a endurecer la configuración del servidor", "risk": "bajo", "icon": "ti-shield"},
                    {"id": "pay_ransom",    "label": "Pagar el rescate",                                   "risk": "alto", "icon": "ti-credit-card"},
                ],
                "correct": "learn_harden",
                "consequence_bad": "El 80% de las empresas que pagan el rescate vuelven a ser atacadas. Pagar no garantiza recuperar los datos y financia futuros ataques.",
                "consequence_good": "Correcto. Prevenir es más barato que recuperarse. Un servidor bien configurado con firewall, puertos mínimos y 2FA habría evitado todo esto.",
            }
        ]
    }
]

ALL_IMMERSIVE_SCENARIOS = SOCIAL_ENGINEERING_SCENARIOS + NETWORK_SCENARIOS

def get_immersive_scenario(scenario_id=None, module=None):
    if scenario_id:
        return next((s for s in ALL_IMMERSIVE_SCENARIOS if s["id"] == scenario_id), None)
    if module == "social":
        import random
        return random.choice(SOCIAL_ENGINEERING_SCENARIOS)
    if module == "networks":
        import random
        return random.choice(NETWORK_SCENARIOS)
    import random
    return random.choice(ALL_IMMERSIVE_SCENARIOS)
