from flask import Flask, render_template, request, escape
from VSearch import search4letters
from random_sample import rnum
from DBcm import UseDatabase

app = Flask(__name__)


'''Главная страничка'''

@app.route('/')
def main_page():
    title = 'Приветвую на главной странице'
    return render_template('MainPage.html',
                            the_title = title)


'''Данные базы данных'''

app.config['dbconfig'] = {'host': '127.0.0.1',
                        'user': 'Darocs',
                        'password': 'DEHIC2005',
                        'database': 'vsearchlogDB'}



'''Сайт с рандомайзером'''



def rlog_request(req: 'flask_request', res: str):
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = '''insert into rlog
                (Min, Max, ip, results)
                values
                (%s, %s, %s, %s)'''

        cursor.execute(_SQL, (req.form['Min'],
                            req.form['Max'],
                            req.remote_addr,
                            res))


'''Ввод данных для рандомайзера'''
@app.route('/rentry')
def retry_page():
    title = 'Приветствую в рандомайзере'
    return render_template('numEnt.html',
                            the_title = title)


'''Результат рандомайзера'''
@app.route('/numRes', methods=['POST'])
def wrnum():
    Min = request.form['Min']
    Max = request.form['Max']
    Min = int(Min)
    Max = int(Max)
    title = 'Твои результаты:'
    results = str(rnum(Min, Max))
    rlog_request(request, results)
    return render_template('numRes.html',
                            the_min = Min,
                            the_max = Max,
                            the_title = title,
                            the_number = results)


'''Логи рандомайзера'''
@app.route('/viewRlog')
def viewRlog_page():
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = '''select Min, Max, ip, results 
                from rlog'''
        cursor.execute(_SQL)
        contents = cursor.fetchall()

    titles = ('Min', 'Max', 'Remote_addr', 'Results')
    return render_template('viewRlog.html',
                            the_title='Отчёты:',
                            the_row_titles=titles,
                            the_data=contents)



'''Сайт с поиском символов в предлоджении'''



def log_request(req: 'flask_request', res: str):
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = '''insert into log3
                (phrase, letters, ip, browser_string, results)
                values
                (%s, %s, %s, %s, %s)'''

        cursor.execute(_SQL, (req.form['phrase'],
                            req.form['letters'],
                            req.remote_addr,
                            req.user_agent.browser,
                            res))


'''Ввод данных для Vsearch'''
@app.route('/entry')
def entry_page():
    return render_template('entry.html',
                           the_title='Приветствую на страничке с поиском символов:')


'''Результат Vsearch'''
@app.route('/search4', methods=['POST'])
def search():
    phrase = request.form['phrase']
    letters = request.form['letters']
    title ='Твои результаты:'
    results = str(search4letters(phrase, letters))
    log_request(request, results)
    return render_template('results.html',
                            the_phrase =  phrase,
                            the_letters = letters,
                            the_title = title,
                            the_results = results)


'''Логи Vsearch'''
@app.route('/viewlog')
def viewlog_page():
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = '''select phrase, letters, ip, results 
                from log3'''
        cursor.execute(_SQL)
        contents = cursor.fetchall()

    titles = ('Фраза', 'Символы', 'Ip компьютера', 'Результат')
    return render_template('viewlog.html',
                            the_title='Отчёты:',
                            the_row_titles=titles,
                            the_data=contents)


'''Запуск сайтов и вывода ошибок'''


if __name__ == '__main__':
    app.run(debug=True)
