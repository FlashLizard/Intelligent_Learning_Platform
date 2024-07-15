from flask_cors import CORS
from flask import Flask, request, jsonify,Response
import random
import regex
import os
import sys
import random
from utils import Logger
from spark.SparkApi import SparkLLM
from audio_to_txt.Ifasr_app import audio2txt_Api
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#print(sys.path)
import json5
from App import app

appid = 'e76d7d8f'
api_secret = 'Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl'
api_key = '990e2770b030441fbcc126c691daf5cd'

domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

# 创建服务器
# app = Flask(__name__)
# CORS(app)

# 创建SparkLLM对象
llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain, False)

get_problems_prompt = '''我以以下格式:
        {
                "subjects": "数学计算" /*问题考察的知识点*/, 
            "count": 3 /*要求提供的题目数量, 不要少于此数量*/,
            "min_difficulty": 3 /*1-10*/,
            "max_difficulty": 8 /*1-10*/,
            "type": ["单选题", "填空题", "判断题"], /*需要的题目类型, 不要给出这里所提到的类型这之外的题目*/
                "others": "希望能出一些计算量比较大的题目"
        }
        给你提供一个对于试题描述的json，请你根据里面的信息以我指定的格式:
        {
                "problems": [
                    {
                        "type": "single_choice" /*注意注意type只能为single_choice, judgement或fillin, 不要给出这之外的类型*/,
                        "problem": "1+1=( )",
                        "choices": ["1","2","3","4"],
                        "answer": [1] /*对应上一个的下标, 通过这里判断单选多选*/,
                        "analysis": "一个很简单的数学题"
                    },
                    {
                        "type": "fillin" /*填空、主观等填写的题目*/,
                        "problem": ["1+2=","4+5=","请回答"], /*以空为分隔符分隔，最后即时没字符也应该有一个结束字符串*/
                        "answer": ["3", "9"] /*几个空几个答案*/,
                        "analysis": "可以化为2进制去计算"
                    },
                    {
                        "type": "judgement",
                        "problem": "6+7=11",
                        "answer": false,
                        "analysis": "可以按计算器"
                    }
                ]
            }
        返回其要求的试题数据。注意只返回5道单选，5道判断，5道填空题。但如果试题描述的"others"要求了题型和题目数量则按照"others"生成题目。
        提供给你的json如下, 请直接返回json, 不要添加任何其他描述:'''



@app.route('/get_downloadproblems', methods=['POST'])
def get_downloadproblems_handler():
    content = request.json
    Logger.info(content)
    """
    {
    "subjects": ["math","chinese"],
   	"time": 10 /*mins*/,
   	"min_difficulty": 3 /*1-10*/,
   	"max_difficulty": 8,
   	"type": ["single_choice", "judgement"],
    "others": "希望能出一些计算量比较大的题目"
   }
    """
    subjects = content['subjects']
    time = content['time']
    types = content['type']
    str_types = ['"'+x+'"' for x in types]
    cnt = max(len(subjects), int(time / 3))
    rest = len(subjects)
    ans = {'problems': []}
    for subject in subjects:
        rest -= 1
        now_cnt = random.randint(1, cnt - rest)
        cnt -= now_cnt
        json_str = f'''{{
        "subjects": "{subject}" /*问题考察的知识点*/,
        "count": {now_cnt} /*要求提供的题目数量, 不要少于此数量或多于此数量*/,
        "min_difficulty": {content['min_difficulty']} /*1-10*/,
        "max_difficulty": {content['max_difficulty']} /*1-10*/,
        "type": {str_types} /*需要的题目类型, 不要给出这里所提到的类型这之外的题目*/, 
        "others": "{content['others']}" /*其他要求*/
        }}'''
        Logger.info(f'json_str:{json_str}')
        question = get_problems_prompt + json_str
        ans_str = llm.query(question)
        ans_str = ans_str[ans_str.find('{'): ans_str.rfind('}') + 1]
        # Logger.info(f'ans_str:{ans_str}')
        now_ans = json5.loads(ans_str)
        ans['problems'].extend(now_ans['problems'])
        paper_text = generate_paper_text(ans)
        filepath = os.path.join('ai_test_system','paper')
        os.makedirs(filepath, exist_ok=True)
        filename = os.path.join(filepath,'test.txt')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(paper_text)
        # 创建下载文件的 Response
        response = Response(paper_text, content_type='text/plain')
        response.headers["Content-Disposition"] = "attachment; filename=problems.txt"
        return response

def generate_paper_text(problems_data):
    problems = problems_data['problems']
    paper_text = []

    option_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']  # 可以扩展到更多选项

    problem_count = {'single_choice': 0, 'fillin': 0, 'judgement': 0}  # 统计每种题型的数量

    single_choice_start = 0
    fillin_start = 0
    judgement_start = 0

    for problem in problems:
        if problem['type'] == 'single_choice':
            problem_count['single_choice'] += 1
            if problem_count['single_choice'] == 1:
                paper_text.append("一、选择题：")
                single_choice_start = len(paper_text)  # 记录选择题开始位置
            paper_text.append(f"{problem_count['single_choice']}. {problem['problem']}")
            for i, choice in enumerate(problem['choices']):
                if i < len(option_letters):
                    paper_text.append(f"{option_letters[i]}. {choice}")
                else:
                    paper_text.append(f"{i+1}. {choice}")  # 超过10个选项时使用数字序号

        elif problem['type'] == 'fillin':
            problem_count['fillin'] += 1
            if problem_count['fillin'] == 1:
                if single_choice_start > 0:
                    paper_text.insert(single_choice_start, "")  # 空行分隔选择题和填空题
                paper_text.append("\n二、填空题：")
                fillin_start = len(paper_text)  # 记录填空题开始位置
            paper_text.append(f"{problem_count['fillin']}. {problem['problem']}")
            paper_text.append("___________")  # 填空题用下划线表示

        elif problem['type'] == 'judgement':
            problem_count['judgement'] += 1
            if problem_count['judgement'] == 1:
                if fillin_start > 0:
                    paper_text.insert(fillin_start, "")  # 空行分隔填空题和判断题
                elif single_choice_start > 0:
                    paper_text.insert(single_choice_start, "")  # 空行分隔选择题和判断题
                paper_text.append("\n三、判断题：")
                judgement_start = len(paper_text)  # 记录判断题开始位置
            paper_text.append(f"{problem_count['judgement']}. {problem['problem']}")
            paper_text.append("A. 是")
            paper_text.append("B. 否")
        paper_text.append('\n')
    # 将列表转换为字符串
    paper_text = "\n".join(map(str, paper_text))

    return paper_text

def save_to_word(filename, paper_text):
    document = Document()
    document.add_heading('试卷内容', level=1)
    document.add_paragraph(paper_text)
    document.save(filename)