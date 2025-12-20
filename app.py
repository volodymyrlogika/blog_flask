from flask import Flask, render_template, request
import sqlite3
import os 

app = Flask(__name__)  # Створюємо веб–додаток Flask

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fdvhifdvhvu13213')

def get_all_articles():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM articles''')
    data = cursor.fetchall()
    conn.close()
    return data


def get_all_categories():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM categories''')
    data = cursor.fetchall()
    conn.close()
    return data


def search_articles(search):
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM articles 
                   WHERE title LIKE ? 
                   OR author LIKE ?
                   ''', ["%"+search+"%", "%"+search+"%"])
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


def get_category_articles(category_id):
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM articles WHERE category_id=?''', [category_id])
    data = cursor.fetchall()
    conn.close()
    return data


def get_comments(article_id):
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM comments WHERE article_id=?''', [article_id])
    data = cursor.fetchall()
    conn.close()
    return data


def add_comment(article_id, email, content):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO comments (article_id, email, content) 
                      VALUES (?, ?, ?)''', (article_id, email, content))
    conn.commit()
    conn.close()


@app.route("/")  # Вказуємо url-адресу для виклику функції
def index():
    message = 'Привіт з пайтону!'
    articles = get_all_articles()
    categories = get_all_categories()
    # Результат, що повертається у браузер
    return render_template("index.html",  articles=articles, categories=categories, message=message, name="Володимир")


@app.route("/article/<int:article_id>", methods=['POST', 'GET'])
def article_page(article_id):
    
    if request.method == 'POST':
        email = request.form.get('email')
        content = request.form.get('content')

        if email and content:
            add_comment(article_id, email, content)

    article = get_article(article_id)
    categories = get_all_categories()
    comments = get_comments(article_id)
    return render_template('article_page.html', article=article, categories=categories, comments=comments)


@app.route("/search")
def search_page():
    categories = get_all_categories()
    search = request.args.get('search')
    if not search:
        return render_template('index.html', articles=[])

    articles = search_articles(search)
    return render_template('index.html', articles=articles, categories=categories)


@app.route("/category/<int:category_id>")
def category_page(category_id):
    categories = get_all_categories()
    articles = get_category_articles(category_id)
    return render_template('index.html', articles=articles, categories=categories)


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
