from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date, timedelta

app = Flask(__name__)

def get_db():
    return sqlite3.connect("data.db")

@app.route("/", methods=["GET", "POST"])
def home():
    today = date.today()
    today_str = today.isoformat()

    conn = get_db()
    c = conn.cursor()

    # 体重表
    c.execute("""
        CREATE TABLE IF NOT EXISTS weight (
            day TEXT,
            value REAL
        )
    """)

    # 每日打卡表
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily (
            day TEXT PRIMARY KEY,
            words INTEGER,
            sport INTEGER,
            plan INTEGER
        )
    """)

    if request.method == "POST":
        # 体重
        weight = request.form.get("weight")
        if weight:
            c.execute(
                "INSERT INTO weight (day, value) VALUES (?, ?)",
                (today_str, float(weight))
            )

        # 打卡
        words = 1 if request.form.get("words") else 0
        sport = 1 if request.form.get("sport") else 0
        plan = 1 if request.form.get("plan") else 0

        c.execute("""
            INSERT OR REPLACE INTO daily (day, words, sport, plan)
            VALUES (?, ?, ?, ?)
        """, (today_str, words, sport, plan))

        conn.commit()
        conn.close()
        return redirect("/")

    # 查询体重历史
    c.execute("SELECT day, value FROM weight ORDER BY day DESC")
    weights = c.fetchall()

    # 查询今日打卡
    c.execute("SELECT words, sport, plan FROM daily WHERE day = ?", (today_str,))
    row = c.fetchone()
    daily = row if row else (0, 0, 0)

    # 今日完成率
    done_count = sum(daily)
    completion_rate = int(done_count / 3 * 100)

    # 连续天数
    streak = 0
    d = today
    while True:
        d_str = d.isoformat()
        c.execute(
            "SELECT words, sport, plan FROM daily WHERE day = ?",
            (d_str,)
        )
        r = c.fetchone()
        if r and sum(r) > 0:
            streak += 1
            d -= timedelta(days=1)
        else:
            break

    # 最近 7 天
    last_7_days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        c.execute(
            "SELECT words, sport, plan FROM daily WHERE day = ?",
            (day.isoformat(),)
        )
        r = c.fetchone()
        percent = int(sum(r) / 3 * 100) if r else 0
        last_7_days.append((day.isoformat(), percent))

    conn.close()

    return render_template(
        "index.html",
        today=today_str,
        daily=daily,
        weights=weights,
        completion_rate=completion_rate,
        streak=streak,
        last_7_days=last_7_days
    )
@app.route("/check")
def check():
    return render_template("check.html")

@app.route("/calendar")
def calendar():
    return render_template("calendar.html")
@app.route("/nederlands")
def nederlands():
    return render_template("nederlands.html")
@app.route("/exercise")
def exercise():
    return render_template("exercise.html")
@app.route("/worship")
def worship():
    return render_template("worship.html")


if __name__ == "__main__":
    app.run()