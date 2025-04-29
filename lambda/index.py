import json
import os
import re
import urllib.request
import urllib.error

def my_model_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']        
        print("Processing message:", message)

        # 会話履歴を使用
        conversation_history = body.get('conversationHistory', [])
        messages = conversation_history.copy()

        # ユーザーメッセージを履歴に追加
        messages.append({
            "role": "user",
            "content": message
        })

        prompt_parts = []
        for msg in messages:
            if msg["role"] == "user":
                prompt_parts.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant":
                prompt_parts.append(f"Assistant: {msg['content']}")
        
        # 全履歴をまとめたプロンプトにする
        prompt = "\n".join(prompt_parts)
        
        # リクエストペイロードを構築
        request_payload = {
            "prompt": prompt,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        # エンドポイントURL
        endpoint_url = "https://5c73-34-125-181-123.ngrok-free.app/generate"
        
        # リクエストを送信
        try:
            req = urllib.request.Request(
                url=endpoint_url,
                data=json.dumps(request_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req) as response:
                response_body = json.loads(response.read().decode('utf-8'))
                print("Response from external API:", json.dumps(response_body, default=str))
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTPError: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"URLError: {e.reason}")
        
        # 応答の検証
        if not response_body.get('generated_text'):
            raise Exception("No response content from the external API")
        
        # アシスタントの応答を取得
        assistant_response = response_body['generated_text']
        
        # アシスタントの応答も履歴に追加
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # 成功レスポンスの返却
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
                "response": assistant_response,
                "conversationHistory": messages
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