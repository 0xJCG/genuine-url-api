import sqlite3

from flask import Flask, request, g, jsonify
from urlparse import urlparse
from tld import get_tld

app = Flask('genuine-url-checker')


DATABASE = '/db/database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('db/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(args=(), one=False):
    query = "SELECT company FROM checked_domains WHERE domain = ? AND tld = ?"
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify(status="online")


@app.route('/check/', methods=['POST'])
def check_url():
    url = request.form['url'].lower().encode('utf8')
    url_object = get_tld(url, as_object=True, fail_silently=True)
    if url_object is not None:
        company = query_db([url_object.domain, url_object.suffix], True)
        if company:
            return jsonify(is_genuine=True, company=company, url=url)
        else:
            return jsonify(is_genuine=False, url=url)
    else:
        return jsonify(error="incorrect url syntax", url=url)


if __name__ == '__main__':
    app.debug = True
    init_db()
    app.run()
