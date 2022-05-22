#-*-coding:GBK -*- 
import json
import os
import random
from turtle import pos

#-*-coding:GBK -*- 
import pymysql

###���Ĵ���

db = pymysql.connect(host="localhost", user="SM_C", passwd="105316", db="container")
print('���ݿ����ӳɹ���')
cur = db.cursor()
sql = "select * from t_container"
cur.execute(sql)
result = cur.fetchall()
result = list(result)
container_list = []
for row in result:
    container_list.append(list(row))
print(container_list)
db.commit()
cur.close()
db.close()


# �����Ʒ���ƺ������Ľ����б�



import random

from pyecharts import options as opts
from pyecharts.charts import Bar, Funnel, Gauge, Geo, Page, Pie, Scatter3D
from pyecharts.globals import ThemeType


def stock_warining():
    ## �����Ʒ���ƺͿ����������б�

    name_stock = []

    for i in container_list:
        temp = []
        # print(i)
        name = i[2]
        # print(name)
        stock = i[5]
        # print(int(sale))
        temp.append(name)
        temp.append(int(stock))
        name_stock.append(temp)

    name_stock_sort = name_stock
    name_stock_sort.sort(key=lambda x :(x[1]))    # ���ݿ�潵������
    # print(name_stock_sort)

    c = (
        Funnel()
        .add(
            "��Ʒ",
            name_stock_sort[:5],
            sort_="ascending",
            label_opts=opts.LabelOpts(position="center"),
            
        )
        .set_global_opts(title_opts=opts.TitleOpts(title="���漱",
                                                       title_textstyle_opts=opts.TextStyleOpts(color="#F39C12",font_family="����",font_size=20),
                                                       pos_left="0%"),
                                                       legend_opts=opts.LegendOpts(pos_left='20%', type_='scroll',pos_top='5%',inactive_color='#D2E9FF'),)
        # .render("funnel_stock_ascending.html")
    )
    return c

# for m in container_list:

def sale_bar():
    name_sale = []

    for i in container_list:
        temp = []
        name = i[2]
        # print(name)
        sale = i[6]
        # print(int(sale))
        temp.append(name)
        temp.append(int(sale))
        name_sale.append(temp)

    name_sale_sort = name_sale
    name_sale_sort.sort(key=lambda x :(x[1]),reverse = True)    # ����������������
    # print(name_sale_sort)


    name_sale_list = []
    sale_sale_list = []

    n = 0
    for i in name_sale_sort:
        n += 1
        name = i[0]
        sale = i[1]
        name_sale_list.append(name)
        sale_sale_list.append(sale)
        if n == 30:
            break
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
        .add_xaxis(name_sale_list)
        .add_yaxis("����", sale_sale_list)
        .set_series_opts(
                             label_opts=opts.LabelOpts(is_show=True,color="#ABEBC6",font_size=10))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="�������а�",
                                                       title_textstyle_opts=opts.TextStyleOpts(color="#F39C12",font_family="����",font_size=20),
                                                       pos_left="10%",pos_top='5%'),
                                                       legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color="#58D68D")),
                             xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color="#58D68D")),
                             yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color="#58D68D")),
            datazoom_opts=opts.DataZoomOpts(),
        )
        .set_colors(colors='#0080FF')
        # .render("bar_datazoom_slider.html")
    )
    return c


def stock_sale_bar(): #��״ͼ
    # �����Ʒ���ơ������Ϳ��Ľ����б�

    name_sale_stock = []

    for i in container_list:
        temp = []
        name = i[2]
        sale = i[6]
        stock = i[5]
        # print(int(sale))
        temp.append(name)
        temp.append(int(stock))
        temp.append(int(sale))
        name_sale_stock.append(temp)

    name_sale_stock_sort = name_sale_stock
    name_sale_stock_sort.sort(key=lambda x :(x[1]),reverse = True)    # ���ݿ�潵������

    name_sale_stock_name_list = []
    name_sale_stock_stock_list = []
    name_sale_stock_sale_list = []

    n = 0
    for i in name_sale_stock_sort:
        n += 1
        name = i[0]
        stock = i[1]
        sale = i[2]
        name_sale_stock_name_list.append(name)
        name_sale_stock_stock_list.append(stock)
        name_sale_stock_sale_list.append(sale)
        if n == 20:
            break
    cate = name_sale_stock_name_list
    c = (      
         Bar(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
            .add_xaxis(cate)
            .add_yaxis("������", name_sale_stock_stock_list)
            .add_yaxis("�����", name_sale_stock_sale_list)
            .set_series_opts(
                             label_opts=opts.LabelOpts(is_show=True,color="#ABEBC6",font_size=12)
            )
            .set_global_opts(title_opts=opts.TitleOpts(title="���ۿ��Ա�ͼ",
                                                       title_textstyle_opts=opts.TextStyleOpts(color="#F39C12",font_family="����",font_size=20),
                                                       pos_left="5%"),
                             legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color="#ABEBC6")),
                             xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color="#58D68D")),
                             yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color="#58D68D")),
                             datazoom_opts=opts.DataZoomOpts(),
                                                     
            )
            .set_colors(["blue", "green"])
            #.render("bar_stack0.html")
    )
    return c


def tab0(name,color): #����
    c = (Pie().
        set_global_opts(
        title_opts=opts.TitleOpts(title=name,pos_left='center',pos_top='center',
                                title_textstyle_opts=opts.TextStyleOpts(color=color,font_size=40,font_family="��������"))))
    return c
 

 
