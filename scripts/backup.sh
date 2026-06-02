#!/bin/bash
# Скрипт для создания бэкапа базы данных
# Запускается через cron на сервере

BACKUP_DIR="/root/smartprice/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

echo "Начинаем создание резервной копии базы данных: $TIMESTAMP"

cd /root/smartprice

if command -v docker-compose &> /dev/null; then
  DC_CMD="docker-compose"
else
  DC_CMD="docker compose"
fi

$DC_CMD -f docker-compose.prod.yml exec -T db pg_dump -U smartprice_user -d smartprice > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "Успех! Бэкап сохранен в $BACKUP_FILE"
  
  # Удаляем бэкапы старше 7 дней
  find "$BACKUP_DIR" -type f -name "*.sql" -mtime +7 -delete
  echo "Старые бэкапы (старше 7 дней) удалены."
else
  echo "Ошибка при создании бэкапа!"
  rm -f "$BACKUP_FILE"
  exit 1
fi
