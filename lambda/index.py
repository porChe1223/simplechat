import json
import os
import re  # 正規表現モジュールをインポート
import urllib.request  # urllibをインポート
import urllib.error

# Lambda コンテキストからリージョンを抽出する関数
def extract_region_from_arn(arn):
    # ARN 形式: arn:aws:lambda:region:account-id:function:function-name
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"  # デフォルト値

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        
        print("Processing message:", message)
        
        # リクエストペイロードを構築
        request_payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        # エンドポイントURL
        endpoint_url = "https://1c54-34-16-141-186.ngrok-free.app/generate"
        
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
                "response": assistant_response
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