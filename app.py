from flask_socketio import SocketIO
from threading import Lock
from flask_socketio import SocketIO, emit, disconnect
from flask import Flask, render_template, session
from flask import jsonify
from flask import request
from datetime import datetime
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
from flask import copy_current_request_context

async_mode = None


app = Flask(__name__)
socket_ = SocketIO(app, async_mode=async_mode)
app.config['SECRET_KEY'] = 'secret!'
socket_ = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


@app.route('/')
def index():
    return render_template('index.html',
                           sync_mode=socket_.async_mode)


@app.route('/check', methods=['POST'])
def check():
    question = request.form.get("question")

    # Create a new ChatBot instance
    # chatbot = ChatBot(
    #     'Terminal',
    #     storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
    #     logic_adapters=[
    #         'chatterbot.logic.BestMatch',
    #     ],
    #     database_uri='mongodb://root:abid123@15.185.205.195:27017/oun_production'
    # )

    chatbot = ChatBot('Training Example')
    # trainer = ListTrainer(bot)
    trainer = ChatterBotCorpusTrainer(chatbot)

    # trainer.train(
    #     "chatterbot.corpus.english"
    # )

    trainer.train([
        "Hi, can I help you?",
        "Sure, I'd like to book a flight to Iceland.",
        "Your flight has been booked."
    ])

    print(question)
    # Get a response to the input text 'I would like to book a flight.'
    response = chatbot.get_response(question)
    print(response)

    final_response = {'statusCode': 200, 'message': response.text}

    return jsonify(final_response)


@socket_.on('chat', namespace='/test')
def test_message(message):
    chatbot = ChatBot('Training Example')
    # trainer = ListTrainer(bot)
    trainer = ChatterBotCorpusTrainer(chatbot)

    trainer.train(
        "chatterbot.corpus.english"
    )
    # Get a response to the input text 'I would like to book a flight.'
    response = chatbot.get_response(message['data'])
    print(response)

    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': response.text, 'count': session['receive_count']})
    print(message['data'])
    print(session['receive_count'])


# FOR DISCONNECTING THE REQUESTS
@socket_.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)
