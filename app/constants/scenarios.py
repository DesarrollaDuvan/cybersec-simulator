"""
app/constants/scenarios.py
Definiciones centralizadas de IDs de escenarios, módulos y niveles de riesgo.
"""

from enum import Enum


class ScenarioModule(str, Enum):
    PHISHING = "phishing"
    PASSWORDS = "passwords"
    SOCIAL = "social"
    NETWORKS = "networks"


class RiskLevel(str, Enum):
    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"


# IDs de escenarios clásicos (simulation.py)
CLASSIC_SCENARIO_IDS = {
    ScenarioModule.PHISHING: ["sc_001", "sc_002", "sc_003"],
    ScenarioModule.PASSWORDS: ["pw_001", "pw_002", "pw_003"],
}

# IDs de escenarios inmersivos (simulation_immersive.py)
IMMERSIVE_SCENARIO_IDS = {
    ScenarioModule.SOCIAL: ["is_001", "is_002", "is_003"],
    ScenarioModule.NETWORKS: ["net_001", "net_002", "net_003"],
}

ALL_SCENARIO_IDS = {
    **CLASSIC_SCENARIO_IDS,
    **IMMERSIVE_SCENARIO_IDS,
}

# Mapa de escenario -> módulo para lookup rápido
SCENARIO_MODULE_MAP = {}
for module, ids in ALL_SCENARIO_IDS.items():
    for sid in ids:
        SCENARIO_MODULE_MAP[sid] = module

# Mapa de escenario -> riesgo
SCENARIO_RISK_MAP = {
    # Phishing
    "sc_001": RiskLevel.ALTO,
    "sc_002": RiskLevel.MEDIO,
    "sc_003": RiskLevel.ALTO,
    # Passwords
    "pw_001": RiskLevel.ALTO,
    "pw_002": RiskLevel.MEDIO,
    "pw_003": RiskLevel.ALTO,
    # Social Engineering
    "is_001": RiskLevel.ALTO,
    "is_002": RiskLevel.ALTO,
    "is_003": RiskLevel.MEDIO,
    # Networks
    "net_001": RiskLevel.ALTO,
    "net_002": RiskLevel.MEDIO,
    "net_003": RiskLevel.ALTO,
}


def get_module_for_scenario(scenario_id: str) -> ScenarioModule | None:
    """Retorna el módulo al que pertenece un escenario."""
    return SCENARIO_MODULE_MAP.get(scenario_id)


def get_risk_for_scenario(scenario_id: str) -> RiskLevel | None:
    """Retorna el nivel de riesgo de un escenario."""
    return SCENARIO_RISK_MAP.get(scenario_id)


def get_all_scenario_ids(module: ScenarioModule | None = None) -> list[str]:
    """Retorna todos los IDs de escenarios, opcionalmente filtrados por módulo."""
    if module:
        return ALL_SCENARIO_IDS.get(module, [])
    all_ids = []
    for ids in ALL_SCENARIO_IDS.values():
        all_ids.extend(ids)
    return all_ids