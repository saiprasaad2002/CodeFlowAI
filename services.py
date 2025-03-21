#PS_QV_05 /queryValidator Import Statements
#PS_CP_11 - PS_CP_14 /chunkPopulator Import Statements
#PS_CA_04 /contentAggregator Import Statements
#PS_IG_09 /instructionGenerator Import Statements
#PS_CG_12 - PS_CG_15 /codeGenerator Import Statements
#PS_RC_10 /repoConsolidator Import Statements

from Utility.llmUtility import ClaudeJSONGenerator
from repository import store_user_data, get_description, logError, store_user_code, store_user_repo, fetchcode, storeData
from Utility.s3Utility import S3utility
import json
from fastapi import HTTPException
import threading
from repository import storeChunksInDB, updateChunkDescriptionInDB, logError, fetchChunksFromDB, getChunkDescription, fetchAllChunks, insertConsolidatedRecord,storeConversation
from fastapi import HTTPException


s3util = S3utility()

#PS_QV_19 - PS_QV_45
# To process the query and email input from user
def process_query_email(query, email):
    try:
        repoid = store_user_data(query, email)
        system_prompt = s3util.getFileLink("Prompts/query_email.txt")
        description = ClaudeJSONGenerator(system_prompt, query)
        result = json.loads(description)
        if result["response"] == "true":
            return {"status": "instructionGenerator", "status_code": 200, "query": query, "description": "No code was given", "email": email, "repo_id": repoid}
        else:
            return {"status": "error", "message": "Invalid description generated", "status_code": 400}
    except Exception as e:
        logError(str(e), repoid, email)
        return {"status": "error", "message": "Internal server error", "status_code": 500}

#PS_QV_46 - PS_QV_74
# To process the query, repo id and email input from user
def process_query_email_repo(query, email, repo_id):
    try:
        store_user_repo(query, email, repo_id)
        description = get_description(repo_id)
        system_prompt = s3util.getFileLink("Prompts/query_description.txt")
        user_input = f""" query : + {query},
          description" : {description}"""
        is_related = ClaudeJSONGenerator(system_prompt, user_input)
        result = json.loads(is_related)
        if result["response"] == "true":
            return {"status": "instructionGenerator", "status_code": 200, "query": query, "description": description, "email": email, "repo_id": repo_id}
        else:
            return {"status": "error", "message": "Query not related to repository content", "status_code": 400}
    except Exception as e:
        logError(str(e), repo_id, email, is_active=True)
        return {"status": "error", "message": "Error processing repository-related query", "status_code": 500}

#PS_QV_75 - PS_QV_106
# To process the query, file structure and email input from user
def process_query_email_structure(query, email, file_structure):
    try:
        repoid = store_user_code(query, email, file_structure)
        file = []
        for item in file_structure:
            for filename, code in item.items():
                file.append({
                "filename": filename,
                "code": code
                })
        system_prompt = s3util.getFileLink("Prompts/prompt_query_file.txt")
        user_input = f"""query : + {query}, file_structure" : {file_structure}"""
        is_related = ClaudeJSONGenerator(system_prompt, user_input)
        result = json.loads(is_related)
        if result["response"] == "true":
            return {"status": "chunkPopulator",  "statuscode": 200, "email": email, "query": query, "repoid": repoid, "code": file}
        else:
            return {"status": "error", "message": "Query not related to file structure", "status_code": 400}
    except Exception as e:
        logError(str(e), repoid, email)
        return {"status": "error", "message": "Error processing file structure-related query", "status_code": 500}
    
# PS_IG_42 - PS_IG_55
# To identify the user intent 
def identify_intent(data: dict):
    try:
        system_prompt = s3util.getFileLink("Prompts/intent_prompt.txt")
        user_prompt = f" query : {data["query"]}"
        intent = ClaudeJSONGenerator(system_prompt, user_prompt)
        intent=json.loads(intent)
        response = generate_instruction(intent, data)
        return response
    
    except Exception as e:
        logError(str(e),data["repo_id"],data["email"])
        raise HTTPException(status_code=500, detail={"error": str(e), "function": "identify_intent", "status code": 500})
    
# PS_IG_58 - PS_IG_90
# To generate the instructions
def generate_instruction(intent, data):
    try:
        if intent["response"] == "design":
            return {"response" : "Invalid"}
            
        elif intent["response"] == "development":
            code = fetchcode(data["repo_id"])
            system_prompt = s3util.getFileLink("Prompts/instruction_prompt.txt")
            user_prompt = f""" code : {code},
                               query : {data["query"]} """
            dev_instructions = ClaudeJSONGenerator(system_prompt, user_prompt)
            instructions = json.loads(dev_instructions)
            return {"status_code" : 200, "email" : data["email"], "repo_id" : data["repo_id"], "query" : data["query"], "code" : code, "instructions": instructions}
        if intent["response"] == "test cases":
            return {"response" : "Invalid"}
    except Exception as e:
        logError(str(e),data["repo_id"],data["email"])
        raise HTTPException(status_code=500, detail={"error": str(e), "function": "generate_instruction", "status code": 500})
