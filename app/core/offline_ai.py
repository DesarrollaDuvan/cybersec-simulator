import random

# Base de conocimiento
KNOWLEDGE = {
    "phishing": [
        {
            "keywords": ["phishing", "correo falso", "email sospechoso", "link raro"],
            "response": lambda q: f"""
El phishing es un tipo de ataque donde intentan engañarte para que reveles información personal.

Por lo que mencionas: "{q}", hay señales típicas como enlaces sospechosos o urgencia en el mensaje.

Recomendación clave:
Nunca hagas clic en enlaces sin verificar el dominio real. Si tienes duda, entra manualmente al sitio oficial.
"""
        }
    ],
    "passwords": [
        {
            "keywords": ["contraseña", "password", "clave"],
            "response": lambda q: """
Una contraseña segura debe tener:

- Mínimo 12 caracteres
- Mezcla de mayúsculas, minúsculas, números y símbolos
- No usar información personal

Ejemplo seguro:
G7#kL9!pQ2@x

Consejo: usa un gestor de contraseñas para no tener que memorizarlas todas.
"""
        }
    ],
    "malware": [
        {
            "keywords": ["virus", "malware", "archivo sospechoso"],
            "response": lambda q: """
El malware es software malicioso que puede robar información o dañar tu sistema.

Señales comunes:
- Archivos desconocidos
- Programas que se instalan solos
- Lentitud repentina del sistema

Recomendación:
Instala un antivirus y no descargues archivos de fuentes no confiables.
"""
        }
    ]
}


def detect_intent(message: str):
    message = message.lower()

    for category, items in KNOWLEDGE.items():
        for item in items:
            for keyword in item["keywords"]:
                if keyword in message:
                    return item

    return None


def generate_offline_response(message: str):
    intent = detect_intent(message)

    if intent:
        return intent["response"](message)

    # fallback inteligente
    generic_responses = [
        f"""
Interesante pregunta: "{message}"

Desde el punto de vista de ciberseguridad, siempre es importante:

- Verificar la fuente de la información
- No confiar en enlaces desconocidos
- Mantener tus sistemas actualizados

Si puedes dar más detalles, puedo ayudarte mejor.
""",
        """
En ciberseguridad, la prevención es clave.

Regla general:
Si algo parece sospechoso, probablemente lo es.

Evita compartir datos personales y verifica siempre antes de actuar.
"""
    ]

    return random.choice(generic_responses)