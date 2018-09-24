from django.shortcuts import render,redirect
from df_user.islogin import islogin
from .models import *
from django.http import JsonResponse

# Create your views here.


# 购物车
@islogin
def cart(request):
    uid = request.session['user_id']
    carts = CartInfo.objects.filter(user_id=uid)
    lenn = len(carts)
    context = {'title':'购物车',
             'page_name':1,
             'carts':carts,
             'len':lenn}
    return render(request,'df_cart/cart.html',context)


# 添加商品
@islogin
def add(request, gid, count):
    # 用户uid购买了gid商品，数量为count
    uid = request.session['user_id']
    gid = int(gid)
    count = int(count)
    # 查询购物车是否已经有此商品，有则增加
    carts = CartInfo.objects.filter(user_id=uid, goods_id=gid)
    if len(carts) >= 1:
        cart = carts[0]
        cart.count = cart.count + count
    else:
        # 不存在则直接加
        cart = CartInfo()
        cart.user_id = uid
        cart.goods_id = gid
        cart.count = count
    cart.save()

    count_s = CartInfo.objects.filter(user_id=uid).count()
    request.session['count'] = count_s
    # 如果是ajax请求则返回json，否则转向购物车
    if request.is_ajax():
        return JsonResponse({'count':count_s})
    else:
        return redirect('/cart/')


# 在数据库中增加商品数量
@islogin
def edit(request, cart_id, count):
    try:
        cart = CartInfo.objects.get(pk=int(cart_id))
        count1 = cart.count = int(count)
        cart.save()
        data = {'ok':0}
    except Exception as e:
        data = {'ok':count1}
    return JsonResponse(data)


# 删除购物车中的商品
@islogin
def delete(request, cart_id):
    cart = CartInfo.objects.filter(pk=int(cart_id))
    cart.delete()
    count = CartInfo.objects.filter(user_id=request.session['user_id']).count()
    request.session['count'] = count
    data = {'count':count}
    return JsonResponse(data)





















