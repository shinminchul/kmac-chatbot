from flask import Flask, request, jsonify
import json
import requests
from hanspell import spell_checker
from konlpy.tag import Twitter
import html.parser

global twitter
twitter=Twitter()
app = Flask(__name__)

def write(uid, content, checked, nlped, answer):
    with open("chatbot_log.csv", "a") as f:
         f.write(uid+"&"+content+"&"+checked+"&"+nlped+"&"+answer+"\n")
	
def spellcheck(questionorg):
    result = spell_checker.check(questionorg).as_dict()
    return result['checked']

def nlp(question):
    string_analyzed = twitter.pos(question, norm=True, stem=True)
    analyzed = []
    for words in string_analyzed:
        analyzed.append(words[0])
    message = ' '.join(analyzed)
    return str(message)

def getAnswer(question):
    url = 'https://westus.api.cognitive.microsoft.com/qnamaker/v2.0/knowledgebases/-API_ADDRESS-'
    headers = {'Content-Type':'application/json; charset=utf-8',
                'Ocp-Apim-Subscription-Key': -subscriptionkey-}
    data = json.dumps({"question": question})
    r = requests.post(url, headers=headers, data=data)
    rjson = json.loads(r.text)
    answer = rjson.get('answers')[0]['answer']
    answer = html.parser.HTMLParser().unescape(answer)
    if answer=="No good match found in the KB":
        answer="이부분은 제가 모르겠어요^^; 펜션지기에게 직접 전화로 문의해주세요 010-2951-3412"
    return answer

@app.route('/keyboard')
def Keyboard():
    dataSend = {
        "type": "buttons",
        "buttons": ["안녕하세요"]
    }
    return jsonify(dataSend)

@app.route('/message', methods=['POST'])
def Message():
    dataReceive = request.get_json()
    uid = dataReceive['user_key']
    content = dataReceive['content']
    checked = spellcheck(content)
    nlped = nlp(checked)
    answer = getAnswer(nlped)
    write(uid, content, checked, nlped, answer)
    dataSend = {
        "message": {
            "text": answer
        }
    }
    return jsonify(dataSend)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
