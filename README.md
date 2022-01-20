# api_yamdb

**REST API для сервиса YaMDb** — базы отзывов о фильмах, книгах и музыке.

## Технологии
* Python 3.7
* [django](https://www.djangoproject.com/)
* [drf](https://www.django-rest-framework.org/)
* [posgresql](https://www.postgresql.org/)
* [docker](https://www.docker.com/)

## Установка
1. Установка docker и docker-compose
```
https://docs.docker.com/engine/install/ubuntu/
```

2. Создать файл .env в /infra/ с переменными окружения
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres # Имя базы данных
POSTGRES_USER=postgres # Администратор базы данных
POSTGRES_PASSWORD=postgres # Пароль администратора
DB_HOST=db
DB_PORT=5432
```
3. Сборка и запуск контейнера
```bash
docker-compose up -d --build
```
4. Миграции
```bash
docker-compose exec web python manage.py migrate
```
5. Создание суперпользователя Django
```bash
docker-compose exec web python manage.py createsuperuser
```
6. Сбор статики
```bash
docker-compose exec web python manage.py collectstatic --no-input
```

Документация доступна по адресу:
http://localhost:8000/redoc/
***

## Примеры работы с авторизацией
### Запрос на отправку письма с кодом подтверждения

        curl --location --request POST 'http://127.0.0.1:8000/api/v1/auth/signup/' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "email": "test@test.com",
            "username": "test"
        }'
Если в БД не найдется пользователь с таким username - создастся новый пользователь
В результате выполнения метода отправляется код авторизации на почту пользователя. Посмотреть отправленные письма можно в папке sent_emails

### Запрос на авторизацию при помощи кода

        curl --location --request POST 'http://127.0.0.1:8000/api/v1/auth/token/' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "username": "test",
           "confirmation_code": "GQ0LM"
        }'

Если пользователь существует и код подтверждения верен, метод вернет AccessToken

### Об авторе
 - [Dmitrii Kartavtsev](https://github.com/xrito)
 - Telegram: https://t.me/harkort