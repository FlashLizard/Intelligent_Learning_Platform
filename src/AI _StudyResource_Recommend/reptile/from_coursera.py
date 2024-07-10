import requests
from bs4 import BeautifulSoup
import random

def reptile_from_coursera(course_name):
    # 这是一个从coursera上随机爬取若干课程的爬虫
    search_res = []

    target_url = 'https://www.coursera.org/search?query=' + course_name
    base_url = 'https://www.coursera.org'

    response = requests.get(target_url)
    if response.status_code == 200:
        # 使用 BeautifulSoup 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        target_a_tags = soup.findAll('a', {'class': 'cds-CommonCard-titleLink'})
        extracted_info = []

        for tag in target_a_tags:
            if tag.has_attr('href') and tag.has_attr('aria-label'):
                href = base_url + tag['href']  # 构造完整的URL
                aria_label = tag['aria-label']
                extracted_info.append((href, aria_label))

        # 检查是否成功提取了URL
        if extracted_info:
            selected_info = random.sample(extracted_info, min(50, len(extracted_info)))  # 随机选择

            # 循环展示选中的内容
            for idx, (href, label) in enumerate(selected_info, start=1):
                print(f"提取到的第{idx}个学习网址:", href)
                print(f"介绍:", label)
                data = {href, label}
                search_res.append(data)
            return search_res

        else:
            return "没有找到期望的信息。"
    else:
        return "获取页面失败，状态码:", response.status_code
