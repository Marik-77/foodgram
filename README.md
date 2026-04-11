# Foodgram

«Продуктовый помощник»: веб-приложение для публикации рецептов, подписок на авторов, списка избранного и выгрузки списка покупок. Есть REST API (Django REST Framework) и фронтенд на React.

---

## Автор

| | |
|---|---|
| **ФИО** | *Петров Марк Алексеевич* |
| **Контакты** | [Telegram](https://t.me/@markeeello) · [GitHub](https://github.com/Marik-77) · [Email](marikp20@gmail.com) |

---

## Стек технологий

**Бэкенд:** Python 3.12, Django 4.2, Django REST Framework, Djoser, django-filter, Gunicorn, Pillow, PostgreSQL (через psycopg2).

**Фронтенд:** React 17, React Router.

**Инфраструктура:** Docker, Docker Compose, Nginx.

---

## Локальный запуск с Docker

### 1. Клонирование репозитория

```bash
git clone https://github.com/<ваш-логин>/foodgram.git
cd foodgram
```

### 2. Переменные окружения

В каталоге `infra` создайте файл `.env` (рядом с `docker-compose.yml`). Пример для локальной разработки с PostgreSQL:

```env
SECRET_KEY=сгенерируйте-надёжный-ключ-для-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_PORT=5432
```

Опционально (если нужны POST-запросы с другого origin при `DEBUG=False`):

```env
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
```

Для образов из Docker Hub (если используете свой префикс):

```env
DOCKERHUB_USERNAME=local
```

### 3. Запуск контейнеров

Из каталога `infra`:

```bash
docker compose up --build
```

При первом старте контейнер **backend** дождётся PostgreSQL, выполнит миграции (`migrate`), соберёт статику (`collectstatic`) и при наличии файла `../data/ingredients.csv` загрузит ингредиенты. Контейнер **frontend** один раз копирует собранные файлы в volume для Nginx и завершается.

### 4. Доступ к приложению

| Что | Адрес |
|-----|--------|
| Сайт (фронтенд) | [http://localhost](http://localhost) |
| Документация API | [http://localhost/api/docs/](http://localhost/api/docs/) |
| Админка Django | [http://localhost/admin/](http://localhost/admin/) |

### 5. Суперпользователь Django (админка)

Учётные данные в репозиторий не коммитятся. После запуска контейнеров создайте администратора:

```bash
docker compose exec backend python manage.py createsuperuser
```

Укажите email, имя пользователя и пароль. **Логин и пароль для проверки проекта** передайте ревьюеру отдельно или пропишите здесь после деплоя (не храните реальные пароли в публичном репозитории).

### 6. Миграции вручную (при необходимости)

Обычно миграции выполняются при старте `backend`. Дополнительно:

```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

---

## Развёрнутый сервис

**Домен или IP:** [https://idealfood.ddns.net](https://idealfood.ddns.net) (пример; замените на актуальный адрес вашего сервера).

Страница с рецептами: [https://idealfood.ddns.net/recipes](https://idealfood.ddns.net/recipes).
