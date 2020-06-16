from flask import Flask, flash, request, jsonify, render_template, Markup
import json, requests
import os
from werkzeug.utils import redirect
from urllib.parse import quote

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.secret_key = "url9876shorten23498key230986"

# open the JSON database file
with open("db.json", "r") as f:
    the_obj = f.read()

# treat the data as JSON
blob = json.loads(the_obj)


# FUNCTION --> convert SHORT ID back to regular ID
def id_to_url(id):
    map = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    shortURL = ""
    # for each digit find the base 62
    while (id > 0):
        shortURL += map[id % 62]
        id //= 62
    # reversing the shortURL
    return shortURL[len(shortURL):: -1]


# FUNCTION --> convert URL to ID
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


# FUNCTION --> ADD URL thru form data
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


# FUNCTION --> GET URL from a SHORT ID
def get_url(id):
    theURL = ''
    for x in blob:
        if blob[x]['short'] == id:
            url = blob[x]['url']
            theURL = url
            comment = blob[x]['comment']
            url_id = blob[x]['id']
            short = blob[x]['short']
            #######
            # print("")
            # print(url_id)
            # print(url)
            # print(short)
            # print(comment)

            return (url)
    return (theURL)


# RETRIEVE A SHORT URL
@app.route('/s/<id>', methods=['GET'])
def goto_url(id):
    website = get_url(id)
    return redirect(website)


# VIEW ALL THE URLS
@app.route('/all', methods=['GET'])
def get_em_all():
    html = '<html><body>'
    tmp_id = ''
    tmp_url = ''
    tmp_short = ''
    for x in blob:
        tmp_id = blob[x]['id']
        tmp_url = blob[x]['url']
        tmp_short = blob[x]['short']
        html += '<b>ID:</b> ' + tmp_id + '<br>'
        html += '<b>URL:</b> ' + tmp_url + '<br>'
        html += '<b>Short:</b>  https://c0nscio.us/s/' + tmp_short + '<br><br>'

    return (html + "</body></html>")


# SHORTEN A URL
@app.route('/shorten', methods=['POST'])
def shorten():
    if 'url' not in request.form:
        return render_template('404.html', errMessage=Markup("<h3>No URL to shorten..</h3>"))

    long_url = request.form['url']

    # start sanitizing the user input...
    if long_url[0:8] == "https://" or long_url[0:7] == "http://":
        # verify the link starts with http or https
        # DIRECTORY TRANSVERSAL ATTACK -->
        # from a link like:   //local/folder/file.conf

        # sanitize the URL by escaping out anything like: <>&' etc that could
        # be used to exploit or inject malicious code.

        sanitized_url = quote(long_url, safe='/:?&,+=-_')
        # sanitized_url = long_url
        shorty = add_url(sanitized_url, request.remote_addr)

        return render_template('test.html',
                               shortURL=Markup("<h4>SHORT URL:  <small><b>" + shorty + "</b></small></h4>"))

    elif long_url[0:4] == "www.":
        # sanitized_url = quote(long_url, safe='/:?&,+=-_')
        sanitized_url = long_url

        shorty = add_url(sanitized_url, request.remote_addr)
        return render_template('test.html',
                               shortURL=Markup("<h4>SHORT URL:  <small><b>" + shorty + "</b></small></h4>"))

    elif long_url[0:2] == "//" or long_url[0:2] == "\\":
        # homie don't play that..
        return render_template('error.html', errMessage=Markup(
            "<h4><b><em>No dice...</em></b></h4><p>Put in a proper link or gtfo, please.<br><small>thank you.</small></p>"))

    else:
        # be lazy and just ask/tell/make them put a proper link:
        return render_template('error.html', errMessage=Markup(
            "<h4><b><em>No dice...</em></b></h4><p>Links need to start with <b><em>https://</em></b>, <b><em>http://</em></b>, or <b><em>www</em></b></p>"))

    return render_template('test.html', shortURL=Markup("<h4>SHORT URL:  <small><b>" + shorty + "</b></small></h4>"))


# MAIN ROUTE
@app.route('/')
def index():
    return render_template('test.html')


# API ROUTE TO SHORTEN URL
@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    if 'url' not in request.form:
        return jsonify({"error": "no URL provided"})

    long_url = request.form['url']

    # start sanitizing the user input...
    if long_url[0:8] == "https://" or long_url[0:7] == "http://" or long_url[0:4] == "www.:
        sanitized_url = quote(long_url, safe='/:?&,+=-_')
        shorty = add_url(sanitized_url, request.remote_addr)
        resp = jsonify({"Success": shorty})
        resp.response_code = 201
        return resp
    else:
        return jsonify({"error": "improper URL provided"})


if __name__ == "__main__":
    app.run(debug=True)
