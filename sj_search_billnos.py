#-*- coding: utf-8 -*
import datetime
import time
import json
import jsonpath
import urllib.request
import urllib.parse
from lxml import etree
import cx_Oracle
import xlrd


#获取请求url
search_bill_url = "https://hdgateway.zto.com/WayBill_GetDetail"

#获取请求头
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '23',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'hdgateway.zto.com',
    'Origin': 'https://www.zto.com',
    'Referer': 'https://www.zto.com/express/expressCheck.html?txtBill=73109972743258',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'x-clientCode': 'pc',
}

'''
    1.读取xlsx文件内容
    2. 获取表格列的内容遍历
'''
# ExcelFile=xlrd.open_workbook(r'C:\Users\Administrator\Desktop\zto_searchbill\zt_bills.xlsx')
# sheet=ExcelFile.sheet_by_name('Sheet1')
# rowNum = sheet.nrows
# colNum = sheet.ncols
# list = []
# for i in range(1,rowNum):
#     rowlist = []
#     for j in range(colNum):
#         rowlist.append(sheet.cell_value(i, j))
#         list.append(rowlist[0])
# # print(list)
# bill_list = [x.strip() for x in list if x.strip()!='']
# print(bill_list)
# # print(bill_list[:10])
# # print(len(bill_list[:10]))

#处理提取出来的单号数据
bill_lists = [str(x) for x in range(73109972754000,73109972755000)]
# print(bill_lists)
bill_lists = [bill_lists[i:i+10] for i in range(0,len(bill_lists),10)]
# print(bill_lists)
# for bill_list in bill_lists:
#     print(bill_list)

#日志内容
crawl_date = datetime.datetime.now().strftime('%Y_%m_%d')
print('爬取时间：'+crawl_date)
crawl_datetime = time.strftime('%Y/%m/%d %H:%M:%S ',time.localtime(time.time()))
print("当前时间： ",crawl_datetime)
tab_name = 'table_name'
db_ora = cx_Oracle.connect('username/password@ip/token')
cursor = db_ora.cursor()


#处理请求，获取响应文本
def handle_request(url,bill):
    data = {
        'billCode': bill,
    }
    print("爬取单号：%s..." % (bill))
    try:
        request = urllib.request.Request(url=url,data=urllib.parse.urlencode(data).encode('utf-8'),headers=headers)
    except urllib.error.URLError as e:
        print("单号：%s 无效！" % (bill))
        print(e.reason)
    try:
        response = urllib.request.urlopen(request)
        content = response.read().decode('utf-8')
        print(content)
        print("爬取结束...")
        return content
    except urllib.error.URLError as e:
        print("单号：%s 无效！" % (bill))
        print(e.reason,e.code, e.headers, sep='\n')


#响应文本转化成json字符串
#写入json文件
def parse_content(content,bill):
    str_bill = json.dumps(json.loads(content),ensure_ascii=False)
    # with open('zt.json','a',encoding='utf-8') as fp:
    #     print("录入单号：%s，到json文件中..." % (bill))
    #     if bill == bill_list[0]:
    #             fp.write('[' + '\n' + str_bill + ',' + '\n')
    #     else:
    #         if bill == bill_list[len(bill_list)-1]:
    #             fp.write(str_bill + '\n' + ']')
    #         else:
    #             fp.write(str_bill + ',' + '\n')
    #     print("已经写入json文件...")
    #     fp.close()


'''
    1.从响应文本转化成对象提取key值
    2.拿到key对应的value
    3.形成字段
'''
def parse_json(content):
    item_no = jsonpath.jsonpath(json.loads(content), '$..billCode')[0]
    print(item_no)
    loc_from = jsonpath.jsonpath(json.loads(content), '$..scanSite.city')[-2:-1][0]
    print(loc_from)
    loc_to = jsonpath.jsonpath(json.loads(content), '$..city')[0]
    print(loc_to)
    do_type = jsonpath.jsonpath(json.loads(content), '$..scanType')
    print(do_type)
    do_time = jsonpath.jsonpath(json.loads(content), '$..scanDate')
    print(do_time)
    do_remark = jsonpath.jsonpath(json.loads(content), '$..stateDescription')
    print(do_remark)
    sy_time = time.strftime('%Y/%m/%d %H:%M:%S ', time.localtime(time.time()))
    print(sy_time)
    do_citycode = jsonpath.jsonpath(json.loads(content), '$..scanSite.code')
    print(do_citycode)
    return item_no,loc_from,loc_to,do_type,do_time,do_remark,sy_time,do_citycode


def main():
    for bill_list in bill_lists:
        for bill_no in bill_list:
            print("获取单号：%s" % (bill_no))
            content = handle_request(search_bill_url,bill_no)
            print(content)
            #result判断单号是否能查到轨迹内容
            result = jsonpath.jsonpath(json.loads(content), '$..result')[0]
            print(jsonpath.jsonpath(json.loads(content), '$..result')[0])
            # print(type(result))

            if result != None:
                # parse_content(content,bill_no)
                item_no, loc_from, loc_to, do_type, do_time, do_remark, sy_time, do_citycode = parse_json(handle_request(search_bill_url,bill_no))
                # print(item_no,loc_from,loc_to,do_type,do_time,do_remark,sy_time,do_citycode)
                print(len(do_remark))

                for num in range(len(do_remark)):
                    insert_sql = 'INSERT INTO %s (item_no,loc_from,loc_to,do_type,do_time,do_remark,sy_time,do_citycode) VALUES (:1, :2, :3, :4, :5, :6, :7, :8)' % (tab_name)
                    val = (item_no,loc_from,loc_to,do_type[num],do_time[num],do_remark[num],sy_time,do_citycode[num])
                    # print(insert_sql)
                    cursor.execute(insert_sql, val)
                    # print(val)
                    db_ora.commit()
                    print("插入成功！")
            else:
                print("单号无效!")

            print('*' * 999)
            time.sleep(3)

    cursor.close()
    db_ora.close()


if __name__ == '__main__':
    main()
