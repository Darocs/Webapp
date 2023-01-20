from flask import Flask, render_template, request, session, copy_current_request_context #Фласк, просто Фласк(Запуск, рендер станички, отправка введённых данных, сессия для авторизации, ещё штучка для параллельной записи)

from VSearch import search4letters #Мой модуль для вывода символов с вписаной строки

from random_sample import rnum #Мой модуль для рандомного числа, используется на странице с рандомайзером 

from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError #Мой модуль для обработки базы данных 

from checker import check_logged_in #Мой модуль для посхалки (в обычных случаях подобные модульи используется для регистрации)

from threading import Thread #Эта фигня для параллельной записи данных в базу даных

from time import sleep

#Переменная для запуска фласка
app = Flask(__name__)

#Пароль для моего модуля 'checker' (в принципе не важно какой он, потому что сайт не в облаке, главное чтобы был) 
app.secret_key = 'DEHIC2005'

#Главная страничка

@app.route('/')
def main_page():
    title = 'Приветвую на главной странице'
    return render_template('MainPage.html',
                            the_title = title)


#Вход

@app.route('/login')
def log_in():
    session['logged_in'] = True
    title = 'Поздраляю, Вы вошли :)'
    return render_template('login.html',
                        the_title = title)


#Выход

@app.route('/logout')
def logout():
    session.pop('logged_in')
    title = 'До свидания :('
    return render_template('logout.html',
                        the_title = title)


#Данные базы данных

app.config['dbconfig'] = {'host': '127.0.0.1',
                        'user': 'Darocs',
                        'password': 'DEHIC2005',
                        'database': 'vsearchlogDB'}



#Сайт рандомайзера



#Ввод данных для рандомайзера
@app.route('/rentry')
def retry_page():
    title = 'Приветствую в рандомайзере'
    return render_template('numEnt.html',
                            the_title = title)


#Результат рандомайзера
@app.route('/numRes', methods=['POST'])
def wrnum():
    @copy_current_request_context
    #Данные которые отправляются в базу данных
    def rlog_request(req: 'flask_request', res: str):
        sleep(5) #Это чисто по приколу с книги (Для понимания как сделать параллельные записи)
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = '''insert into rlog
                    (Min, Max, ip, results)
                    values
                    (%s, %s, %s, %s)'''

            cursor.execute(_SQL, (req.form['Min'],
                                req.form['Max'],
                                req.remote_addr,
                                res))

    Min = request.form['Min']
    Max = request.form['Max']
    Min = int(Min)
    Max = int(Max)
    title = 'Твои результаты'
    results = str(rnum(Min, Max))

#Это предотвращение некотрых ошибок с базой данных   
    try:    
        t = Thread(target=rlog_request, args=(request, results)) #Параллельная запись
        t.start()

    except Exception as err:
        print('***** Logging is failed with this error: ', str(err))

    return render_template('numRes.html',
                            the_min = Min,
                            the_max = Max,
                            the_title = title,
                            the_number = results)


#Логи рандомайзера
@app.route('/viewRlog')
@check_logged_in
def viewRlog_page():

#Это предотвращение некотрых ошибок с базой данных   
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = '''select Min, Max, ip, results 
                    from rlog'''
            cursor.execute(_SQL)
            contents = cursor.fetchall()

        titles = ('Min', 'Max', 'Remote_addr', 'Results')
        return render_template('viewRlog.html',
                                the_title='Отчёты',
                                the_row_titles=titles,
                                the_data=contents)
                                                       
    except ConnectionError as err:
        print('Is your database switched on? Error: ', str(err))

    except CredentialsError as err:
        print('User-id or Password issues. Error:', str(err))

    except SQLError as err:
        print('Is your query correct? Error: ', str(err))

    except Exception as err:
        print('Something went wrong: ', str(err))



#Сайт для поиском символов в предлоджении



#Ввод данных для Vsearch
@app.route('/entry')
def entry_page():
    return render_template('entry.html',
                           the_title='Приветствую на страничке с поиском символов')


#Результат Vsearch
@app.route('/search4', methods=['POST'])
def search():

#Данные которые отправляются в базу данных
    @copy_current_request_context
    def log_request(req: 'flask_request', res: str):
        sleep(5) #Это чисто по приколу с книги (Для понимания как сделать параллельные записи)
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

    phrase = request.form['phrase']
    letters = request.form['letters']
    title ='Твои результаты'
    results = str(search4letters(phrase, letters))

#Это предотвращение некотрых ошибок с базой данных   
    try:    
        t = Thread(target=log_request, args=(request, results))
        t.start()

    except Exception as err:
        print('***** Logging is failed with this error: ', str(err))

    return render_template('results.html',
                            the_phrase =  phrase,
                            the_letters = letters,
                            the_title = title,
                            the_results = results)


#Логи Vsearch
@app.route('/viewlog')
@check_logged_in
def viewlog_page():

#Это предотвращение некотрых ошибок с базой данных   
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = '''select phrase, letters, ip, results 
                    from log3'''
            cursor.execute(_SQL)
            contents = cursor.fetchall()

        titles = ('Фраза', 'Символы', 'Ip компьютера', 'Результат')
        return render_template('viewlog.html',
                                the_title='Отчёты',
                                the_row_titles=titles,
                                the_data=contents)

    except ConnectionError as err:
        print('Is your database switched on? Error: ', str(err))

    except CredentialsError as err:
        print('User-id or Password issues. Error:', str(err))

    except SQLError as err:
        print('Is your query correct? Error: ', str(err))

    except Exception as err:
        print('Something went wrong: ', str(err))


#Запуск сайта и вывода ошибок


if __name__ == '__main__':
    app.run(debug=True)
