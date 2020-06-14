from flask import Flask, flash, request, jsonify, render_template, Markup
import json, requests
import os
from werkzeug.utils import redirect


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.secret_key = "url9876shorten23498key230986"


with open("db.json", "r") as f:
    the_obj = f.read()

blob = json.loads(the_obj)


def id_to_url(id):
    map = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    shortURL = ""
    # for each digit find the base 62
    while (id > 0):
        shortURL += map[id % 62]
        id //= 62
    # reversing the shortURL
    return shortURL[len(shortURL):: -1]


def url_to_id(shortURL):
    id = 0
    for i in shortURL:
        val_i = ord(i)
        if (val_i >= ord('a') and val_i <= ord('z')):
            id = id * 62 + val_i - ord('a')
        elif (val_i >= ord('A') and val_i <= ord('Z')):
            id = id * 62 + val_i - ord('Z') + 26
        else:
            id = id * 62 + val_i - ord('0') + 52
    return id


def add_url(url, comment):
    # short-url = add_url("https://afakeurl.com", "a comment")
    nextKey = 0
    nextID = 0

    for x in blob:
        nextKey += 1
        tmp = blob[x]['id']
        # print(tmp)
        if nextKey == len(blob):
            # last
            nextID = int(blob[x]['id']) + 1
            nextKey += 1

    short = id_to_url(nextID)
    blob[nextKey] = {'id': nextID, 'url': url, 'short': short, 'comment': comment}
    with open('db.json', 'w') as f:
        json.dump(blob, f, indent=4)
    return ("https://c0nscio.us/s/" + short)


def get_url(id):
    for x in blob:
        if blob[x]['short'] == id:
            url = blob[x]['url']
            comment = blob[x]['comment']
            url_id = blob[x]['id']
            short = blob[x]['short']
            #######
            #print("")
            #print(url_id)
            #print(url)
            #print(short)
            #print(comment)

            return(url)


# RETRIEVE A SHORT URL
@app.route('/l/<id>', methods=['GET'])
def goto_url(id):
    website = get_url(id)
    return redirect(website)


# SHORTEN A URL
@app.route('/shorten', methods=['POST'])
def shorten():
    if 'url' not in request.form:
        return "No URL"
    shorty = add_url(request.form['url'], 'comment')

    return render_template('test.html', shortURL=Markup("<h4>SHORT URL:  <small><b>" + shorty + "</b></small></h4>"))


# MAIN ROUTE
@app.route('/')
def index():
    return render_template('test.html')


@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    if 'url' not in request.form:
        return jsonify({"error": "no URL provided"})
    shorty = add_url(request.form['url'], 'test')
    return jsonify({"Success": shorty})


if __name__ == "__main__":
    app.run(debug=True)
