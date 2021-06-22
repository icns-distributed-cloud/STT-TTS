import requests
import json
from xml.etree.ElementTree import Element, SubElement, ElementTree

import settings

kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"

rest_api_key = settings.get_apiKey('rest_api_key')

headers = {
    "Content-Type": "application/octet-stream",

    "Authorization": "KakaoAK " + rest_api_key,
}

with open('sample2.mp3', 'rb') as fp:
    audio = fp.read()

res = requests.post(kakao_speech_url, headers=headers, data=audio)
print(res.text)
result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
result = json.loads(result_json_string)
print(result)
print(type(result['value']))