# 基于星火大模型的智能课程推荐
import json

from src.spark.SparkApi import SparkLLM
import time
import json5
from reptile.from_coursera import reptile_from_coursera
from reptile.from_edx import reptile_from_edx

with open('../config.json', encoding='utf-8') as f:
    config = json5.load(f)
appid = config['appid']
api_secret = config['api_secret']
api_key = config['api_key']

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
        "我的要求是：" + limit + "。请从下列课程中选择出最符合我要求的课程，注意，你只用回答一个数字，来表示python列表中的第几项：" + contents.__str__())
    print(ans)

    x = int(ans) - 1

    if 0 <= x < len(urls):
        result = {
            "url": urls[x],
            "course": courses[x],
            "star": stars[x],
            "content": contents[x]
        }
        return json.dumps(result, indent=4)

    else:
        return "返回编号错误"
