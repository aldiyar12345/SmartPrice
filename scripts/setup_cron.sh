#!/bin/bash
# Скрипт для настройки cron задачи для бэкапа базы данных
# Запускать на сервере (DigitalOcean droplet)

SCRIPT_PATH="/root/smartprice/scripts/backup.sh"
LOG_PATH="/root/smartprice/backups/backup.log"

# Делаем скрипт бэкапа исполняемым
chmod +x "$SCRIPT_PATH"

# Проверяем, есть ли уже такая задача в cron
if crontab -l 2>/dev/null | grep -q "$SCRIPT_PATH"; then
    echo "Cron задача для бэкапа уже настроена."
else
    # Добавляем задачу на выполнение каждый день в 03:00 ночи
    (crontab -l 2>/dev/null; echo "0 3 * * * $SCRIPT_PATH >> $LOG_PATH 2>&1") | crontab -
    echo "Cron задача успешно добавлена (каждый день в 03:00)."
    echo "Логи будут записываться в $LOG_PATH"
fi
