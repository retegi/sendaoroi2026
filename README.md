# Sendaoroi

Web pública de Sendaoroi construida con Django, Tailwind CSS y Docker, preparada para entorno bilingüe (`/es/` y `/eu/`).

## Desarrollo local

1. Copia variables de entorno:
   - `cp .env.example .env`
2. Arranca servicios:
   - `docker compose up -d --build`
3. URL local:
   - [http://127.0.0.1:8001/es/](http://127.0.0.1:8001/es/)

### Comandos útiles en desarrollo

- Migraciones: `docker compose exec web python manage.py migrate`
- Crear superusuario: `docker compose exec web python manage.py createsuperuser`
- Collectstatic: `docker compose exec web python manage.py collectstatic --noinput`
- Chequeo Django: `docker compose exec web python manage.py check`
- Tailwind build: `npm run build`
- Tailwind watch: `npm run dev`

## Producción (Docker)

Compose de producción:

- `docker-compose.yml` + `docker-compose.prod.yml`

Arranque:

- `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build`

El servicio web queda escuchando solo en localhost del servidor:

- `127.0.0.1:8050:8000`

Nginx debe hacer `proxy_pass` a:

- `http://127.0.0.1:8050`

## Variables de entorno requeridas

Definir al menos estas variables en `.env`:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `CONTACT_EMAIL`
- `DEFAULT_FROM_EMAIL`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
