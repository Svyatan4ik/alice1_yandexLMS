from flask import Flask, request, jsonify
import logging
from collections import OrderedDict

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}


def make_response():
    """Создает ответ с гарантированным порядком полей"""
    return OrderedDict([
        ('text', ''),
        ('tts', ''),
        ('buttons', []),
        ('end_session', False)
    ])


@app.route('/post', methods=['POST'])
def main():
    try:
        req = request.get_json()
        logging.info(f'Request: {req}')

        # Проверка структуры запроса
        if not all(key in req for key in ['session', 'request', 'version']):
            response = make_response()
            response['text'] = response['tts'] = "Ошибка: неверный формат запроса"
            return jsonify({
                "version": "1.0",
                "response": response
            }), 400

        # Создаем базовый ответ с правильным порядком полей
        response = {
            "version": req['version'],
            "session": req['session'],
            "response": make_response()
        }

        handle_dialog(req, response)

        logging.info(f'Response: {response}')
        return jsonify(response)

    except Exception as e:
        logging.error(f'Error: {str(e)}')
        response = make_response()
        response['text'] = response['tts'] = f"Произошла ошибка: {str(e)}"
        return jsonify({
            "version": "1.0",
            "response": response
        }), 500


def handle_dialog(req, res):
    user_id = req['session']['user']['user_id']
    is_new_session = req['session']['new']

    if is_new_session:
        sessionStorage[user_id] = {
            'suggests': ["Не хочу.", "Не буду.", "Отстань!"],
            'attempts': 0
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['tts'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    user_command = req['request']['original_utterance'].lower()

    if any(word in user_command for word in ['ладно', 'куплю', 'покупаю', 'хорошо']):
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['tts'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return

    sessionStorage[user_id]['attempts'] += 1
    attempts = sessionStorage[user_id]['attempts']

    if attempts > 3:
        response_text = f"Вы уже {attempts} раз отказались! Ну купите слона!"
    else:
        response_text = f"Все говорят '{user_command}', а ты купи слона!"

    res['response']['text'] = response_text
    res['response']['tts'] = response_text
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    suggests = sessionStorage[user_id]['suggests']
    buttons = [{"title": suggest, "hide": True} for suggest in suggests[:2]]

    buttons.append({
        "title": "Ладно",
        "url": "https://market.yandex.ru/search?text=слон",
        "hide": True
    })

    sessionStorage[user_id]['suggests'] = suggests[1:] + [suggests[0]]
    return buttons


if __name__ == '__main__':
    app.run()
