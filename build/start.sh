#!/bin/bash
# deploy_alice_skill.sh - Упрощенный скрипт для развертывания навыка Алисы

# Выход при ошибках
set -eu

# --- Конфигурация ---
APP_NAME="alice_skill"
GIT_REPO="https://github.com/Svyatan4ik/alice1_yandexLMS"  # Замените на ваш репозиторий
PYTHON_VERSION="3.9"                                     FLASK_APP="flask_app.py"  # Имя вашего основного файла Flask
PORT=5000

# Проверка зависимостей
echo "🔍 Проверяем зависимости..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 не установлен"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git не установлен"; exit 1; }

# Клонирование/обновление репозитория
echo "📥 Работаем с репозиторием..."
if [ ! -d "$APP_NAME" ]; then
  git clone "$GIT_REPO" "$APP_NAME"
  cd "$APP_NAME"
else
  cd "$APP_NAME"
  git pull
fi

# Настройка окружения
echo "🐍 Создаем виртуальное окружение..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📦 Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

# Экспорт переменной FLASK_APP
export FLASK_APP=$FLASK_APP
export FLASK_ENV=development

# Запуск приложения
echo "🚀 Запускаем Flask-приложение..."
echo "ℹ️ Используемый файл приложения: $FLASK_APP"
echo "🌐 Сервер будет доступен по адресу:"
echo "   http://$(hostname -I | awk '{print $1}'):$PORT"
echo "   или"
echo "   http://localhost:$PORT"

flask run --host=0.0.0.0 --port=$PORT