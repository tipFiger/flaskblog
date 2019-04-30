from flask import Blueprint, render_template, request, redirect, url_for, session

# 密码的编码与解码
from werkzeug.security import generate_password_hash, check_password_hash

from back.models import User, ArticleType, db, Article, Notice, Flink
from utils.functools import is_login

back_blue = Blueprint('back', __name__)  # 实例化蓝图

@back_blue.route('/register/', methods=['GET', 'POST'])  # 使用蓝图管理函数
def register():
    if request.method == 'GET':
        return render_template('back/register.html')
    if request.method == 'POST':
        # 获取前端传来的数据
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        # 数据校验
        if username and password and password2:
            # 先校验账号，查询数据库
            user = User.query.filter(User.username == username).first()
            if user:
                error = '用户已存在,请重新注册'
                return render_template('back/register.html', error=error)
            else:
                # 校验密码
                if password2 == password:
                    # 保存数据
                    user = User()
                    user.username = username
                    user.password = generate_password_hash(password)
                    user.save()
                    return redirect(url_for('back.login'))

                else:
                    error = '两次密码不一致，请重新输入'
                    return render_template('back/register.html', error=error)
        else:
            error = '请输入完整数据'
            return render_template('back/register.html', error=error)


@back_blue.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('back/login.html')
    if request.method == 'POST':
        # 获取提交数据数据（post=》form）
        username = request.form.get('username')
        password = request.form.get('password')
        # 数据校验
        if username and password:
            # 先去数据库获取数据
            user = User.query.filter(User.username == username).first()
            if not user:
                error = '账号不存在，请先注册'
                return render_template('back/login.html', error=error)
            if not check_password_hash(user.password, password):
                error = '请核对密码重新输入'
                return render_template('back/login.html', error=error)
            session['user_id'] = user.id  # 状态保持设置session
            return redirect(url_for('back.index') )
        else:
            error = '请填写完整信息'
            return render_template('back/login.html',error=error)


@back_blue.route('/index/', methods=['GET'])
@is_login
def index():
    # 获取session，通过id 拿到用户名  渲染到前端页面
    user_id = session.get('user_id')
    user = User.query.filter(User.id==user_id).first()
    username = user.username    # bug:如果没有注册过这里会报错
    return render_template('back/index.html',username=username)

@back_blue.route('/logout/',methods=['GET'])
@is_login
def logout():
    del session['user_id']
    return redirect(url_for('back.login'))




# ###########################

# 分类相关（显示分类列表）  category.html
@back_blue.route('/a_type/', methods=['GET', 'POST'])
def a_type():
    if request.method == 'GET':
        # 获取所有分类信息
        types = ArticleType.query.all()
        # 渲染到页面
        return render_template('back/category.html',types=types)

# 添加分类,保存信息，然后跳转回分类页面，分类页面获取所有信息
@back_blue.route('/add_category/', methods=['GET', 'POST'])
def add_category():
    if request.method == 'GET':
        return render_template('back/add-category.html')
    if request.method == 'POST':
        atype = request.form.get('atype')
        if atype:
            # 保存分类信息
            art_type = ArticleType()
            art_type.t_name = atype
            db.session.add(art_type)
            db.session.commit()
            return redirect(url_for('back.a_type'))

        else:
            error = '请填写分类信息'
            return render_template('back/add-category.html')

@back_blue.route('/update_category/<int:id>/', methods=['GET', 'POST'])
def update_category(id):
    if request.method == 'GET':
        return render_template('back/update-category.html')
    if request.method == 'POST':
        atype = ArticleType.query.get(id)
        g_name = request.form.get('g_name')
        if g_name:
            atype.t_name = g_name
            atype.save()
            return redirect(url_for('back.a_type'))


# 删除分类
@back_blue.route('/del_type/<int:id>/', methods=['GET', 'POST'])
def del_type(id):
    atype = ArticleType.query.get(id)
    db.session.delete(atype)
    db.session.commit()
    return redirect(url_for('back.a_type'))

# #############################33

# # 后台首页跳转 文章分类列表
@back_blue.route('/article/', methods=['GET', 'POST'])
def article():
    if request.method == 'GET':
        articles = Article.query.all()
        types = ArticleType.query.all()
        return render_template('back/article.html', articles=articles, types=types)
#
# # 分类列表跳转添加分类页面
@back_blue.route('/add_article/',methods=['GET','POST'])
def add_artilce():
    if request.method == 'GET':
        types = ArticleType.query.all()
        return render_template('back/add-article.html', types=types)
    if request.method == 'POST':
        print('sdfsdfs')
        title = request.form.get('title')
        desc = request.form.get('desc')
        category = request.form.get('category')
        content = request.form.get('content')
        if title and desc and category and content:
            # 保存数据
            art = Article()
            art.title = title
            art.desc = desc
            art.content = content
            art.type = category
            db.session.add(art)
            db.session.commit()
            return redirect(url_for('back.article'))
        else:
            error = '请填写完整文章信息'
            return render_template('back/add-article.html', error=error)


