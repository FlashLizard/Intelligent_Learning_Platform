# 基于星火大模型的智能课程推荐
import json

from flask import jsonify

from spark.SparkApi import SparkLLM
import time
import json5
from .reptile.from_coursera import reptile_from_coursera
from .reptile.from_edx import reptile_from_edx

appid = 'e76d7d8f'
api_secret = 'Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl'
api_key = '990e2770b030441fbcc126c691daf5cd'

domain = "generalv3.5"  # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址


#
# def search_ans_in_database(num: int):
#     """
#     从数据库中根据课程编号搜索课程
#     return:课程的url，与简介，最好能带一张图片
#     """
#     pass


def ai_recommend(limit: str, course_list: list):
    urls = []
    courses = []
    stars = []
    contents = []

    for item in course_list:
        for element in item:
            if element.startswith('http'):
                urls.append(element)
            else:
                details = element.split(',')
                courses.append(details[0])
                stars.append(details[1].strip())
                contents.append(', '.join(details[2:]).strip())

    # 打印结果（可以根据需要更改为其他操作）
    print("URLs:", urls)
    print("Courses:", courses)
    print("Stars:", stars)
    print("Contents:", contents)
    llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)

    ans = llm.query(
        "我的要求是：" + limit + "。请从下列课程中选择出最符合我要求的课程，注意，你需要返回一个python列表，每一项都是一个整数来表示课程列表中的第几项：" + contents.__str__())
    print('ans:',ans)
    string_list = ans.replace("'", '"')

    # 使用 json.loads 将字符串转换为列表
    list = json.loads(string_list)
    for a in list:
        print(a)
    x = [int(a)-1 for a in list]
    results = []
    for i in x:
        if 0 <= i < len(urls):
            result = {
                "url": urls[i],
                "course": courses[i],
                "star": stars[i],
                "content": contents[i]
            }
            results.append(result)
    print('results:',results)
    return jsonify(results)
    # return json.dumps(result, indent=4)
