import json
import os
import subprocess
import time
from datetime import datetime, timedelta

from werkzeug.exceptions import HTTPException

from flask import Flask, abort, redirect, render_template, request, session, url_for
from flask_session import Session

APP_PASSWORD = "0303"
APP_DIR = "/home/momo/piz/flask"

# データ配置用ディレクトリ
DATA_DIR = "/home/momo/piz/flask/ir_data"

MODE_LIST = ["custom"]
COLOR_LIST = ["momo", "w", "r", "g", "b", "c", "m", "y"]
PATTERN_LIST = ["fixed", "blink1", "blink2", "blink3", "fadein", "flash", "rainbow"]


def json_to_dict(input_path: str) -> dict:
    """
    jsonを読み込みdict型で返す
    データディレクトリからのpath
    """
    with open(os.path.join(DATA_DIR, input_path), mode="rt", encoding="utf-8") as f:
        return json.load(f)


def dict_to_json(input_dict: dict, output_path: str) -> None:
    """
    dict型のものをjsonで保存する
    データディレクトリからのpath
    """
    with open(os.path.join(DATA_DIR, output_path), mode="wt", encoding="utf-8") as f:
        json.dump(input_dict, f, ensure_ascii=False, indent=4)
    return None


app = Flask(__name__)
app_prefix = ""

# sessionのシークレットキー
app.secret_key = "momo-pizero"
# sessionの有効期限
app.permanent_session_lifetime = timedelta(hours=72)

# Flask-Sessionの設定
app.config["SESSION_TYPE"] = "filesystem"  # メモリ上に保存
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_USE_SIGNER"] = True

# セッション拡張機能の初期化
Session(app)

# jsonをutf-8にする
app.config["JSON_AS_ASCII"] = False


@app.before_request
def before_request():
    # 全てのリクエストの前に実行

    remote_addr = request.remote_addr
    request_path = request.path
    is_logged_in = "piz_auth" in session

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"{remote_addr} - [{now}] {request.path}")

    request_path_split = request_path.split("/")
    request_path_split = request_path_split + ["", ""]

    # path_not_login_only = ["login"]

    # if is_logged_in:
    #     # ログインしていたらOK
    #     return None

    # elif request_path_split[1] in path_not_login_only:
    #     # ログインしていたらトップへ
    #     if is_logged_in:
    #         return redirect(url_for("index"))
    #     else:
    #         return None

    # elif not is_logged_in:
    #     # ログインしていなかったらログインへ
    #     return redirect(url_for("login", redirect_to=request.url))

    # return abort(403)


@app.errorhandler(HTTPException)
def handle_exception(e):
    return render_template("_http_error.html", e=e), e.code


@app.route(app_prefix + "/")
def index():
    return redirect(url_for("remocon"))


# @app.route(app_prefix + "/login")
# def login():
#     return render_template(
#         "login.html",
#         error=request.args.get("error"),
#     )


# @app.route(app_prefix + "/login", methods=["POST"])
# def login_post():
#     input_password = request.form["input_password"]
#     redirect_to = request.form.get("redirect_to")

#     if input_password == APP_PASSWORD:  # ログイン成功
#         session["piz_auth"] = True
#         # リダイレクト
#         if redirect_to == "None" or redirect_to is None:
#             redirect_to = url_for("index")
#         return redirect(redirect_to)
#     else:  # ログイン失敗
#         return redirect(url_for("login", redirect_to=redirect_to, error=1))


# @app.route(app_prefix + "/logout")
# def logout():
#     session.pop("piz_auth", None)
#     return redirect(url_for("login"))


@app.route(app_prefix + "/remocon")
def remocon():
    return render_template("remocon.html")


@app.route(app_prefix + "/pwr-on")
def r_on():
    subprocess.run("sudo systemctl start ir_signal.service", shell=True)
    return redirect(url_for("remocon"))


@app.route(app_prefix + "/pwr-off")
def r_off():
    subprocess.run("sudo systemctl stop ir_signal.service", shell=True)
    return redirect(url_for("remocon"))


@app.route(app_prefix + "/mode")
def r_mode():
    mode = request.args.get("mode")
    print(mode)
    if mode in MODE_LIST:
        status = json_to_dict("status.json")
        status["mode"] = mode
        status["update"] = "1"
        dict_to_json(status, "status.json")
        return "", 204
    return "", 400


@app.route(app_prefix + "/color")
def r_color():
    color = request.args.get("color")
    print(color)
    if color in COLOR_LIST:
        status = json_to_dict("status.json")
        status["mode"] = "custom"
        status["color"] = color
        status["update"] = "1"
        dict_to_json(status, "status.json")
        return "", 204
    return "", 400


@app.route(app_prefix + "/pattern")
def r_pattern():
    pattern = request.args.get("pattern")
    print(pattern)
    if pattern in PATTERN_LIST:
        status = json_to_dict("status.json")
        status["mode"] = "custom"
        status["pattern"] = pattern
        status["update"] = "1"
        dict_to_json(status, "status.json")
        return "", 204
    return "", 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 3000)),
        debug=True,
    )
