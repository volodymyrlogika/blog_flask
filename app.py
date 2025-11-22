from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__) # Створюємо веб–додаток Flask
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

def get_articles_by_category(category_id):
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
    cursor.execute('''SELECT * FROM comments WHERE article_id=? ORDER BY created_at DESC''', [article_id])
    data = cursor.fetchall()
    conn.close()
    return data

def add_comment(article_id, author_name, author_email, content):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO comments (article_id, author_name, author_email, content) 
                      VALUES (?, ?, ?, ?)''', [article_id, author_name, author_email, content])
    conn.commit()
    conn.close()

def add_article(title, author, content, image, category_id):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO articles (title, author, content, image, category_id) 
                      VALUES (?, ?, ?, ?, ?)''', [title, author, content, image, category_id])
    conn.commit()
    conn.close()


@app.route("/") # Вказуємо url-адресу для виклику функції
def index():
    message = 'Привіт з пайтону!'
    articles = get_all_articles()
    categories = get_all_categories()
    return render_template("index.html", articles=articles, message=message, name="Володимир", categories=categories) #Результат, що повертається у браузер


@app.route("/article/<int:article_id>", methods=['GET', 'POST'])
def article_page(article_id):
    if request.method == 'POST':
        author_name = request.form.get('author_name')
        author_email = request.form.get('author_email')
        content = request.form.get('content')
        
        if author_name and content:
            add_comment(article_id, author_name, author_email, content)
    
    article = get_article(article_id)
    categories = get_all_categories()
    comments = get_comments(article_id)
    return render_template('article_page.html', article=article, categories=categories, comments=comments)

@app.route("/search")
def search_page():
    search = request.args.get('search')
    if not search:
        return render_template('index.html', articles=[])
    
    articles = search_articles(search)
    return render_template('index.html', articles=articles)

@app.route("/category/<int:category_id>")
def category_page(category_id):
    articles = get_articles_by_category(category_id)
    categories = get_all_categories()
    return render_template('index.html', articles=articles, categories=categories)

@app.route("/add_article", methods=['GET', 'POST'])
def add_article_page():
    categories = get_all_categories()
    
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        
        # Обробка зображення
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Додаємо timestamp до імені файлу для унікальності
                import time
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        if title and author and content and category_id:
            add_article(title, author, content, image_filename, category_id)
            return redirect(url_for('index'))
    
    return render_template('add_article.html', categories=categories)


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)

