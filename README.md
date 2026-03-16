# LK Nails & Lashes

## Local run

1. Create/update `Site Settings` in Django admin for salon info and SMTP.
2. Apply migrations:

```bash
python3 manage.py migrate
```

3. Seed starter data:

```bash
python3 manage.py seed_salon_data
```

4. Run the server:

```bash
python3 manage.py runserver
```

## Production deploy outline

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Prepare env file from [`.env.example`](/Users/copv/Data/lknails/.env.example).
3. Apply migrations and collect static:

```bash
python3 manage.py migrate
python3 manage.py collectstatic --noinput
```

4. Run with Gunicorn:

```bash
gunicorn -c gunicorn.conf.py
```

5. Put Nginx in front using [deploy/nginx.lknailslashes.de.conf](/Users/copv/Data/lknails/deploy/nginx.lknailslashes.de.conf).
6. Optionally run as systemd service using [deploy/lknails.service](/Users/copv/Data/lknails/deploy/lknails.service).

## Production notes

- App secrets and deployment flags are read from environment variables in [`.env.example`](/Users/copv/Data/lknails/.env.example).
- Gmail SMTP is not read from env by default in this project. It is configured in the database through `Site Settings`.
- For production, set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, trusted origins, and secure cookie flags.
- Health check endpoint is available at `/health/`.

# lknails
