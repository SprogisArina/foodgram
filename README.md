# Foodgram — «Продуктовый помощник»

## Foodgram — это онлайн-платформа для публикации рецептов

Пользователи могут:

📝 Создавать рецепты с ингредиентами и шагами приготовления

🔍 Искать рецепты по тегам (например, «завтрак», «десерты»)

❤️ Добавлять рецепты в избранное

🛒 Формировать список покупок для выбранных рецептов

📥 Скачивать список ингредиентов в PDF

Ссылка на [сайт](https://fooodgram.sytes.net/)

Автор [SprogisArina](https://github.com/SprogisArina/)

## Технологии:

Backend:
- python 3.9
- Django REST Framework 3.16
- Djoser 2.3

Frontend: React

База данных: PostgreSQL

Деплой: Docker, Nginx, GitHub Actions (CI/CD)

## Развертывание

### CI/CD

[Файл](https://github.com/SprogisArina/foodgram/blob/main/.github/workflows/main.yml) для GitHub Actions

### Локальное развертывание с Докером

Клонирование репозитория

```
git clone https://github.com/SprogisArina/foodgram.git
```

Переход в папку проекта

```
cd foodgram/infra/ 
```

Настройка .env: в главной папке проекта создайте файл .env. Пример в .env.example

Запуск контейнеров

```
docker compose up -d --build
```

Подготовка базы данных

```
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py load_ingredients
```

Сервер уже работает в контейнере. Доступ: http://localhost:8000


### Локальное развертывание без Докера

Клонирование репозитория

```
git clone https://github.com/SprogisArina/foodgram.git
```

Переход в папку проекта

```
cd foodgram/backend/
```

Настройка виртуального окружения

```
python -m venv venv
source venv/Scripts/activate
```

или для Linux/Mac

```
source venv/bin/activate
```

Установка зависимостей

```
pip install -r requirements.txt
```

Миграции и суперпользователь

```
python manage.py migrate
python manage.py createsuperuser
```

Импорт данных

```
python manage.py load_ingredients
```

Запуск сервера

```
python manage.py runserver
```
