# app.py
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import PollForm, RegisterForm, LoginForm
from models import db, User, Poll, Option
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Конфигурация приложения
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на реальный секретный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///polls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Название функции для маршрута входа

# Функция загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Создание таблиц в базе данных (если они еще не существуют)
with app.app_context():
    db.create_all()

# Главная страница с списком опросов
@app.route('/')
def root():
    polls = Poll.query.all()
    return render_template('index.html', polls=polls)

# Маршрут для регистрации пользователей
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Проверяем, существует ли уже пользователь с таким именем
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Имя пользователя уже существует. Пожалуйста, выберите другое.', 'danger')
            return redirect(url_for('register'))
        # Создаем нового пользователя с хэшированным паролем
        hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация успешна. Пожалуйста, войдите в систему.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Маршрут для входа пользователей
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Ищем пользователя по имени
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # Выполняем вход пользователя
            login_user(user)
            flash('Вход выполнен успешно.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('root'))
        else:
            flash('Неправильное имя пользователя или пароль.', 'danger')
    return render_template('login.html', form=form)

# Маршрут для выхода пользователей
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы.', 'success')
    return redirect(url_for('root'))

# Маршрут для создания нового опроса (только для авторизованных пользователей)
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_poll():
    form = PollForm()
    if form.validate_on_submit():
        # Создаем новый опрос
        new_poll = Poll(question=form.question.data)
        db.session.add(new_poll)
        db.session.flush()  # Получить ID нового опроса без коммита

        # Добавляем варианты ответов
        for option_text in form.options.data:
            option = Option(text=option_text, poll_id=new_poll.id)
            db.session.add(option)
        db.session.commit()
        flash('Опрос успешно создан!', 'success')
        return redirect(url_for('root'))
    return render_template('create_poll.html', form=form)

# Маршрут для отображения и голосования по опросу
@app.route('/poll/<int:poll_id>', methods=['GET', 'POST'])
def view_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    if request.method == 'POST':
        selected_option_id = request.form.get('option')
        if selected_option_id:
            option = Option.query.get(int(selected_option_id))
            if option and option.poll_id == poll.id:
                option.votes += 1
                db.session.commit()
                flash('Ваш голос был зачислен!', 'success')
                return redirect(url_for('view_results', poll_id=poll.id))
        flash('Пожалуйста, выберите вариант ответа.', 'warning')
    return render_template('view_poll.html', poll=poll)

# Маршрут для отображения результатов опроса
@app.route('/results/<int:poll_id>')
def view_results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    total_votes = sum(option.votes for option in poll.options)
    return render_template('view_results.html', poll=poll, total_votes=total_votes)

if __name__ == '__main__':
    app.run(debug=True)