def gau():#���������
    c = (
        Gauge(init_opts=opts.InitOpts(width="400px", height="400px"))
            .add(series_name="��λ������", data_pair=[["", 90]])
            .set_global_opts(title_opts=opts.TitleOpts(title="���������",
                                                       title_textstyle_opts=opts.TextStyleOpts(color="#F39C12",font_family="����",font_size=20),
                                                       pos_left="20%"),
            legend_opts=opts.LegendOpts(is_show=False),
            tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{a} <br/>{b} : {c}%"),
            
        )
            #.render("gauge.html")
    )
    return c
 
 
# def radius():
#     cate = ['�ͻ�A', '�ͻ�B', '�ͻ�C', '�ͻ�D', '�ͻ�E', '�����ͻ�']
#     data = [153, 124, 107, 99, 89, 46]
#     c=Pie()
#     c.add('', [list(z) for z in zip(cate, data)],
#             radius=["30%", "75%"],
#             rosetype="radius")
#     c.set_global_opts(title_opts=opts.TitleOpts(title="�ͻ����۶�ռ��", padding=[1,250],title_textstyle_opts=opts.TextStyleOpts(color="#FFFFFF")),
#                       legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color="#FFFFFF"),type_="scroll",orient="vertical",pos_right="5%",pos_top="middle")
#                       )
#     c.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
#     c.set_colors(['red',"orange", "yellow", "green", "Cyan", "purple"])
    
#     return c
 
 
# def funnel():
#     cate = ['����', 'ע��', '���빺�ﳵ', '�ύ����', '����ɹ�']
#     data = [30398, 15230, 10045, 8109, 5698]
#     c = Funnel()
#     c.add("�û���", [list(z) for z in zip(cate, data)], 
#                sort_='ascending',
#                label_opts=opts.LabelOpts(position="inside"))
#     c.set_global_opts(title_opts=opts.TitleOpts(title=""))
 
 
#     return c
 
 
def geo():
    city_num = [('�人',105),('�ɶ�',70),('����',99),
            ('����',80),('����',60),('����',34),
            ('�Ϻ�',65),('����',54),('��³ľ��',76),
            ('������',47),('����',56),('����',85)]
    start_end = [('����','�ɶ�'),('�人','����'),('�人','����'),
             ('��ɳ','����'),('�人','����'),('�人','�Ϻ�'),
             ('����','����'),('����','��³ľ��'),('�Ϻ�','������'),
             ('�人','����'),('����','����')]
    c = Geo()
    c.add_schema(maptype='china', 
                itemstyle_opts=opts.ItemStyleOpts(color='#0080FF', border_color='white'))
    # 4.�������
    c.add('', data_pair=city_num, color='white')
    c.add('', data_pair=start_end, type_="lines",label_opts=opts.LabelOpts(is_show=False),
         effect_opts=opts.EffectOpts(symbol="arrow", 
                                     color='gold', 
                                     symbol_size=1))
    c.set_global_opts(
        title_opts = opts.TitleOpts(title="���ŵ��������",
                                                       title_textstyle_opts=opts.TextStyleOpts(color="#F39C12",font_family="����",font_size=20),
                                                       pos_left="20%"),)
    
    return c
 
 
def scatter3D():
    data = [(random.randint(0, 10), random.randint(0, 10), random.randint(0, 10)) for _ in range(80)]
    c = (Scatter3D()
            .add("", data)
            .set_global_opts(
              title_opts=opts.TitleOpts(title="����������",
                                                       title_textstyle_opts=opts.TextStyleOpts(color="#F39C12",font_family="����",font_size=20),
                                                       pos_left="20%"),
            )
        )
    return c
        

from pyecharts.charts import Page

page = Page() 
page.add(
         tab0("�������顪�������������ݿ��ӻ�","#FDFEFE"),
        #  tab0("OFFICETOUCH","#2CB34A"), 
         geo(),
         sale_bar(),
         stock_warining(),
         stock_sale_bar(),
         gau(),
        #  radius(),
        #  funnel(),
         
         scatter3D(),
         )
page.render("../datacenter.html")

from bs4 import BeautifulSoup

with open("datacenter.html", "r+", encoding='utf-8') as html:
    html_bf = BeautifulSoup(html, 'lxml')
    divs = html_bf.select('.chart-container')
    divs[0]["style"] = "width:40%;height:10%;position:absolute;top:0%;left:30%;"   
    divs[1]["style"] = "width:30%;height:50%;position:absolute;top:10%;left:2%;"     
    divs[2]["style"] = "width:40%;height:45%;position:absolute;top:56%;left:2%;"   
    divs[3]["style"] = "width:32%;height:45%;position:absolute;top:12%;left:67%;"  
    divs[4]["style"] = "width:34%;height:40%;position:absolute;top:12%;left:34%;"   
    divs[5]["style"] = "width:45%;height:40%;position:absolute;top:58%;left:32%;"    
    divs[6]["style"] = "width:35%;height:40%;position:absolute;top:55%;left:62%;"   
    # divs[7]["style"] = "width:35%;height:40%;position:absolute;top:50%;left:60%;"
    body = html_bf.find("body")
    body["style"] = "background-image: url(https://img.zcool.cn/community/017d6a5c513b9ca801213f26c6f65d.png@1280w_1l_2o_100sh.png)"  # ������ɫ
    html_new = str(html_bf)
    html.seek(0, 0)
    html.truncate()
    html.write(html_new)
print('Start visualing!')
