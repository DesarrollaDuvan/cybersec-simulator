# app/data/__init__.py
# Carga de datos desde archivos YAML

import os
from typing import Any
import yaml

_SCENARIOS_CACHE: dict[str, list[dict]] = {}
_DATA_DIR = os.path.join(os.path.dirname(__file__), "scenarios")


def load_scenarios(filename: str) -> list[dict]:
    """Carga escenarios desde un archivo YAML con cache."""
    if filename in _SCENARIOS_CACHE:
        return _SCENARIOS_CACHE[filename]

    filepath = os.path.join(_DATA_DIR, filename)
    if not os.path.exists(filepath):
        return []

    with open(filepath, encoding="utf-8") as f:
        data = yaml.safe_load(f) or []

    _SCENARIOS_CACHE[filename] = data
    return data


def get_phishing_scenarios() -> list[dict]:
    return load_scenarios("phishing.yaml")


def get_password_scenarios() -> list[dict]:
    return load_scenarios("passwords.yaml")


def get_social_scenarios() -> list[dict]:
    return load_scenarios("social_engineering.yaml")


def get_network_scenarios() -> list[dict]:
    return load_scenarios("networks.yaml")


def get_all_classic_scenarios() -> list[dict]:
    return get_phishing_scenarios() + get_password_scenarios()


def get_all_immersive_scenarios() -> list[dict]:
    return get_social_scenarios() + get_network_scenarios()


def get_scenario_by_id(scenario_id: str) -> dict | None:
    """Busca un escenario por ID en todos los archivos."""
    for filename in ["phishing.yaml", "passwords.yaml", "social_engineering.yaml", "networks.yaml"]:
        for scenario in load_scenarios(filename):
            if scenario.get("id") == scenario_id:
                return scenario
    return None


def get_random_scenario(module: str | None = None) -> dict | None:
    """Retorna un escenario aleatorio, opcionalmente filtrado por módulo."""
    import random

    if module == "phishing":
        scenarios = get_phishing_scenarios()
    elif module == "passwords":
        scenarios = get_password_scenarios()
    elif module == "social":
        scenarios = get_social_scenarios()
    elif module == "networks":
        scenarios = get_network_scenarios()
    elif module == "classic":
        scenarios = get_all_classic_scenarios()
    elif module == "immersive":
        scenarios = get_all_immersive_scenarios()
    else:
        scenarios = get_all_classic_scenarios() + get_all_immersive_scenarios()

    return random.choice(scenarios) if scenarios else None


def clear_cache() -> None:
    """Limpia el cache (útil para tests)."""
    _SCENARIOS_CACHE.clear()