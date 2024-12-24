import json
import os
import sys

from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from authlib.integrations.flask_client import OAuth

app = Flask(__name__, static_url_path='', static_folder="static", template_folder="templates")
app.secret_key = "secret key"

login_manager = LoginManager(app)
login_manager.login_view = "login"

oauth = OAuth(app)

github = oauth.register(
    name='github',
    client_id='Ov23liK3LZ0d1iUbaqon',
    client_secret='9fbde05897c16d1d7a62f3c0800116764771c567',
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_users():
    try:
        ensure_directory_exists("instance")  # Убедитесь, что директория существует
        with open("instance/users.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    print("Saving users to file...")  # Отладочный вывод
    ensure_directory_exists("instance")  # Убедитесь, что директория существует
    with open("instance/users.json", "w") as file:
        json.dump(users, file, indent=4)

users = load_users()

class User(UserMixin):
    def __init__(self, user_id, username, provider, provider_id):
        self.id = user_id
        self.username = username
        self.provider = provider
        self.provider_id = provider_id

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id, users[user_id]["username"], users[user_id]["provider"], users[user_id]["provider_id"])
    return None

@app.route("/vk_auth", methods=["POST"])
def vk_login():
    user_obj = request.json
    name = user_obj.get('name', '')  # В случае отсутствия 'name' будет пустая строка
    surname = user_obj.get('surname', '')  # Аналогично для фамилии

    # Сохраняем имя в сессии, чтобы оно было доступно только текущему пользователю
    session['name'] = name
    session['surname'] = surname

    return jsonify({
        'status': 'ok',
    })

@app.route('/')
def index_page():
    # Получаем данные из сессии
    name = session.get('name', None)  # None, если пользователь не авторизован
    surname = session.get('surname', None)
    return render_template("index.html", reg=bool(name), name=name, surname=surname)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            init_db(app)
    else:
        app.run(debug=True, port=8080, host="0.0.0.0")
