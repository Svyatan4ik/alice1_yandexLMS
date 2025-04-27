from flask import Flask, request, Response
import json
import logging
from collections import OrderedDict

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Хранилище сессий
sessionStorage = {}


def create_response():
    """Создает шаблон ответа с правильным порядком полей"""
    return OrderedDict([
        ('text', ''),
        ('tts', ''),
        ('buttons', []),
        ('end_session', False)
    ])


def build_full_response(req, response_data):
    """Собирает полный ответ с сохранением порядка полей"""
    return OrderedDict([
        ('response', response_data),
        ('session', req.get('session', {})),
        ('version', req.get('version', '1.0'))
    ])


@app.route('/post', methods=['POST'])
def main():
    try:
        # Получаем и проверяем запрос
        req = request.get_json()
        if not req:
            return error_response('Invalid JSON received')

        logging.info(f'Incoming request: {json.dumps(req, indent=2, ensure_ascii=False)}')

        # Обрабатываем диалог
        response_data = handle_dialog(req)

        # Формируем полный ответ
        full_response = build_full_response(req, response_data)

        logging.info(f'Outgoing response: {json.dumps(full_response, indent=2, ensure_ascii=False)}')

        # Сериализуем с сохранением порядка
        return Response(
            json.dumps(full_response, ensure_ascii=False),
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f'Error: {str(e)}', exc_info=True)
        return error_response(str(e))


def error_response(error_msg):
    """Создает ответ об ошибке"""
    response = create_response()
    response['text'] = f'Произошла ошибка: {error_msg}'
    response['tts'] = response['text']
    return Response(
        json.dumps({
            'response': response,
            'version': '1.0'
        }, ensure_ascii=False),
        mimetype='application/json',
        status=500
    )


def handle_dialog(req):
    """Основная логика обработки диалога"""
    response = create_response()

    # Получаем идентификатор пользователя
    user_id = req.get('session', {}).get('user', {}).get('user_id', 'unknown')

    # Новая сессия
    if req.get('session', {}).get('new', False):
        sessionStorage[user_id] = {
            'suggests': ["Не хочу.", "Не буду.", "Отстань!"],
            'attempts': 0
        }
        response['text'] = 'Привет! Купи слона!'
        response['tts'] = 'Привет! Купи слона!'
        response['buttons'] = get_suggests(user_id)
        return response

    # Обрабатываем команду пользователя
    user_command = req.get('request', {}).get('original_utterance', '').lower()

    # Пользователь согласился
    if any(word in user_command for word in ['ладно', 'куплю', 'покупаю', 'хорошо']):
        response['text'] = 'Слона можно найти на Яндекс.Маркете!'
        response['tts'] = 'Слона можно найти на Яндекс.Маркете!'
        response['end_session'] = True
        return response

    # Увеличиваем счетчик отказов
    sessionStorage.setdefault(user_id, {'attempts': 0, 'suggests': []})
    sessionStorage[user_id]['attempts'] += 1

    # Формируем ответ в зависимости от количества попыток
    attempts = sessionStorage[user_id]['attempts']
    if attempts > 3:
        response['text'] = f"Вы уже {attempts} раз отказались! Ну купите слона!"
    else:
        response['text'] = f"Все говорят '{user_command}', а ты купи слона!"

    response['tts'] = response['text']
    response['buttons'] = get_suggests(user_id)

    return response


def get_suggests(user_id):
    """Генерирует подсказки для ответа"""
    suggests = sessionStorage.get(user_id, {}).get('suggests', [])

    buttons = []
    for suggest in suggests[:2]:
        buttons.append(OrderedDict([
            ('title', suggest),
            ('hide', True)
        ]))

    # Добавляем кнопку с ссылкой
    buttons.append(OrderedDict([
        ('title', 'Ладно'),
        ('url', 'https://market.yandex.ru/search?text=слон'),
        ('hide', True)
    ]))

    # Обновляем подсказки для следующего раза
    if suggests:
        sessionStorage[user_id]['suggests'] = suggests[1:] + [suggests[0]]

    return buttons


if __name__ == '__main__':
    app.run()
