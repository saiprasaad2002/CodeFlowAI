#PS_QV_01 - PS_QV_02 /queryValidator Import Statements
#PS_CP_01 - PS_CP_07 /chunkPopulator Import Statements
#PS_CA_01 - PS_CA_02 /contentAggregator Import Statements
#PS_IG_01 - PS_IG_04 /instructionGenerator Import Statements
#PS_CG_01 - PS_CG_01 /codeGenerator Import Statements
#PS_RC_O1 - PS_RC_06 /repoConsolidator Import Statements

from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from controller import query_validate_query, instruction_validate_query, validateInput,validateQueryValidationInput, validateAndProcessInput, controllerContentAggregator
from typing import List, Dict, Optional, Union
from repository import logError
import httpx


app = FastAPI()


class CodeFile(BaseModel):
    filename: str
    code: str

#PS_CP_18 
#Pydantic class to validate the user input for /chunkPopulator endpoint
class QueryValidationInput(BaseModel):
    statuscode: int
    email: str
    query: str
    repoid: str
    code: List[Dict]

#PS_CA_05
#pydantic class to validate the user input for /contentAggregator
class InputJSON(BaseModel):
    statuscode:int
    query:str
    repoid: str
    email: str

#PS_CG_17
#pydantic class for validation in /codeGenerator
class ChangeInstruction(BaseModel):
    add: str
    delete: Union[str, None]
    update: Union[str, None]

#PS_CG_17
#pydantic class for validation in /codeGenerator
class FileInstruction(BaseModel):
    filename: str
    changes: ChangeInstruction
    reason: str

#PS_CG_17
#pydantic class for validation in /codeGenerator
class Instruction(BaseModel):
    intent: str
    instruction: FileInstruction

#PS_CG_17
#pydantic class for validation in /codeGenerator
class CodeGeneratorInput(BaseModel):
    status_code: int
    email: str
    repo_id: str
    query: str
    code: str
    instructions: List[Instruction]

class UserRequest(BaseModel):
    query: str
    email: str
    repo_id: Optional[str] = None 
    file_structure: Optional[List[Dict]] = None

class QueryModel(BaseModel):
    status_code : int
    query: str
    description: str
    email: str
    repo_id: str

class Payload(BaseModel):
    status_code: int
    repo_id: str
    email: str
    generatedCode: str
    description : str

#PS_CP_95, PS_CG_49
#redirects to the respective API
async def route_function(response, API_name):
    try:
        async with httpx.AsyncClient() as client:
            sample = await client.post(
                f"http://k8s-poc-rndpocin-baeb333b97-1835103098.us-east-1.elb.amazonaws.com:8080/{API_name}",
                json=response,
                timeout= 300.0
            )
            if sample.status_code == 200:
                return sample.json()
            else:
                return {"error": f"API {API_name} returned status {sample.status_code}", "response": sample.text, "statuscode": sample.status_code}
    except httpx.ReadTimeout:
        return {"error": f"Request to {API_name} timed out", "statuscode": 504}
    except httpx.RequestError as e:
        return {"error": f"Request to {API_name} failed", "details": str(e), "statuscode": 500}
    except Exception as e:
        return {"error": "Unexpected error occurred", "details": str(e), "statuscode": 500}

#PS_QV_09 - PS_QV_106
# To perform validation of the input
@app.post("/queryValidator")
async def query_validator(request_data: UserRequest):
    try:
        response = query_validate_query(request_data.dict())
        # PS_QV_64
        if response["status"] == 'instructionGenerator':
            response.pop('status')
            result = await route_function(response, 'instructionGenerator')
            if "error" in result:
                return JSONResponse(status_code=result["statuscode"], content=result)
            return result
        # PS_QV_96
        elif response["status"] == 'chunkPopulator':
            response.pop('status')
            result = await route_function(response, 'chunkPopulator')
            if "error" in result:
                return JSONResponse(status_code=result["statuscode"], content=result)
            return result
        else:
            return response  
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    
# PS_IG_14 - PS_IG_91
# To validate the user input and to route the response.
@app.post("/instructionGenerator")
async def post_validate_query(query_payload: QueryModel):
    try:
        data = query_payload.dict()
        response = instruction_validate_query(data)
        return await route_function(response, 'codeGenerator')
    except ValueError as ve:
        logError(str(ve),data["repo_id"],data["email"])
        raise HTTPException(status_code=400, detail={"error": str(ve), "status code": 400})
    except Exception as e:
        logError(str(e),data["repo_id"],data["email"])
        print(f"Detailed error in /instructionGenerator: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e), "function": "post_validate_query", "status code": 500})
    
# PS_RC_12 - PS_RC_88
# To validate the user input and return the response
@app.post("/repoConsolidator")
async def routeAPI(payload: Payload):
    try:
        response = validateInput(payload.dict())
        return response
    except ValueError as e:
        logError("Validation failed", payload.repo_id, payload.email)
        return {"statuscode": 400, "errormessage": "Validation failed"}
    except Exception as e:
        logError("routeAPI error", payload.repo_id, payload.email)
        return {"statuscode": 400, "errormessage": "routeAPI error"}

#PS_CP_17 - PS_CP_19
#postChunkPopulator routes the payload to controller function
@app.post("/chunkPopulator")
async def postChunkPopulator(payload: QueryValidationInput):
    try:
        response = validateQueryValidationInput(payload)
        if response:
            API_name = "contentAggregator"
            return await route_function(response, API_name)
        return JSONResponse(status_code=200, content=response)
    except ValueError as e:
        logError("Post Chunk Failed", payload.repoid, payload.email)
        return JSONResponse(status_code=400, content={"errorMessage": str(e), "status_code": 400})

#PS_CA_06 - PS_CA_45, PS_CA_111, PS_CA_117, PS_CA_123, PS_CA_127, PS_CA_132
#contentAggregator routes the input payload to the controller function
@app.post("/contentAggregator")
async def contentAggregator(input_json: InputJSON):
    try:
        statuscode = input_json.statuscode
        query = input_json.query
        repo_id = input_json.repoid
        email = input_json.email
        response = controllerContentAggregator(statuscode, query, repo_id, email)
        if response:
            API_name = "instructionGenerator"
            return await route_function(response,API_name)
        return response
    except Exception as e:
        logError("Content Aggregator routing failed", repo_id, email)
        return {"status_code": 400, "message": f"An error occurred: {str(e)}"}

#PS_CG_17 - PS_CG_18, PS_CG_71, PS_CG_82, PS_CG_93          
#routeAPI routes the input payload to the controller function
@app.post("/codeGenerator")
async def routeAPI(payload: CodeGeneratorInput):
    try:
        instructions_list = [inst.instruction for inst in payload.instructions]
        
        results = validateAndProcessInput(
            email=payload.email,
            repo_id=payload.repo_id,
            query=payload.query,
            code=payload.code,
            instructions=instructions_list
        )
        if results:
            API_name = "repoConsolidator"
            return await route_function(results,API_name)
        return results
    except HTTPException as e:
        logError("Validation failed", payload.repo_id, payload.email)
        return JSONResponse(status_code=e.status_code, content={"statuscode": e.status_code, "errormessage": e.detail})
    except Exception as e:
        logError(f"Route API processing failed: {e}", payload.repo_id, payload.email)
        return JSONResponse(status_code=400, content={"statuscode": 400, "errormessage": f"Route API processing failed: {e}"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)