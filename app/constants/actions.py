"""
app/constants/actions.py
Constantes centralizadas para acciones, etiquetas y niveles de riesgo.
Elimina duplicación entre simulation.py y model.py (legacy).
"""

# ════════════════════════════════════════════════════════════════
# PHISHING
# ════════════════════════════════════════════════════════════════

PHISHING_ACTION_LABELS = {
    "click_link": "Abrió el enlace sospechoso",
    "reply": "Respondió el correo con información",
    "ignore": "Ignoró y eliminó el correo",
    "report": "Reportó el correo como phishing",
}

PHISHING_ACTION_DISPLAY = {
    "click_link": "Abrió el enlace",
    "reply": "Respondió el correo",
    "ignore": "Ignoró el correo",
    "report": "Reportó como phishing",
}

# ════════════════════════════════════════════════════════════════
# CONTRASEÑAS (PASSWORD SCENARIOS)
# ════════════════════════════════════════════════════════════════

PASSWORD_ACTION_LABELS = {
    "choose_strong": "Eligió la contraseña más fuerte",
    "choose_common": "Eligió una contraseña común o predecible",
    "use_name": "Eligió usar nombre y año",
    "reuse_old": "Reutilizó una contraseña anterior",
    "use_manager": "Usó un gestor para generar contraseña aleatoria",
    "increment_year": "Solo cambió el año al final de la contraseña",
    "reuse": "Reutilizó exactamente la misma contraseña",
    "use_personal": "Usó información personal como contraseña",
    "refuse_and_report": "Se negó a compartir y escaló a TI",
    "share_whatsapp": "Compartió la contraseña por WhatsApp",
    "share_verbal": "Dijo la contraseña en persona",
    "create_temp": "Creó una contraseña temporal por su cuenta",
}

# ════════════════════════════════════════════════════════════════
# MAPA DE RIESGO UNIFICADO
# ════════════════════════════════════════════════════════════════

RISK_MAP = {
    # Phishing
    "click_link": "alto",
    "reply": "medio",
    "ignore": "bajo",
    "report": "bajo",
    # Contraseñas — acciones correctas
    "choose_strong": "bajo",
    "use_manager": "bajo",
    "refuse_and_report": "bajo",
    # Contraseñas — acciones incorrectas
    "choose_common": "alto",
    "use_name": "alto",
    "reuse_old": "alto",
    "increment_year": "medio",
    "reuse": "alto",
    "use_personal": "alto",
    "share_whatsapp": "alto",
    "share_verbal": "alto",
    "create_temp": "medio",
}

# ════════════════════════════════════════════════════════════════
# LEGACY / COMPATIBILIDAD (model.py usaba ACTION_LABELS)
# ════════════════════════════════════════════════════════════════

# Alias para compatibilidad con código legacy que use ACTION_LABELS
ACTION_LABELS = PHISHING_ACTION_LABELS.copy()
ACTION_LABELS["open_email"] = "Abrió el enlace sospechoso"

# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def get_action_label(action: str, module: str = "phishing") -> str:
    """Obtiene la etiqueta legible para una acción según el módulo."""
    if module == "phishing":
        return PHISHING_ACTION_LABELS.get(action, action)
    if module == "passwords":
        return PASSWORD_ACTION_LABELS.get(action, action)
    return action


def get_action_display(action: str, module: str = "phishing") -> str:
    """Obtiene la etiqueta corta para mostrar en UI."""
    if module == "phishing":
        return PHISHING_ACTION_DISPLAY.get(action, action)
    return PASSWORD_ACTION_LABELS.get(action, action)


def get_risk_level(action: str) -> str:
    """Obtiene el nivel de riesgo para una acción."""
    return RISK_MAP.get(action, "medio")


def is_phishing_action(action: str) -> bool:
    """Verifica si la acción pertenece al módulo phishing."""
    return action in PHISHING_ACTION_LABELS


def is_password_action(action: str) -> bool:
    """Verifica si la acción pertenece al módulo passwords."""
    return action in PASSWORD_ACTION_LABELS