from pymysql import cursors, connect


# 连接数据库
conn = connect(host='127.0.0.1',
               user='root',
               password='123456',
               db='guest',
               charset='utf8mb4',
               cursorclass=cursors.DictCursor)

try:
    with conn.cursor() as cursor:
        # 创建嘉宾数据
        sql = 'INSERT INFO sign_guest (realname, phone, email, sign, event_id, create_time) VALUES ("tom",18800110002,"tom@mail.com",0,1,NOW());'
        cursor.execute(sql)
    # 提交事物
    conn.commit()

    with conn.cursor() as cursor:
        # 查询添加的嘉宾
        sql = "SELECT realname,phone,email,sign FROM sign_guest WHERE phone=%s"
        cursor.execute(sql, ('18800110002',))
        result = cursor.fetchone()
        print(result)
finally:
    conn.close()


