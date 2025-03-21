from sqlalchemy import create_engine, Column, String, Text, Boolean, DateTime, ForeignKey,func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from sqlalchemy import update
from Utility.secretUtility import SecretUtility
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError

Base = declarative_base()
SCHEMA_NAME = 'designdevtest'

class ChunkRelations(Base):
    __tablename__ = 'chunkrelations'
    __table_args__ = {'schema': SCHEMA_NAME}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255))
    chunk = Column(Text)
    description = Column(Text)
    repo_id = Column(UUID(as_uuid=True), ForeignKey('designdevtest.repository.repo_id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Consolidated(Base):
    __tablename__ = 'consolidated'
    __table_args__ = {'schema': SCHEMA_NAME}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo_id = Column(UUID(as_uuid=True))
    code = Column(Text)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Conversation(Base):
    __tablename__ = 'conversation'
    __table_args__ = {'schema': SCHEMA_NAME}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255))
    repo_id = Column(UUID(as_uuid=True))
    question = Column(Text)
    code = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ErrorLog(Base):
    __tablename__ = 'errorlog'
    __table_args__ = {'schema': SCHEMA_NAME}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    error_message = Column(Text)
    repo_id = Column(UUID(as_uuid=True), nullable= True)
    email = Column(String(255), unique= False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Repository(Base):
    __tablename__ = 'repository'
    __table_args__ = {'schema': 'designdevtest'}
    repo_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_block = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

class UserDetails(Base):
    __tablename__ = 'userdetails'
    __table_args__ = {'schema': SCHEMA_NAME}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

def connectToCloudDatabase():
    try:
        secrets = SecretUtility()
        connection_str = f"postgresql+psycopg2://{secrets.getSecret('DB_USER')}:{secrets.getSecret('DB_PWD')}@{secrets.getSecret('DB_HOST')}:{secrets.getSecret('DB_PORT')}/{secrets.getSecret('DB_NAME')}"
        engine = create_engine(connection_str)
        return engine
    except Exception as e:
        raise e

engine = connectToCloudDatabase()
Session = sessionmaker(bind=engine)


def insertORMRecord(record):
    session = Session()
    try:
        session.add(record)
        session.commit()
        session.refresh(record)
        return {"status_code": 200, "message": "Insertion Successful"}
    except IntegrityError as ie:
        session.rollback()
        print(f"IntegrityError: {ie.orig}")
        return {"status_code": 400, "message": str(ie.orig)}
    except DataError as de:
        session.rollback()
        print(f"DataError: {de.orig}")
        return {"status_code": 400, "message": str(de.orig)}
    except DatabaseError as db_err:
        session.rollback()
        print(f"DatabaseError: {db_err.orig}")
        return {"status_code": 400, "message": str(db_err.orig)}
    except Exception as e:
        session.rollback()
        print(f"General Exception: {e}")
        return {"status_code": 400, "message": "Insertion Failed"}
    finally:
        session.close()

def updateORMRecord(query):
    session = Session()
    try:
        session.execute(query)
        session.commit()
        return {"status_code": 200, "message": "Update Success"}
    except Exception:
        session.rollback()
        return {"status_code": 400, "message": "Update Failed"}
    finally:
        session.close()

def fetchORMData(query_function):
    session = Session()
    try:
        def serialize_orm(obj):
            return {column.name: str(getattr(obj, column.name)) for column in obj.__table__.columns}
        query = query_function(session)
        result = query.all()
        data = [serialize_orm(r) for r in result]
        return {"status_code": 200, "message": "Fetch Success", "data": data}
    except Exception:
        return {"status_code": 400, "message": "Fetch Failed", "data": []}
    finally:
        session.close()
    
def fetchORMData1(query_function):
    session = Session()
    try:
        query = query_function(session)
        result = query.all()
        return {"status_code": 200, "message": "Fetch Success", "data": result}
    except Exception:
        return {"status_code": 400, "message": "Fetch Failed", "data": []}
    finally:
        session.close()