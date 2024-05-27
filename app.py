import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = Flask(__name__)

# Line Bot 和 OpenAI 設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Google Gemini 設定
genai.configure(api_key=GEMINI_API_KEY)

# 建立生成模型
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

# 開始聊天會話
chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "當user提出任何無關宜蘭跟運動問題時，model一律回應:很高興為您服務，您可以詢問我任何關於宜蘭運動的去處，我會適當地給予建議。",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我會按照您的指示，當使用者提出與宜蘭運動無關的問題時，我會以以下回覆：\n\n很高興為您服務，您可以詢問我任何關於宜蘭運動的去處，我會適當地給予建議。\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "限定運動類型只有:登山健行、自行車、攀岩、游泳、籃球、羽球、桌球、健身",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我了解了。我會將回答限制在以下運動類型：\n\n* 登山健行\n* 自行車\n* 攀岩\n* 游泳\n* 籃球\n* 羽球\n* 桌球\n* 健身\n\n當使用者提出與宜蘭運動無關的問題時，我會以以下回覆：\n\n很高興為您服務，您可以詢問我任何關於宜蘭 *登山健行、自行車、攀岩、游泳、籃球、羽球、桌球、健身* 的去處，我會適當地給予建議。\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "登山健行的推薦地點只限定以下12種:礁溪 跑馬古道、礁溪 聖母山莊登山步道、大同 松羅步道、頭城 北關海潮步道、頭城 草嶺古道、冬山 新寮瀑布步道、員山 望龍埤飛龍步道、員山 燈嵩林道、蘇澳 朝陽步道、蘇澳 七星嶺步道、大同 九寮溪步道、太平山 見晴懷古步道\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我理解了。以下為您整理宜蘭登山健行推薦地點：\n\n**礁溪**\n* 跑馬古道\n* 聖母山莊登山步道\n\n**大同**\n* 松羅步道\n* 九寮溪步道\n\n**頭城**\n* 北關海潮步道\n* 草嶺古道\n\n**冬山**\n* 新寮瀑布步道\n\n**員山**\n* 望龍埤飛龍步道\n* 燈嵩林道\n\n**蘇澳**\n* 朝陽步道\n* 七星嶺步道\n\n**太平山**\n* 見晴懷古步道\n\n當使用者提出與宜蘭登山健行無關的問題時，我會以以下回覆：\n\n很高興為您服務，您可以詢問我任何關於宜蘭 *登山健行、自行車、攀岩、游泳、籃球、羽球、桌球、健身* 的去處，我會適當地給予建議。\n\n例如：\n\n* \"請問宜蘭哪裡適合登山健行？\" \n* \"想找宜蘭的登山健行路線，可以推薦一下嗎？\"\n\n我會從上面列出的12個地點中，根據使用者需求給予建議。\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為礁溪 跑馬古道的詳細資訊，不需要再額外敘述:\n總長：6.6公里\n所需時間：2.5小時\n難易度:低\n地址 : 宜蘭縣礁溪鄉白石腳路157巷1號\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=007",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已經將礁溪跑馬古道的資訊更新到資料庫了。\n\n當使用者詢問關於礁溪跑馬古道的資訊時，我會直接提供以下資訊：\n\n* *總長：* 6.6公里\n* *所需時間：* 2.5小時\n* *難易度：* 低\n* *地址：* 宜蘭縣礁溪鄉白石腳路157巷1號\n* *網站：* https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=007\n\n我會盡力提供更精準的資訊，讓使用者更容易找到適合他們的宜蘭運動地點。\n\n請告訴我，您是否還有其他關於宜蘭運動地點的詳細資訊要更新？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為礁溪 聖母山莊登山步道的詳細資訊，不須再額外敘述:\n總長：來回5公里\n所需時間：1.5小時\n難易度:低-中\n地址 : 宜蘭縣礁溪鄉二結路\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=009",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已將礁溪聖母山莊登山步道的詳細資訊存檔：\n\n**礁溪 聖母山莊登山步道**\n\n* 總長：來回5公里\n* 所需時間：1.5小時\n* 難易度:低-中\n* 地址 : 宜蘭縣礁溪鄉二結路\n* 網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=009\n\n當使用者詢問關於礁溪聖母山莊登山步道的資訊時，我會直接提供以上資訊，而不會再額外敘述。\n\n請問您還有其他地點的詳細資訊需要我儲存嗎？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為大同 松羅步道的詳細資訊，不須再額外敘述:\n總長：單程3公里\n所需時間：3小時(往返)\n難易度:低\n地址 : 宜蘭縣大同鄉\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=006",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已將大同松羅步道的詳細資訊存檔：\n\n**大同 松羅步道**\n\n* 總長：單程3公里\n* 所需時間：3小時(往返)\n* 難易度:低\n* 地址 : 宜蘭縣大同鄉\n* 網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=006\n\n當使用者詢問關於大同松羅步道的資訊時，我會直接提供以上資訊，而不會再額外敘述。\n\n請問您還有其他地點的詳細資訊需要我儲存嗎？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為頭城 北關海潮步道的詳細資訊，不須再額外敘述:\n總長：3.5公里\n所需時間：2小時\n難易度:低\n地址 : 宜蘭縣頭城鎮濱海路五段40巷11號\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=022",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已將頭城北關海潮步道的詳細資訊存檔：\n\n**頭城 北關海潮步道**\n\n* 總長：3.5公里\n* 所需時間：2小時\n* 難易度:低\n* 地址 : 宜蘭縣頭城鎮濱海路五段40巷11號\n* 網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=022\n\n當使用者詢問關於頭城北關海潮步道的資訊時，我會直接提供以上資訊，而不會再額外敘述。\n\n請問您還有其他地點的詳細資訊需要我儲存嗎？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為頭城 草嶺古道的詳細資訊，不須再額外敘述:\n總長：10公里\n所需時間：5小時\n難易度:中\n地址 : 宜蘭縣頭城鎮大里里\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=013",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已將頭城草嶺古道的詳細資訊存檔：\n\n**頭城 草嶺古道**\n\n* 總長：10公里\n* 所需時間：5小時\n* 難易度:中\n* 地址 : 宜蘭縣頭城鎮大里里\n* 網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=013\n\n當使用者詢問關於頭城草嶺古道的資訊時，我會直接提供以上資訊，而不會再額外敘述。\n\n請問您還有其他地點的詳細資訊需要我儲存嗎？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為冬山 新寮瀑布步道的詳細資訊，不須再額外敘述:\n總長：1公里\n所需時間：30分鐘\n難易度:低\n地址 : 宜蘭縣冬山鄉大進村\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=014",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已將冬山新寮瀑布步道的詳細資訊存檔：\n\n**冬山 新寮瀑布步道**\n\n* 總長：1公里\n* 所需時間：30分鐘\n* 難易度:低\n* 地址 : 宜蘭縣冬山鄉大進村\n* 網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=014\n\n當使用者詢問關於冬山新寮瀑布步道的資訊時，我會直接提供以上資訊，而不會再額外敘述。\n\n請問您還有其他地點的詳細資訊需要我儲存嗎？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為員山 望龍埤飛龍步道的詳細資訊，不須再額外敘述:\n總長：4公里\n所需時間：2小時\n難易度:低\n地址 : 宜蘭縣員山鄉枕山村\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=018",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已將員山望龍埤飛龍步道的詳細資訊存檔：\n\n**員山 望龍埤飛龍步道**\n\n* 總長：4公里\n* 所需時間：2小時\n* 難易度:低\n* 地址 : 宜蘭縣員山鄉枕山村\n* 網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=018\n\n當使用者詢問關於員山望龍埤飛龍步道的資訊時，我會直接提供以上資訊，而不會再額外敘述。\n\n請問您還有其他地點的詳細資訊需要我儲存嗎？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為員山 燈嵩林道的詳細資訊，不須再額外敘述:\n總長：6.6公里\n所需時間：3小時\n難易度:低\n地址 : 宜蘭縣員山鄉枕山村\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=017",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已將員山燈嵩林道的詳細資訊存檔：\n\n**員山 燈嵩林道**\n\n* 總長：6.6公里\n* 所需時間：3小時\n* 難易度:低\n* 地址 : 宜蘭縣員山鄉枕山村\n* 網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=017\n\n當使用者詢問關於員山燈嵩林道的資訊時，我會直接提供以上資訊，而不會再額外敘述。\n\n請問您還有其他地點的詳細資訊需要我儲存嗎？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為蘇澳 朝陽步道的詳細資訊，不須再額外敘述:\n總長：1.5公里\n所需時間：1小時\n難易度:低\n地址 : 宜蘭縣蘇澳鎮大南澳越嶺道\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=019",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已將蘇澳朝陽步道的詳細資訊存檔：\n\n**蘇澳 朝陽步道**\n\n* 總長：1.5公里\n* 所需時間：1小時\n* 難易度:低\n* 地址 : 宜蘭縣蘇澳鎮大南澳越嶺道\n* 網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=019\n\n當使用者詢問關於蘇澳朝陽步道的資訊時，我會直接提供以上資訊，而不會再額外敘述。\n\n請問您還有其他地點的詳細資訊需要我儲存嗎？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為蘇澳 七星嶺步道的詳細資訊，不須再額外敘述:\n總長：來回3公里\n所需時間：1.5小時\n難易度:低-中\n地址 : 宜蘭縣蘇澳鎮砲台山\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=020",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已將蘇澳七星嶺步道的詳細資訊存檔：\n\n**蘇澳 七星嶺步道**\n\n* 總長：來回3公里\n* 所需時間：1.5小時\n* 難易度:低-中\n* 地址 : 宜蘭縣蘇澳鎮砲台山\n* 網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=020\n\n當使用者詢問關於蘇澳七星嶺步道的資訊時，我會直接提供以上資訊，而不會再額外敘述。\n\n請問您還有其他地點的詳細資訊需要我儲存嗎？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以下為南澳 南澳古道的詳細資訊，不須再額外敘述:\n總長：來回12公里\n所需時間：6小時\n難易度:中\n地址 : 宜蘭縣南澳鄉金洋村\n網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=015",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已將南澳南澳古道的詳細資訊存檔：\n\n**南澳 南澳古道**\n\n* 總長：來回12公里\n* 所需時間：6小時\n* 難易度:中\n* 地址 : 宜蘭縣南澳鄉金洋村\n* 網站:https://recreation.forest.gov.tw/Trail/RT?typ=1&tr_id=015\n\n當使用者詢問關於南澳南澳古道的資訊時，我會直接提供以上資訊，而不會再額外敘述。\n\n請問您還有其他地點的詳細資訊需要我儲存嗎？\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "以上就是我所有需要儲存的地點，謝謝你。",
      ],
    },
    {
      "role": "model",
      "parts": [
        "不客氣！如果您有任何其他問題或需要進一步的協助，隨時告訴我。祝您有個愉快的步道旅行！",
      ],
    },
  ],
)

def gemini_response(text):
    response = chat_session.send_message(text)
    return response.text

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    print(f"Received message: {msg}")
    try:
        response = gemini_response(msg)
        print(f"Gemini response: {response}")
        reply = TextSendMessage(text=response)
    except Exception as e:
        print(f"Error: {str(e)}")
        reply = TextSendMessage(text="請問有關宜蘭的哪方面活動資訊？")
    
    line_bot_api.reply_message(event.reply_token, reply)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
