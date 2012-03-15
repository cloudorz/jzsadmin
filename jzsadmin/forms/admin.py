# coding: utf-8

from flaskext.wtf import Form, TextAreaField, HiddenField, BooleanField, \
        SubmitField, TextField, ValidationError, SelectField, PasswordField, \
        required, email, equal_to, regexp, optional, length

from jzsadmin.models import City


class LoginForm(Form):
    name = TextField('用户名', validators=[
        required(message="用户名必填")])
    password = PasswordField('密码', validators=[
        required(message="请输入密码")])
    remember = BooleanField(u"记住我")
    
    submit = SubmitField(u"登录")
    next = HiddenField()

def get_cities():
    cities = Cate.query
    res = [(c.label, c.name) for c in cities]

    return res

class EntryForm(Form):
    title = TextField(u"标题", validators=[required(message=u"必填")])
    brief = TextAreaField(u"简介", validators=[required(message=u"必填")])
    desc = TextAreaField(u"描述", validators=[required(message=u"必填")])
    tags = TextField(u"标签", validators=[required(message=u"必填")])
    address = TextField(u"地址", validators=[required(message=u"必填")])
    worktime = TextField(u"服务时间", validators=[required(message=u"必填")])
    serviceitems = TextField(u"服务项目", validators=[required(message=u"必填")])
    serviceareas = TextField(u"服务地区", validators=[required(message=u"必填")])
    contracts = TextField(u"联系号码", validators=[required(message=u"必填")])
    linkman = TextField(u"联系人", validators=[required(message=u"必填")])
    location = TextField(u"经纬度", validators=[required(message=u"必填")])

    submit = SubmitField(u"提交")
    next = HiddenField()

class CateForm(Form):
    name = TextField(u"分类名称", validators=[required(message=u"必填")])
    label = TextField(u"label", validators=[required(message=u"必填")])
    no = TextField(u"序号", validators=[required(message=u"必填")])

    submit = SubmitField(u"提交")
    next = HiddenField()

class CityForm(Form):
    name = TextField(u"城市名称", validators=[required(message=u"必填")])
    label = TextField(u"label", validators=[required(message=u"必填")])
    no = TextField(u"序号", validators=[required(message=u"必填")])

    submit = SubmitField(u"提交")
    next = HiddenField()
