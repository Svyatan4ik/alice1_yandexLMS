from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    try:
        req = request.get_json()
        logging.info(f'Request: {req}')

        # Проверка структуры запроса
        if not all(key in req for key in ['session', 'request', 'version']):
            return jsonify({
                "response": {
                    "text": "Ошибка: неверный формат запроса",
                    "end_session": False
                },
                "version": "1.0"
            }), 400

        # Формируем базовый ответ
        response = {
            "version": req['version'],
            "session": req['session'],
            "response": {
                "end_session": False,
                "text": "Произошла ошибка обработки запроса"
            }
        }

        handle_dialog(req, response)

        logging.info(f'Response: {response}')
        return jsonify(response)

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
    user_id = req['session']['user']['user_id']
    is_new_session = req['session']['new']

    if is_new_session:
        # Инициализация новой сессии
        sessionStorage[user_id] = {
            'suggests': ["Не хочу.", "Не буду.", "Отстань!"],
            'attempts': 0
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['tts'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обработка команд пользователя
    user_command = req['request']['original_utterance'].lower()

    if any(word in user_command for word in ['ладно', 'куплю', 'покупаю', 'хорошо']):
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['tts'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return

    # Увеличиваем счетчик отказов
    sessionStorage[user_id]['attempts'] += 1

    # Формируем ответ с учетом количества попыток
    attempts = sessionStorage[user_id]['attempts']
    if attempts > 3:
        res['response']['text'] = f"Вы уже {attempts} раз отказались! Ну купите слона!"
    else:
        res['response']['text'] = f"Все говорят '{user_command}', а ты купи слона!"

    res['response']['tts'] = res['response']['text']
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    suggests = sessionStorage[user_id]['suggests']
    buttons = [{"title": suggest, "hide": True} for suggest in suggests[:2]]

    # Добавляем кнопку с ссылкой
    buttons.append({
        "title": "Ладно",
        "url": "https://market.yandex.ru/search?text=слон",
        "hide": True
    })

    # Ротация подсказок
    sessionStorage[user_id]['suggests'] = suggests[1:] + [suggests[0]]

    return buttons


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)