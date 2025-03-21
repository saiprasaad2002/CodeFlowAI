#PS_QV_03 - PS_QV_04 /queryValidator Import Statements
#PS_CP_08 - PS_CP_10 /chunkPopulator Import Statements
#PS_CA_03 /contentAggregator Import Statements
#PS_IG_05 - PS_IG_08 /instructionGenerator Import Statements
#PS_CG_10 - PS_CG_11 /codeGenerator Import Statements
#PS_RC_07 - PS_RC_09 /repoConsolidator Import Statements

from repository import logError
from services import process_query_email, process_query_email_repo, process_query_email_structure, processPayload, identify_intent, chunkAndProcessCodeBlock, serviceContentAggregator,generateCode
from fastapi import HTTPException
import re
from pydantic import BaseModel
from typing import Union,List

class ChangeInstruction(BaseModel):
    add: str
    delete: Union[str, None]
    update: Union[str, None]

class FileInstruction(BaseModel):
    filename: str
    changes: ChangeInstruction
    reason: str

#PS_QV_12 - #PS_QV_19
#To check the payload and pass to respective functions
def query_validate_query(request_data):
    try:
        request_data = {k: v.strip() if isinstance(v, str) else v for k, v in request_data.items()}
        query = request_data.get('query')
        email = request_data.get('email')
        if not query or not email:
            error_message = "Missing required fields"
            return {"status": "error", "message": error_message, "status_code": 400}
        if not request_data.get('repo_id') and not request_data.get('file_structure'):
            return process_query_email(query, email)
        elif request_data.get('repo_id') and not request_data.get('file_structure'):
            return process_query_email_repo(query, email, request_data['repo_id'])
        elif not request_data.get('repo_id') and request_data.get('file_structure'):
            return process_query_email_structure(query, email, request_data['file_structure'])
    except HTTPException as e:
        raise e
    except Exception as e:
        logError(str(e), None, email, is_active=True)
        return {"status": "error", "message": "Internal server error", "status_code": 500}
    
# PS_IG_17 - PS_IG_21
# To validate the payload
def instruction_validate_query(data: dict):
    try:
        data["status_code"] = "200"
        clean_data = {k: v.strip() for k, v in data.items()}
        
        if all(clean_data.values()):
            intent = identify_intent(data)
            return intent
        else:
            raise ValueError("Some required fields are empty")
    except ValueError as ve:
        logError(str(ve),data["repo_id"],data["email"])
        raise HTTPException(status_code=400, detail={"error": str(ve), "status code": 400})
    except Exception as e:
        logError(str(e),data["repo_id"],data["email"])
        raise HTTPException(status_code=500, detail={"error": str(e), "function": "validate_query", "status code": 500})

# PS_RC_15 - PS_RC_22
# To validate the user payload and return response
def validateInput(payload: dict):
    try:
        payload["status_code"] = "200"
        clean_data = {k: v.strip() for k, v in payload.items()}
        if all(clean_data.values()):
            response = processPayload(clean_data)
            return response
        else:
            raise ValueError("Some required fields are empty")
    except ValueError as e:
        logError("Validation process error", payload['repo_id'], payload['email'])
        raise e
    except Exception as e:
        logError("Validation process error", payload['repo_id'], payload['email'])
        raise e
    
#PS_CP_20 - PS_CP_41
#validateQueryValidationInput validates the payload
def validateQueryValidationInput(payload):
    try:
        if not payload.code:
            raise ValueError('Code cannot be empty')
        str_repoid = str(payload.repoid)
        if not re.match(r'\b[a-f0-9]{8}\b-[a-f0-9]{4}\b-[a-f0-9]{4}\b-[a-f0-9]{4}\b-[a-f0-9]{12}\b', str_repoid):
            raise ValueError('Validation Failed because repoid does not match UUID format')
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', payload.email):
            raise ValueError('Validation Failed because email is missing or invalid format')
        return chunkAndProcessCodeBlock(payload.query, payload.statuscode, payload.email, payload.repoid, payload.code)
    except ValueError as e:
        logError(str(e), payload.repoid, payload.email)
        raise

#PS_CA_11 - PS_CA_44, #PS_CA_46 - PS_CA_47, PS_CA_110, PS_CA_116, PS_CA_120 - PS_CA_122, PS_CA_124 - PS_CA_126, PS_CA_131
#controllerContentAggregator validates the input payload
def controllerContentAggregator(statuscode, query, repo_id: str, email: str):
    try:
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValueError('Validation Failed because email is missing or invalid format')
        str_repoid = str(repo_id)
        if not re.match(r'\b[a-f0-9]{8}\b-[a-f0-9]{4}\b-[a-f0-9]{4}\b-[a-f0-9]{4}\b-[a-f0-9]{12}\b', str_repoid):
            raise ValueError('Validation Failed because repoid does not match UUID format')
        response = serviceContentAggregator(statuscode, query, repo_id, email)
        return response
    except ValueError as e:
        logError(str(e), repo_id, email)
        return {"statusCode": 400, "statusMessage": str(e)}

#PS_CG_19 - PS_CG_31, PS_CG_46
#validates the input payload
def validateAndProcessInput(email: str, repo_id: str, query: str, code, instructions: List[FileInstruction]):
    try:
        results=[]
        for instruction in instructions: 
            instruction_filename = instruction.filename.strip()
            changes = instruction.changes
            reason = instruction.reason.strip()
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
                raise ValueError('Validation Failed because email is missing or invalid format')

            if not re.match(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b", repo_id):
                raise ValueError('Validation Failed because repo id does not match UUID format')

            result = generateCode(
                email=email,
                repoId=repo_id,
                userQuery=query,
                filename=instruction_filename,
                changes=changes,
                reason=reason,
                code=code
            )
            results.append(result)
            return result
    except Exception as e:
        logError("Validation failed", repo_id, email)
        raise HTTPException(status_code=400, detail=str(e))

