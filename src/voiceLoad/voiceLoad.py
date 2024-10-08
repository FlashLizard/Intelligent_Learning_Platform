import base64
import hashlib
import hmac
import json
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import requests

APPId = "e76d7d8f"
APISecret = "Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl"
APIKey = "990e2770b030441fbcc126c691daf5cd"

# 填写在开放平台申请的APPID、APIKey、APISecret
# 相应编码音频base64编码后数据(不超过4M)
# apiname取值:
# 1.创建声纹特征库 createGroup
# 2.添加音频特征 createFeature
# 3.查询特征列表 queryFeatureList
# 4.特征比对1:1 searchScoreFea
# 5.特征比对1:N searchFea
# 6.更新音频特征 updateFeature
# 7.删除指定特征 deleteFeature
# 8.删除声纹特征库 deleteGroup

class Gen_req_url(object):
    """生成请求的url"""

    def sha256base64(self, data):
        sha256 = hashlib.sha256()
        sha256.update(data)
        digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
        return digest

    def parse_url(self, requset_url):
        stidx = requset_url.index("://")
        host = requset_url[stidx + 3:]
        # self.schema = requset_url[:stidx + 3]
        edidx = host.index("/")
        if edidx <= 0:
            raise Exception("invalid request url:" + requset_url)
        self.path = host[edidx:]
        self.host = host[:edidx]

    # build websocket auth request url
    def assemble_ws_auth_url(self, requset_url, api_key, api_secret, method="GET"):
        self.parse_url(requset_url)
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        # date = "Thu, 12 Dec 2019 01:57:27 GMT"
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(self.host, date, method, self.path)
        signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        values = {
            "host": self.host,
            "date": date,
            "authorization": authorization
        }

        return requset_url + "?" + urlencode(values)


