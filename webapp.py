from flask import Flask, request, render_template
import networkx as nx
import numpy as np

app = Flask(__name__)

imdb = nx.read_edgelist('data/imdb_edges_clean.tsv', delimiter='\t')
movies = np.loadtxt('data/movies_with_difficulty.tsv', dtype=str,
                    delimiter='\t')

length = movies.shape[0]
result = 'correct'
correct, total = 0, 0


@app.route('/')
def home():
    global total, correct
    total = 0
    correct = 0
    return render_template('home.html')


@app.route('/play', methods=['POST'])
def play():
    global movie1, movie2
    difficulty = int(str(request.form['difficulty']))

    movie1, movie2, movie_difficulty = movies[np.random.randint(length)]
    # re-randomize if movie pair is too difficult
    while int(movie_difficulty) > difficulty:
        movie1, movie2, movie_difficulty = movies[np.random.randint(length)]
    return render_template('play.html', movie1=movie1, movie2=movie2,
                           difficulty=difficulty)


@app.route('/results', methods=['POST'])
def results():
    global movie1, movie2
    difficulty = int(str(request.form['difficulty']))

    answers = set(imdb.neighbors(movie1)) & set(imdb.neighbors(movie2))
    good = [ans.lower() for ans in answers]

    global total, correct
    total += 1
    submission = str(request.form['actor_name'].encode('utf-8'))
    answers_html = '<br>'.join(answers)

    if submission.lower() in good:
        correct += 1
        result = 'correct'
    else:
        result = 'incorrect'

    return render_template('results.html', submission=submission,
                           result=result, correct=correct, total=total,
                           answers_html=answers_html, difficulty=difficulty)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
