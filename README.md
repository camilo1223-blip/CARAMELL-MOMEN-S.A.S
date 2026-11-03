# 🍬 CARAMELL MOMEN S.A.S.

Sistema web de compra y venta de dulces y confitería, desarrollado con Python, Flask, SQLAlchemy, HTML, CSS y JavaScript. Incluye catálogo, carrito, registro e inicio de sesión, pedidos, panel administrativo y asistente Caramell Assistant con integración opcional de Google Gemini.

## Estructura única del proyecto

```text
caramell_momen/
├── app.py
├── vercel.json
├── requirements.txt
├── .env.example
├── .gitignore
├── .vercelignore
├── README.md
├── backend/
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── seed_data.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── catalog.py
│   │   ├── orders.py
│   │   ├── admin.py
│   │   └── chatbot.py
│   └── services/
│       └── gemini_service.py
├── frontend/
│   ├── templates/
│   └── static/
└── tests/
    └── test_caramell.py
```

## 1. Ejecutar en tu computador

Requisitos: Python 3.11 o superior.

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Instala dependencias e inicia:
```bash
pip install -r requirements.txt
python app.py
```

Abre `http://127.0.0.1:5000`.

Para desarrollo local, si no configuras `DATABASE_URL`, se usa SQLite dentro de `backend/`. La base se crea y se carga con los datos iniciales al iniciar la aplicación.

## 2. Publicar el proyecto en GitHub

1. Crea un repositorio nuevo en GitHub, por ejemplo `caramell-momen`.
2. Descomprime esta carpeta y abre una terminal dentro de `caramell_momen` (la carpeta que contiene `app.py`).
3. Ejecuta:

```bash
git init
git add .
git commit -m "Primera version de CARAMELL MOMEN"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/caramell-momen.git
git push -u origin main
```

Reemplaza `TU_USUARIO` por tu usuario real de GitHub. No subas el archivo `.env`, contraseñas, claves API ni bases de datos locales. El `.gitignore` ya excluye esos archivos.

## 3. Publicar en Vercel conectado a GitHub

1. Entra a Vercel e inicia sesión con GitHub.
2. Selecciona **Add New → Project** y elige el repositorio `caramell-momen`.
3. Deja como **Root Directory** la raíz del repositorio (la carpeta donde está `app.py`).
4. Vercel detectará la configuración de Python mediante `vercel.json` y `requirements.txt`.
5. En **Environment Variables**, agrega las variables indicadas abajo.
6. Pulsa **Deploy**. Cada nuevo `git push` a la rama conectada volverá a desplegar el sitio.

### Variables necesarias en Vercel

Configura como mínimo:

- `SECRET_KEY`: una clave secreta larga, aleatoria y exclusiva para producción.
- `ADMIN_REGISTRATION_KEY`: una clave privada y difícil de adivinar para registrar administradores.
- `DATABASE_URL`: cadena de conexión de una base de datos PostgreSQL o MySQL alojada externamente.

Opcional:
- `GEMINI_API_KEY`: clave de Google AI Studio para activar Gemini.
- `GEMINI_MODEL`: modelo de Gemini que tengas habilitado.

Después de agregar o cambiar variables, vuelve a desplegar el proyecto.

## 4. IMPORTANTE: base de datos en Vercel

Vercel ejecuta la aplicación en funciones y su almacenamiento local no es persistente. Por eso, SQLite en `/tmp` solamente sirve como modo de demostración: los registros, pedidos y cambios pueden desaparecer o no compartirse entre instancias.

**Para usar la tienda de verdad, configura `DATABASE_URL` con una base PostgreSQL persistente** (por ejemplo, un servicio PostgreSQL compatible con SQLAlchemy) o MySQL. La aplicación normaliza automáticamente las URLs `postgres://` y `postgresql://` para utilizar `psycopg`.

No uses la base SQLite incluida en tu computador como base de producción ni guardes información real de clientes en el modo temporal.

## 5. Pruebas

```bash
python -m unittest discover -s tests -v
```

## 6. Seguridad antes de abrir la tienda al público

- Cambia las claves `SECRET_KEY` y `ADMIN_REGISTRATION_KEY` por valores privados.
- Revisa y cambia las credenciales de demostración que aparecen en las pantallas/documentación antes de publicar.
- No compartas `GEMINI_API_KEY` ni cadenas `DATABASE_URL`.
- Configura una base de datos persistente y realiza copias de seguridad.
- Verifica los flujos de registro, compra, pedidos y administración en el despliegue de prueba antes de usarlo con clientes.