@back_blue.route('/update_article/<int:id>/', methods=['GET', 'POST'])
def update_article(id):
    if request.method == 'GET':
        types = ArticleType.query.all()
        return render_template('back/update-article.html', types=types)
    if request.method == 'POST':
        art = Article.query.get(id)
        ctitle = request.form.get('g_title')
        ccontent = request.form.get('g_content')
        cdesc = request.form.get('g_desc')
        ccategory = request.form.get('g_category')
        if ctitle and cdesc and ccontent or ccategory:   # bug 不全部选中无法提交， 分类必须要选中
            art.title = ctitle
            art.content = ccontent
            art.desc = cdesc
            art.type = ccategory
            art.save()
            return redirect(url_for('back.article'))


@back_blue.route('/del_article/<int:id>/', methods=['GET', 'POST'])
def del_article(id):
    a_article = Article.query.get(id)
    db.session.delete(a_article)
    db.session.commit()
    return redirect(url_for('back.article'))


#############################
# 公告功能
@back_blue.route('/notice/', methods=['GET','POST'])
def notice():
    if request.method == 'GET':
        notices = Notice.query.all()
        return render_template('back/notice.html', notices=notices)

# 添加公告
@back_blue.route('/add_notice/', methods=['GET','POST'])
def add_notice():
    if request.method == 'GET':
        return render_template('back/add-notice.html')
    if request.method == 'POST':
        notice = Notice()
        notice.title = request.form.get('title')
        notice.content = request.form.get('content')
        db.session.add(notice)
        db.session.commit()
        return redirect(url_for('back.notice'))
    return render_template('back/add-notice.html',error='请填写完整信息')

#  删除公告
@back_blue.route('/del_notice/<int:id>/',methods=['GET','POST'])
def del_notice(id):
    notice = Notice.query.get(id)
    db.session.delete(notice)
    db.session.commit()
    return redirect(url_for('back.notice'))

# 更新公告
@back_blue.route('/update_notice/<int:id>/',methods=['GET','POST'])
def update_notice(id):
    if request.method == 'GET':
        return render_template('back/update-notice.html')
    if request.method == 'POST':
        notice = Notice.query.get(id)
        utitle = request.form.get('title')
        ucontent = request.form.get('content')
        if utitle or ucontent:
            notice.title = utitle
            notice.content = ucontent
            db.session.add(notice)
            db.session.commit()
            return redirect(url_for('back.notice'))
        else:
            return render_template('back/update-notice.html',error='请填写完整信息')


# ###############################
# 友情连接功能
@back_blue.route('/flink/', methods=['GET','POST'])
def flink():
    if request.method == 'GET':
        flinks = Flink.query.all()
        return render_template('back/flink.html', flinks=flinks)


# 添加链接
@back_blue.route('/add_flink/', methods=['GET','POST'])
def add_flink():
    if request.method == 'GET':
        return render_template('back/add-flink.html')
    if request.method == 'POST':
        flink = Flink()
        flink.lname = request.form.get('name')
        flink.lurl = request.form.get('url')
        db.session.add(flink)
        db.session.commit()
        return redirect(url_for('back.flink'))
#
# # 删除链接
@back_blue.route('/del_flink/<int:id>/',methods=['GET','POST'])
def del_flink(id):
    flink = Flink.query.get(id)
    db.session.delete(flink)
    db.session.commit()
    return redirect(url_for('back.flink'))
#
# # 更新链接
@back_blue.route('/update_flink/<int:id>/',methods=['GET','POST'])
def update_flink(id):
    if request.method == 'GET':
        return render_template('back/update-flink.html')
    if request.method == 'POST':
        flink = Flink.query.get(id)
        utitle = request.form.get('name')
        ulurl = request.form.get('url')
        if utitle or ulurl:
            flink.lname = utitle
            flink.lurl = ulurl
            db.session.add(flink)
            db.session.commit()
            return redirect(url_for('back.flink'))
        return render_template('back/update-flink.html', error='请填写完整信息')






@back_blue.route('/loginlog/', methods=['GET','POST'])
def loginlog():
    return render_template('back/loginlog.html')

@back_blue.route('/manage_user/', methods=['GET','POST'])
def manage_user():
    return render_template('back/manage-user.html')

@back_blue.route('/setting/', methods=['GET','POST'])
def setting():
    return render_template('back/setting.html')


@back_blue.route('/readset/', methods=['GET','POST'])
def readset():
    return render_template('back/readset.html')


# 后台跳转至前台首页
@back_blue.route('/w_index', methods=['GET'])
def w_index():
    return render_template('web/index.html')
