#图片处理
import base64
import binascii
import hashlib
import json
import os
import shutil
import sys
import time
from typing import Container

import cv2
#import memcache
import numpy as np
import pymysql
import requests
# 数据库相关操作
from app01 import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import HttpResponse, render
#检索
from fuzzywuzzy import fuzz, process
#登陆用
from pyDes import CBC, PAD_PKCS5, des
from xpinyin import Pinyin

# Create your views here.







url = "http://127.0.0.1:18081/recognition/prediction"

# with open(os.path.join(".",  imgpath), 'rb') as file:
#     image_data1 = file.read()
# image = cv2_to_base64(image_data1)
# data = {"key": ["image"], "value": [image]}

# for i in range(1):
#     r = requests.post(url=url, data=json.dumps(data))
#     print(r.json())



KEY='mHAxsLYz'      #秘钥
PICTURE_ROOT = './PaddleClas/dataset/retail'



def cv2_to_base64(image):
    return base64.b64encode(image).decode('utf8')


def des_encrypt(s):
    """
    DES 加密
    :param s: 原始字符串
    :return: 加密后字符串，16进制
    """
    secret_key = KEY
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return binascii.b2a_hex(en)


def des_descrypt(s):
    """
    DES 解密
    :param s: 加密后的字符串，16进制
    :return:  解密后的字符串
    """
    secret_key = KEY
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    sessionID = de.split('_')
    openid = sessionID[0]
    return openid


def SKexpired(old_sessionID, code):
    
    s_openid = des_descrypt(old_sessionID)

    appid = "wx433732b2940b7d4c"
    secret = "b4e95c5b998cd13ba9d09e077343f2e7"
    code2SessionUrl = "https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code".format(
        appid=appid, secret=secret, code=code)
    resp = requests.get(code2SessionUrl)
    respDict = resp.json()
    s_session_key = respDict.get("session_key")

    s = str(s_openid) + '_' +str(s_session_key)
    sessionID = des_encrypt(s)

    models.TUser.objects.filter(openid=s_openid).update(session_key=s_session_key) 

    return sessionID


def information():
    container = models.TContainer.objects.all()

    container_all = []
    for i in container:
        temp = []
        temp.append(i.number)  
        temp.append(i.container_name)
        temp.append(i.container_price)
        temp.append(i.picture_address)
        temp.append(i.stock)
        container_all.append(temp)
    
    return container_all


def update():
    container_all = information()
    os.remove('./PaddleClas/dataset/retail/data_update.txt')
             
    with open('./PaddleClas/dataset/retail/data_update.txt','a+',encoding='utf-8') as fh:

        for container_single in container_all:
            container_name = container_single[1]
            container_address = container_single[3]
            fh.write(container_address + '\t' + container_name + '\n')
        fh.close()

    os.system('python3 ./PaddleClas/deploy/python/build_gallery.py -c ./PaddleClas/deploy/configs/build_product.yaml -o IndexProcess.data_file="./PaddleClas/dataset/retail/data_update.txt" -o IndexProcess.index_dir="./PaddleClas/dataset/retail/index_update"')



# 识别模块
def reference(request):
    if request.method == "POST":
        sessionID = request.POST.get('sessionID')
        isSKexpried = request.POST.get('isSKexpried')
        code = request.POST.get('code')
        value = request.POST.get('picture')

        res_all = models.TContainer.objects.all()

        if isSKexpried:
            sessionID = SKexpired(sessionID, code)

        image_name = base64.b64decode(value)
        start_time = time.time()


        image_file = './PaddleClas/dataset/retail/test1.jpg'
        with open(image_file, "wb") as fh:
             fh.write(image_name)
             fh.close()

###      商品识别

        rec_docs_list = []

        price_all = 0.0


        with open(os.path.join(".",  image_file), 'rb') as file:
            image_data1 = file.read()
            image = cv2_to_base64(image_data1)
            data = {"key": ["image"], "value": [image]}

            for i in range(1):
                r = requests.post(url=url, data=json.dumps(data))
                result = r.json()['value'][0]
                result=eval(result)

                if result == []:
                    rec_deplay_str_all = "Please connect root to upload container's name and it's price!\n"
                    return JsonResponse({"state": 'true',"container": rec_deplay_str_all})

                else:   

                    print(type(result))
                    for rec_docs in result:
                        price_all = 0
                        rec_docs_price = []
                        rec_docs_list.append(rec_docs['rec_docs'])

                    number_list = []

                    for rec_docs_sig in rec_docs_list:
                        for res in res_all:
                            if  res.container_name== rec_docs_sig:
                                temp = []
                                rec_price = res.container_price
                                price_all += float(rec_price)
                                number_list.append(res.number)
                                temp.append(rec_docs_sig)
                                temp.append(rec_price)
                                rec_docs_price.append(temp)

                print(rec_docs_price)
                stop_time = time.time()
                print(stop_time-start_time)
             
                return JsonResponse({"state": 'true', "number":number_list ,"container": rec_docs_price, "price_all": price_all, "picture_test":'test1.jpg'})
    else:
        return JsonResponse({"state": 'false'})


