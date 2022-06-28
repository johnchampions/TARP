from flask import Flask, jsonify, redirect, url_for
from flask_dance.contrib.facebook import facebook
from oauth import github_blueprint
app = Flask(__name__)

app.secret_key = "dev"
app.register_blueprint(github_blueprint, url_prefix='/login')


@app.route("/ping")
def ping():
    return jsonify(ping="pong")

@app.route("/facebook")
def login():
    if not facebook.authorized:
        return redirect(url_for('github.login'))
    res = facebook.get('/user')
    return f"You are @{res.json()['login']} on GitHub"


if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')

