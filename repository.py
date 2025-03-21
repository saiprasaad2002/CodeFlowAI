#PS_QV_06 /queryValidator Import Statements
#PS_CP_15 - PS_CP_16 /chunkPopulator Import Statements
#PS_IG_10 - PS_IG_13 /instructionGenerator Import Statements
#PS_CG_16 /codeGenerator Import Statements
#PS_RC_11 /repoConsolidator Import Statements

from sqlalchemy import update
import uuid
from Utility.dbUtility import insertORMRecord, updateORMRecord, fetchORMData1,fetchORMData, ErrorLog, UserDetails, Consolidated, Conversation, Repository, ChunkRelations

# PS_QV_14 - PS_QV_15, PS_QV_17, PS_QV_39 - PS_QV_40, PS_QV_42, PS_QV_68 - PS_QV_69, PS_QV_71, PS_QV_100 - PS_QV_101, PS_QV_103
#To insert the error message inside the database 
def logError(message: str, repoid: uuid, email: str):
    log_record = ErrorLog(
        error_message=message,
        repo_id=str(repoid),
        email=email
    )
    try:
        result = insertORMRecord(log_record)
        if result["status_code"] != 200:
            print(f"Failed to log error. Status Code: {result['status_code']}, Message: {result['message']}")
    except Exception as e:
        print(f"Exception occurred during logging to database: {e}")

#PS_QV_21 - PS_QV_22
# To store the user data
def store_user_data(query, email):
    repo_id = ''
    code = Repository(code_block = None)
    try:
        result = insertORMRecord(code)
        if result["status_code"] != 200:
            print(f"Failed to log error. Status Code: {result['status_code']}, Message: {result['message']}")
        else:
            def query_function(session):
                return session.query(Repository).order_by(Repository.created_at.desc())
            result = fetchORMData(query_function)
            repo_id = repo_id + str(result["data"][0]["repo_id"])
    except Exception as e:
        print(f"Exception occurred during logging to database: {e}")

    user_details = UserDetails(email=email, is_active=True)
    try:
        result = insertORMRecord(user_details)
        if result["status_code"] != 200:
            print(f"Failed to log error. Status Code: {result['status_code']}, Message: {result['message']}")
    except Exception as e:
        print(f"Exception occurred during logging to database: {e}")

    conversation = Conversation( email = email, repo_id = repo_id, question = query, code = None)
    try:
        result = insertORMRecord(conversation)
        if result["status_code"] != 200:
            print(f"Failed to log error. Status Code: {result['status_code']}, Message: {result['message']}")
    except Exception as e:
        print(f"Exception occurred during logging to database: {e}")
    finally:
        return repo_id
    
#PS_QV_44 - PS_QV_45
# To store the user data and file structure
def store_user_code(query, email, file_structure):
    repo_id = ''
    code = Repository(code_block = str(file_structure))
    try:
        result = insertORMRecord(code)
        if result["status_code"] != 200:
            print(f"Failed to log error. Status Code: {result['status_code']}, Message: {result['message']}")
        else:
            def query_function(session):
                return session.query(Repository).order_by(Repository.created_at.desc())
            result = fetchORMData(query_function)
            repo_id = repo_id + str(result["data"][0]["repo_id"])
    except Exception as e:
        print(f"Exception occurred during logging to database: {e}")
    user_details = UserDetails(email=email, is_active=True)
    try:
        result = insertORMRecord(user_details)
        if result["status_code"] != 200:
            print(f"Failed to log error. Status Code: {result['status_code']}, Message: {result['message']}")
    except Exception as e:
        print(f"Exception occurred during logging to database: {e}")
    conversation = Conversation( email = email, repo_id = repo_id, question = query, code = str(file_structure))
    try:
        result = insertORMRecord(conversation)
        if result["status_code"] != 200:
            print(f"Failed to log error. Status Code: {result['status_code']}, Message: {result['message']}")
    except Exception as e:
        print(f"Exception occurred during logging to database: {e}")
    finally:
        return repo_id
    
#PS_QV_79 - PS_QV_80
# To store the user data
def store_user_repo(query, email, repo_id):
    conversation = Conversation( email = email, repo_id = repo_id, question = query, code = None)
    try:
        result = insertORMRecord(conversation)
        if result["status_code"] != 200:
            print(f"Failed to log error. Status Code: {result['status_code']}, Message: {result['message']}")
    except Exception as e:
        print(f"Exception occurred during logging to database: {e}")
#PS_QV_51 - PS_QV_54
# To get the description with repo id
def get_description(repo_id):
    def query_function(session):
        return session.query(Consolidated).filter(Consolidated.repo_id == repo_id)
    result = fetchORMData(query_function)
    return result["data"][0]["description"]