#登录

def login_in(request):
    if request.method == "POST":
        code = request.POST.get('code')
        userinfo = request.POST.get('userinfo')
    userinfo = json.loads(userinfo)
    s_nickname = userinfo['nickName']

    appid = "wx433732b2940b7d4c"
    secret = "b4e95c5b998cd13ba9d09e077343f2e7"
    code2SessionUrl = "https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code".format(
        appid=appid, secret=secret, code=code)
    resp = requests.get(code2SessionUrl)
    respDict = resp.json()
    s_openid = respDict.get("openid")    #需要存入的openid
    s_session_key = respDict.get("session_key")    #需要存入的session_key

    s = str(s_openid) + '_' +str(s_session_key)
    sessionID = des_encrypt(s)
    sessionID = str(sessionID)

    old_openid = models.TUser.objects.filter(openid=s_openid)   #old_openid是查询数据库中是否有s_openid，无为空
    old_openid = old_openid.values()
    if not bool(old_openid):                                           #判断表中是否还有对应openid
        s_user = models.TUser(openid = s_openid, nickname = s_nickname, session_key = s_session_key)  
        s_user.save()
        update()
    else:
        models.TUser.objects.filter(openid=s_openid).update(session_key=s_session_key)  #替换session_key


    return JsonResponse({"sessionID": sessionID})


def record(request):             #增加模块
    if request.method == "POST":
        sessionID = request.POST.get('sessionID')
        isSKexpried = request.POST.get('isSKexpried')
        code = request.POST.get('code')
        s_container_name = request.POST.get('container_name')         #商品名称 str
        s_container_price = request.POST.get('container_price')       #商品单价 float
        s_stock = request.POST.get('container_stock')                #商品库存 int

        picture = request.FILES['productimage']   #照片

        if isSKexpried:
            sessionID = SKexpired(sessionID, code)

        value_name = s_container_name
        print(s_container_name)


        p = Pinyin()                 
        name = p.get_pinyin(value_name).replace('-','')
        
        s_picture_address = 'gallery/'+ name + '.jpg'

        with open(os.path.join(PICTURE_ROOT,s_picture_address), 'wb') as fh:
            for chunk in picture.chunks():
                fh.write(chunk)
            fh.close()

        last_data = models.TContainer.objects.last()           #查询t_container表中最后一条数据，以便于商品录入排序
        if not bool(last_data.number):
            s_number = 1                                         #序号
        else:
            s_number = last_data.number + 1
        
        old_container = models.TContainer.objects.filter(container_name=s_container_name)     
        old_container = old_container.values() 
        print(s_stock)

        if not bool(old_container): 

            s_container = models.TContainer(number=s_number, container_name=s_container_name, container_price=s_container_price,stock = s_stock, picture_address=s_picture_address)
            s_container.save()
            update()
            
            print("库存为："+s_stock)

            return JsonResponse({"state": 'true', "sessionID": sessionID})

        else:
            return JsonResponse({"state": 'true', "sessionID": sessionID})
    else:
        return JsonResponse({"state": 'false'})



def delete(request):                #删除模块
    if request.method == "POST":
        sessionID = request.POST.get('sessionID')
        isSKexpried = request.POST.get('isSKexpried')
        code = request.POST.get('code')
        d_number = request.POST.get('number')
        d_container_name = request.POST.get('container_name')

        value_name = d_container_name


        p = Pinyin()                 
        name = p.get_pinyin(value_name).replace('-','')
        
        s_picture_address = os.path.join(PICTURE_ROOT,'gallery/'+ name + '.jpg')
        os.remove(s_picture_address)

        if isSKexpried:
             sessionID = SKexpired(sessionID, code)

        d_number = int(d_number)
        old_container = models.TContainer.objects.filter(number = d_number)     #查询t_container表中所有数据，判断表中是否已经包含目标商品
        old_container = old_container.values()

        if not bool(old_container):                                         #表内不含待删除商品
            return JsonResponse({"state": 'false', "sessionID": sessionID})
        else:
            models.TContainer.objects.filter(number = d_number).delete()
            
            update()
            return JsonResponse({"state": 'true', "sessionID": sessionID})
            
    else:
        return JsonResponse({"state": 'false'})


def replace(request):               #修改模块
    if request.method == "POST":
        sessionID = request.POST.get('sessionID')
        isSKexpried = request.POST.get('isSKexpried')
        code = request.POST.get('code')
        number = request.POST.get('number')
        r_container_name = request.POST.get('container_name')
        r_container_price = request.POST.get('container_price')
        r_stock = request.POST.get('container_stock')
        isimageRevised = request.POST.get('isimageRevised')
        

        if isimageRevised == True:
            r_picture = request.FILES['productimage']
            p = Pinyin()                 
            name = p.get_pinyin(r_container_name).replace('-','')
            s_picture_address = os.path.join(PICTURE_ROOT,'gallery/'+ name + '.jpg')
            with open(s_picture_address, 'wb+') as fh:
                fh.write(r_picture.read())
                fh.close()

        if isSKexpried:
            sessionID = SKexpired(sessionID, code)

            
        numbers = int(number)

        containers = models.TContainer.objects.all()

        for i in containers:
            if i.number == numbers:
                stock = i.stock + int(r_stock)
                break

        models.TContainer.objects.filter(number=number).update(container_name=r_container_name)

        models.TContainer.objects.filter(number=number).update(container_price=r_container_price)

        models.TContainer.objects.filter(number=number).update(stock=stock)

        update()

        return JsonResponse({"state": 'true', "sessionID": sessionID})
        
    else:
        return JsonResponse({"state": 'false'})


