from flask import Flask, render_template
import sqlite3

app = Flask(__name__) # Створюємо веб–додаток Flask


def get_all_articles():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM articles''')
    data = cursor.fetchall()
    conn.close()
    return data


def get_article(article_id):
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM articles WHERE id=?''', [article_id])
    data = cursor.fetchone()
    conn.close()
    return data


@app.route("/") # Вказуємо url-адресу для виклику функції
def index():
    message = 'Привіт з пайтону!'
    articles = get_all_articles()
    return render_template("index.html", articles=articles, message=message, name="Володимир") #Результат, що повертається у браузер


@app.route("/article/<int:article_id>")
def article_page(article_id):
    article = get_article(article_id)
    return render_template('article_page.html', article=article)

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)

