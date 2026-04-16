from flask import Flask, render_template, request, url_for, redirect
import sqlite3

def db_connection(): 
  conn = sqlite3.connect("board.db")
  conn.row_factory = sqlite3.Row
  print("db 연결 완료")

  return conn

def init_db():
  conn = db_connection()
  cursor = conn.cursor()

  cursor.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id NOT NULL UNIQUE, user_ps NOT NULL)""")
  cursor.execute("""CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(100) NOT NULL, body TEXT NOT NULL)""")
  cursor.execute("""INSERT OR IGNORE INTO users(user_id, user_ps) VALUES ('admin', '1234')""")
  
  conn.commit()
  conn.close()

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def login():
  if request.method == 'POST':
    user_id = request.form['user_id']
    user_ps = request.form['user_ps']
    
    conn = db_connection()
    try:
      cursor = conn.cursor()
      sql = f"SELECT * FROM users WHERE user_id = '{user_id}' AND user_ps = '{user_id}'"
      cursor.execute(sql)
      user = cursor.fetchone()

      if user:
        return redirect(url_for('main'))
      else:
        return redirect(url_for('login'))
      
    finally:
      conn.close()

  return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
  if request.method == 'POST':
    user_id = request.form['user_id']
    user_ps = request.form['user_ps']

    conn = db_connection()
    try:
      cursor = conn.cursor()
      sql = f"INSERT INTO users (user_id, user_ps) VALUES ('{user_id}', '{user_ps}')"
      cursor.execute(sql)
      conn.commit()

      return redirect(url_for('login'))
    except sqlite3.IntegrityError:
      return '이미 존재하는 아이디입니다. <a href="/">메인페이지로 돌아가기</a>'
    finally:
      conn.close()

  return render_template('register.html')

@app.route('/main')
def main():
  conn = db_connection()
  try:
    cursor = conn.cursor()

    sql = "SELECT * FROM posts ORDER BY id DESC"
    cursor.execute(sql)

    posts = cursor.fetchall()

  finally:
    conn.close()

  return render_template('main.html', posts=posts)

@app.route('/create', methods = ['GET', 'POST'])
def create():
  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']
    conn = db_connection()
    try:
      cursor = conn.cursor()
      sql = f"INSERT INTO posts (title, body) VALUES ('{title}', '{body}')"
      cursor.execute(sql)
      conn.commit()
      return redirect(url_for('main'))
    
    finally:
      conn.close()

  return render_template('create.html')

@app.route('/read/<int:id>')
def read(id):
  conn = db_connection()
  try:
    cursor = conn.cursor()
    sql = f"SELECT * FROM posts WHERE id = '{id}'"
    cursor.execute(sql)
    post = cursor.fetchone()
    if not post:
      return "존재하지 않는 게시글입니다. <a href="/">메인페이지로 돌아가기</a>"

  finally:
    conn.close()

  return render_template('read.html', post=post)

@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']
    conn = db_connection()
    try:
      cursor = conn.cursor()
      sql = f"UPDATE posts SET title = '{title}', body = '{body}' WHERE id = '{id}'"
      cursor.execute(sql)
      conn.commit()
      return redirect(url_for('main'))
    
    finally:
      conn.close()
  else:
    conn = db_connection()
    try:
      cursor = conn.cursor()
      sql = f"SELECT * FROM posts WHERE id = '{id}'"
      cursor.execute(sql)
      post = cursor.fetchone()
      if not post:
        return '존재하지 않는 게시글입니다. <a href="/">메인페이지로 돌아가기</a>'
    finally:
      conn.close()

  return render_template('update.html', post=post)

@app.route('/delete/<int:id>', methods = ['GET', 'POST'])
def delete(id):
  conn = db_connection()
  try:
    cursor = conn.cursor()
    sql = f"DELETE FROM posts WHERE id = '{id}'"
    cursor.execute(sql)
    conn.commit()
  finally:
    conn.close()
  return '삭제되었습니다. <a href="/main">메인페이지로 돌아가기</a>'

if __name__ == '__main__':
    init_db()
    app.run(port=8081, debug=True)
