# import base64
# import requests
# f = open(r'./pic2/3.png', 'rb')
# img = base64.b64encode(f.read())
# params = {
#     'image': img,
# }

# # url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=EKX6T4njm4QLWqzbiisqhXC2&client_secret=R6gIbRC1jPtMrwVioUcGbZoV3iI1pXoL'
# #
# # headers = {
# #     'Content-Type': 'application/json; charset=UTF-8',
# # }
# #
# #
# # r = requests.get(url=url, headers=headers)
# # print(r.text)
#
# url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer?access_token=' + "24.a5ea80bf8988c4e038a988e1512fc460.2592000.1547641431.282335-15191508"
# # headers = {
# #     'Content-Type': 'application/x-www-form-urlencoded',
# # }
# #
# # r = requests.post(url=url, headers=headers, data=params)
# # print(r.text)
#
# headers = {
#     'Content-Type': 'application/json',
# }
# # data = {
# #     'text': '江苏吴江区',
# # }
# r = requests.post(url=url,headers=headers)
# print(r.text)
#

import requests
import json

# url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=EKX6T4njm4QLWqzbiisqhXC2&client_secret=R6gIbRC1jPtMrwVioUcGbZoV3iI1pXoL'
#
# headers = {
#     'Content-Type': 'application/json; charset=UTF-8',
# }
#
#
# r = requests.get(url=url, headers=headers)
# print(r.text)

url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/depparser?access_token=24.b560ce390ea8826a876e4a39a8e5013d.2592000.1547641837.282335-15191508'

headers = {
    'Content-Type': 'application/json',
}

data ={
  "text": "和平荣业大街76号",
  "mode": 1
}

r = requests.post(url=url, data=json.dumps(data).encode('gbk'), headers=headers)
print(r.text)









