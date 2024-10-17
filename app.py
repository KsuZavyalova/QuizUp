from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import PollForm
from models import db, Poll, Option

app = Flask(__name__)

# Конфигурация приложения
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///polls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)

# Создание таблиц в базе данных
with app.app_context():
    db.create_all()

# Главная страница с списком опросов
@app.route('/')
def root():
    polls = Poll.query.all()
    return render_template('index.html', polls=polls)

# Маршрут для обработки голосования
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
                return redirect(url_for('view_results', poll_id=poll.id))
    return render_template('view_poll.html', poll=poll)

# Маршрут для отображения результатов опроса
@app.route('/results/<int:poll_id>')
def view_results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    total_votes = sum(option.votes for option in poll.options)
    return render_template('view_results.html', poll=poll, total_votes=total_votes)

# Маршрут для создания нового опроса
@app.route('/create', methods=['GET', 'POST'])
def create_poll():
    form = PollForm()
    if form.validate_on_submit():
        new_poll = Poll(question=form.question.data)
        db.session.add(new_poll)
        db.session.flush()  # Получить ID нового опроса без коммита

        for option_text in form.options.data:
            option = Option(text=option_text, poll_id=new_poll.id)
            db.session.add(option)
        db.session.commit()
        return redirect(url_for('root'))
    return render_template('create_poll.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)