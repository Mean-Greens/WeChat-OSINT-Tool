from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Store words in memory (you might want to use a database in production)
words = set()

@app.route('/api/query', methods=['POST'])
def query_llm():
    data = request.json
    query = data.get('query', '')
    # Here you would typically integrate with your actual LLM
    # For now, we'll just return a mock response
    response = f"Sample response using words: {', '.join(words)}"
    return jsonify({'response': response})

@app.route('/api/words', methods=['GET'])
def get_words():
    return jsonify({'words': list(words)})

@app.route('/api/words', methods=['POST'])
def add_word():
    data = request.json
    word = data.get('word', '').strip()
    if word:
        words.add(word)
    return jsonify({'words': list(words)})

@app.route('/api/words/<word>', methods=['DELETE'])
def remove_word(word):
    words.discard(word)
    return jsonify({'words': list(words)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)