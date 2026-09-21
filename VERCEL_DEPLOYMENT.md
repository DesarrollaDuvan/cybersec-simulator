# Guía de Despliegue en Vercel

Este documento te guiará paso a paso para desplegar tu aplicación Flask en Vercel.

## ⚠️ Importante: Limitaciones de SQLite en Vercel

Vercel es una plataforma serverless donde el sistema de archivos es **efímero**. Esto significa que:
- Los archivos creados durante la ejecución (incluyendo `database.db`) se pierden después de cada función
- **No uses SQLite para producción en Vercel** - los datos no persistirán
- Para producción, usa una base de datos externa como PostgreSQL, MySQL o MongoDB

### Bases de Datos Recomendadas para Producción:
- **PostgreSQL**: [Supabase](https://supabase.com/), [Neon](https://neon.tech/), [Railway](https://railway.app/)
- **MySQL**: [PlanetScale](https://planetscale.com/), [Aiven](https://aiven.io/)
- **MongoDB**: [MongoDB Atlas](https://www.mongodb.com/atlas)

## Pasos para Desplegar en Vercel

### 1. Prepara tu Repositorio

Asegúrate de que tu código esté en un repositorio de Git (GitHub, GitLab o Bitbucket):

```bash
git add .
git commit -m "Preparar para Vercel"
git push origin main
```

### 2. Instala la CLI de Vercel (Opcional)

```bash
npm install -g vercel
```

### 3. Conecta tu Repositorio a Vercel

**Opción A: Desde la Web de Vercel**
1. Ve a [vercel.com](https://vercel.com) e inicia sesión
2. Haz clic en "Add New Project"
3. Importa tu repositorio de GitHub/GitLab/Bitbucket
4. Vercel detectará automáticamente el archivo `vercel.json`

**Opción B: Desde la Línea de Comandos**
```bash
cd /workspace
vercel login
vercel
```

### 4. Configura las Variables de Entorno

En el dashboard de Vercel, ve a **Settings → Environment Variables** y agrega:

```
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
ANTHROPIC_API_KEY=tu-api-key-de-anthropic
OPENAI_API_KEY=tu-api-key-de-openai (si usas OpenAI)
GOOGLE_API_KEY=tu-api-key-de-google (si usas Google AI)
FLASK_ENV=production
```

### 5. Configura la Base de Datos (Recomendado para Producción)

Si vas a usar una base de datos externa:

1. Crea una base de datos en uno de los servicios recomendados arriba
2. En Vercel, agrega la variable de entorno:
   ```
   DATABASE_URL=postgresql://usuario:password@host:port/database
   ```

3. Modifica `config.py` para usar la URL de la base de datos:

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Usar base de datos externa si está disponible
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///database.db' if not os.environ.get('VERCEL') else 'sqlite:///vercel_temp.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ... resto de configuración
```

### 6. Despliega

**Desde la Web:**
- Vercel desplegará automáticamente después de conectar el repositorio
- Cada push a la rama principal triggerará un nuevo deploy

**Desde CLI:**
```bash
# Deploy de producción
vercel --prod

# Deploy de preview (para testing)
vercel
```

## Estructura de Archivos para Vercel

El proyecto ya incluye los archivos necesarios:

- ✅ `vercel.json` - Configuración de Vercel
- ✅ `requirements.txt` - Dependencias de Python
- ✅ `run.py` - Punto de entrada de la aplicación
- ✅ `.env.example` - Ejemplo de variables de entorno

## Consideraciones Importantes

### 1. Tiempo de Respuesta
- Las funciones serverless tienen un timeout máximo (10s en plan hobby, 60s en pro)
- Para operaciones largas (como generación de IA), considera usar streaming o background jobs

### 2. Archivos Estáticos
- Los archivos en `/app/static` se sirven correctamente
- Templates Jinja2 funcionan normalmente

### 3. Logs y Debugging
- Usa `print()` para logs básicos (se ven en `vercel logs`)
- Revisa los logs en el dashboard de Vercel para debugging

### 4. Dominio Personalizado
- Puedes agregar un dominio personalizado en Settings → Domains

## Comandos Útiles

```bash
# Ver logs en tiempo real
vercel logs --follow

# Ver deployments anteriores
vercel ls

# Eliminar un deployment
vercel rm <deployment-url>
```

## Solución de Problemas

### Error: "Module not found"
- Asegúrate de que todas las dependencias estén en `requirements.txt`
- Ejecuta `pip freeze > requirements.txt` para actualizar

### Error: "Database locked" o datos que desaparecen
- **¡No uses SQLite en producción!** Migra a PostgreSQL u otra base de datos externa

### Error: Timeout
- Optimiza las respuestas de la API
- Considera usar streaming para respuestas largas
- Upgrade a un plan superior si necesitas más tiempo

## Recursos Adicionales

- [Documentación oficial de Vercel para Python](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Flask en Vercel](https://vercel.com/guides/deploying-flask-with-vercel)
- [Variables de entorno en Vercel](https://vercel.com/docs/concepts/projects/environment-variables)

---

**Nota Final**: Para desarrollo y testing, puedes usar Vercel con SQLite temporal. Para producción con datos persistentes, **es obligatorio** usar una base de datos externa.
