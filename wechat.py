#_author:   86502
#_date:   2018/8/12 12:28
import itchat
import pymysql
from contextlib import closing
import requests
import time
from requests.exceptions import RequestException
import random
import json


def get_msg():
    data_list = []
    db = pymysql.connect(host="localhost", user="root", password="WangKang19921225+", db="goods", port=3306)  # 服务器登录信息
    cur = db.cursor()
    sql = "select * from test4"  # 表名
    try:
        i = 0
        cur.execute(sql)   # 获取指针
        results = cur.fetchall()
        for row in results:  # 迭代表中数据
            id = row[0]
            shop_url = row[1]
            pic_url = row[2]
            name = row[3]
            num = row[4]
            price = row[5]
            origin_price = row[6]
            sku_arr = row[7]
            data_list.append((id, shop_url, pic_url, name, num, price, origin_price, sku_arr))  # 存入列表
            i += 1
        return data_list
    except Exception as e:
        raise e
    finally:
        db.close()


def sent_chat_rooms_msg(name, context, tim):
    user_name = ""
    itchat.get_chatrooms(update=True)  # 获取所有聊天室信息
    my_room = itchat.search_chatrooms(name)  # 查找目标聊天室
    for room in my_room:
        if room['NickName'] == name:
            user_name = room['UserName']  # 获取目标聊天室user_name
            break
    try:
        print("sending...")
        f = "C:/Users/86502/PycharmProjects/untitled2/picture.png"  # 图片存储地址
        itchat.send_image(f, user_name)  # 发送图片
        rd_num = random.randint(1, 2)
        time.sleep(2 * rd_num)
        itchat.send_msg(context, user_name)  # 发送信息
        time.sleep(tim * rd_num)
        print("msg send successfully")
        return user_name
    except:
        print("failed to send msg")


def download_image(url):   # 图片下载
    try:
        with closing(requests.get(url, stream=True)) as response:
            with open('picture.png', 'wb') as file:
                for data in response.iter_content(128):
                    file.write(data)
    except RequestException:
        print("picture print failed")


def get_chat_name():
    name_list = list()
    needed_list = list()
    mps_list = itchat.get_chatrooms()
    for i in mps_list:
        name_list.append(i["NickName"])
    for i in name_list:
        print(i)
        choice = input("如果需要该群组，请输入'1',否则输入'0' :")
        if choice == "1":
            needed_list.append(i)
    return needed_list


def time_set():
    while True:
        tim_str = input("请输入每条消息的间隔时间(s)：")
        try:
            tim = float(tim_str)
            return tim
        except ValueError:
            print("Invalid input!")


def select_special_goods(goods_list):
    id_list = list()
    context = list()
    file = open("goods_list.txt", mode="r")
    lis = file.readlines()
    file.close()
    for i in lis:
        j = i.strip()
        id_list.append(j)
    for i in goods_list:
        for j in id_list:
            if i[0] == j:
                context.append(i)
                id_list.remove(j)
    return context


def create_msg(ori_price, price, name, jd_url, id):
    ori_price_str = str(ori_price)
    diff = ori_price - price
    if diff <= 13:
        sold_price = str(round(price + diff * 0.5, 1))
    elif 50 >= diff > 13:
        sold_price = str(round(price + 13, 1))
    else:
        sold_price = str(round(price + diff * 0.3, 1))
    msg = "商品名：" + name + "\n" + jd_url + "\n" + "以上链接为商品源链接,方便您查看商品详情(不解答商品参数问题),付款以支付价格为准,购买请加内购助手.\n" + "商品ID:" + id + "（商品唯一标识）" + "原价: ￥" + ori_price_str + "支付价格：￥" + sold_price + " (北京地区包邮,价格仅供参考)"
    return msg


def send_special_goods(create_msg, send_mag_to_someone, download_image):
    def inner(goods_list, tim):
        count = 0
        with open('goods_list.json', 'r+', encoding='utf-8') as f:
            file = json.load(f)
        print(file)
        for goods in goods_list:
            for i in file["goods"]:
                if goods[0] == i:
                    download_image(goods[2])
                    msg = create_msg(goods[6], goods[5], goods[3], goods[2], goods[0])
                    for j in file["goods"][i]:
                        send_mag_to_someone(j, tim, msg)
                    count += 1
        counts = str(count)
        print("列表商品发送完成，共计发送 " + counts + " 条消息")
    return inner


def send_mag_to_someone(nickname, tim, context):
    user_name = ""
    my_friend = itchat.search_friends(nickname)
    for i in my_friend:
        if i["NickName"] == nickname:
            user_name = i["UserName"]
    try:
        print("sending...")
        f = "C:/Users/86502/PycharmProjects/untitled2/picture.png"  # 图片存储地址
        itchat.send_image(f, toUserName=user_name)  # 发送图片
        rd_num = random.randint(1, 2)
        time.sleep(2 * rd_num)
        itchat.send_msg(context, toUserName=user_name)  # 发送信息
        time.sleep(tim * rd_num)
        print("msg send successfully")
    except:
        print("Failed to send msg")


def continue_send(create_msg, download_image, sent_chat_rooms_msg):
    def inner(data_list, name, tim):
        index = 0
        choice = input("请输入发送方式：\n1.从头发送 \n2.继续上次发送\n:")
        if choice == "1":
            index = 0
        elif choice == "2":
            with open("index.txt", "r") as f:
                begin = f.read()
            for data in data_list:
                if data[0] == begin:
                    index = data_list.index(data)
        data_length = str(len(data_list[index:]))
        print("将有 " + data_length + " 条数据准备发送...")
        for j, data in enumerate(data_list[index:]):
            k = str(j + 1)
            print("准备发送第 " + k + " 条数据")
            msg = create_msg(data[6], data[5], data[3], data[1], data[0])
            download_image(data[2])
            sent_chat_rooms_msg(name, msg, tim)
            with open("index.txt", "w") as f:
                f.write(data[0])
    return inner


def main():
    tim = time_set()
    # itchat.login()  # 更改用户时用该行登录微信
    itchat.auto_login(enableCmdQR=False, hotReload=True)  # 微信登录 (命令行二维码 enableCmdQR=True）

    # name = "一家人抢红包群"  # 目标发送群
    name_list = get_chat_name()     # 获得群聊列表
    goods_list = get_msg()          # 获取商品列表

    data_length = str(len(goods_list))
    print("将有 " + data_length + " 条数据准备发送...")

    send_special = send_special_goods(create_msg, send_mag_to_someone, download_image)
    send_special(goods_list, tim)
    # time.sleep(240)

    for name in name_list:
        continue_sent = continue_send(create_msg, download_image, sent_chat_rooms_msg)
        continue_sent(goods_list, name, tim)


if __name__ == "__main__":
    main()
