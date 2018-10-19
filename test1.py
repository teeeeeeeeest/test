# -*- coding: utf-8 -*-

import pandas as pd
import pymysql
import time
from datetime import datetime
from pyecharts import Bar, Page, Timeline, Line, Overlap
import settings as s


conn = pymysql.connect(host=s.HOST,user=s.USER,password=s.PASSWORD,db=s.DB,charset=s.CHARSET)
conn1 = pymysql.connect(host=s.WEATHER_HOST,user=s.WEATHER_USER,password=s.WEATHER_PASSWORD,db=s.WEATHER_DB,charset=s.WEATHER_CHARSET)

df = pd.DataFrame()
#week_day_dict = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期天'}
df['日期'] = [datetime.strftime(x,'%Y-%m-%d') for x in list(pd.date_range(end=s.END_TIME, periods=s.PERIODS, closed='left'))]
#df['星期'] = [week_day_dict[y] for y in [x.weekday() for x in list(pd.date_range(end=datetime.now(), periods=8, closed='left'))]]

def order(df2,order_count_j,order_count_h,shop_order,*city):
    df_orderj = pd.read_sql(order_count_j.format(city[0],city[0]), con=conn) if city else pd.read_sql(order_count_j, con=conn)
    df_orderh = pd.read_sql(order_count_h.format(city[0],city[0]), con=conn) if city else pd.read_sql(order_count_h, con=conn)
    result = pd.merge(df_orderj,df_orderh,how='outer',on=['日期'])
    if result.size == 0:
        return None
    df_order = pd.merge(df,result,how='outer',on='日期')
#    if df_order['借伞订单'].all() == 0:
#        print(df_order)
#        return None
    df_order = df_order.fillna(0)
    try:
        city_shop = df2[df2['城市']==s.citys[city[0]]]['数量'].tolist()[0] if city else sum(df2['数量'])
    except IndexError:
        return None
    df_order[['借伞订单','借伞收入','借伞用户量','转售','已取消','有效伞桶']] = \
    df_order[['借伞订单','借伞收入','借伞用户量','转售','已取消','有效伞桶']].astype('int64')
    df_order['有效伞桶率'] = df_order['有效伞桶']/city_shop
    df_order['借伞收入'] = df_order['借伞收入']/100
    df_order['平均每单收入'] = df_order['借伞收入']/df_order['还伞订单']
    df_order['单桶订单量'] = df_order['借伞订单']/city_shop
    df_order['单桶借伞用户量'] = df_order['借伞用户量']/city_shop
    df_order['单桶转售量'] = df_order['转售']/city_shop
    df_order['单桶取消量'] = df_order['已取消']/city_shop
    df_shop_order = pd.read_sql(shop_order.format(city[0],city[0]), con=conn) if shop_order else None
    df_order['有效伞桶率'] = df_order['有效伞桶率'].apply(lambda x: format(x, '.1%'))    
    df_order = df_order.fillna(0).round(2)
#    if city:
#        get_weather = pd.read_sql(weather.format(citys[city[0]]), con=conn1)
#        df_order = pd.merge(get_weather,df_order,on='日期')
#        df_order.sort_values('日期', inplace=True)
    return (df_order, df_shop_order) if city else df_order

def shops():   
    df_mob_shop = pd.read_sql(s.mob_shop, con=conn)
    df_mob_shop['city_id'] = df_mob_shop['pid']	
    df_mob_shop.loc[df_mob_shop['pid'] == 0,'city_id'] = df_mob_shop['id']
    def df(x, y):
        df = df_mob_shop[(df_mob_shop['online']==x)&(df_mob_shop['status']==y)].groupby(['city_id'])['city_id'].count().reset_index(name="数量")
        if x == 0:
            df = df_mob_shop[(df_mob_shop['online']==x)&(df_mob_shop['status']==y)&(df_mob_shop['qy_time'] > '2017-12-31')].groupby(['city_id'])['city_id'].count().reset_index(name="数量")
        df['城市'] = [s.citys[x] for x in df['city_id']]
        return df[['城市','数量']]
    return (df(0,2), df(1,2))


