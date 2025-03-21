import boto3
from Utility.secretUtility import SecretUtility
import urllib.parse
from dotenv import load_dotenv
import os
from botocore.exceptions import ClientError
import json
 
load_dotenv()

class S3utility:
    
    def __init__(self):
        self.secret =SecretUtility()
        self.bucket_name = self.secret.getSecret("S3_ENDPOINT")
        self.s3_client = boto3.client('s3', region_name=os.getenv("AWS_REGION"))
        
    def getFileLink(self, fileName):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=fileName)
            file_content = response['Body'].read()
            return file_content.decode('utf-8')
        except ClientError as e:
            raise e

    #PS_42 - PS_43
    #The `addFileToS3` method uploads a file to an S3 bucket using the provided filename and file content.
    #It uses the `s3Client` to put the object into the specified bucket, logging the successful upload upon completion.
    #The method handles exceptions by logging any errors that occur during the upload process and re-raising them
    def addFileToS3(self, fileName, fileContent):
        try:
            self.s3Client.put_object(Bucket=self.bucketName, Key=fileName, Body=fileContent)
        except ClientError as e:
            raise e
    def getFile(self, url_or_key):
        try:
            # If the URL is provided, extract the bucket name and key
            if url_or_key.startswith("http"):
                # Parse the public URL to get the key
                parsed_url = urllib.parse.urlparse(url_or_key)
                if parsed_url.netloc != f"{self.bucket_name}.s3.amazonaws.com":
                    raise ValueError("The provided URL does not match the configured bucket name.")
                file_key = parsed_url.path.lstrip('/')  # Remove the leading '/'
            else:
                # If not a URL, assume it is the file key
                file_key = url_or_key
            # Use the extracted key to get the object
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            print(response)
            file_content = response['Body'].read()
            return file_content.decode('utf-8')
        except Exception as e:
            raise Exception(f"An error occurred while fetching the file: {str(e)}")

    def uploadFile(self, file_path, folder_name, file_name):
        s3_key = f"{folder_name}/{file_name}"
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            public_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            return public_url
        except Exception as e:
            raise Exception(f"An error occurred while uploading the file: {str(e)}")

if __name__ == "__main__":
    file_path ='./instruction_prompt.txt'
    folder_name = 'Prompts'  
    file_name = 'instruction_prompt.txt'
    s3_utility = S3utility()
    try:
        public_url = s3_utility.uploadFile(file_path, folder_name, file_name)
        print(f"File successfully uploaded to: {public_url}")
        url=public_url
        content=s3_utility.getFile(url)
        print(content)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