def gen_req_body(apiname, APPId, file_path=None,
                 groupId=None, featureId=None, featureInfo=None,
                 groupName=None, groupInfo=None, dstFeatureId=None):
    """
    生成请求的body
    :param apiname
    :param APPId: Appid
    :param file_name:  文件路径
    :return:
    """
    if apiname == 'createFeature':

        with open(file_path, "rb") as f:
            audioBytes = f.read()
        body = {
            "header": {
                "app_id": APPId,
                "status": 3
            },
            "parameter": {
                "s782b4996": {
                    "func": "createFeature",
                    "groupId": groupId,
                    "featureId": featureId,
                    "featureInfo": featureInfo,
                    "createFeatureRes": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            },
            "payload": {
                "resource": {
                    "encoding": "lame",
                    "sample_rate": 16000,
                    "channels": 1,
                    "bit_depth": 16,
                    "status": 3,
                    "audio": str(base64.b64encode(audioBytes), 'UTF-8')
                }
            }
        }
    elif apiname == 'createGroup':

        body = {
            "header": {
                "app_id": APPId,
                "status": 3
            },
            "parameter": {
                "s782b4996": {
                    "func": "createGroup",
                    "groupId": groupId,
                    "groupName": groupName,
                    "groupInfo": groupInfo,
                    "createGroupRes": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            }
        }
    elif apiname == 'deleteFeature':

        body = {
            "header": {
                "app_id": APPId,
                "status": 3

            },
            "parameter": {
                "s782b4996": {
                    "func": "deleteFeature",
                    "groupId": "iFLYTEK_examples_groupId",
                    "featureId": "iFLYTEK_examples_featureId",
                    "deleteFeatureRes": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            }
        }
    elif apiname == 'queryFeatureList':

        body = {
            "header": {
                "app_id": APPId,
                "status": 3
            },
            "parameter": {
                "s782b4996": {
                    "func": "queryFeatureList",
                    "groupId": "iFLYTEK_examples_groupId",
                    "queryFeatureListRes": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            }
        }
    elif apiname == 'searchFea':

        with open(file_path, "rb") as f:
            audioBytes = f.read()
        body = {
            "header": {
                "app_id": APPId,
                "status": 3
            },
            "parameter": {
                "s782b4996": {
                    "func": "searchFea",
                    "groupId": "iFLYTEK_examples_groupId",
                    "topK": 1,
                    "searchFeaRes": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            },
            "payload": {
                "resource": {
                    "encoding": "lame",
                    "sample_rate": 16000,
                    "channels": 1,
                    "bit_depth": 16,
                    "status": 3,
                    "audio": str(base64.b64encode(audioBytes), 'UTF-8')
                }
            }
        }
    elif apiname == 'searchScoreFea':

        with open(file_path, "rb") as f:
            audioBytes = f.read()
        body = {
            "header": {
                "app_id": APPId,
                "status": 3
            },
            "parameter": {
                "s782b4996": {
                    "func": "searchScoreFea",
                    "groupId": groupId,
                    "dstFeatureId": dstFeatureId,
                    "searchScoreFeaRes": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            },
            "payload": {
                "resource": {
                    "encoding": "lame",
                    "sample_rate": 16000,
                    "channels": 1,
                    "bit_depth": 16,
                    "status": 3,
                    "audio": str(base64.b64encode(audioBytes), 'UTF-8')
                }
            }
        }
    elif apiname == 'updateFeature':

        with open(file_path, "rb") as f:
            audioBytes = f.read()
        body = {
            "header": {
                "app_id": APPId,
                "status": 3
            },
            "parameter": {
                "s782b4996": {
                    "func": "updateFeature",
                    "groupId": "iFLYTEK_examples_groupId",
                    "featureId": "iFLYTEK_examples_featureId",
                    "featureInfo": "iFLYTEK_examples_featureInfo_update",
                    "updateFeatureRes": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            },
            "payload": {
                "resource": {
                    "encoding": "lame",
                    "sample_rate": 16000,
                    "channels": 1,
                    "bit_depth": 16,
                    "status": 3,
                    "audio": str(base64.b64encode(audioBytes), 'UTF-8')
                }
            }
        }
    elif apiname == 'deleteGroup':
        body = {
            "header": {
                "app_id": APPId,
                "status": 3
            },
            "parameter": {
                "s782b4996": {
                    "func": "deleteGroup",
                    "groupId": "iFLYTEK_examples_groupId",
                    "deleteGroupRes": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            }
        }
    else:
        raise Exception(
            "输入的apiname不在[createFeature, createGroup, deleteFeature, queryFeatureList, searchFea, searchScoreFea,updateFeature]内，请检查")
    return body


def req_url(api_name, APPId, APIKey, APISecret, file_path=None,
            groupId=None, featureId=None, featureInfo=None,
            groupName=None, groupInfo=None, dstFeatureId=None
            ):
    """
    开始请求
    :param APPId: APPID
    :param APIKey:  APIKEY
    :param APISecret: APISecret
    :param file_path: body里的文件路径
    :return:
    """
    gen_req_url = Gen_req_url()
    body = gen_req_body(apiname=api_name, APPId=APPId, file_path=file_path,
                        groupId=groupId, featureId=featureId, featureInfo=featureInfo,
                        groupName=groupName, groupInfo=groupInfo, dstFeatureId=dstFeatureId
                        )
    request_url = gen_req_url.assemble_ws_auth_url(requset_url='https://api.xf-yun.com/v1/private/s782b4996', method="POST", api_key=APIKey, api_secret=APISecret)

    headers = {'content-type': "application/json", 'host': 'api.xf-yun.com', 'appid': '$APPID'}
    response = requests.post(request_url, data=json.dumps(body), headers=headers)
    tempResult = json.loads(response.content.decode('utf-8'))
    print(tempResult)
    return tempResult


"""
 * 1.声纹识别接口,请填写在讯飞开放平台-控制台-对应能力页面获取的APPID、APIKey、APISecret
 * 2.groupId要先创建,然后再在createFeature里使用,不然会报错23005,修改时需要注意保持统一
 * 3.音频base64编码后数据(不超过4M),音频格式需要16K、16BIT的MP3音频。
 * 4.主函数只提供调用示例,其他参数请到对应类去更改,以适应实际的应用场景。
"""

def voiceStackBuild(file_path, groupId, groupName, groupInfo):    # 新建一个声纹库，用于初始化

    #file_path = 'voices/讯飞开放平台.mp3'
    res = req_url(api_name='createGroup', APPId=APPId,
            APIKey=APIKey, APISecret=APISecret, file_path=file_path,
            groupId=groupId, groupName=groupName, groupInfo=groupInfo)
    print('voiceStackBuild_res:',res)
    # 获取并解码 text 字段
    encoded_text = res["payload"]["createGroupRes"]["text"]
    decoded_text = base64.b64decode(encoded_text).decode('utf-8')

    # 解析解码后的 JSON 字符串
    decoded_json = json.loads(decoded_text)

    # 提取 groupName、groupId 和 groupInfo 的值
    group_name = decoded_json["groupName"]
    group_id = decoded_json["groupId"]
    group_info = decoded_json["groupInfo"]

    return group_name, group_id, group_info

def voiceAdd(file_path, groupId, featureId, featureInfo):   #  为一个新用户在声纹库中新建一个声纹
    #file_path = 'voices/讯飞开放平台.mp3'
    res = req_url(api_name='createFeature', APPId=APPId,
            APIKey=APIKey, APISecret=APISecret, file_path=file_path,
                  groupId=groupId, featureId=featureId, featureInfo=featureInfo)
    print("VoiceAdd_res:",res)
    # 获取并解码 text 字段
    # encoded_text = res["payload"]["createGroupRes"]["text"]
    encoded_text = res["payload"]["createFeatureRes"]["text"]
    decoded_text = base64.b64decode(encoded_text).decode('utf-8')

    # 解析解码后的 JSON 字符串
    decoded_json = json.loads(decoded_text)

    # 提取 groupName、groupId 和 groupInfo 的值
    featureId = decoded_json["featureId"]

    return featureId



def voiceVerify(file_path, groupId, dstFeatureId):    # 登录验证
    #file_path = 'voices/讯飞开放平台.mp3'
    res = req_url(api_name='searchScoreFea', APPId=APPId, APIKey=APIKey, APISecret=APISecret, 
                  file_path=file_path, groupId=groupId, dstFeatureId=dstFeatureId)
    print("voiceVerify_res:",res)
    encoded_text = res["payload"]["searchScoreFeaRes"]["text"]
    decoded_text = base64.b64decode(encoded_text).decode('utf-8')

    # 解析解码后的 JSON 字符串
    decoded_json = json.loads(decoded_text)

    # 提取 groupName、groupId 和 groupInfo 的值
    score = decoded_json["score"]
    featureInfo = decoded_json["featureInfo"]
    featureId = decoded_json["featureId"]

    return score, featureInfo, featureId