from flask import Flask, render_template, request
from pyshorteners import Shortener

app = Flask(__name__)

def shorten_link(long_link):
    shortener = Shortener()
    return shortener.clckru.short(long_link)


def expand_link(short_link):
    shortener = Shortener()
    return shortener.clckru.expand(short_link)


@app.route('/', methods=['GET', 'POST'])
def link_shorter_page():
    output = None
    if request.method == 'POST':
        long_link = request.form.get('long_link', '')
        output = shorten_link(long_link)
    return render_template('link_shorter_page.html', output=output)


if __name__ == '__main__':
    app.run(debug=True)    
