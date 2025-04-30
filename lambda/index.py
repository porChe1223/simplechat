import json
import os
import urllib.request
import urllib.error

API_URL = os.environ.get("API_URL", "https://ef59-35-231-117-249.ngrok-free.app").strip()

def my_model_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        
        # ユーザーメッセージを追加
        conversation_history.append({
            "role": "user",
            "content": message
        })

        # FastAPIへのリクエスト
        payload = {
            "prompt": message,
            "max_new_tokens": 32,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        request = urllib.request.Request(
            url=f"{API_URL}/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(request) as res:
            resp_data = res.read()
            response_body = json.loads(resp_data)
            print("FastAPI response:", json.dumps(response_body, default=str))

        if "generated_text" not in response_body:
            raise Exception("No generated_text in response")

        # 応答を会話履歴に追加
        conversation_history.append({
            "role": "assistant",
            "content": response_body["generated_text"]
        })

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": response_body["generated_text"],
                "conversationHistory": conversation_history
            })
        }

    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
