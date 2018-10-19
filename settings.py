

citys = {
4:"深圳",
42:"广州",
53:"杭州",
85:"海口",
11:"上海",
201:"福州",
82:"珠海",
80:"惠州",
78:"东莞",
75:"成都",
66:"佛山",
205:"长沙",
206:"南京",
207:"武汉",
211:"重庆",
213:"厦门"
        }



# 查询数据库连接方式
HOST = '120.78.54.149'
USER = 'root'
PASSWORD = 'r5g9PaUziftZ'
DB = 'mobrella_api'
CHARSET = 'utf8'

# 查询天气数据库连接方式
WEATHER_HOST = '192.168.1.254'
WEATHER_USER = 'root'
WEATHER_PASSWORD = 'root!!!'
WEATHER_DB = 'wyh'
WEATHER_CHARSET = 'utf8'

START_TIME = ''
END_TIME = time.strftime("%Y-%m-%d", time.localtime())
PERIODS = 8


weather = '''
SELECT date AS '日期', `day` AS '日间天气', `night` AS '夜间天气' FROM `weather` WHERE city = '{}'
'''

mob_shop = '''
SELECT c.pid, c.id, s.`online`, s.`status`, qy_time
FROM mob_shop s 
LEFT JOIN mob_pail p ON p.shop_id = s.id
INNER JOIN mob_shop_category sc ON sc.id = s.cat_id
INNER JOIN mob_city c ON c.id = s.city_id
WHERE s.is_del = 0 #未删除
AND s.cat_id != 73 #排除地推
AND s.cat_id != 74 #排除地推
AND s.shop_name NOT LIKE "%地推%"
AND s.shop_name NOT LIKE "%测试%"
AND s.shop_name NOT LIKE "%test%"
AND (p.type != 1 or p.type is null)
'''
order_countJ = '''
SELECT DATE_FORMAT(o.borrow_time, "%Y-%m-%d") as '日期' , 
COUNT(IF(o.`status`!=3,1,NULL)) AS '借伞订单',
COUNT(DISTINCT IF(o.`status`!=3,o.user_id,NULL)) AS '借伞用户量',
COUNT(DISTINCT IF(o.`status`!=3,o.pass_id,NULL)) AS '有效伞桶'
FROM mob_order o
INNER JOIN mob_shop so ON o.borrow_shop_id = so.id
LEFT JOIN mob_pail p ON p.shop_id = so.id
INNER JOIN mob_pail_kind k ON p.kind_id = k.id
INNER JOIN mob_shop_category sc ON sc.id = so.cat_id
INNER JOIN mob_city c ON c.id = so.city_id
WHERE (o.borrow_time BETWEEN '2018-08-01' AND '2018-10-01')
AND o.user_id != '766921' # 排除测试
#AND o.from_type = 3 # 支付宝订单
AND so.cat_id != 73 # 排除地推商家
AND so.cat_id != 74 # 排除地推商家
#AND o.is_resale = 0 # 排除转售
#AND o.`status` = 2 # 已完结订单
AND so.`online` = 1 # 已上线的伞桶
AND so.is_del = 0 # 未删除的伞桶
AND DATE(o.borrow_time) != CURDATE()
#AND p.type != 1
AND k.type_name NOT LIKE "%地推%"
AND k.type_name NOT LIKE "%测试%"
AND k.type_name NOT LIKE "%test%"
AND k.type_name NOT LIKE "%拉新%"
AND (c.pid = {} or c.id = {}) # 城市
GROUP BY 日期
'''

order_countH = '''
SELECT DATE_FORMAT(o.finish_time, "%Y-%m-%d") as '日期' , 
COUNT(IF(o.`status`!=3,1,NULL)) AS '还伞订单',
SUM(IF(o.`status`=2 AND o.is_resale=0,payment_amount,NULL)) AS '借伞收入',
COUNT(IF(o.`status`=2 AND o.is_resale!=0,1,NULL)) AS '转售',
COUNT(IF(o.`status`=3,1,NULL)) AS '已取消'
FROM mob_order o
INNER JOIN mob_shop so ON o.borrow_shop_id = so.id
LEFT JOIN mob_pail p ON p.shop_id = so.id
INNER JOIN mob_pail_kind k ON p.kind_id = k.id
INNER JOIN mob_shop_category sc ON sc.id = so.cat_id
INNER JOIN mob_city c ON c.id = so.city_id
WHERE (o.finish_time BETWEEN '2018-08-01' AND '2018-10-01')
AND o.user_id != '766921' # 排除测试
#AND o.from_type = 3 # 支付宝订单
AND so.cat_id != 73 # 排除地推商家
AND so.cat_id != 74 # 排除地推商家
#AND o.is_resale = 0 # 排除转售
#AND o.`status` = 2 # 已完结订单
AND so.`online` = 1 # 已上线的伞桶
AND so.is_del = 0 # 未删除的伞桶
AND DATE(o.finish_time) != CURDATE()
#AND p.type != 1
AND k.type_name NOT LIKE "%地推%"
AND k.type_name NOT LIKE "%测试%"
AND k.type_name NOT LIKE "%test%"
AND k.type_name NOT LIKE "%拉新%"
AND (c.pid = {} or c.id = {}) # 城市
GROUP BY 日期
'''

