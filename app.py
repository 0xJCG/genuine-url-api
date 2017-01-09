from flask import Flask, request, g, jsonify
from urlparse import urlparse

app = Flask('genuine-url-checker')


def is_valid_url(url):
    import re
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.match(url) is not None


@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify(status="online")


@app.route('/check/', methods=['POST'])
def check_url():
    url = request.form['url'].lower().encode('utf8')
    if is_valid_url(url):
        web = urlparse(url)
        domain = web.netloc
    else:
        return jsonify(error="incorrect url syntax", url=url)


if __name__ == '__main__':
    app.debug = True
    app.run()