# PS_IG_73- PS_IG_74
# To get the code block.
def fetchcode(repo_id):
    def query_function(session):
        return session.query(Repository).filter(Repository.repo_id == repo_id)
    result = fetchORMData(query_function)
    return result["data"][0]["code_block"]


# PS_RC_58 - PS_RC_84
# To store the data in their respective tables.

def storeData(generated_code, repo_id, email, description):

    try:
        info = Consolidated(repo_id = repo_id, description = description)
        result = insertORMRecord(info)
        if result["status_code"] != 200:
            print(f"Failed to log error. Status Code: {result['status_code']}, Message: {result['message']}")
    except Exception as e:
        print(f"Exception occurred during logging to database: {e}")

    try:
        consolidated_record = update(Repository).where(Repository.repo_id == repo_id).values(code_block = generated_code) 
        result = updateORMRecord(consolidated_record)
        if result["status_code"] != 200:
            print(f"Failed to log error. Status Code: {result['status_code']}, Message: {result['message']}")
    except Exception as e:
        print(f"Exception occurred during logging to database: {e}")

#PS_CP_56 - PS_CP_59
#storeChunksInDB stores the chunks inside the database
def storeChunksInDB(chunks: list, repoid: str, email: str, filename:str):
    chunk_ids = []
    for chunk in chunks:
        chunk_record = ChunkRelations(
            id=uuid.uuid4(),
            chunk=chunk,
            repo_id=repoid,
            filename = filename
        )
        try:
            result = insertORMRecord(chunk_record)
            if result["status_code"] != 200:
                log_error_message = f"Error inserting chunk, status code: {result['status_code']}"
                logError(log_error_message, repoid, email)
                raise Exception(result["message"])
            else:
                chunk_ids.append(chunk_record.id)
        except Exception as e:
            logError(str(e), repoid, email)
            raise
    return chunk_ids

#PS_CP_77 - PS_CP_119
#updateChunkDescriptionInDB updates the chunk with their respective generated description
def updateChunkDescriptionInDB(chunk_ids: list, descriptions: list, repoid: str, email: str):
    for chunk_id, description in zip(chunk_ids, descriptions):
        update_query = update(ChunkRelations).where(
            ChunkRelations.id == chunk_id,
            ChunkRelations.repo_id == repoid
        ).values(description=description)
        try:
            result = updateORMRecord(update_query)
            if result["status_code"] != 200:
                logError(f"Error updating chunk description, status code: {result['status_code']}", repoid, email)
                raise Exception(result["message"])
        except Exception as e:
            logError(f"Error updating chunk description: {e}", repoid, email)
            raise

#PS_CP_42 - PS_CP_76
#fetchChunksFromDB fetches the chunks from the database to send it for generating description
def fetchChunksFromDB(repoid: str):
    def query_function(session):
        return session.query(ChunkRelations.chunk).filter_by(repo_id=repoid)
    result = fetchORMData1(query_function)
    return result

#PS_CA_52 - PS_CA_56
#getChunkDescription fetches the description
def getChunkDescription(repo_id: str,email):
    try:
        def query_function(session):
            return session.query(ChunkRelations.description).filter_by(repo_id=repo_id)
        result = fetchORMData1(query_function)
        return result
    except Exception as e:
        logError(str(e),repo_id,email)
        return {"statusCode": 400, "statusMessage": "An error occurred in getChunkDescription() function"}

#PS_CA_57 - PS_CA_59
#fetchAllChunks fetches the chunks from the database
def fetchAllChunks(repo_id: str):
    try:
        def query_function(session):
            return session.query(ChunkRelations.chunk).filter(ChunkRelations.repo_id == repo_id)
        result = fetchORMData1(query_function)
        return result
    except Exception as e:
        logError(str(e), repo_id)
        return {"statusCode": 400, "statusMessage": "An error occurred in fetchAllChunks() function"}

#PS_CA_96 - PS_CA_108, PS_CA_112 - PS_CA_114
#inserts the consolidated description
def insertConsolidatedRecord(description: str, code_block: str, repo_id: str):
    try:
        insertion = Consolidated(description=description, code=code_block, repo_id=repo_id)
        result = insertORMRecord(insertion)
        return result
    except Exception as e:
        logError(str(e), repo_id)
        return {"statusCode": 400, "statusMessage": "An error occurred in insertConsolidatedRecord() function"}

#PS_CG_37 - PS_CG_44
#stores the user conversation inside the database
def storeConversation(email: str, repoId: str, query: str, code: str):
    try:
        conversation = Conversation(email=email, repo_id=repoId, question=query, code=code)
        result = insertORMRecord(conversation)
        return result
    except Exception as e:
        error_log = ErrorLog(error_message="Conversation storage failed", repo_id=repoId, email=email)
        insertORMRecord(error_log)
        raise