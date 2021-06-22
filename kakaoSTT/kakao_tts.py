import requests
import json
from urllib.parse import urlencode

import settings


kakao_text_url = "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize"

rest_api_key = settings.get_apiKey('rest_api_key')

headers = {
    "Content-Type": "application/xml",
    "Authorization": "KakaoAK " + rest_api_key
}

with open('sample.xml', 'rb') as fp:
    text = fp.read()

# text = '<speak>높은 음질의 자연스러운 음성 합성 기술을, 다양한 오디오 콘텐츠와 음성안내 서비스에 사용해 보세요. 기술 후원은 <say-as inter  pret-as="telephone">82-010-0000-0000</say-as>로 연락 부탁드립니다.</speak>'.encode()
 
# text2 = urlencode(text).encode('utf-8')
res = requests.post(kakao_text_url, headers=headers, data=text)
with open('result.mp3', 'wb') as f:
    f.write(res.content)
print(res.headers['Content-Type'])
print(res.headers['X-TTS-TEXT'])
# result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
# result = json.loads(result_json_string)
# print(result)
# print(result['value'])