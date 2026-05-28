from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# Простое хранилище статистики (в памяти)
stats = {
    'total_visits': 0,
    'today_visits': 0,
    'last_visit_date': None
}

def reset_today_if_needed():
    """Обнуляет счётчик сегодняшних посещений, если наступил новый день"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if stats['last_visit_date'] != today:
        stats['today_visits'] = 0
        stats['last_visit_date'] = today

@app.route('/visit', methods=['POST'])
def register_visit():
    """Регистрирует новое посещение"""
    reset_today_if_needed()
    
    stats['total_visits'] += 1
    stats['today_visits'] += 1
    
    return jsonify({
        'success': True,
        'total_visits': stats['total_visits'],
        'today_visits': stats['today_visits']
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Возвращает текущую статистику"""
    reset_today_if_needed()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)