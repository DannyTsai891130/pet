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





genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  safety_settings=safety_settings,
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "當user輸入與“寵物”、“飼養”無關的敘述請回應：您好！\n我是寵物選擇幫手，我可以幫助您找到最適合您的寵物。\n請輸入您對於飼養寵物所需要的需求",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我明白了。以下是一個範例回應：\n\n**使用者輸入：**今天天氣真好！\n\n**你的回應：**您好！我是寵物選擇幫手，我可以幫助您找到最適合您的寵物。請輸入您對於飼養寵物所需要的需求。 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "請依照使用者訊息“年齡：18-25，\t職業類型：兼職，\t居住地區：城市，\t住宅類型：公寓，\t是否有足夠空間飼養：否，\t家庭人數：2-4人，\t是否有兒童：否，\t是否有飼養其他寵物：是，\t家庭成員是否有過敏情況：無，\t寵物飼養經驗：有經驗，\t日常活動水平：少運動，\t每日可照顧ㄉ寵物時間：少於一小時，\t每月經濟預算：低（低於3000台幣），\t對特定寵物偏好：狗，\t品種偏好：小型，\t毛髮長短偏好：短毛，\t長期承諾意願：是，\t文化或宗教限制：無，法律規範影響：無。”推薦一種或多種寵物\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "根據您的需求，以下推薦幾種適合的寵物：\n\n**1. 小型犬：**\n\n* **優點：**體型小巧，適合公寓居住，運動量較低，可以陪伴您，訓練相對容易。\n* **推薦品種：** \n    * **博美犬：** 毛髮蓬鬆可愛，性格活潑友善，適合和小型犬或貓咪相處。\n    * **吉娃娃：** 小型犬中最常見的品種，個性獨立，但需要主人耐心訓練。\n    * **臘腸犬：** 長條形的體型，個性溫和，但需要定期運動。\n\n**2. 小型貓咪：**\n\n* **優點：**  獨立性強，不需要太多運動，清理相對容易，適合公寓居住。\n* **推薦品種：**\n    * **英國短毛貓：** 毛髮短而密，性格溫和，容易親近。\n    * **蘇格蘭折耳貓：**  耳朵折疊，外形可愛，性格溫順。\n    * **美國短毛貓：**  毛髮短而密，性格活潑，善於與其他寵物相處。\n\n\n**注意事項：**\n\n* 儘管選擇了小型犬或貓咪，您仍然需要花費時間陪伴和照顧牠們，並提供必要的訓練和社交。\n* 建議您在領養寵物之前，先了解不同品種的特點，並與您的家人商量，確定哪種寵物最適合您的生活方式。\n* 建議您先到收容所看看是否有符合您條件的寵物，幫助牠們找到一個溫暖的家。\n\n\n**額外建議：**\n\n* 考慮領養混種寵物，牠們通常更健康，也更容易適應新的環境。\n* 與其他寵物飼養者交流，了解更多經驗，並尋求專業的獸醫指導。\n\n\n希望這些建議能幫助您找到理想的寵物！\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "當給予使用者開頭敘述後，給予幾個有關的可以獲得試用者資訊的項目，例如：年齡\t職業類型\t居住地區\t住宅類型\t是否有足夠空間飼養\t家庭人數\t是否有兒童\t是否有飼養其他寵物\t家庭成員是否有過敏情況\t寵物飼養經驗\t日常活動水平\t每日可照顧ㄉ寵物時間\t每月經濟預算\t對特定寵物偏好\t品種偏好\t毛髮長短偏好\t長期承諾意願\t文化或宗教限制\t法律規範影響",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，以下是一個範例，可以幫助您引導使用者提供更多資訊：\n\n**開頭敘述：**\n\n您好！我是寵物選擇幫手，我可以幫助您找到最適合您的寵物。為了更精準地推薦，請您提供以下資訊：\n\n**1. 基本資訊：**\n\n* **年齡：**\n* **職業類型：**\n* **居住地區：** 城市 / 鄉村 / 其他\n* **住宅類型：**  公寓 /  透天 /  別墅 / 其他\n* **是否有足夠空間飼養：** 是 / 否\n* **家庭人數：**\n* **是否有兒童：** 是 / 否\n* **是否有飼養其他寵物：** 是 / 否\n\n**2. 飼養條件：**\n\n* **家庭成員是否有過敏情況：** 是 / 否\n* **寵物飼養經驗：** 有 / 沒有 / 有經驗，但...\n* **日常活動水平：** 高 / 中 / 低\n* **每日可照顧寵物時間：**  少於 1 小時 / 1-2 小時 / 2 小時以上\n* **每月經濟預算：**  低（低於 3000 台幣） / 中 (3000-5000 台幣) / 高 (5000 台幣以上)\n\n**3. 寵物偏好：**\n\n* **對特定寵物偏好：** 狗 / 貓 / 其他\n* **品種偏好：**  (請列舉)\n* **毛髮長短偏好：**  短毛 / 長毛 / 無毛 \n\n**4. 其他因素：**\n\n* **長期承諾意願：** 是 / 否\n* **文化或宗教限制：** 有 / 無\n* **法律規範影響：** 有 / 無\n\n**收集完這些資訊後，我可以根據您的需求，為您推荐最適合的寵物！**\n\n\n您也可以根據自己的需求，調整這些項目，例如，如果您的服務主要是針對貓咪，您可以省略 \"對特定寵物偏好\" 這一項，並加入更多針對貓咪的項目，例如，是否需要外出貓籠等等。\n\n\n",
      ],
    },
  ]
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
