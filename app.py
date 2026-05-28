from flask import Flask, render_template, request, jsonify
import random
import os

app = Flask(__name__)

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

@app.route('/')
def index():
    joke = random.choice(get_all_jokes())
    return render_template('index.html', joke=joke)

@app.route('/vote/<direction>', methods=['POST'])
def vote(direction):
    if direction == 'up':
        message = "Спасибо за оценку! 👍"
    elif direction == 'down':
        message = "Жаль, что не понравилось... 😔"
    else:
        return jsonify({'error': 'Неверное значение'}), 400
    
    new_joke = random.choice(get_all_jokes())
    return jsonify({'success': True, 'new_joke': new_joke, 'message': message})

@app.route('/next', methods=['POST'])
def next_joke():
    new_joke = random.choice(get_all_jokes())
    return jsonify({'new_joke': new_joke})

@app.route('/add', methods=['GET', 'POST'])
def add_joke():
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if text:
            with open(USER_JOKES_FILE, 'a', encoding='utf-8') as f:
                f.write(text + '\n')
            return render_template('add.html', success='Анекдот добавлен!')
        else:
            return render_template('add.html', error='Текст не может быть пустым')
    return render_template('add.html')

if __name__ == '__main__':
    print(f"Загружено анекдотов: {len(get_all_jokes())}")
    app.run(debug=True)