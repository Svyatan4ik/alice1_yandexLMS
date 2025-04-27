#!/bin/bash
# deploy_alice_skill.sh - Упрощенный скрипт для развертывания навыка Алисы

# Выход при ошибках
set -eu

# --- Конфигурация ---
APP_NAME="alice_skill"
GIT_REPO="https://github.com/Svyatan4ik/alice1_yandexLMS"  # Замените на ваш репозиторий
PYTHON_VERSION="3.9"                                     # Версия Python
PORT=5000                                               # Порт для Flask

# --- 1. Проверка зависимостей ---
echo "🔍 Проверяем зависимости..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 не установлен"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git не установлен"; exit 1; }

# --- 2. Клонирование репозитория ---
echo "📥 Клонируем репозиторий..."
if [ ! -d "$APP_NAME" ]; then
  git clone "$GIT_REPO" "$APP_NAME"
  cd "$APP_NAME"
else
  cd "$APP_NAME"
  git pull
fi

# --- 3. Настройка виртуального окружения ---
echo "🐍 Создаем виртуальное окружение Python $PYTHON_VERSION..."
python3 -m venv venv
source venv/bin/activate

# --- 4. Установка зависимостей ---
echo "📦 Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

# --- 5. Запуск приложения ---
echo "🚀 Запускаем Flask-приложение..."
echo "➡️ Вебхук должен быть указан вручную в кабинете разработчика:"
echo "   URL: http://$(hostname -I | awk '{print $1}'):$PORT/post"
echo "   Или: http://your-public-ip:$PORT/post"

flask run --host=0.0.0.0 --port=$PORT

# --- Подсказка для Ngrok (если нужно) ---
echo "ℹ️ Для тестирования извне можно использовать Ngrok:"
echo "   ngrok http $PORT"