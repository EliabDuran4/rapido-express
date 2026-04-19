# 🚀 Guía de Despliegue en Render.com (100% Gratuito)
## Rápido Express — Portal de Noticias

---

## ¿Qué necesitas?
- Cuenta en [github.com](https://github.com) (gratuita)
- Cuenta en [render.com](https://render.com) (gratuita, sin tarjeta de crédito)
- Git instalado en tu PC

---

## PASO 1 — Subir el proyecto a GitHub

Abre una terminal en la carpeta `rapido_express/`:

```bash
git init
git add .
git commit -m "primer commit - rapido express"
```

Ve a [github.com/new](https://github.com/new) y crea un repositorio llamado `rapido-express`.
Luego conecta y sube:

```bash
git remote add origin https://github.com/TU_USUARIO/rapido-express.git
git branch -M main
git push -u origin main
```

> ⚠️ Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub.

---

## PASO 2 — Crear cuenta en Render

1. Ve a [render.com](https://render.com)
2. Click en **"Get Started for Free"**
3. Regístrate con tu cuenta de **GitHub** (más fácil, conecta directo)

---

## PASO 3 — Crear el Web Service

1. En el dashboard de Render, click en **"New +"** → **"Web Service"**
2. Click en **"Connect a repository"**
3. Selecciona tu repositorio `rapido-express`
4. Render detectará el `render.yaml` automáticamente

Si no lo detecta, configura manualmente:

| Campo | Valor |
|-------|-------|
| **Name** | `rapido-express` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind=0.0.0.0:$PORT --timeout 120 --workers 2 app:app` |
| **Plan** | `Free` |

5. Click en **"Create Web Service"**

---

## PASO 4 — Esperar el deploy (2-3 minutos)

Render mostrará los logs en tiempo real. Cuando veas:

```
==> Your service is live 🎉
```

Tu app estará disponible en una URL como:
```
https://rapido-express.onrender.com
```

Esa URL es la que le compartes a la profesora.

---

## ⚠️ Nota importante — Plan gratuito de Render

El plan gratuito tiene una limitación: **el servidor se "duerme"** después de 15 minutos
sin visitas. La primera vez que alguien entre tardará ~30 segundos en despertar.
Después de eso funciona normal.

Para la práctica esto es perfectamente aceptable.

---

## PASO 5 — Re-despliegue automático tras cambios

Cada vez que hagas `git push`, Render re-despliega automáticamente:

```bash
# Modificar algo, luego:
git add .
git commit -m "actualización"
git push
# Render detecta el push y re-despliega solo ✅
```

---

## Persistencia de archivos en Render

Al igual que Azure, Render resetea el sistema de archivos en cada deploy.
Los archivos subidos por usuarios se pierden al re-deployar.

**Solución incluida en el proyecto:**
El CSV de ejemplo (`data/ejemplo.csv`) siempre está en el repositorio,
así que siempre habrá al menos una noticia visible.

Para la práctica, los uploads temporales funcionan perfectamente durante
la demostración: subes el archivo, se ve en el portal, le muestras a la
profesora, perfecto.

---

## Resumen visual del proceso

```
Tu PC                    GitHub                   Render
  │                        │                        │
  ├─ git init              │                        │
  ├─ git add .             │                        │
  ├─ git commit ──────────►│                        │
  ├─ git push ─────────────►                        │
  │                        ├─ webhook ─────────────►│
  │                        │                        ├─ pip install
  │                        │                        ├─ gunicorn start
  │                        │                        └─ 🌐 URL pública lista
```

---

## URL final de ejemplo

```
https://rapido-express.onrender.com
```

Comparte esa URL con tu profesora y con tus compañeros.
Cualquiera puede entrar, ver las noticias, y subir un CSV nuevo.