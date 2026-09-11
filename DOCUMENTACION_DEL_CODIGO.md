# Documentación del Código - CyberTutor IA

## 📋 Tabla de Contenidos

1. [Visión General del Proyecto](#visión-general-del-proyecto)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura de Directorios](#estructura-de-directorios)
4. [Componentes Principales](#componentes-principales)
5. [Flujo de Ejecución Paso a Paso](#flujo-de-ejecución-paso-a-paso)
6. [Módulos y Funcionalidades](#módulos-y-funcionalidades)
7. [Base de Datos y Modelos](#base-de-datos-y-modelos)
8. [Integración con IA](#integración-con-ia)
9. [Guía de Uso](#guía-de-uso)

---

## 🎯 Visión General del Proyecto

**CyberTutor IA** es una plataforma educativa de ciberseguridad que combina:
- **Simulaciones interactivas** de phishing y gestión de contraseñas
- **Simulaciones inmersivas** multi-etapa de ingeniería social y redes
- **Quiz dinámico** con preguntas fijas y generadas por IA
- **Chat educativo** con asistencia de IA
- **Panel administrativo** para seguimiento de progreso

### Tecnologías Utilizadas

| Tecnología | Propósito |
|------------|-----------|
| Flask | Framework web principal |
| SQLAlchemy | ORM para base de datos |
| Flask-Login | Gestión de autenticación |
| SQLite | Base de datos |
| OpenRouter API | Integración con modelos de IA (DeepSeek, Llama) |
| Gemini API | Cliente alternativo de IA |
| YAML | Almacenamiento de escenarios |
| SSE (Server-Sent Events) | Streaming de respuestas de IA |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/CSS/JS)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │Dashboard │ │Simulación│ │   Quiz   │ │     Chat     │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (Flask - Python)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Rutas (Routes)                     │   │
│  │  /auth  /simulation  /quiz  /chat  /admin  /sim      │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Servicios (Services)                 │   │
│  │  QuizService | SimulationService | ImmersiveService  │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Capa de IA (AIClient Protocol)           │   │
│  │         OpenRouterClient | GeminiClient               │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Modelos (SQLAlchemy ORM)                │   │
│  │  User | QuizResult | SimulationResult | CourseVisit  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 DATOS Y CONFIGURACIÓN                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  SQLite DB   │  │ YAML Scenarios│  │    .env Config   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Directorios

```
/workspace
├── run.py                      # Punto de entrada principal
├── config.py                   # Configuración de la aplicación
├── requirements.txt            # Dependencias Python
├── database.db                 # Base de datos SQLite
├── .env                        # Variables de entorno (API keys)
│
├── app/
│   ├── __init__.py             # Factory pattern - create_app()
│   ├── extensions.py           # Inicialización de extensiones Flask
│   │
│   ├── models/                 # Modelos de datos
│   │   ├── user.py             # Modelo User (autenticación)
│   │   ├── progress.py         # QuizResult, SimulationResult, CourseVisit, SimulationProgress
│   │   └── result.py           # Modelo Result (legacy)
│   │
│   ├── routes/                 # Blueprints de rutas
│   │   ├── main.py             # Dashboard y páginas estáticas
│   │   ├── auth.py             # Login, registro, logout
│   │   ├── simulation.py       # Simulaciones clásicas (phishing, passwords)
│   │   ├── simulation_immersive.py  # Simulaciones inmersivas multi-etapa
│   │   ├── quiz.py             # Sistema de quiz
│   │   ├── chat.py             # Chat con IA
│   │   ├── admin.py            # Panel administrativo
│   │   └── results.py          # Vista de resultados (legacy)
│   │
│   ├── services/               # Lógica de negocio
│   │   ├── quiz_service.py     # Gestión de quizzes
│   │   ├── simulation_service.py    # Simulaciones clásicas
│   │   └── immersive_service.py     # Simulaciones inmersivas
│   │
│   ├── ai/                     # Integración con IA
│   │   ├── __init__.py         # Exportación de funciones y factory
│   │   ├── client.py           # Protocolo AIClient y fábrica
│   │   ├── openrouter_client.py     # Implementación OpenRouter
│   │   ├── gemini_client.py         # Implementación Gemini
│   │   └── prompts.py          # Templates de prompts para IA
│   │
│   ├── data/                   # Datos estáticos
│   │   ├── __init__.py         # Carga de escenarios YAML
│   │   └── scenarios/          # Archivos YAML con escenarios
│   │       ├── phishing.yaml
│   │       ├── passwords.yaml
│   │       ├── social_engineering.yaml
│   │       └── networks.yaml
│   │
│   ├── constants/              # Constantes compartidas
│   │   ├── actions.py          # Etiquetas de acciones y riesgos
│   │   ├── scenarios.py        # IDs y mapeo de escenarios
│   │   └── __init__.py
│   │
│   ├── core/                   # Núcleo (offline AI, etc.)
│   │   └── offline_ai.py
│   │
│   ├── templates/              # Plantillas HTML (no mostrado en detalle)
│   └── static/                 # Archivos estáticos (CSS, JS)
│
├── tests/                      # Tests unitarios e integración
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
└── migrations/                 # Migraciones de base de datos (Alembic)
```

---

## 🔧 Componentes Principales

### 1. Punto de Entrada (`run.py`)

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

**Propósito**: Inicia la aplicación Flask usando el patrón factory.

---

### 2. Factory de Aplicación (`app/__init__.py`)

**Función `create_app()`**:
1. Crea instancia Flask
2. Carga configuración desde `config.Config`
3. Inicializa extensiones (DB, Login, Migrate, CSRF, Cache)
4. Registra modelos dentro del contexto de app
5. Configura `login_manager.user_loader`
6. Crea tablas de base de datos
7. Registra todos los blueprints de rutas

```python
# Blueprints registrados:
/chat           → chat.py
/admin          → admin.py
/               → main.py
/auth           → auth.py
/simulation     → simulation.py
/sim            → simulation_immersive.py
/quiz           → quiz.py
```

---

### 3. Configuración (`config.py`)

La clase `Config` define:
- **SECRET_KEY**: Para sesiones seguras
- **SQLALCHEMY_DATABASE_URI**: Conexión a SQLite
- **ANTHROPIC_API_KEY**: (Legacy, actualmente usa OpenRouter/Gemini)
- **SESSION_COOKIE_***: Configuración de seguridad de sesiones
- **PERMANENT_SESSION_LIFETIME**: Duración de sesión (24 horas)

---

### 4. Extensiones (`app/extensions.py`)

Instancias singleton de extensiones Flask:
- `db`: SQLAlchemy (base de datos)
- `login_manager`: Flask-Login (autenticación)
- `migrate`: Flask-Migrate (migraciones DB)
- `csrf`: CSRFProtect (protección CSRF)
- `cache`: Flask-Caching (caché)

---

## 📊 Modelos de Datos

### User (`app/models/user.py`)

**Tabla**: `user`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | Primary key |
| email | String(100) | Email único |
| password | String(255) | Hash de contraseña |
| name | String(100) | Nombre del usuario |
| is_admin | Boolean | Rol de administrador |
| is_active | Boolean | Estado de cuenta |
| created_at | DateTime | Fecha de creación |
| last_login | DateTime | Último acceso |

**Propiedades calculadas**:
- `quiz_count`: Número de quizzes realizados
- `avg_quiz_score`: Promedio de puntajes
- `best_quiz_score`: Mejor puntaje
- `simulation_count`: Simulaciones completadas
- `simulation_correct`: Decisiones correctas
- `courses_visited`: Cursos visitados
- `overall_progress`: Progreso general (0-100%)

**Relaciones**:
- `quiz_results`: One-to-many con QuizResult
- `simulation_results`: One-to-many con SimulationResult
- `course_visits`: One-to-many con CourseVisit

---

### QuizResult (`app/models/progress.py`)

**Tabla**: `quiz_result`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key a user |
| score | Integer | Puntaje (0-100) |
| correct | Integer | Respuestas correctas |
| total | Integer | Total de preguntas |
| created_at | DateTime | Fecha del quiz |

---

### SimulationResult (`app/models/progress.py`)

**Tabla**: `simulation_result`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key a user |
| scenario_id | String(20) | ID del escenario |
| action_taken | String(30) | Acción del usuario |
| is_correct | Boolean | Si fue correcta |
| points | Integer | Puntos obtenidos |
| risk_level | String(10) | Nivel de riesgo (alto/medio/bajo) |
| created_at | DateTime | Fecha de decisión |

---

### CourseVisit (`app/models/progress.py`)

**Tabla**: `course_visit`

Registra visitas a módulos educativos:
- `user_id`: Usuario
- `course_id`: ID del curso (phishing, contraseña, ingenieria, redes)
- `visited_at`: Fecha de visita

---

### SimulationProgress (`app/models/progress.py`)

**Tabla**: `simulation_progress`

Para simulaciones inmersivas multi-etapa:
- `current_stage`: Etapa actual
- `completed_stages`: Lista JSON de etapas completadas
- `total_points`: Puntos acumulados
- `choices`: Diccionario JSON de decisiones por etapa
- `started_at`, `updated_at`, `completed_at`: Fechas de seguimiento

---

## 🛣️ Rutas y Endpoints

### Autenticación (`app/routes/auth.py`)

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/auth/login` | GET, POST | Inicio de sesión |
| `/auth/register` | GET, POST | Registro de usuario |
| `/auth/logout` | GET | Cerrar sesión |

**Flujo de Login**:
1. Verifica si usuario ya está autenticado
2. Obtiene email y password del formulario
3. Busca usuario en BD por email
4. Valida contraseña con `check_password_hash`
5. Verifica que cuenta esté activa
6. Actualiza `last_login`
7. Llama `login_user()` para crear sesión
8. Redirige a admin o home según rol

---

### Dashboard (`app/routes/main.py`)

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/` | GET | Dashboard principal (requiere login) |
| `/phishing` | GET | Módulo de phishing |
| `/contraseña` | GET | Módulo de contraseñas |
| `/ingenieria` | GET | Módulo de ingeniería social |
| `/redes` | GET | Módulo de redes |

---

### Simulaciones Clásicas (`app/routes/simulation.py`)

**Módulos**: Phishing y Contraseñas

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/simulation/` | GET | Selección de módulo |
| `/simulation/phishing` | GET | Inicia escenario phishing aleatorio |
| `/simulation/passwords` | GET | Inicia escenario contraseñas aleatorio |
| `/simulation/decision` | POST | Procesa decisión del usuario |
| `/simulation/decision/stream` | GET, POST | **SSE**: Stream de análisis de IA |
| `/simulation/trap/banco` | GET | Página trampa (click en enlace falso) |
| `/simulation/trap/netflix` | GET | Página trampa Netflix |
| `/simulation/phishing-caught` | GET | Página "caíste en phishing" |

**Flujo de Decisión**:
1. Obtiene acción del usuario y scenario_id
2. Busca escenario en datos YAML
3. Determina si acción es correcta (comparación directa)
4. Calcula puntos preliminarmente
5. Guarda `SimulationResult` en BD inmediatamente
6. Renderiza template con campos de IA vacíos
7. Frontend solicita stream SSE para llenar análisis de IA

**Streaming SSE**:
- Usa `Response` con `mimetype="text/event-stream"`
- Genera chunks JSON con tipo: `field`, `chunk`, `points`, `done`
- Permite mostrar respuesta de IA carácter por carácter

---

### Simulaciones Inmersivas (`app/routes/simulation_immersive.py`)

**Módulos**: Ingeniería Social y Redes

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/sim/` | GET | Home con lista de escenarios |
| `/sim/<scenario_id>` | GET | Inicia/reanuda simulación |
| `/sim/decision` | POST | Procesa decisión (JSON) |
| `/sim/<scenario_id>/results` | GET | Muestra resultados finales |

**Diferencias con simulaciones clásicas**:
- Multi-etapa (varias decisiones secuenciales)
- Guarda progreso intermedio en `SimulationProgress`
- Respuesta JSON en lugar de HTML
- Permite reanudar donde se dejó

---

### Quiz (`app/routes/quiz.py`)

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/quiz/` | GET | Pantalla de inicio |
| `/quiz/load` | POST | Carga preguntas (fijas + IA) |
| `/quiz/question/<index>` | GET | Muestra pregunta específica |
| `/quiz/question/<index>/json` | GET | Versión JSON de pregunta |
| `/quiz/answer` | POST | Envía respuesta |
| `/quiz/results` | GET | Muestra resultados finales |

**Flujo**:
1. Usuario inicia quiz
2. `QuizService.load_quiz()` selecciona 7 preguntas fijas + 3 de IA
3. Preguntas se guardan en sesión Flask
4. Usuario responde cada pregunta
5. `QuizService.submit_answer()` valida y guarda en sesión
6. Al finalizar, `calculate_results()` guarda en BD y calcula nivel

---

### Chat (`app/routes/chat.py`)

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/chat/` | GET | Interfaz de chat |
| `/chat/message` | POST | Envía mensaje a IA |
| `/chat/clear` | POST | Limpia historial |
| `/chat/status` | GET | Diagnóstico de conexión IA |

**System Prompt**: Define rol de "CyberTutor IA" como experto en ciberseguridad educativo.

**Flujo**:
1. Usuario envía mensaje
2. Recupera historial de sesión
3. Llama `chat_openrouter()` con historial + system prompt
4. Guarda respuesta en historial (máximo 20 mensajes)
5. Retorna respuesta JSON al frontend

---

### Administración (`app/routes/admin.py`)

**Requiere rol admin** (`@admin_required`)

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin/` | GET | Dashboard con estadísticas globales |
| `/admin/users` | GET | Lista de usuarios (paginada, con búsqueda) |
| `/admin/users/create` | GET, POST | Crear usuario |
| `/admin/users/<id>/edit` | GET, POST | Editar usuario |
| `/admin/users/<id>/toggle` | POST | Activar/desactivar usuario |
| `/admin/users/<id>/delete` | POST | Eliminar usuario |
| `/admin/users/<id>/reset-password` | POST | Resetear contraseña |
| `/admin/users/<id>/progress` | GET | Progreso detallado de usuario |
| `/admin/api/stats` | GET | API JSON para gráficas en tiempo real |

**Estadísticas Globales** (`get_global_stats()`):
- Total usuarios activos
- Total quizzes y simulaciones
- Promedio de puntajes
- Tasa de aciertos en simulaciones
- Nuevos usuarios últimos 7 días
- Distribución de puntajes (experto/avanzado/intermedio/principiante)
- Cursos más visitados
- Top 5 usuarios por mejor puntaje

**Cache**: `get_global_stats()` usa caché de 60 minutos para optimizar rendimiento.

---

## ⚙️ Servicios (Lógica de Negocio)

### QuizService (`app/services/quiz_service.py`)

**Responsabilidades**:
- Gestionar banco de 15 preguntas fijas
- Combinar con preguntas generadas por IA
- Validar respuestas
- Calcular resultados y niveles
- Guardar historial en BD

**Métodos principales**:

```python
load_quiz() → list
    # Selecciona 7 preguntas fijas aleatorias
    # Genera 3 preguntas con IA basadas en temas cubiertos
    # Fallback: usa preguntas fijas adicionales si IA falla
    # Guarda en sesión: questions, answers, current_index

get_question(index) → dict | None
    # Retorna pregunta por índice

submit_answer(question_id, answer) → dict
    # Valida respuesta
    # Guarda en sesión
    # Retorna: is_correct, correct_answer, explanation

calculate_results() → dict
    # Calcula score porcentual
    # Determina nivel (Experto/Avanzado/Intermedio/Principiante)
    # Guarda QuizResult en BD
    # Prepara detalle para template

get_user_stats(user_id) → dict
    # Estadísticas históricas del usuario
```

**Niveles de Quiz**:
| Score | Nivel | Mensaje |
|-------|-------|---------|
| ≥90 | Experto | ¡Excelente! Dominio sólido |
| ≥70 | Avanzado | Muy bien, sigue practicando |
| ≥50 | Intermedio | Vas por buen camino |
| <50 | Principiante | Hay oportunidad de mejorar |

---

### SimulationService (`app/services/simulation_service.py`)

**Responsabilidades**:
- Iniciar simulaciones aleatorias
- Procesar decisiones de usuario
- Registrar clicks en trampas de phishing
- Calcular estadísticas por módulo y riesgo

**Métodos principales**:

```python
start_simulation(module) → dict | None
    # Obtiene escenario aleatorio del módulo
    # Guarda scenario_id en sesión

process_decision(scenario_id, user_action) → dict
    # Obtiene escenario
    # Llama IA para análisis (analyze_phishing o analyze_password)
    # Determina si es correcto
    # Guarda SimulationResult en BD
    # Retorna: ai_analysis, ai_tip, points, risk_level, red_flags

register_trap_click(scenario_id, force) → bool
    # Registra cuando usuario hace click en enlace de phishing
    # Evita duplicados (a menos que force=True)

get_user_stats(user_id) → dict
    # Estadísticas por módulo (sc_, pw_, is_, net_)
    # Distribución por nivel de riesgo
```

**Lógica de Puntuación**:
- **Phishing**:
  - report correcto: 100 pts
  - report cuando era ignore: 90 pts
  - ignore correcto: 75 pts
  - reply: 25 pts
  - click_link: 0 pts

- **Contraseñas**:
  - Acción correcta: 100 pts
  - Acción incorrecta: 10 pts

---

### ImmersiveService (`app/services/immersive_service.py`)

**Responsabilidades**:
- Gestionar progreso multi-etapa
- Procesar decisiones secuenciales
- Calcular resultados finales

**Métodos principales**:

```python
get_or_create_progress(scenario_id) → SimulationProgress
    # Obtiene o crea registro de progreso

start_simulation(scenario_id) → dict | None
    # Verifica si ya completó (redirige a resultados)
    # Determina etapa inicial según progreso guardado
    # Retorna: scenario, stage_index, progress

process_decision(scenario_id, stage_id, choice_id) → dict | None
    # Obtiene info de stage y choice
    # Llama IA para análisis (analyze_immersive)
    # Actualiza progreso en BD
    # Determina siguiente stage
    # Retorna: verdict, explanation, lesson, points, has_next, next_stage

_update_progress(progress, stage_id, choice_id, points, is_correct, scenario)
    # Agrega stage a completed_stages
    # Guarda choice en diccionario choices
    # Acumula puntos
    # Actualiza current_stage o marca como completado

get_results(scenario_id) → dict | None
    # Calcula porcentaje de score
    # Retorna: scenario, total_points, max_points, score_pct

reset_progress(scenario_id) → bool
    # Elimina progreso para permitir rejugar
```

**Estructura de Escenario Inmersivo**:
```yaml
- id: "is_001"
  title: "Ingeniería Social - Llamada Falsa"
  stages:
    - id: "stage_1"
      scene_text: "Recibes una llamada..."
      choices:
        - id: "choice_a"
          label: "Verificar identidad"
      correct: "choice_a"
      consequence_good: "Evitas el fraude"
      consequence_bad: "Caes en el engaño"
```

---

## 🤖 Integración con IA

### Arquitectura de Clientes IA

**Patrón**: Protocol + Factory Pattern

```
┌─────────────────┐
│   AIClient      │ ← Protocolo (interface)
│   (Protocol)    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│Open  │ │Gemini   │
│Router│ │Client   │
│Client│ │         │
└───────┘ └─────────┘
```

### AIClient Protocol (`app/ai/client.py`)

Define métodos requeridos:
```python
analyze_phishing(scenario, user_action) → dict
analyze_password(scenario, user_action) → dict
analyze_phishing_stream(scenario, user_action) → generator
analyze_password_stream(scenario, user_action) → generator
analyze_immersive(scenario, stage, choice, is_correct) → dict
generate_quiz_questions(topics_covered) → list
chat(messages, system) → str
is_available() → bool
```

### AIClientFactory

Patrón Singleton para gestionar cliente activo:
```python
# Registro inicial (en app/ai/__init__.py)
AIClientFactory.register(OpenRouterClient)  # Por defecto

# Obtener instancia
client = AIClientFactory.get_client()
```

---

### OpenRouterClient (`app/ai/openrouter_client.py`)

**Proveedor**: OpenRouter API (acceso a múltiples modelos)

**Modelos configurados**:
- `openrouter/auto`: Router automático (primario)
- `meta-llama/llama-3.1-8b-instruct:free`: Fallback gratuito

**Características**:
- Fallback automático entre modelos
- Soporte streaming SSE
- Limpieza de bloques `<thinking>` (DeepSeek style)
- Parsing robusto de JSON (con regex fallback)

**Métodos clave**:

```python
_call_with_fallback(messages) → tuple[str, str]
    # Intenta modelos en orden
    # Retorna: (respuesta, modelo_usado)

_generate_json(prompt) → dict | list
    # Llama API con formato JSON
    # Limpia markdown (```)
    # Extrae JSON con regex si es necesario

_stream_json_result(prompt) → generator
    # Obtiene respuesta completa
    # Stream campo por campo (analysis, tip)
    # Formato SSE: data: {...}\n\n

chat(messages, system) → str
    # Agrega system prompt
    # Llama con fallback
    # Limpia razonamiento interno
```

---

### GeminiClient (`app/ai/gemini_client.py`)

**Proveedor**: Google Gemini API

**Modelo**: `gemini-2.0-flash` (rápido, gratuito en AI Studio)

**Características**:
- Dos modelos: texto normal + modo JSON
- System instructions nativas
- Historial de chat integrado

**Diferencias con OpenRouter**:
- Usa librería `google.generativeai`
- Soporta `system_instruction` nativamente
- Streaming simulado (obtiene completo, luego stream character-by-character)

---

### Prompts (`app/ai/prompts.py`)

Templates centralizados para consistencia:

#### PHISHING_ANALYSIS_PROMPT
```
ESCENARIO:
- Remitente: {sender}
- Asunto: {subject}
- Cuerpo: {body}
- Señales: {clues}
- Acción correcta: {correct_action}

DECISIÓN: {user_action_label}

Responde JSON:
{
  "analysis": "...",
  "tip": "...",
  "points": 0-100
}
```

#### PASSWORD_ANALYSIS_PROMPT
Similar pero enfocado en buenas prácticas de contraseñas.

#### IMMERSIVE_ANALYSIS_PROMPT
Para simulaciones multi-etapa:
```json
{
  "verdict": "correcto|incorrecto|parcial",
  "explanation": "...",
  "lesson": "...",
  "points": 0-100
}
```

#### QUIZ_GENERATION_PROMPT
Genera 3 preguntas nuevas basadas en temas cubiertos.

#### CHAT_SYSTEM
Define personalidad de CyberTutor IA:
- Experto en ciberseguridad
- Educativo y amigable
- Máximo 3-4 párrafos
- Sin tecnicismos innecesarios

---

### Funciones Helper (`app/ai/__init__.py`)

```python
get_ai_client() → AIClient
    # Retorna singleton registrado

analyze_phishing(scenario, user_action) → dict
    # Delegate al cliente activo

chat_openrouter(messages, system) → str
    # Usa OpenRouter específicamente (para chat)
```

---

## 📦 Datos y Escenarios

### Carga de Escenarios (`app/data/__init__.py`)

**Fuente**: Archivos YAML en `app/data/scenarios/`

**Cache**: Los escenarios se cachean en memoria para rendimiento.

**Funciones**:
```python
load_scenarios(filename) → list
    # Carga YAML con cache

get_scenario_by_id(scenario_id) → dict | None
    # Busca en todos los archivos YAML

get_random_scenario(module) → dict | None
    # Filtra por módulo y selecciona aleatorio
```

### Estructura de Escenarios YAML

#### Phishing (`phishing.yaml`)
```yaml
- id: "sc_001"
  module: "phishing"
  sender: "soporte@banco-seguro-col.net"
  subject: "⚠ Urgente: Su cuenta ha sido bloqueada"
  body: "..."
  link_display: "http://..."
  correct_action: "report"
  risk: "alto"
  clues:
    - "Dominio no coincide"
    - "Lenguaje de urgencia"
```

#### Contraseñas (`passwords.yaml`)
```yaml
- id: "pw_001"
  module: "passwords"
  title: "Crear contraseña nueva"
  context: "Debes crear contraseña para sistema..."
  clues:
    - "Opción A: usa nombre + año"
    - "Opción B: gestor de contraseñas"
  correct_action: "use_manager"
```

#### Ingeniera Social (`social_engineering.yaml`)
```yaml
- id: "is_001"
  title: "Llamada de soporte técnico"
  stages:
    - id: "stage_1"
      scene_text: "Suena el teléfono..."
      transcript:
        - speaker: "Llamador"
          text: "Hola, soy de Microsoft..."
      choices:
        - id: "choice_a"
          label: "Colgar y reportar"
        - id: "choice_b"
          label: "Seguir instrucciones"
      correct: "choice_a"
      consequence_good: "Evitas acceso remoto"
      consequence_bad: "Instalan malware"
```

---

## 🔐 Constantes (`app/constants/`)

### Actions (`actions.py`)

**PHISHING_ACTION_LABELS**:
```python
{
    "click_link": "Abrió el enlace sospechoso",
    "reply": "Respondió el correo",
    "ignore": "Ignoró el correo",
    "report": "Reportó como phishing"
}
```

**RISK_MAP**:
Mapea cada acción a nivel de riesgo (alto/medio/bajo).

### Scenarios (`scenarios.py`)

**Enum ScenarioModule**:
```python
PHISHING = "phishing"
PASSWORDS = "passwords"
SOCIAL = "social"
NETWORKS = "networks"
```

**ALL_SCENARIO_IDS**:
Diccionario con IDs válidos por módulo.

**SCENARIO_MODULE_MAP**:
Lookup rápido: `scenario_id → module`

---

## 🔄 Flujo de Ejecución Paso a Paso

### 1. Inicio de Aplicación

```
1. Ejecutar: python run.py
2. Importa create_app() desde app/__init__.py
3. create_app():
   a. Crea Flask(__name__)
   b. Carga config.Config
   c. Inicializa extensiones (db, login_manager, etc.)
   d. Dentro de app_context:
      - Importa modelos (User, SimulationProgress, etc.)
      - Configura user_loader
      - db.create_all()
   e. Registra blueprints
   f. Retorna app
4. app.run(debug=True) inicia servidor
```

---

### 2. Flujo de Registro de Usuario

```
1. Usuario visita /auth/register
2. auth.register() renderiza register.html
3. Usuario envía formulario (POST)
4. Valida:
   - email y password obligatorios
   - password ≥ 6 caracteres
   - email no existe
5. Crea User:
   - email (lowercase)
   - password (hash con generate_password_hash)
   - is_admin=False
   - is_active=True
6. Guarda en BD
7. Flash message: "Cuenta creada"
8. Redirige a /auth/login
```

---

### 3. Flujo de Login

```
1. Usuario visita /auth/login
2. Si ya autenticado → redirect home
3. Usuario envía credenciales
4. auth.login():
   a. Busca User por email
   b. Valida password con check_password_hash
   c. Verifica is_active
   d. Actualiza last_login
   e. login_user(user, remember)
   f. Si is_admin → redirect /admin/
      Si no → redirect /
```

---

### 4. Flujo de Simulación Clásica

```
1. Usuario visita /simulation/phishing
2. simulation.start_phishing():
   a. SimulationService.start_simulation("phishing")
      - get_random_scenario(module="phishing")
      - session["current_scenario"] = scenario["id"]
   b. Renderiza simulation.html con datos del escenario

3. Usuario selecciona acción (ej: "report")
4. POST a /simulation/decision
5. simulation.decision():
   a. Obtiene user_action y scenario_id
   b. get_scenario_by_id(scenario_id)
   c. Determina is_correct:
      - user_action == correct_action
      - O: report cuando correct_action es ignore → también correcto
   d. Calcula points (fallback local)
   e. Determina labels de acción (PHISHING_ACTION_DISPLAY)
   f. Guarda SimulationResult en BD:
      - user_id, scenario_id, action_taken
      - is_correct, points, risk_level
   g. Renderiza result.html con:
      - ai_analysis="" (vacío)
      - ai_tip="" (vacío)
      - points, user_action, correct_action, risk_level

6. Frontend detecta campos vacíos
7. Frontend llama GET a /simulation/decision/stream?action=report&scenario_id=sc_001
8. simulation.decision_stream():
   a. Obtiene scenario
   b. get_ai_client() → OpenRouterClient
   c. client.analyze_phishing_stream(scenario, user_action)
   d. Generator yield chunks SSE:
      - {"type": "field", "field": "analysis"}
      - {"type": "chunk", "content": "C"}
      - {"type": "chunk", "content": "a"}
      - ...
      - {"type": "field", "field": "tip"}
      - ...
      - {"type": "points", "content": 100}
      - {"type": "done"}
9. Frontend recibe chunks y actualiza DOM en tiempo real
```

---

### 5. Flujo de Quiz

```
1. Usuario visita /quiz/
2. Renderiza quiz.html con stage='start'

3. Usuario clickea "Iniciar Quiz"
4. POST a /quiz/load
5. quiz.load_quiz():
   a. QuizService.load_quiz()
      - random.sample(QUESTION_BANK, 7) → preguntas fijas
      - topics = [q["question"][:40] for q in fixed]
      - generate_quiz_questions(topics) → IA genera 3 preguntas
      - Si IA falla → fallback a preguntas fijas adicionales
      - Marca preguntas IA con ai_generated=True
      - session['quiz_questions'] = all_questions
      - session['quiz_answers'] = {}
      - session['quiz_current'] = 0
   b. Retorna JSON: {status: 'ok', total: 10}

6. Frontend redirige a /quiz/question/0

7. GET a /quiz/question/0
8. quiz.get_question(0):
   a. QuizService.get_question(0)
   b. Renderiza quiz.html con:
      - stage='question'
      - question, options, index, total

9. Usuario selecciona respuesta (ej: "B")
10. POST a /quiz/answer con JSON: {question_id: "q001", answer: "B"}
11. quiz.submit_answer():
    a. QuizService.submit_answer("q001", "B")
       - Busca pregunta por ID
       - Compara answer.upper() == correct
       - Guarda en session['quiz_answers']:
         {q001: {given: "B", correct: "B", is_correct: True}}
       - Retorna: {is_correct, correct_answer, explanation}

12. Frontend muestra explicación
13. Usuario clickea "Siguiente"
14. Repite pasos 7-13 hasta última pregunta

15. GET a /quiz/results
16. quiz.results():
    a. QuizService.calculate_results()
       - total = len(questions)
       - correct_count = sum(is_correct for each answer)
       - score = round((correct_count / total) * 100)
       - Determina nivel (Experto/Avanzado/Intermedio/Principiante)
       - Guarda QuizResult en BD
       - Prepara detail array con todas las preguntas
    b. Renderiza quiz.html con stage='results', score, level, detail
```

---

### 6. Flujo de Chat con IA

```
1. Usuario visita /chat/
2. chat.chat_view():
   a. session['chat_history'] = []
   b. Renderiza chat.html

3. Usuario escribe mensaje: "¿Qué es phishing?"
4. POST a /chat/message con JSON: {message: "¿Qué es phishing?"}
5. chat.send_message():
   a. Obtiene user_message
   b. history = session.get('chat_history', [])
   c. messages = history + [{"role": "user", "content": user_message}]
   d. chat_openrouter(messages, SYSTEM_PROMPT)
      - OpenRouterClient.chat(messages, system)
      - full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
      - _call_with_fallback(full_messages)
         - Intenta openrouter/auto
         - Si falla → meta-llama/llama-3.1-8b-instruct:free
      - _clean(response_text) → elimina <thinking>...</thinking>
   e. history.append({"role": "user", ...})
   f. history.append({"role": "assistant", "content": ai_message})
   g. session['chat_history'] = history[-20:] (máximo 20 mensajes)
   h. Retorna JSON: {response: ai_message}

6. Frontend muestra respuesta
7. Repite desde paso 3

8. Opcional: POST a /chat/clear
   - session['chat_history'] = []
```

---

### 7. Flujo de Simulación Inmersiva

```
1. Usuario visita /sim/
2. sim_immersive.home():
   a. get_social_scenarios() → carga social_engineering.yaml
   b. get_network_scenarios() → carga networks.yaml
   c. Renderiza sim_home.html con lista de escenarios

3. Usuario clickea escenario "is_001"
4. GET a /sim/is_001
5. sim_immersive.play("is_001"):
   a. ImmersiveService.start_simulation("is_001")
      - get_scenario_by_id("is_001")
      - get_or_create_progress("is_001")
         - Query SimulationProgress por user_id + scenario_id
         - Si no existe → crea nuevo registro
      - Si progress.is_completed → retorna {"completed": True}
      - stage_ids = [s["id"] for s in scenario["stages"]]
      - Si progress.current_stage existe → encuentra índice
        Si no → stage_index = 0
      - Retorna: {scenario, stage_index, progress}
   b. Si result["completed"] → redirect a results
   c. Renderiza sim_play.html con scenario y stage_index

6. Frontend muestra stage actual (scene_text, choices)
7. Usuario selecciona choice (ej: "choice_a")
8. POST a /sim/decision con JSON:
   {scenario_id: "is_001", stage_id: "stage_1", choice_id: "choice_a"}
9. sim_immersive.decision():
   a. ImmersiveService.process_decision("is_001", "stage_1", "choice_a")
      - get_scenario_by_id("is_001")
      - get_or_create_progress("is_001")
      - stage_info = stage con id "stage_1"
      - choice_info = choice con id "choice_a"
      - is_correct = (choice_id == stage_info["correct"])
      - analyze_immersive(scenario, stage_info, choice_info, is_correct)
         - OpenRouterClient.analyze_immersive(...)
         - format_immersive_prompt(...)
         - _generate_json(prompt) → {verdict, explanation, lesson, points}
      - _update_progress(progress, stage_id, choice_id, points, is_correct)
         - Agrega stage_id a completed_stages
         - choices[stage_id] = choice_id
         - total_points += points
         - current_stage = siguiente stage (o None si último)
         - Si último stage → completed_at = now
      - Determina has_next = (next_idx < len(stages))
      - Retorna JSON con:
        {verdict, explanation, lesson, points, total_points,
         is_correct, consequence, has_next, next_stage, next_index, completed}
   b. Retorna jsonify(result)

10. Frontend recibe JSON:
    - Si has_next=True → muestra siguiente stage
    - Si completed=True → redirect a /sim/is_001/results

11. GET a /sim/is_001/results
12. sim_immersive.results("is_001"):
    a. ImmersiveService.get_results("is_001")
       - scenario = get_scenario_by_id("is_001")
       - progress = SimulationProgress.query.filter_by(...)
       - total_pts = progress.total_points
       - max_pts = len(stages) * 100
       - score_pct = min(round(total_pts / max_pts * 100), 100)
       - Retorna: {scenario, total_points, max_points, score_pct, progress}
    b. Renderiza sim_results.html con resultados
```

---

### 8. Flujo Administrativo

```
1. Admin visita /admin/
2. auth.login() verifica is_admin=True → redirect /admin/

3. admin.dashboard():
   a. @admin_required verifica current_user.is_admin
   b. get_global_stats() (cacheado 60 min)
      - total_users = User.query.filter_by(is_admin=False).count()
      - active_users = ...filter_by(is_active=True).count()
      - total_quiz = QuizResult.query.count()
      - avg_score = func.avg(QuizResult.score)
      - correct_sims = SimulationResult.query.filter_by(is_correct=True).count()
      - new_users_week = User.query.filter(created_at >= week_ago).count()
      - Top 5 users por best_score (JOIN con QuizResult)
      - score_dist = distribución por rangos (experto, avanzado, etc.)
      - course_visits = COUNT por course_id (GROUP BY)
   c. Renderiza admin/dashboard_admin.html con stats

4. Admin visita /admin/users
5. admin.users():
   a. Obtiene ?q=search&page=2
   b. query = User.query.filter_by(is_admin=False)
   c. Si search → filter(email.ilike('%search%') | name.ilike(...))
   d. users_paginated = query.order_by(created_at.desc()).paginate(page=2, per_page=15)
   e. Renderiza admin/users_admin.html

6. Admin edita usuario /admin/users/5/edit
7. admin.edit_user(5):
   a. user = User.query.get_or_404(5)
   b. POST con nuevos datos
   c. user.name = request.form.get('name')
   d. user.email = request.form.get('email')
   e. user.is_active = bool(form.get('is_active'))
   f. Si password nuevo → user.password = generate_password_hash(new_password)
   g. db.session.commit()
   h. Redirect a /admin/users
```

---

## 💾 Base de Datos

### Esquema Completo

```sql
-- Tabla: user
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) DEFAULT '',
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

CREATE INDEX ix_user_admin_active ON user(is_admin, is_active);
CREATE INDEX ix_user_created_at ON user(created_at);
CREATE INDEX ix_user_last_login ON user(last_login);

-- Tabla: quiz_result
CREATE TABLE quiz_result (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    total INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE INDEX ix_quizresult_user_created ON quiz_result(user_id, created_at);
CREATE INDEX ix_quizresult_score ON quiz_result(score);

-- Tabla: simulation_result
CREATE TABLE simulation_result (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    scenario_id VARCHAR(20) NOT NULL,
    action_taken VARCHAR(30) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    points INTEGER DEFAULT 0,
    risk_level VARCHAR(10) DEFAULT 'medio',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE INDEX ix_simresult_user_created ON simulation_result(user_id, created_at);
CREATE INDEX ix_simresult_scenario_correct ON simulation_result(scenario_id, is_correct);
CREATE INDEX ix_simresult_user_scenario ON simulation_result(user_id, scenario_id);

-- Tabla: course_visit
CREATE TABLE course_visit (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id VARCHAR(30) NOT NULL,
    visited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE INDEX ix_coursevisit_user_course ON course_visit(user_id, course_id);
CREATE INDEX ix_coursevisit_visited_at ON course_visit(visited_at);

-- Tabla: simulation_progress
CREATE TABLE simulation_progress (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    scenario_id VARCHAR(20) NOT NULL,
    current_stage VARCHAR(30),
    completed_stages JSON DEFAULT '[]',
    total_points INTEGER DEFAULT 0,
    choices JSON DEFAULT '{}',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE INDEX ix_simprogress_user_scenario ON simulation_progress(user_id, scenario_id);
CREATE INDEX ix_simprogress_updated_at ON simulation_progress(updated_at);

-- Tabla: result (legacy)
CREATE TABLE result (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    outcome VARCHAR(50),
    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE INDEX ix_result_user_id ON result(user_id);
```

---

## 🔑 Variables de Entorno (.env)

```bash
# Clave secreta para sesiones Flask
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria

# API Keys para IA (al menos una requerida)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxx

# Entorno (production habilita SESSION_COOKIE_SECURE)
FLASK_ENV=development  # o production
```

---

## 🧪 Testing

### Tests Unitarios (`tests/unit/`)

- `test_quiz_service.py`: Prueba lógica de QuizService
- `test_simulation_service.py`: Prueba SimulationService
- `test_ai_clients.py`: Prueba clientes IA (mock de API)

### Tests de Integración (`tests/integration/`)

- `test_simulation_flow.py`: Flujo completo de simulación
- `test_auth_flow.py`: Registro, login, logout

### Fixtures (`tests/conftest.py`)

Configuración compartida:
- App en modo testing
- Base de datos temporal
- Cliente de test Flask

---

## 🚀 Despliegue

### Docker

**Dockerfile**: Construye imagen con Python, dependencias y app.

**docker-compose.yml**: Orquesta servicios:
- Web (Flask)
- (Opcional) Base de datos PostgreSQL (actualmente usa SQLite embebido)

### Producción

1. Configurar `.env` con SECRET_KEY segura
2. Establecer `FLASK_ENV=production`
3. Configurar API keys de IA
4. Usar servidor WSGI (Gunicorn/uWSGI) detrás de nginx
5. Habilitar HTTPS (requerido para SESSION_COOKIE_SECURE)

---

## 📝 Resumen de Características Clave

### Seguridad
- Hash de contraseñas con Werkzeug
- Protección CSRF en formularios
- Sesiones HTTP-only con SameSite=Lax
- Validación de roles (admin vs usuario)

### Rendimiento
- Cache de estadísticas globales (60 min)
- Cache de escenarios YAML en memoria
- Índices de base de datos optimizados

### Experiencia de Usuario
- Streaming SSE para respuestas de IA (efecto "typing")
- Progreso persistente en simulaciones multi-etapa
- Feedback inmediato con explicaciones educativas
- Niveles y puntuaciones gamificadas

### Extensibilidad
- Protocol AIClient permite cambiar proveedores de IA
- Escenarios en YAML (fáciles de editar/agregar)
- Servicios separados por responsabilidad
- Blueprints modulares por funcionalidad

---

## 📞 Soporte y Mantenimiento

### Agregar Nuevo Escenario
1. Editar archivo YAML correspondiente en `app/data/scenarios/`
2. Seguir estructura existente
3. Reiniciar app (o llamar `clear_cache()`)

### Agregar Nuevo Módulo de IA
1. Crear clase en `app/ai/nuevo_cliente.py`
2. Implementar protocolo `AIClient`
3. Registrar en `app/ai/__init__.py`: `AIClientFactory.register(NuevoClient)`

### Cambiar Modelos de IA
Editar `MODELS` lista en `app/ai/openrouter_client.py`

---

**Documentación creada para CyberTutor IA - Plataforma Educativa de Ciberseguridad**
