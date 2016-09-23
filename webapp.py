from flask import Flask, request, render_template, session
import networkx as nx
import numpy as np
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)   # random cookie

imdb = nx.read_edgelist('data/imdb_edges_clean.tsv', delimiter='\t')
movies = np.loadtxt('data/movies_with_difficulty.tsv', dtype=str,
                    delimiter='\t')

length = movies.shape[0]


@app.route('/')
def home():
    session['total'] = 0
    session['correct'] = 0
    return render_template('home.html')


@app.route('/play', methods=['POST'])
def play():
    session['difficulty'] = int(str(request.form['difficulty']))

    session['movie1'], session['movie2'], session['movie_difficulty'] = \
        movies[np.random.randint(length)]
    # re-randomize if movie pair is too difficult
    while int(session['movie_difficulty']) > session['difficulty']:
        session['movie1'], session['movie2'], session['movie_difficulty'] = \
            movies[np.random.randint(length)]
    return render_template('play.html', difficulty=session['difficulty'],
                           movie1=session['movie1'], movie2=session['movie2'])


@app.route('/results', methods=['POST'])
def results():
    y_pos = int(request.form['y_pos'])
    border_height = int(request.form['border_height'])

    answers = set(imdb.neighbors(session['movie1'])) & \
        set(imdb.neighbors(session['movie2']))
    good = [ans.lower() for ans in answers]

    session['total'] += 1
    submission = str(request.form['actor_name'].encode('utf-8'))
    answers_html = ', '.join(answers)

    if submission.lower() in good:
        session['correct'] += 1
        result = 'correct'
    else:
        result = 'incorrect'

    return render_template('results.html', submission=submission,
                           result=result, correct=session['correct'],
                           total=session['total'], answers_html=answers_html,
                           difficulty=session['difficulty'],
                           y_pos=y_pos, border_height=border_height)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
