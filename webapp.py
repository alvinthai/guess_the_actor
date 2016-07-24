from flask import Flask, request
import networkx as nx
import numpy as np


app = Flask(__name__)

G = nx.read_edgelist('data/imdb_edges.tsv', delimiter='\t')
movies = np.loadtxt('data/movie_edges2.tsv', dtype=str, delimiter='\t')

length = movies.shape[0]
result = 'correct'
correct, total = 0, 0


@app.route('/', methods=['GET', 'POST'])
def webapp():
    global movie1, movie2

    if not request.form:
        movie1, movie2 = movies[np.random.randint(length)]
        # check to avoid weird movie titles that start with quotes
        while movie1 != movie1.strip('\"\'') or movie2 != movie2.strip('\"\''):
            movie1, movie2 = movies[np.random.randint(length)]
        return '''
            <form action="" method="post">
                <p>Guess the actor in both these movies!
                <p>Movie 1: {}
                <p>Movie 2: {}
                <p>
                <p><input type=text name=answer>
                <p><input type=submit value=Submit>
            </form>
        '''.format(movie1, movie2)

    else:
        answers = set(G.neighbors(movie1)) & set(G.neighbors(movie2))
        good = [ans.lower().replace('.', '') for ans in answers]
        global total, correct
        total += 1

        if str(request.form['answer']).lower().replace('.', '') in good:
            correct += 1
            result = 'correct'
        else:
            result = 'incorrect'

        return '''
            <p>{} is {}!
            <p>Correct Answers: {}/{}
            <p>
            <body>
                <details>
                    <summary>Reveal Answer(s)</summary>
                        {}
                </details>
            </body>
            <p><br />
            <form action="" method="post">
                <p><input type=submit value='Play Another Round!'>
            </form>
        '''.format(str(request.form['answer']), result, correct, total,
                   '<br />'.join(answers))


if __name__ == '__main__':
    app.run()