def out_bar(df,city):
    attr = [i for i in df['日期']]
    v1 = [i for i in df['借伞订单']]
    v11 = [i for i in df['还伞订单']]
    v2 = [i for i in df['借伞收入']]
    v3 = [i for i in df['借伞用户量']]
    v4 = [i for i in df['转售']]
    v5 = [i for i in df['已取消']]
    v6 = [i for i in df['有效伞桶']]
    v7 = [i for i in df['平均每单收入']]
    bar = Bar("{}近7日关键指标变化".format(city),title_text_size=16)
    bar.add("借伞订单", attr, v1,mark_line=["average"], mark_point=["max", "min"])
    bar.add("还伞订单", attr, v11,mark_line=["average"], mark_point=["max", "min"])
    bar.add("借伞收入", attr, v2,mark_line=["average"], mark_point=["max", "min"])
    bar.add("借伞用户量", attr, v3,mark_line=["average"], mark_point=["max", "min"])
    bar.add("转售", attr, v4,mark_line=["average"], mark_point=["max", "min"])
    bar.add("已取消", attr, v5,mark_line=["average"], mark_point=["max", "min"])
    bar.add("有效伞桶", attr, v6,mark_line=["average"], mark_point=["max", "min"],legend_pos='center',xaxis_name_size=6,xaxis_interval=0)
    line = Line()
    line.add("平均每单收入", attr, v7, yaxis_formatter=" 元")
    overlap = Overlap()
    overlap.add(bar)
    overlap.add(line, yaxis_index=1, is_add_yaxis=True)
    return overlap

def get_pic():
    a = order(df2,s.order_countJA,s.order_countHA,'')
    sz = order(df2,s.order_countJ,s.order_countH,s.shop_order,4)[0]
    gz = order(df2,s.order_countJ,s.order_countH,s.shop_order,42)[0]
    hz = order(df2,s.order_countJ,s.order_countH,s.shop_order,53)[0]
    hk = order(df2,s.order_countJ,s.order_countH,s.shop_order,85)[0]
    sh = order(df2,s.order_countJ,s.order_countH,s.shop_order,11)[0]
    bar_a = out_bar(a,"全国")
    bar_sz  = out_bar(sz,"深圳")
    bar_gz  = out_bar(gz,"广州")
    bar_hz  = out_bar(hz,"杭州")
    bar_hk  = out_bar(hk,"海口")
    bar_sh  = out_bar(sh,"上海")
    timeline = Timeline(is_auto_play=False, timeline_bottom=0)
    timeline.add(bar_a, '全国')
    timeline.add(bar_sz, '深圳')
    timeline.add(bar_gz, '广州')
    timeline.add(bar_hz, '杭州')
    timeline.add(bar_hk, '海口')
    timeline.add(bar_sh, '上海')
    page = Page()
    page.add(timeline)
    page.render('{}数据图.html'.format(time.strftime("%Y%m%d", time.localtime())))

def main():
    global df1, df2
    df1, df2 = shops()[0], shops()[1]
    a = order(df2,s.order_countJA,s.order_countHA,'')
    with open('{}月数据表.csv'.format(time.strftime("%Y%m%d", time.localtime())), 'w', encoding='utf_8_sig') as f:
        f.write("----------------------已审核未上线伞桶数-----------------------")
        f.write("\n")
        df1.to_csv(f,index=False)
        f.write("\n")
        f.write("----------------------已上线伞桶数-----------------------")
        f.write("\n")
        df2.to_csv(f,index=False)
        f.write("\n")
        f.write("----------------------全国7日订单变化-----------------------")
        f.write("\n")
        a.to_csv(f, index=None)
        f.write("\n")
        for city in s.citys.keys():
            print(city)
            try:
                df_order, df_shop_order = order(df2,s.order_countJ,s.order_countH,s.shop_order,city)[0],  order(df2,s.order_countJ,s.order_countH,s.shop_order,city)[1]
                f.write("----------------------{}7日订单变化-----------------------".format(s.citys[city]))
                f.write("\n")
                df_order.fillna(0).round(2).to_csv(f, index=None)
                f.write("\n")
                f.write("----------------------{}7日订单量前五名的伞桶-----------------------".format(s.citys[city]))
                f.write("\n")
                df_shop_order[df_shop_order['COUNT(1)'].rank(ascending=False,method='min')<6].rename(columns={'COUNT(1)':'订单量'}).to_csv(f, index=None)
                f.write("\n")
            except TypeError:
                pass
        

if __name__=='__main__':
    try:
        main()
        get_pic()
    except pymysql.InternalError as e:
        print('Got error {!r}, errno is {}'.format(e, e.args[0]))
        print('Try again...')
        main()
    #except Exception as e:
     #   print(e)
    finally:
        conn.close()
        conn1.close()
