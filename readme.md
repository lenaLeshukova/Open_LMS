# Open LMS — Платформа для онлайн-обучения 

Служебный проект SPA веб-приложения (LMS-системы), разработанный на Django REST Framework. Позволяет пользователям размещать свои полезные курсы и учебные материалы, а также отслеживать историю платежей. Бэкенд-сервер общается с клиентом посредством JSON-структур.

## 🛠 Стек технологий
* **Python** 3.12
* **Django** 5.2+ (с поддержкой конфигурации `MAILERS`)
* **Django REST Framework** (DRF)
* **Poetry** (управление зависимостей)
* **PostgreSQL** & **Psycopg (Binary)** (база данных)
* **Pillow** (работа с изображениями и аватарами)
* **Python-dotenv** (изоляция секретных переменных окружения)


---

## 🚀 Инструкция по локальному развертыванию

### 1. Клонирование репозитория
```bash
git clone https://github.com
cd Open_LMS
```

### 2. Настройка виртуального окружения через Poetry
Убедитесь, что у вас установлен Poetry. Установите все зависимости проекта:
```bash
poetry install
poetry shell
```

### 3. Настройка переменных окружения
Создайте в корне проекта файл `.env` и заполните его своими данными:
```env
# Django настройки
SECRET_KEY=your_django_secret_key
DEBUG=True

# Настройки базы данных PostgreSQL
DB_NAME=open_lms
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=127.0.0.1
DB_PORT=5432

# Настройки почты Яндекс SMTP
EMAIL_PASSWORD=your_yandex_app_password
```

### 4. Подготовка базы данных и миграции
Перед первым запуском убедитесь, что в вашей СУБД PostgreSQL создана пустая база данных `open_lms`. Затем последовательно примените миграции и загрузите тестовые данные платежей:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata users/fixtures/payments_data.json
```

### 5. Запуск сервера разработки
```bash
python manage.py runserver
```
Сервер будет доступен по локальному адресу: `http://127.0.0.1:8000/`

---

## 📡 Эндпоинты API (Примеры для тестирования в Postman)

### 📚 Курсы (Реализовано через ViewSets)
* `GET` `/api/courses/` — Получить список всех курсов.
* `POST` `/api/courses/` — Создать новый курс (передавать `title` и `description` в Body -> form-data).
* `GET` `/api/courses/<id>/` — Получить детальную информацию о курсе.
* `PUT` `/api/courses/<id>/` — Полностью обновить курс.
* `DELETE` `/api/courses/<id>/` — Удалить курс.

### 📝 Уроки (Реализовано через Generics)
* `GET` `/api/lessons/` — Получить список всех уроков.
* `POST` `/api/lessons/create/` — Создать новый урок (в Body -> form-data обязательно передать `course` с ID существующего курса).
* `GET` `/api/lessons/<id>/` — Получить детали урока.
* `PUT` `/api/lessons/update/<id>/` — Редактировать урок.
* `DELETE` `/api/lessons/delete/<id>/` — Удалить урок.

### 💳 Платежи (Реализовано через Generics с фильтрацией)
* `GET` `/api/payments/` — Получить список всех платежей.

**Возможности фильтрации и сортировки (Query-параметры):**
* **Сортировка по дате оплаты (по возрастанию):** `/api/payments/?ordering=payment_date`
* **Сортировка по дате оплаты (по убыванию):** `/api/payments/?ordering=-payment_date`
* **Фильтрация по конкретному курсу:** `/api/payments/?paid_course=<id_курса>`
* **Фильтрация по конкретному уроку:** `/api/payments/?paid_lesson=<id_урока>`
* **Фильтрация по способу оплаты (наличные):** `/api/payments/?payment_method=cash`
* **Фильтрация по способу оплаты (перевод):** `/api/payments/?payment_method=transfer`

*Пример комбинированного запроса:* `/api/payments/?paid_course=1&ordering=-payment_date`
