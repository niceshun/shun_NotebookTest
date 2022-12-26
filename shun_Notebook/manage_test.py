
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from mysql_util_test import MysqlUtil
from passlib.hash import sha256_crypt
from functools import wraps
import time
from forms_test import LoginForm, RegisterForm, ArticleForm

app = Flask(__name__)  # 创建应用
app.config['SECRET_KEY'] = 'shun'  # 设置密钥

# 首页
@app.route('/')
def index():
    db = MysqlUtil()  # 实例化数据库类
    count = 3  # 每页显示的博客数量
    page = request.args.get('page')   # 获取当前页码
    if page is None:
        page = 1  # 默认设置页码为1
    # 分页查询
    # 从article表中提取数据，并按照时间降序排列
    sql = f'SELECT * FROM articles ORDER BY create_date DESC LIMIT {(int(page)-1)*count},{count}'
    articles = db.fetchall(sql)  # 获取多条记录
    # 遍历文章数据
    return render_template('home.html', articles=articles, page=int(page))  # 渲染模板

# 关于我们
@app.route('/about')
def about():
    return render_template('about.html')  # 渲染模板

# 笔记详情
@app.route('/article/<string:id>/')
def article(id):
    db = MysqlUtil()  # 实例化数据库类
    sql = "SELECT * FROM articles WHERE id = '%s'" % (id)  # 根据ID查询博客
    article = db.fetchone(sql)  # 获取一条记录
    return render_template('article.html', article=article)  # 渲染模板

# 用户登录
@app.route('/login', methods=['GET','POST'])
def login():
    if "logged_in" in session:    # 如果用户已登录，直接跳转到控制台
        return redirect(url_for("dashboard"))

    form = LoginForm(request.form)   # 实例化表单类
    if form.validate_on_submit():    # 如果提交表单并字段验证通过
        # 从表单中获取数据
        username = request.form['username']
        password_candidate = request.form['password']
        sql = "SELECT * FROM users WHERE username = '%s'" % (username)  # 根据提交的用户名查询user数据库中的数据
        db = MysqlUtil()  # 实例化数据库
        result = db.fetchone(sql)  # 获取一条记录
        password = sha256_crypt.encrypt(result['password'])  # 用户保存于数据库中的密码
        if sha256_crypt.verify(password_candidate, password):  # 用户输入的密码与数据库中的密码做对比
            # 把相应参数写入session中
            session['logged_in'] = True
            session['username'] = username
            flash('登录成功！', 'success') # 闪存登录成功的消息
            return redirect(url_for('dashboard'))  # 跳转到控制台
        else:  # 如果密码错误
            flash('用户名与密码不匹配！', 'danger')  # 闪存密码错误的消息

    return render_template('login.html',form=form)  # 验证失败则继续回到登录页面

# 用户注册
@app.route('/register', methods=['GET','POST'])
def register():
    if "logged_in" in session:    # 如果用户已登录，直接跳转到控制台
        return redirect(url_for('dashboard'))

    form = RegisterForm(request.form)  # 实例化注册表单
    if form.validate_on_submit():   # 提交表单并审核通过
        # 从表单中获取数据
        username = request.form['username']
        email = request.form['email']
        password_candidate = request.form['password']
        re_password_candidate = request.form['re_password']
        if password_candidate == re_password_candidate:
            db = MysqlUtil()
            sql = "INSERT INTO users(username,email,password) VALUES ('%s','%s','%s')" % \
                (username, email, password_candidate)  # 把用户信息输入到数据库
            db.insert(sql)
            flash('注册成功', 'success')
            return redirect(url_for('login'))  # 跳转到登录页面
        else:
            flash('两次密码不相同！','danger')  # 闪存消息

    return render_template('register.html', form=form)

# 如果用户已经登录
def is_logged_in(f):  # 判断登录标志是否在session中
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('无权访问，请先登录！', 'danger')
            return redirect(url_for('login'))
    return wrap

# 退出
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()  # 关闭session
    flash('您已成功退出!', 'success')
    return redirect(url_for('login'))  # 跳转到登录页面

# 控制台
@app.route('/dashboard')
@is_logged_in
def dashboard():
    db = MysqlUtil()
    # 根据作者名称去查询数据库中articles中数据，按照创建日期排序
    sql = "SELECT * FROM articles WHERE author = '%s' ORDER BY create_date DESC" % session['username']
    results = db.fetchall(sql)   # 接收所有的查询记录
    if results:
        return render_template('dashboard.html', articles=results)
    else:
        msg = '暂无笔记记录!'
        return render_template('dashboard.html', msg=msg)

# 添加笔记
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)  # 实例化articles表单
    if request.method == 'POST' and form.validate():   # 判断输入方式以及表单验证是否通过
        # 获取表单中的数据
        title = form.title.data
        content = form.content.data
        author = session['username']
        create_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db = MysqlUtil()  # 实例化数据库
        sql = "INSERT INTO articles(title,content,author,create_date) \
            VALUES ('%s', '%s', '%s', '%s')" % (title, content, author, create_date)  # 插入sql语句
        db.insert(sql)
        flash('创建成功!','success')  # 闪存成功信息
        return redirect(url_for('dashboard'))

    return render_template('add_article.html',form=form)  # 渲染表单

# 编辑笔记
@app.route('/edit_article/<string:id>', methods=['GET','post'])
@is_logged_in
def edit_article(id):
    db = MysqlUtil()
    fetch_sql = "SELECT * FROM articles WHERE id = '%s' and author = '%s' \
                " % (id, session['username'])  # 根据用户名及id搜索博客
    article = db.fetchone(fetch_sql)  # 获取一条记录
    # 检测笔记不存在的时候
    if not article:
        flash('ID错误！','danger')
        return redirect(url_for('dashboard'))
    # 获取表单
    form = ArticleForm(request.form)  # 获取表单
    if request.method == 'POST' and form.validate():  # 验证请求的方法以及验证表单数据
        title = request.form['title']
        content = request.form['content']
        update_sql = "UPDATE articles SET title = '%s', content = '%s' WHERE id = '%s' and author = '%s'"\
            % (title, content, id, session['username'])
        db = MysqlUtil()
        db.update(update_sql)  # 修改数据库中相应博客
        flash('修改成功！', 'success')
        return redirect(url_for('dashboard'))

    # 从数据库中获取表单数据
    form.title.data = article['title']
    form.content.data = article['content']
    return render_template('edit_article.html', form=form)  # 渲染模板

# 删除笔记
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    db = MysqlUtil()  # 实例化数据库类
    sql = "DELETE FROM articles WHERE id = '%s' and author = '%s'" % (id, session['username'])
    db.delete(sql)  # 删除数据库中相应的数据
    flash('删除成功!', 'success')
    return redirect(url_for('dashboard'))  # 跳转到控制台

# 404报告
@app.errorhandler(404)
def page_not_found():
    """
    404
    """
    return render_template("/404.html"),404

# 起始函数
if __name__ == "__main__":
    app.secret_key = "key123456"
    app.run(debug=True)
















































