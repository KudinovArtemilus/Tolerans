from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "data.db"

# Создание таблицы при первом запуске
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS manipulators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manipulator TEXT NOT NULL,
            axis TEXT NOT NULL,
            value REAL
        )
        """)
        conn.commit()

# Заполнение стартовыми данными (только если пусто)
def seed_data():
    data = [
      {"Манипулятор":"C2", "Оси":["A1","A2","A3","A4","A5","A6","A7","A8"], "Значения":[50,None,70,30,90,None,None,100]},
      {"Манипулятор":"C1.1", "Оси":["A1","A2","A3","A4","A5","A6","A7","A8"], "Значения":[50,50,60,50,50,None,None,70]},
      {"Манипулятор":"C1.2", "Оси":["A1","A2","A3","A4","A5","A6","A7","A8"], "Значения":[100,60,60,50,50,None,None,50]},
      {"Манипулятор":"C3", "Оси":["A1","A2","A3","A4","A5","A6","A7","A8"], "Значения":[8,None,50,7,80,None,None,8]}
    ]

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM manipulators")
        if cur.fetchone()[0] == 0:  # если пусто — добавим
            for item in data:
                for axis, value in zip(item["Оси"], item["Значения"]):
                    cur.execute("INSERT INTO manipulators (manipulator, axis, value) VALUES (?, ?, ?)",
                                (item["Манипулятор"], axis, value))
        conn.commit()

# Получение таблицы в формате {манипулятор: {ось: значение}}
def get_table():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT manipulator, axis, value FROM manipulators")
        rows = cur.fetchall()
    table = {}
    for manipulator, axis, value in rows:
        if manipulator not in table:
            table[manipulator] = {}
        table[manipulator][axis] = value
    return table

# HTML-шаблон
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Таблица погрешностей манипуляторов С</title>
    <style>
        table { border-collapse: collapse; width: 80%; margin: 20px auto; }
        th, td { border: 1px solid #555; padding: 6px; text-align: center; }
        th { background: #eee; }
        input { width: 60px; text-align: center; }
        button { margin: 10px; padding: 5px 15px; }
    </style>
</head>
<body>
    <h2 style="text-align:center;">Таблица погрешностей манипуляторов С</h2>
    <form method="post">
        <table>
            <tr>
                <th>Манипулятор</th>
                {% for axis in axes %}
                    <th>{{ axis }}</th>
                {% endfor %}
            </tr>
            {% for manipulator, values in table.items() %}
            <tr>
                <td>{{ manipulator }}</td>
                {% for axis in axes %}
                    <td><input type="text" name="{{ manipulator }}-{{ axis }}" value="{{ values.get(axis, '') if values.get(axis) is not none else '' }}"></td>
                {% endfor %}
            </tr>
            {% endfor %}
        </table>
        <div style="text-align:center;">
            <button type="submit">Сохранить</button>
        </div>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            table = get_table()
            for manipulator, values in table.items():
                for axis in values:
                    value = request.form.get(f"{manipulator}-{axis}")
                    value = float(value) if value else None
                    cur.execute("UPDATE manipulators SET value=? WHERE manipulator=? AND axis=?",
                                (value, manipulator, axis))
            conn.commit()
        return redirect(url_for("index"))

    table = get_table()
    # определяем порядок осей (берём из первой строки)
    axes = sorted(next(iter(table.values())).keys())
    return render_template_string(html_template, table=table, axes=axes)


if __name__ == "__main__":
    init_db()
    seed_data()
    app.run(debug=True)