def search(request):             #查询模块
    if request.method == "POST":
        sessionID = request.POST.get('sessionID')
        isSKexpried = request.POST.get('isSKexpried')
        code = request.POST.get('code')

        if isSKexpried:
            sessionID = SKexpired(sessionID, code)

        container_all = information()
  
        return JsonResponse({"state": 'true', "sessionID": sessionID, 'container_all': container_all})
    else:
        return JsonResponse({"state": 'false'})


def find(request):    #检索模块
    if request.method== "POST":
        sessionID = request.POST.get('sessionID')
        isSKexpried = request.POST.get('isSKexpried')
        code = request.POST.get('code')
        searchtarget = request.POST.get('searchtarget')

        if isSKexpried:
            sessionID = SKexpired(sessionID, code)

        container = models.TContainer.objects.all()

        find_result = []
        for i in container:
            
            value = fuzz.partial_ratio("%s"%searchtarget,i.container_name)
            
            if value>=80:
                temp = []
                temp.append(i.number)  
                temp.append(i.container_name)
                temp.append(i.container_price)
                temp.append(i.picture_address)
                temp.append(i.stock)
                find_result.append(temp)

        return JsonResponse({"state": 'true', "sessionID": sessionID,"container_all":find_result})
    else:
        return JsonResponse({"state": 'false'})


def stock_sale(request):   #商品销售
    if request.method == "POST":
        sessionID = request.POST.get('sessionID')
        isSKexpried = request.POST.get('isSKexpried')
        code = request.POST.get('code')
        number_s = request.POST.get('numberlist')

        if isSKexpried:
            sessionID = SKexpired(sessionID, code)
        
        print(number_s)
        
        number_s = number_s.split(',')
        number_s = list(map(int, number_s))
        print(number_s)

        classify = []
        container_sale = []

        for i in number_s:
            Temp = []
            if i not in classify:
                Temp.append(i)
                classify.append(i)
                temp = 0
                for j in number_s:
                    if Temp[0] == j:
                        temp = temp + 1
                Temp.append(temp)
                container_sale.append(Temp)

        print(container_sale)

        container = models.TContainer.objects.all()

        for i in container_sale:                    #[['number','stock'],.....]
            for j in container:
                if j.number == i[0]:
                    stock = j.stock - i[1]
                    models.TContainer.objects.filter(number=i[0]).update(stock=stock)
                    break
        return JsonResponse({"state": 'true', "sessionID": sessionID})
    else:
        return JsonResponse({"state": 'false'})



def reference_client(request):
    if request.method == 'POST':
        req = json.loads(request.body) #将json编码的字符串再转换为python的数据结构
        print('req')
        name = req['name']
        img_str = req['image'] #得到unicode的字符串
        img_decode_ = img_str.encode('ascii') #从unicode变成ascii编码
        img_decode = base64.b64decode(img_decode_) #解base64编码，得图片的二进制
        img_np_ = np.frombuffer(img_decode, np.uint8)
        img = cv2.imdecode(img_np_, cv2.COLOR_RGB2BGR) #转为opencv格式
        img_path_client = './PaddleClas/dataset/test_pic/test_client.jpg'
        cv2.imwrite(img_path_client, img) #存储路径
        ###      商品识别
        res_all = models.TContainer.objects.all()

        rec_docs_list = []

        price_all = 0.0

        with open(os.path.join(".",  img_path_client), 'rb') as file:
            image_data1 = file.read()
            image = cv2_to_base64(image_data1)
            data = {"key": ["image"], "value": [image]}

            for i in range(1):
                r = requests.post(url=url, data=json.dumps(data))
                result = r.json()['value'][0]
                result=eval(result)

                if result == []:
                    rec_deplay_str_all = "Please connect root to upload container's name and it's price!\n"
                    return JsonResponse({"state": 'true',"container": rec_deplay_str_all})
                else:   

                    print(type(result))
                    for rec_docs in result:
                        price_all = 0
                        rec_docs_price = []
                        rec_docs_list.append(rec_docs['rec_docs'])

                    print(rec_docs_list)

                    for rec_docs_sig in rec_docs_list:
                        for res in res_all:
                            if  res.container_name== rec_docs_sig:
                                rec_price = res.container_price
                                price_all += float(rec_price)
                                rec_docs_price.append(rec_docs_sig)
                                rec_docs_price.append(rec_price)

                print(rec_docs_price)
                return JsonResponse({"state": 'true',"container": rec_docs_price,"price_all": price_all,"picture_test":'test_client.jpg'})

    else:
        return JsonResponse({"state": 'false'})
