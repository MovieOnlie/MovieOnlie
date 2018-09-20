from django.template import loader
from django.contrib.auth import authenticate, login, logout
from .my_util import get_random_str,get_random_color
from django.core.cache import cache
import uuid
import hashlib
from .models import MyUser
from .models import Category,Page
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io

# Create your views here.


def get_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()

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

def my_index(req):
    cate_gory = Category.objects.all()[:8]
    user = req.user
    # 初始化 默认值
    is_login = False
    user_name = ""
    u_icon = ""
    # 判断用户user 是不是MyUser的实例
    if isinstance(user, MyUser):
        # 如果判断通过说明是登录过
        is_login = True
        # 拼接用户头像 req.get_host() 拿到前端浏览器地址栏里输入域名加端口
        u_icon = "http://{host}/static/uploads/{icon_url}".format(
            host=req.get_host(),
            icon_url=user.icon.url
        )
    return render(req,'index.html',{'u_name':user.username,'category':cate_gory,'icon':u_icon})


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
def active(req,random_str):
    res = cache.get(random_str)
    print(res)
    if res:
        #通过邮箱找到对应用户
        #给用户的状态字段做更新，从未激活太编程激活状态
        return HttpResponse(res + "激活成功")
    else:
        return HttpResponse("验证连接无效")
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
                    user_now = req.user
                    # 初始化 默认值
                    is_login = False
                    user_name = ""
                    u_icon = ""
                    # 判断用户user 是不是MyUser的实例
                    if isinstance(user, MyUser):
                        # 如果判断通过说明是登录过
                        is_login = True
                        # 拼接用户头像 req.get_host() 拿到前端浏览器地址栏里输入域名加端口
                        u_icon = "http://{host}/static/uploads/{icon_url}".format(
                            host=req.get_host(),
                            icon_url=user.icon.url
                        )
                    return  render(req,'index.html',{'u_name':user_now.username,'category':cate_gory,'icon':u_icon})
            else:
                return HttpResponse("账号密码错误或未注册")
        else:
            return HttpResponse("请补全信息")

def new_logout(req):
    logout(req)
    return HttpResponse("退出成功")
    # return redirect('new_index')

# 个人中心
def my_person(req):
    user = req.user
    u_icon = "http://{host}/static/uploads/{icon_url}".format(
        host=req.get_host(),
        icon_url=user.icon.url
    )
    return render(req, 'personal.html', {'user': user, 'icon': u_icon})


def my_modify(req):
    if req.method == 'GET':
        return render(req,'modify.html')
    else:
        user = req.user
        params = req.POST
        npwd = params.get('newpwd')
        if npwd == user.password or npwd == '':
            return HttpResponse("密码设置失败")
        else:
            user.set_password(npwd)
            user.save()
            return HttpResponse("修改成功")
