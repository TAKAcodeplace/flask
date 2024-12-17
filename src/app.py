# -*- coding: utf-8 -*-
"""Webアプリのサンプルです"""

from datetime import datetime, timedelta
from typing import Dict, List

from flask import Flask, Response, redirect, render_template, request, url_for
from markupsafe import Markup

import omikuji
import school_timetable
import weather_forecast

application = Flask(__name__, static_folder="static", template_folder="templates")

# グローバル変数: 掲示板投稿データのリスト
bulletin_board_posts: List[Dict[str, str]] = []


@application.route("/")
@application.route("/index")
def index() -> str:
    """トップページ"""
    return render_template("./index.html")


@application.route("/tomorrow_plan", methods=["GET", "POST"])
def tomorrow_plan() -> str:
    """明日の予定を表示する"""
    global bulletin_board_posts  # グローバル変数を利用

    # 明日の日付（曜日表示付き）
    DAY_NAME = "月火水木金土日"
    tomorrow_dt = datetime.now() + timedelta(days=1)
    tomorrow_dt_str = f"{tomorrow_dt.strftime('%Y/%m/%d')}({DAY_NAME[tomorrow_dt.weekday()]})"

    # 明日の天気予報
    weather_osaka = weather_forecast.get_osaka_tomorrow_weather()

    # 明日の時間割
    tomorrow_lessons = school_timetable.get_tomorrow_timetable()
    timetable = [[lesson.period, lesson.subject, lesson.classroom, lesson.teacher] for lesson in tomorrow_lessons]

    # おみくじを引く処理
    fortune_result = ""
    fortune_advice = ""
    if request.method == "POST" and "draw_fortune" in request.form:
        fortune = omikuji.draw()
        fortune_result = fortune.result.value
        fortune_advice = fortune.advice

    return render_template(
        "./tomorrow_plan.html",
        date=tomorrow_dt_str,
        weather_area="大阪",
        weather_result=weather_osaka,
        school_timetable=timetable,
        fortune_result=fortune_result,
        fortune_advice=Markup(fortune_advice.replace("\n", "<br>")),
        posts=bulletin_board_posts,  # 掲示板の投稿データをテンプレートに渡す
    )


# 修正


@application.route("/bulletin_board", methods=["POST"])
def bulletin_board() -> Response:
    """掲示板への投稿処理"""
    global bulletin_board_posts  # グローバル変数を利用
    name = request.form.get("name", "匿名")
    content = request.form.get("content", "")
    if content.strip():
        bulletin_board_posts.append(
            {"name": name, "content": content, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        )
    return redirect(url_for("tomorrow_plan"))  # 投稿後にリダイレクト
