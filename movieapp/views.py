from django.template import loader
from django.contrib.auth import authenticate, login, logout

from helper import week_rank
from .my_util import get_random_str,get_random_color
from django.core.cache import cache
from django.views.decorators.cache import cache_page
import uuid
import hashlib
from .models import MyUser
from .models import Category,Page
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
from django.core.mail import send_mail
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io

# Create your views here.

#生成随机字符串
def get_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()


#生成随机图片验证码
def get_verify_img(req):
    #画布背景颜色
    bg_color = get_random_color()
    img_size = (150,70)
    #实例化一个画布
    image = Image.new("RGB",img_size,bg_color)
    #实例化一个画笔
    draw = ImageDraw.Draw(image,"RGB")
    #设置文本颜色
    # text_color = (255,0,0)
    #创建字体
    font_path ="/home/xiaohuoche/NBteam/MovieOnline/static/fonts/ADOBEARABIC-BOLDITALIC.OTF"
    font = ImageFont.truetype(font_path,30)

    source = "asdfghjklqwertyuiopzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM123456789"
    code_str =""
    for i in range(4):
        text_color = get_random_color()
        tmp_num = random.randrange(len(source))
        random_str = source[tmp_num]
        code_str += random_str
        draw.text((30 + 30*i, 20), random_str, text_color, font)
    req.session['code'] = code_str
    buf = io.BytesIO()
    #将图片保存到缓存区
    image.save(buf,'png')
    #将缓存区的内容，返回给前端
    return HttpResponse(buf.getvalue(),'image/png')


#主页面
def my_index(req):
    cate_gory = Category.objects.all()[:8]
    user = req.user
    print(user.username)
    if isinstance(user, MyUser):
        # 如果判断通过说明是登录过
        # 拼接用户头像 req.get_host() 拿到前端浏览器地址栏里输入域名加端口
        u_icon = "http://{host}{icon_url}".format(
            host=req.get_host(),
            icon_url=user.icon.url
        )
        # print(u_icon)
        return render(req,'index.html',{'u_name':user.username,'category':cate_gory,'icon':u_icon})
    return render(req,'index.html',{'category':cate_gory})


#注册功能
def register(req):
    if req.method =="GET":
        return render(req,"register.html")
    else:
        params = req.POST
        u_name = params.get("u_name")
        u_email = params.get("u_email")
        u_phone = params.get("u_phone")
        pwd = params.get("pwd")
        confirm_pwd = params.get("confirm_pwd")
        icon = req.FILES['u_icon']
        random_str = get_random_str()
        #判断用户的输入是否满足基本要求
        if u_name and len(u_name)>6 and pwd and confirm_pwd and pwd == confirm_pwd:
            # 判断用户是否已经被注册
            exists_flag = MyUser.objects.filter(username=u_name).exists()
            if exists_flag :
                return HttpResponse("该用户被注册")
            else:
                #如果没有被注册，那么就创建用户
                user = MyUser.objects.create_user(username=u_name,email=u_email,password=pwd,phone=u_phone)
                # 生成随机字符
                random_str = get_str()
                # 拼接验证连接
                url = "http://10.3.133.35:8000/homework/active/" + random_str
                # 加载激活模板
                tmp = loader.get_template('active.html')
                # 渲染
                html_str = tmp.render({'url': url})
                print(html_str)

                # 准备邮箱数据
                title = "邮箱验证"
                msg = ""
                email_from = settings.DEFAULT_FROM_EMAIL
                reciever = [
                    u_email,
                ]
                send_mail(title, msg, email_from, reciever, html_message=html_str)
                cache.set(random_str, u_email, 120)
                user.icon = icon
                user.save()
                return render(req,'my_login.html')
        else:
            return HttpResponse("账号密码格式错误")


#邮箱激活
def active(req,random_str):
    res = cache.get(random_str)
    print(res)
    if res:
        #通过邮箱找到对应用户
        #给用户的状态字段做更新，从未激活太编程激活状态
        return HttpResponse(res + "激活成功")
    else:
        return HttpResponse("验证连接无效")