shop_order = '''
SELECT so.id AS 伞点编号, so.shop_name AS 伞点名称, COUNT(1)
FROM mob_order o
INNER JOIN mob_shop so ON o.borrow_shop_id = so.id
LEFT JOIN mob_pail p ON p.shop_id = so.id
INNER JOIN mob_pail_kind k ON p.kind_id = k.id
INNER JOIN mob_shop_category sc ON sc.id = so.cat_id
INNER JOIN mob_city c ON c.id = so.city_id
WHERE DATE_SUB(CURDATE(), INTERVAL 7 DAY) <=date(o.borrow_time)
AND o.user_id != '766921' # 排除测试
#AND o.from_type = 3 # 支付宝订单
AND so.cat_id != 73 # 排除地推商家
AND so.cat_id != 74 # 排除地推商家
#AND o.is_resale = 0 # 排除转售
#AND o.`status` = 2 # 已完结订单
AND so.`online` = 1 # 已上线的伞桶
AND so.is_del = 0 # 未删除的伞桶
AND DATE(o.borrow_time) != CURDATE()
#AND p.type != 1
AND k.type_name NOT LIKE "%地推%"
AND k.type_name NOT LIKE "%测试%"
AND k.type_name NOT LIKE "%test%"
AND k.type_name NOT LIKE "%拉新%"
AND (c.pid = {} or c.id = {}) # 城市
GROUP BY so.id
ORDER BY COUNT(1) DESC
'''
order_countJA = '''
SELECT DATE_FORMAT(o.borrow_time, "%Y-%m-%d") as '日期' , 
COUNT(IF(o.`status`!=3,1,NULL)) AS '借伞订单',
COUNT(DISTINCT IF(o.`status`!=3,o.user_id,NULL)) AS '借伞用户量',
COUNT(DISTINCT IF(o.`status`!=3,o.pass_id,NULL)) AS '有效伞桶'
FROM mob_order o
INNER JOIN mob_shop so ON o.borrow_shop_id = so.id
LEFT JOIN mob_pail p ON p.shop_id = so.id
INNER JOIN mob_pail_kind k ON p.kind_id = k.id
INNER JOIN mob_shop_category sc ON sc.id = so.cat_id
INNER JOIN mob_city c ON c.id = so.city_id
WHERE (o.borrow_time BETWEEN '2018-08-01' AND '2018-10-01')
AND o.user_id != '766921' # 排除测试
#AND o.from_type = 3 # 支付宝订单
AND so.cat_id != 73 # 排除地推商家
AND so.cat_id != 74 # 排除地推商家
#AND o.is_resale = 0 # 排除转售
#AND o.`status` = 2 # 已完结订单
AND so.`online` = 1 # 已上线的伞桶
AND so.is_del = 0 # 未删除的伞桶
AND DATE(o.borrow_time) != CURDATE()
#AND p.type != 1
AND k.type_name NOT LIKE "%地推%"
AND k.type_name NOT LIKE "%测试%"
AND k.type_name NOT LIKE "%test%"
AND k.type_name NOT LIKE "%拉新%"
GROUP BY 日期
'''

order_countHA = '''
SELECT DATE_FORMAT(o.finish_time, "%Y-%m-%d") as '日期' , 
COUNT(IF(o.`status`!=3,1,NULL)) AS '还伞订单',
SUM(IF(o.`status`=2 AND o.is_resale=0,payment_amount,NULL)) AS '借伞收入',
COUNT(IF(o.`status`=2 AND o.is_resale!=0,1,NULL)) AS '转售',
COUNT(IF(o.`status`=3,1,NULL)) AS '已取消'
FROM mob_order o
INNER JOIN mob_shop so ON o.borrow_shop_id = so.id
LEFT JOIN mob_pail p ON p.shop_id = so.id
INNER JOIN mob_pail_kind k ON p.kind_id = k.id
INNER JOIN mob_shop_category sc ON sc.id = so.cat_id
INNER JOIN mob_city c ON c.id = so.city_id
WHERE (o.finish_time BETWEEN '2018-08-01' AND '2018-10-01')
AND o.user_id != '766921' # 排除测试
#AND o.from_type = 3 # 支付宝订单
AND so.cat_id != 73 # 排除地推商家
AND so.cat_id != 74 # 排除地推商家
#AND o.is_resale = 0 # 排除转售
#AND o.`status` = 2 # 已完结订单
AND so.`online` = 1 # 已上线的伞桶
AND so.is_del = 0 # 未删除的伞桶
AND DATE(o.finish_time) != CURDATE()
#AND p.type != 1
AND k.type_name NOT LIKE "%地推%"
AND k.type_name NOT LIKE "%测试%"
AND k.type_name NOT LIKE "%test%"
AND k.type_name NOT LIKE "%拉新%"
GROUP BY 日期
'''


