"""
diagnostico_gemini.py
Ejecuta este script desde la raíz del proyecto para identificar el problema:
    python diagnostico_gemini.py

Te dirá exactamente qué está fallando.
"""

import sys
import os

print("=" * 55)
print("  DIAGNÓSTICO GEMINI — CyberTutor IA")
print("=" * 55)

# ── 1. Verificar .env ────────────────────────────────────
print("\n[1] Cargando variables de entorno...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("    ✓ python-dotenv disponible")
except ImportError:
    print("    ✗ python-dotenv NO instalado → ejecuta: pip install python-dotenv")
    sys.exit(1)

api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    print("    ✗ GEMINI_API_KEY no encontrada en .env")
    print("      Asegúrate de que tu .env tenga:")
    print("      GEMINI_API_KEY=AIzaSy...")
    sys.exit(1)
elif not api_key.startswith("AIza"):
    print(f"    ⚠ GEMINI_API_KEY parece inválida (no empieza con 'AIza'): {api_key[:12]}...")
else:
    print(f"    ✓ GEMINI_API_KEY encontrada: {api_key[:12]}...")

# ── 2. Verificar librería ────────────────────────────────
print("\n[2] Verificando librería google-generativeai...")
try:
    import google.generativeai as genai
    print(f"    ✓ google-generativeai instalado")
except ImportError:
    print("    ✗ google-generativeai NO instalado")
    print("      Ejecuta: pip install google-generativeai")
    sys.exit(1)

# ── 3. Verificar __init__.py en app/ai/ ─────────────────
print("\n[3] Verificando estructura de carpetas...")
ai_dir   = os.path.join("app", "ai")
init_file = os.path.join(ai_dir, "__init__.py")

if not os.path.isdir(ai_dir):
    print(f"    ✗ Carpeta '{ai_dir}' no existe")
    os.makedirs(ai_dir, exist_ok=True)
    print(f"    → Carpeta '{ai_dir}' creada automáticamente")
else:
    print(f"    ✓ Carpeta '{ai_dir}' existe")

if not os.path.isfile(init_file):
    print(f"    ✗ '{init_file}' no existe (Python no reconoce la carpeta como módulo)")
    with open(init_file, "w") as f:
        f.write("")
    print(f"    → '{init_file}' creado automáticamente")
else:
    print(f"    ✓ '{init_file}' existe")

client_file = os.path.join(ai_dir, "gemini_client.py")
if not os.path.isfile(client_file):
    print(f"    ✗ '{client_file}' no existe — cópialo desde los archivos generados")
else:
    print(f"    ✓ '{client_file}' existe")

# ── 4. Probar conexión real con Gemini ───────────────────
print("\n[4] Probando conexión con la API de Gemini...")
try:
    genai.configure(api_key=api_key)
    model    = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Responde solo 'OK' en español.")
    text     = response.text.strip()
    print(f"    ✓ Conexión exitosa. Respuesta: '{text}'")
except Exception as e:
    error_str = str(e)
    print(f"    ✗ Error al conectar: {error_str}")

    if "API_KEY_INVALID" in error_str or "invalid" in error_str.lower():
        print("\n    → La API key es inválida.")
        print("      Ve a https://aistudio.google.com/app/apikey y genera una nueva.")
    elif "quota" in error_str.lower():
        print("\n    → Cuota agotada. Espera o revisa tu plan en Google AI Studio.")
    elif "not found" in error_str.lower() or "404" in error_str:
        print("\n    → Modelo no disponible. Prueba con 'gemini-1.5-flash' en gemini_client.py")
    elif "network" in error_str.lower() or "connection" in error_str.lower():
        print("\n    → Error de red. Verifica tu conexión a internet.")
    else:
        print("\n    → Error desconocido. Revisa el mensaje arriba.")
    sys.exit(1)

# ── 5. Probar respuesta JSON ─────────────────────────────
print("\n[5] Probando respuesta JSON...")
try:
    model_json = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={"response_mime_type": "application/json"}
    )
    resp = model_json.generate_content('Devuelve exactamente: {"status": "ok"}')
    import json
    parsed = json.loads(resp.text.strip())
    print(f"    ✓ JSON funciona correctamente: {parsed}")
except Exception as e:
    print(f"    ✗ Error en modo JSON: {e}")
    print("      El modo JSON puede no estar disponible en tu región o plan.")
    print("      Cambia en gemini_client.py la función ask_gemini_json() para no usar response_mime_type")

print("\n" + "=" * 55)
print("  DIAGNÓSTICO COMPLETO")
print("=" * 55)
print("Si todos los pasos muestran ✓, el problema está")
print("en la importación de gemini_client en chat.py.")
print("Verifica que chat.py tenga:")
print("  from app.ai.gemini_client import ask_gemini, history_to_gemini")
print("=" * 55)
