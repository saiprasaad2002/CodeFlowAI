from abc import abstractmethod
import json
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
SECRET_NAME = os.getenv("SECRET_NAME")

class SecretUtility():
    def __init__(self):        
        try:
            secretsManager = boto3.client('secretsmanager', region_name=AWS_REGION)
            secretResponse = secretsManager.get_secret_value(SecretId=SECRET_NAME)
            if 'SecretString' in secretResponse:
                secret = secretResponse['SecretString']
                self._secretDict = json.loads(secret)
            else:
                self._secretDict = {}
        except ClientError as e:
            raise e
        except Exception as e:
            raise e

    def getSecret(self, key):
        secret = self._secretDict.get(key)
        if secret is not None:
            print(f"Retrieved secret for key: {key}")
        else:
            print(f"No secret found for key: {key}")
        return secret
    