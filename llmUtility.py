# PS_LLM_01
# To import the necessary libraries
import json
import boto3
import os
from Utility.secretUtility import SecretUtility
from dotenv import load_dotenv

load_dotenv()
# PS_LLM_02 - PS_LLM_19
# To communicate with Large Language Model and return the response

def ClaudeJSONGenerator(content, system):
    try: 
        secret = SecretUtility()
        BEDROCK_MODEL_ID = secret.getSecret("BEDROCK_MODEL_ENDPOINT")
        _bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')        
        request = {
            "anthropic_version": "bedrock-2023-05-31",
            "system": content ,
            "messages": [{
                "role" : "user",
                "content" : system
            }],
            "max_tokens":4096
        }
        request = json.dumps(request)
        response = _bedrock.invoke_model(modelId=BEDROCK_MODEL_ID, body=request)
        model_response = json.loads(response["body"].read())
        response_text = model_response["content"][0]["text"]
        return response_text
    except Exception as e:
        return f"Error: {str(e)}"


