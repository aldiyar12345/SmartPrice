# SmartPrice Playbook (Runbook)

Этот документ описывает основные операционные сценарии для поддержки продакшена проекта SmartPrice. 

## Сценарий 1: Перезапуск приложения и обновление (Deployment & Restart)

**Ситуация:** Нужно выкатить новую версию или перезапустить зависшие контейнеры.

**Действия:**
1. Зайдите на сервер через SSH:
   ```bash
   ssh root@165.22.253.31
   ```
2. Перейдите в директорию проекта:
   ```bash
   cd ~/smartprice
   ```
3. Скачайте свежие изменения из репозитория:
   ```bash
   git pull origin main
   ```
4. Перезапустите все контейнеры в фоне:
   ```bash
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml up -d --build
   ```
5. Проверьте статус (health check):
   Перейдите по адресу `http://smrtprc.me/api/auth/health/` (или аналогичному health-эндпоинту) и убедитесь, что ответ `200 OK`.

---

## Сценарий 2: Действия при высоком Error Rate (> 5%)

**Ситуация:** Сработал алерт в Telegram/Grafana о высоком уровне ошибок (500 Internal Server Error).

**Действия:**
1. Откройте **Grafana Dashboard** (`http://smrtprc.me:3000`) и посмотрите панель "Error Rate", чтобы понять, когда начался рост ошибок.
2. Подключитесь к серверу и посмотрите логи backend-сервиса (они теперь в JSON-формате для удобства парсинга):
   ```bash
   cd ~/smartprice
   docker-compose -f docker-compose.prod.yml logs --tail=100 backend
   ```
3. Если ошибка связана с базой данных (например, `OperationalError: FATAL: too many connections`):
   - Проверьте загрузку базы: `docker stats`
   - Перезапустите контейнеры: `docker-compose -f docker-compose.prod.yml restart backend`
4. Если ошибка на уровне кода после недавнего релиза:
   - Сделайте откат: `git checkout HEAD~1` (вернуться на предыдущий коммит).
   - Пересоберите контейнеры (см. Сценарий 1).

---

## Сценарий 3: Восстановление Базы Данных (Disaster Recovery)

**Ситуация:** Данные на продакшене были повреждены, и товары не отображаются на сайте.

**Действия:**
1. Зайдите на сервер:
   ```bash
   ssh root@165.22.253.31
   cd ~/smartprice
   ```
2. Убедитесь, что дамп базы (`backend/db_dump.json`) присутствует:
   ```bash
   ls backend/db_dump.json
   ```
3. Выполните скрипт восстановления БД внутри запущенного контейнера:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python restore_db.py
   ```
4. Если скрипт говорит, что данные уже есть, но они повреждены, вам нужно сначала зайти в shell и очистить таблицы, затем запустить `restore_db.py` снова:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python manage.py flush --no-input
   docker-compose -f docker-compose.prod.yml exec backend python restore_db.py
   ```
5. Проверьте сайт, чтобы убедиться, что товары появились в каталоге.
