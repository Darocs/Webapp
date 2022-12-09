from flask import Flask, render_template, request, escape
from VSearch import search4letters
from Random import rnum
import mysql.connector

app = Flask(__name__)


def rlog_request(req: 'flask_request', res: str):

    dbconfig = {'host': '127.0.0.1',
                'user': 'Darocs',
                'password': 'DEHIC2005',
                'database': 'vsearchlogDB'}

    conn = mysql.connector.connect(**dbconfig)

    cursor = conn.cursor()

    _SQL = '''insert into rlog
            (Min, Max, ip, results)
            values
            (%s, %s, %s, %s)'''

    cursor.execute(_SQL, (req.form['Min'],
                        req.form['Max'],
                        req.remote_addr,
                        res))

    conn.commit()

    cursor.close()

    conn.close()


def log_request(req: 'flask_request', res: str):

    dbconfig = {'host': '127.0.0.1',
                'user': 'Darocs',
                'password': 'DEHIC2005',
                'database': 'vsearchlogDB'}

    conn = mysql.connector.connect(**dbconfig)

    cursor = conn.cursor()

    _SQL = '''insert into log3
            (phrase, letters, ip, browser_string, results)
            values
            (%s, %s, %s, %s, %s)'''

    cursor.execute(_SQL, (req.form['phrase'],
                        req.form['letters'],
                        req.remote_addr,
                        req.user_agent.browser,
                        res))

    conn.commit()

    cursor.close()

    conn.close()

@app.route('/search4', methods=['POST'])
def search():
    phrase = request.form['phrase']
    letters = request.form['letters']
    title ='Here are you results:'
    results = str(search4letters(phrase, letters))
    log_request(request, results)
    return render_template('results.html',
                            the_phrase =  phrase,
                            the_letters = letters,
                            the_title = title,
                            the_results = results)

@app.route('/')
@app.route('/entry')
def entry_page():
    return render_template('entry.html',
                           the_title='Welcome to search4letters on the web!')


@app.route('/rentry')
def retry_page():
    title = 'Welcom to random number page'
    return render_template('numEnt.html',
                            the_title = title)


@app.route('/numRes', methods=['POST'])
def wrnum():
    Min = request.form['Min']
    Max = request.form['Max']
    Min = int(Min)
    Max = int(Max)
    title = 'Here your resulst:'
    results = str(rnum(Min, Max))
    rlog_request(request, results)
    return render_template('numRes.html',
                            the_min = Min,
                            the_max = Max,
                            the_title = title,
                            the_number = results)


@app.route('/viewlog')
def viewlog_page():
    contents = []
    with open('numlog.log') as log:
        for line in log:
            contents.append([])
            for item in line.split('|'):
                contents[-1].append(escape(item))
    titles = ('Form Data', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                            the_title='Here your logs!',
                            the_row_titles=titles,
                            the_data=contents,)

if __name__ == '__main__':
    app.run(debug=True)
