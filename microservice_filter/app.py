from flask import Flask, request, jsonify

app = Flask(__name__)
BAD_WORDS = [
    'дурак', 'идиот', 'тупой', 'дебил', 'урод',
    'мат', 'хер', 'фигня', 'хрень', 'бред', "хуй", "даун"
]

@app.route('/check', methods=['POST'])
def check_text():
    """Проверяет текст на наличие запрещённых слов"""
    data = request.get_json()
    text = data.get('text', '').lower()
    
    # Ищем запрещённые слова
    found_words = []
    for word in BAD_WORDS:
        if word in text:
            found_words.append(word)
    
    if found_words:
        return jsonify({
            'approved': False,
            'message': f'Текст содержит запрещённые слова: {", ".join(found_words)}'
        })
    else:
        return jsonify({
            'approved': True,
            'message': 'Текст прошёл проверку'
        })

@app.route('/health', methods=['GET'])
def health():
    """Проверка, что микросервис работает"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)