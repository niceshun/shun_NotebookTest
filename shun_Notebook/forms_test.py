from wtforms import Form, StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_wtf import FlaskForm
from mysql_util_test import MysqlUtil
from flask import flash

# Login Form Class
class LoginForm(FlaskForm):
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='请输入用户名'),
            Length(min=2, max=25, message='长度在2~25个字符之间')
        ]
    )
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=25, message='长度在6~25个字符之间')
        ]
    )

    def validate_username(self, field):
        sql = "SELECT * FROM users WHERE username = '%s'" % (field.data) # 根据用户名搜索user表中的记录
        db = MysqlUtil()   # 实例化数据库操作类
        result = db.fetchone(sql)  # 获取一条记录
        if not result:
            raise ValidationError("用户名不存在")

# Article Form Class
class ArticleForm(Form):
    title = StringField(
        '标题',
        validators=[
            DataRequired(message='长度在2~30个字符之间'),
            Length(min=2, max=30)
        ]
    )
    content = TextAreaField(
        '内容',
        validators=[
            DataRequired(message='长度不少于5个字符'),
            Length(min=5)
        ]
    )

# Register Form Class
class RegisterForm(FlaskForm):
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='请输入用户名'),
            Length(min=2, max=25, message='长度在4-25个字符之间')
        ]
    )
    email = StringField(
        '邮箱',
        validators=[
            DataRequired(message='请输入电子邮箱'),
            Length(min=2, max=25, message='长度在4-25个字符之间')
        ]
    )
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20, message='长度在6-20个字符之间'),
        ]
    )
    re_password = PasswordField(
        '确认密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20, message='长度在6-20个字符之间'),
        ]
    )
    def validate_username(self,field):
        sql = "SELECT * FROM users  WHERE username = '%s'" % (field.data) # 根据用户名查找user表中记录
        db = MysqlUtil() # 实例化数据库操作类
        result = db.fetchone(sql) # 获取一条记录
        if not result:
            flash('用户名可用！', 'success') # 闪存信息
        else:
            # flash('用户名不可用！', 'danger')  # 闪存信息
            raise ValidationError("用户名不可用！")








































