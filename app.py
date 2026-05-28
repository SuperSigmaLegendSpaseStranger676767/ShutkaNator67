from flask import Flask, render_template, request, jsonify
import random
import os
import requests

app = Flask(__name__)

# Адреса микросервисов (при запуске через Docker)
COUNTER_URL = "http://counter:5001"
FILTER_URL = "http://filter:5002"

# Файлы с анекдотами
MAIN_JOKES_FILE = 'Hah.txt'
USER_JOKES_FILE = 'UserJokes.txt'

def get_all_jokes():
    jokes = []
    if os.path.exists(MAIN_JOKES_FILE):
        with open(MAIN_JOKES_FILE, 'r', encoding='utf-8') as f:
            jokes += [line.strip() for line in f if line.strip()]
    if os.path.exists(USER_JOKES_FILE):
        with open(USER_JOKES_FILE, 'r', encoding='utf-8') as f:
            jokes += [line.strip() for line in f if line.strip()]
    if not jokes:
        jokes = ["Анекдотов пока нет"]
    return jokes

def get_random_joke():
    return random.choice(get_all_jokes())

def send_visit_to_counter():
    """Отправляет информацию о посещении в микросервис счётчика"""
    try:
        response = requests.post(f"{COUNTER_URL}/visit", timeout=2)
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка связи со счётчиком: {e}")
        return None

def check_joke_with_filter(text):
    """Проверяет анекдот через фильтр плохих слов"""
    try:
        response = requests.post(
            f"{FILTER_URL}/check",
            json={'text': text},
            timeout=2
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {'approved': True, 'message': 'Фильтр недоступен, анекдот принят'}
    except requests.exceptions.RequestException as e:
        print(f"Ошибка связи с фильтром: {e}")
        return {'approved': True, 'message': 'Фильтр недоступен, анекдот принят'}

@app.route('/')
def index():
    # Отправляем статистику в микросервис (не блокируем ответ)
    try:
        send_visit_to_counter()
    except:
        pass
    
    joke = get_random_joke()
    return render_template('index.html', joke=joke)

@app.route('/vote/<direction>', methods=['POST'])
def vote(direction):
    if direction == 'up':
        message = "Спасибо за оценку! 👍"
    elif direction == 'down':
        message = "Жаль, что не понравилось 😔"
    else:
        return jsonify({'error': 'Неверное значение'}), 400
    
    new_joke = get_random_joke()
    return jsonify({'success': True, 'new_joke': new_joke, 'message': message})

@app.route('/next', methods=['POST'])
def next_joke():
    new_joke = get_random_joke()
    return jsonify({'new_joke': new_joke})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Получает статистику из микросервиса счётчика"""
    try:
        response = requests.get(f"{COUNTER_URL}/stats", timeout=2)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Не удалось получить статистику'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Ошибка: {e}'}), 500

@app.route('/add', methods=['GET', 'POST'])
def add_joke():
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if text:
            # Проверяем через фильтр
            filter_result = check_joke_with_filter(text)
            
            if filter_result.get('approved', False):
                with open(USER_JOKES_FILE, 'a', encoding='utf-8') as f:
                    f.write(text + '\n')
                return render_template('add.html', success='Анекдот добавлен!')
            else:
                return render_template('add.html', error=filter_result.get('message', 'Анекдот не прошёл проверку'))
        else:
            return render_template('add.html', error='Текст не может быть пустым')
    return render_template('add.html')

if __name__ == '__main__':
    print(f"Загружено анекдотов: {len(get_all_jokes())}")
    app.run(debug=True, host='0.0.0.0', port=5000)