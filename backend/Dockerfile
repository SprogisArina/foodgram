FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN echo '#!/bin/bash \n\
    python manage.py migrate --noinput \n\
    python manage.py collectstatic --noinput \n\
    exec "$@"' > /entrypoint.sh && \
        chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]