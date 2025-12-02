# app.py - Ashray Flask Backend with Leo Chatbot (Render.com ready)
from flask import Flask, request, jsonify, render_template, session
import os
from groq import Groq
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="templates/static")
app.secret_key = os.environ.get('SECRET_KEY', 'ashray-ritesh-2025-secret')

# Groq client
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

# Leo's System Prompt
SYSTEM_PROMPT = """Your name is Leo. You are a warm, understanding, and empathetic digital friend and mental health companion..."""  # your full prompt

CRISIS_KEYWORDS = ['suicide', 'kill myself', 'self harm', 'hurt myself', 'end my life',
                   'marna chahta', 'jeena nahi', 'khud ko maar', 'overdose', 'cut myself']

def is_crisis(text):
    return any(keyword in text.lower() for keyword in CRISIS_KEYWORDS)

def get_crisis_response():
    return """Please reach out for immediate help:

India Helplines:
• KIRAN: 1800-599-0019 (24/7)
• Tele-MANAS: 14416
• Emergency: 112

You're not alone. These people care and can help right now. ❤️"""

@app.route('/')
def index(): return render_template('index.html')

@app.route('/Leo')
def leo(): return render_template('Leo.html')

@app.route('/dairy')
def dairy(): return render_template('dairy.html')

@app.route('/letters')
def letters(): return render_template('letters.html')

@app.route('/login')
def login(): return render_template('login.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'Kuch toh bol yaar!'})

    if is_crisis(user_message):
        return jsonify({'response': get_crisis_response()})

    if 'chat_history' not in session:
        session['chat_history'] = []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(session['chat_history'][-10:])
    messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.9,
            max_tokens=150
        )
        response = completion.choices[0].message.content.strip()
        if len(response) > 200:
            response = response[:197] + "..."

        session['chat_history'].append({"role": "user", "content": user_message})
        session['chat_history'].append({"role": "assistant", "content": response})
        if len(session['chat_history']) > 20:
            session['chat_history'] = session['chat_history'][-20:]
        session.modified = True

        return jsonify({'response': response})

    except Exception as e:
        print("Error:", e)
        return jsonify({'response': 'Arre yaar, thodi problem hai. Try again?'})

@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    session.pop('chat_history', None)
    return jsonify({'success': True})

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))