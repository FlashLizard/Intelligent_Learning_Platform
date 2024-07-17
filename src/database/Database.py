import mysql.connector
from mysql.connector import Error
import json
import json5
from utils import Logger


database = None
mysql_password = '111111'
mysql_port = 3306
try:
    with open("../config.json") as f:
        f_json = json5.load(f)
        mysql_password = f_json["mysql_password"]
        mysql_port = f_json["mysql_port"]
except Exception as e:
    Logger.error(f"Load config.json failed, use default")
    mysql_password = '111111'
    mysql_port = 3306


# 连接到MySQL数据库
def connect(host='localhost', user='root', database=None):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=mysql_password,
            database=database,
            port = mysql_port
        ) if database is not None else mysql.connector.connect(
            host=host,
            user=user,
            password=mysql_password,
            port = mysql_port
        )
        Logger.info("Connected to MySQL")
    except Error as e:
        Logger.error(f"The error '{e}' occurred")
    return connection

# 获取数据库
def get_database():
    global database
    if(database == None):
        user = connect()
        cursor = user.cursor()
        cursor.execute(f"SHOW DATABASES LIKE 'ilp'")
        result = cursor.fetchone() is not None
        if(not result):
            cursor.execute("CREATE DATABASE ilp")
            cursor.execute("USE ilp")
            cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL
            )
            """)
            cursor.execute("""
            CREATE TABLE tests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                test_name VARCHAR(255) NOT NULL,
                test_time DATETIME,
                test_questions JSON,
                test_score INT,
                test_subjects JSON,
                user_answers JSON,
                test_result_analysis JSON,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """)
            user.commit()
        user.close()
        database = connect(database='ilp')
    return database


def delete_database():
    user = connect()
    cursor = user.cursor()
    try:
        cursor.execute("DROP DATABASE IF EXISTS ilp")
        Logger.info("Database deleted")
    except Error as e:
        Logger.error(f"The error '{e}' occurred")
    user.commit()
    user.close()

# 增加用户
def create_user(username):
    if(get_user_id(username) is not None):
        return None
    query = "INSERT INTO users (username) VALUES (%s)"
    cursor = get_database().cursor()
    cursor.execute(query, (username,))
    get_database().commit()
    Logger.info(f"User {username} created")
    return cursor.lastrowid

# 增加测试数据
def create_test(user_id, test_name, test_time, test_questions, user_answers, test_result_analysis,test_score, test_subjects):
    cursor = get_database().cursor()
    query = """
    INSERT INTO tests (user_id, test_name, test_time, test_questions, user_answers, test_result_analysis, test_score, test_subjects)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (user_id, test_name, test_time, json.dumps(test_questions), json.dumps(user_answers), json.dumps(test_result_analysis), test_score, json.dumps(test_subjects)))
    get_database().commit()
    return cursor.lastrowid

# 查询用户的所有测试数据
def get_user_tests(user_id):
    cursor = get_database().cursor(dictionary=True)
    query = "SELECT test_name,test_time,id,test_score,test_subjects FROM tests WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    return cursor.fetchall()

# 查询具体的测试数据
def get_test_by_id(test_id):
    cursor = get_database().cursor(dictionary=True)
    query = "SELECT * FROM tests WHERE id = %s"
    cursor.execute(query, (test_id,))
    result = cursor.fetchone()
    if result is None:
        return None
    return result

# 删除测试数据
def delete_test(test_id):
    cursor = get_database().cursor()
    query = "DELETE FROM tests WHERE id = %s"
    cursor.execute(query, (test_id,))
    get_database().commit()

def get_user_id(username):
    cursor = get_database().cursor()
    query = "SELECT id FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result is None:
        return None
    cursor.fetchall()
    return result[0]

# 示例使用
if __name__ == "__main__":
    delete_database()
    # 增加用户
    user_id = create_user("JohnDoe")
    
    # 增加测试数据
    test_id = create_test(user_id, "测试一", "2024-07-03 12:00:00", {"q1": "What is AI?"}, {"q1": "Artificial Intelligence"}, {"score": 100},100,["math"])
    
    # 查询用户的所有测试数据
    tests = get_user_tests(user_id)
    print(tests)
    
    # 查询具体的测试数据
    test = get_test_by_id(test_id)
    print(test)
    
    # 删除测试数据
    delete_test(test_id)
    delete_database()
    get_database().close()
