from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Хранилище сессий
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    try:
        # Проверяем JSON
        if not request.is_json:
            return jsonify({
                "response": {
                    "text": "Произошла ошибка: ожидается JSON",
                    "end_session": False
                },
                "version": "1.0"
            }), 400

        req = request.get_json()
        logging.info(f'Request: {req}')

        # Создаем базовый ответ
        res = {
            "response": {
                "end_session": False
            },
            "version": req.get("version", "1.0")
        }

        # Обрабатываем запрос
        handle_dialog(req, res)

        logging.info(f'Response: {res}')
        return jsonify(res)

    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return jsonify({
            "response": {
                "text": f"Произошла ошибка: {str(e)}",
                "end_session": False
            },
            "version": "1.0"
        }), 500


def handle_dialog(req, res):
    # Получаем user_id из разных возможных мест в запросе
    user_id = (
            req.get('session', {}).get('user', {}).get('user_id') or
            req.get('session', {}).get('user_id') or
            "default_user"
    )

    # Инициализация новой сессии
    if req.get('session', {}).get('new', False):
        sessionStorage[user_id] = {
            'suggests': ["Не хочу.", "Не буду.", "Отстань!"],
            'attempts': 0
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['tts'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обработка ответа пользователя
    user_command = req.get('request', {}).get('original_utterance', '').lower()

    if user_command in ['ладно', 'куплю', 'покупаю', 'хорошо']:
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['tts'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return

    # Увеличиваем счетчик попыток
    sessionStorage[user_id]['attempts'] += 1

    # Формируем ответ
    res['response']['text'] = f"Все говорят '{user_command}', а ты купи слона!"
    res['response']['tts'] = f"Все говорят '{user_command}', а ты купи слона!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    if user_id not in sessionStorage:
        return []

    suggests = sessionStorage[user_id]['suggests']
    buttons = [
        {"title": suggest, "hide": True}
        for suggest in suggests[:2]
    ]

    # Ротация подсказок
    sessionStorage[user_id]['suggests'] = suggests[1:] + [suggests[0]]

    # Добавляем кнопку с ссылкой
    buttons.append({
        "title": "Ладно",
        "url": "https://market.yandex.ru/search?text=слон",
        "hide": True
    })

    return buttons


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
