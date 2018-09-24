from django.shortcuts import render,redirect
from .models import *
from hashlib import sha1
from django.http import JsonResponse, HttpResponseRedirect
from .islogin import islogin
from df_goods.models import GoodsInfo
from df_order.models import OrderInfo
from django.core.paginator import Paginator
from df_cart.models import *

# Create your views here.


# 接收用户页面路径，返回用户注册的HTML页面路径
def register(request):
    return render(request, 'df_user/register.html')


# 接收用户注册提交按钮路径，处理post请求参数，保存到数据库中，并返回给用户登录界面的html页面路径
def register_handle(request):
    # 接收POST参数
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    uemail = post.get('email')
    upwd2 = post.get('cpwd')
    # 判断用户名是否存在
    if UserInfo.objects.filter(uname=uname).count() != 0:
        return redirect('/user/register/')
    # 判断密码是否一致
    if upwd != upwd2:
        return redirect('/user/register/')
    # 进行密码加密
    s1 = sha1()
    s1.update(upwd.encode("utf8"))
    upwd3 = s1.hexdigest()
    # 把注册信息保存到数据库中
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()
    return redirect('/user/login/')


# 接收js文件数据用于查询用户名是否存在并返回结果
def register_exist(request):
    # 接收get请求的用户名参数
    uname = request.GET.get('uname')
    # 调用数据库查询是否存在，用count()返回数值（0或1）
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count':count})


# 接收登录请求，返回登录页面路径
def login(request):
    # 接收cookies值
    uname = request.COOKIES.get('uname','')
    # 用来处理登录页面一些参数判断
    context= {'title':'用户登录', 'error_name':0, 'error_pwd':0, 'uname':uname}
    return render(request, 'df_user/login.html', context)


# 接收登录请求，判断数据库中是否存在用户数据
def login_handle(request):
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    # 当jizhu有值时,即jizhu被勾选等于1时,返回的数据为1,否则get返回后面的0
    jizhu = post.get('jizhu',0)
    # 查询结果为一个列表
    users = UserInfo.objects.filter(uname=uname)
    # 判断：如果未查到则说明用户名错误，如果查到则判断密码是否正确，如果密码正确，则返回用户中心
    if len(users) == 1:
        s1 = sha1()
        # 给get到的密码进行编码后加密
        s1.update(upwd.encode("utf-8"))
        # 加密后的密码和数据库中的密码进行判断
        if s1.hexdigest() == users[0].upwd:
            # 获取登录之前进入的页面,如果没有,则进入首页
            url = request.COOKIES.get('url', '/')
            # 用变量记住, 方便设置cookie
            red = HttpResponseRedirect(url)
            if jizhu != 0:
                # 设置cookie保存用户名
                red.set_cookie('uname',uname)
            else:
                # max_age指的是过期时间,当为-1时为立刻过期
                red.set_cookie('uname', '', max_age=-1)
            # 把用户id和名字放入session中
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return red
        else:
            context = {'title': '用户登录', 'error_name': 0, 'error_pwd': 1, 'uname': uname, 'upwd': upwd}
            return render(request, 'df_user/login.html', context)
    context = {'title': '用户登录', 'error_name': 1, 'error_pwd': 0, 'uname': uname, 'upwd': upwd}
    return render(request, 'df_user/login.html', context)


# 个人信息
@islogin
def info(request):
    user_email = UserInfo.objects.get(id=request.session['user_id']).uphone
    user_address = UserInfo.objects.get(id=request.session['user_id']).uaddress
    # 最近浏览
    goods_ids = request.COOKIES.get('goods_ids', '')
    goods_id_list = goods_ids.split(',')
    goods_list=[]
    if len(goods_ids):
        for goods_id in goods_id_list:
            goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))

    context = {'title': '用户中心',
               'user_email': user_email,
               'user_name': request.session['user_name'],
               'user_address':user_address,
               'page_name':1,'info':1,
               'goods_list':goods_list}
    return render(request, 'df_user/user_center_info.html', context)


# 订单
@islogin
def order(request, pageid):
    """
        此页面用户展示用户提交的订单，由购物车页面下单后转调过来，也可以从个人信息页面查看
        根据用户订单是否支付、下单顺序进行排序
    """
    # 提取用户ID
    uid = request.session.get('user_id')
    # 订单信息，根据是否支付、下单顺序进行排序
    orderinfos = OrderInfo.objects.filter(user_id=uid).order_by('zhifu', '-oid')
    # 分页
    # 获取orderinfos list  以两个为一页的 list
    paginator = Paginator(orderinfos, 2)
    # 获取 上面集合的第 pageid 个 值
    orderlist = paginator.page(int(pageid))
    # 获取一共多少页
    plist = paginator.page_range
    # 3页分页显示
    qian1 = 0
    hou = 0
    hou2 = 0
    qian2 = 0
    dd = int(pageid)
    lenn = len(plist)
    if dd>1:
        qian1 = dd-1
    if dd>=3:
        qian2 = dd-2
    if dd<lenn:
        hou = dd+1
    if dd+2<=lenn:
        hou2 = dd+2
    # 构造上下文
    context = {'page_name': 1, 'title': '全部订单', 'pageid': int(pageid),
               'order': 1, 'orderlist': orderlist, 'plist': plist,
               'pre':qian1,'next':hou,'pree':qian2,'lenn':lenn,'nextt':hou2}
    return render(request, 'df_user/user_center_order.html', context)


# 收货地址
@islogin
def site(request):
    # 提取用信息
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.ushou =post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uphone = post.get('uphone')
        user.uyoubian = post.get('uyoubian')
        user.save()
    context = {'title': '用户中心', 'user': user,'page_name':1,'site':1}
    return render(request, 'df_user/user_center_site.html', context)


# 退出登录
@islogin
def logout(request):
    request.session.flush()
    return redirect('/')






