#登录功能
def my_login_v1(req):
    if req.method == 'GET':
        return render(req,'my_login.html')
    else:
        #拿参数
        cate_gory = Category.objects.all()[:8]
        params = req.POST
        u_name = params.get("u_name")
        pwd = params.get("pwd")
        code = params.get("verify_code")
        server_code = req.session.get("code")
        print(code,server_code)
        #校验数据格式
        if u_name and len(u_name)>3 and pwd and len(pwd)>3:
            user = authenticate(username = u_name,password = pwd)
            # print(user)
            if user:
                if server_code.lower() == code.lower():
                    login(req,user)
                    # 初始化 默认值
                    is_login = False
                    # 判断用户user 是不是MyUser的实例
                    if isinstance(user, MyUser):
                        # 如果判断通过说明是登录过
                        is_login = True
                        # 拼接用户头像 req.get_host() 拿到前端浏览器地址栏里输入域名加端口
                        u_icon = "http://{host}/static/uploads/{icon_url}".format(
                            host=req.get_host(),
                            icon_url=user.icon.url
                        )
                    return redirect('my_index')
            else:
                return HttpResponse("账号密码错误或未注册")
        else:
            return HttpResponse("请补全信息")


#登出功能
def new_logout(req):
    logout(req)
    return HttpResponse("退出成功")
    # return redirect('new_index')


# 个人中心
def my_person(req):
    user = req.user
    u_icon = "http://{host}{icon_url}".format(
        host=req.get_host(),
        icon_url=user.icon.url
    )
    return render(req, 'personal.html', {'user': user, 'icon': u_icon})


#修改个人资料
def my_modify(req):
    if req.method == 'GET':
        return render(req, 'modify.html')
    else:
        user = req.user
        params = req.POST
        npwd = params.get("npassword")
        qphone = params.get("qphone")
        print(npwd)
        if npwd == user.password and len(npwd) > 3:
            return HttpResponse('修改失败')
        else:
            user.set_password(npwd)

        if qphone == user.phone and len(qphone) != 11:
            return HttpResponse('修改失败')
        else:
            user.phone = qphone
            user.save()
            return HttpResponse('修改成功')


#一级分类显示
def my_content(req):
    #Category,Page
    user = req.user
    u_name = user.username
    category = Category.objects.all()
    page = Page.objects.all()
    for i in page:
        i.len_name = len(i.name)
        # print(type(i.name))
        pname = i.name
        i.names = pname[0:6] + "..."
    return render(req,'my_content.html',locals())


#分类下的电影显示
def my_contentpage(req,cid):
    user = req.user
    print(user)
    u_name = user.username
    category = Category.objects.all()
    page = Page.objects.filter(category_id = cid)
    for i in page:
        i.len_name = len(i.name)
        # print(type(i.name))
        pname = i.name
        i.names = pname[0:6] + "..."
    print(page[0].len_name)
    return render(req,'my_content.html',locals())


# 搜索功能的实现
def my_query(req):
    my_set =set()
    if req.method == 'GET':
        return render(req, 'my_content.html')
    else:
        params = req.POST
        query = params.get('mquery')
        # print(query)
        page = Page.objects.filter(name__icontains = query)
        print(page)
        for i in page:
            i.len_name = len(i.name)
            pname = i.name
            i.names = pname[0:6] + "..."
    return render(req,'my_content.html',locals())


#排行榜
def seniority(req):
    page = Page.objects.order_by('-views')[:5]
    return render(req,'seniority.html',locals())


#排行榜+redias缓存
def seniority_test(request, id):

    # 加入到周排行中
    week_rank.add_rank(id)

    page = Page.objects.get(pk=id)

    # 获取前5的周点击排行
    rank_ids = week_rank.get_week_rank_ids(5)
    page = [Page.objects.get(pk=id_) for id_ in rank_ids]

    return render(request, 'seniority.html', locals())
