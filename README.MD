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
    git@github.com:RuslanSibgatulin/Webstore.git

## Переменные окружения
Подготовить файлы с переменными окружения по аналогии с файлами `docker/envs/*.example` и пересохранить в файлы `*.env`

## Запуск
    make start

### При первичном запуске необходимо выполнить команды инициализации
    make init

### Для демонстрации загрузите демо-контент
    make loaddata


# Функционал
- [Каталог](http://127.0.0.1/items/)
- [Админ-панель](http://127.0.0.1/admin/)

