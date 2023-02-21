# Webstore - интернет магазин.
![CI](https://github.com/RuslanSibgatulin/Webstore/actions/workflows/test.yml/badge.svg)

Каталог товаров с быстрой покупкой через сторонюю платежную систему.

## Используемые технологии
- Код приложения на Python
- Фреймворк [Django 4.1](https://docs.djangoproject.com/en/4.1/)
- Платёжная система [stripe](https://stripe.com/docs/development/quickstart?lang=python#install-sdk)
- СУБД - Postgres
- Все компоненты системы запускаются через Docker-compose.

# Запуск приложения
## Клонировать репозиторий
    git clone https://github.com/RuslanSibgatulin/Webstore.git

## Переменные окружения
Подготовить файлы с переменными окружения по аналогии с файлами `docker/envs/*.example` и пересохранить в файлы `*.env`.
Обязательно заполнить следующие параметры:

    DJANGO_SECRET_KEY - рандомная строка длиной 50 символов
    STRIPE_PUBLIC - публичный ключ https://dashboard.stripe.com/developers
    STRIPE_SECRET - секретный ключ вашего аккаунта stripe.com

## Запуск
    make start

### При первичном запуске необходимо выполнить команды инициализации
    make init

### Для демонстрации загрузите демо-контент
    make loaddata


# Функционал
- [Каталог](http://<your-domain>/items/)
- [Админ-панель](http://<your-domain>/admin/)