# PS_RC_23 - PS_RC_85
# To store the given payload in database
def processPayload(payload: dict):
    try:
        repo_id = payload['repo_id']
        generated_code = payload['generatedCode']
        email = payload['email']
        description = payload["description"]
        storeData(generated_code, repo_id, email, description)
        return {
            "statusCode": 200,
            "email": email,
            "code" : generated_code
        }
    except Exception as e:
        logError("Processing error", payload['repo_id'], payload['email'])
        raise e

#PS_CP_42 - PS_CP_76
#chunkAndProcessCodeBlock chunks the code block per 4000 characters
def chunkAndProcessCodeBlock(query: str, statuscode: int, email: str, repoid: str, code):
    try:
        for code_file in code:
            filename = code_file['filename']
            code = code_file['code']
            chunks = [code[i:i+4000] for i in range(0, len(code), 4000)] if len(code) > 4000 else [code]
            threads = [threading.Thread(target=processChunk, args=(chunk,)) for chunk in chunks]
            for thread in threads:
                thread.start()
        
            for thread in threads:
                thread.join()
            chunk_ids = storeChunksInDB(chunks, repoid, email, filename)
            fetched_chunks_result = fetchChunksFromDB(repoid)
            if fetched_chunks_result['status_code'] != 200:
                raise Exception(f"Failed to fetch chunks: {fetched_chunks_result['message']}")
            fetched_chunks = [chunk[0] for chunk in fetched_chunks_result['data']]
            s3_utility = S3utility()
            description_prompt = s3_utility.getFileLink("Prompts/descriptionGen.txt")
            descriptions = [ClaudeJSONGenerator(description_prompt, chunk) for chunk in fetched_chunks]
            if descriptions:
                updateChunkDescriptionInDB(chunk_ids, descriptions, repoid, email)
        return {
            "statuscode":200,
            "query": query,
            "repoid": repoid,
            "email": email,
        }
    except Exception as e:
        logError(f"Chunk Processing Error : {e}", repoid, email)
        raise ValueError(f"Chunk Processing Error during chunkAndProcessCodeBlock: {e}")

def processChunk(chunk: str):
    return chunk

#PS_CA_48 - PS_CA_95, PS_CA_128 - PS_CA_130
#serviceContentAggregator fetches the chunk description for consolidation
def serviceContentAggregator(statuscode, query, repo_id: str, email: str):
    try:
        response = getChunkDescription(repo_id,email)
        chunks = fetchAllChunks(repo_id)
        if response["status_code"] != 200:
            return response
        chunk_descriptions = [chunk[0] for chunk in response["data"]]
        code_chunks = [chunk[0] for chunk in chunks["data"]]
        combined_code_block = "\n".join(code_chunks)
        combined_description = " ".join(chunk_descriptions)
        summary = generateSummary(combined_description)
        insertConsolidatedRecord(summary, combined_code_block, repo_id)
        return {"status_code":statuscode,"query":query,"description":str(summary),"email":email,"repo_id":repo_id}
    except Exception as e:
        logError(f"An error occurred in serviceContentAggregator: {str(e)}",repo_id,email)
        return {"statusCode": 400, "statusMessage": f"An error occurred in serviceContentAggregator(): {e}"}
    
#PS_CA_93 - PS_CA_95, PS_CA_109, PS_CA_115, PS_CA_118 - PS_CA_119
#generates consolidated description
def generateSummary(combined_description: str):
    s3utility = S3utility()
    wholeDescGenPrompt = s3utility.getFileLink("Prompts/wholedescription.txt")
    description =  ClaudeJSONGenerator(wholeDescGenPrompt,combined_description)
    return description

#PS_CG_32 - PS_CG_36, PS_CG_45
#generateCode generates code block
def generateCode(email: str, repoId: str, userQuery: str, filename, changes, reason, code):
    try:
        s3Utility = S3utility()
        codeGenprompt = s3Utility.getFileLink("Prompts/code.txt")
        userinput = f"user query: {userQuery}, code: {code}, filename:{filename}, changes: {changes}, reason: {reason}"
        generated_code = ClaudeJSONGenerator(codeGenprompt,userinput)
        storeConversation(email, repoId, userQuery, generated_code)
        dictGenCode = json.loads(generated_code)
        description = dictGenCode['description']
        gencode = dictGenCode['code']
        return {"status_code":200, "repo_id": repoId, "email": email, "generatedCode": str(gencode), "description":description}
    except Exception as e:
        logError(f"LLM code generation failed:{e}", repoId, email)
        raise HTTPException(status_code=400, detail="LLM code generation failed")