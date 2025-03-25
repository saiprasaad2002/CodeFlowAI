# DesignDevTest

![Python](https://img.shields.io/badge/Python-3.12-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115.7-green.svg) ![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20S3-orange.svg) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-SQLAlchemy-blue.svg)

## Overview

This project hosts a microservices-based application built with Python, FastAPI, and SQLAlchemy, designed to process user queries, manage code repositories, and generate code or content using AWS Bedrock's Large Language Model (Claude). Leverages a PostgreSQL database for persistent storage, AWS S3 for file management, and a modular architecture with endpoints `/queryValidator`, `/chunkPopulator`, `/contentAggregator`, `/instructionGenerator`, `/codeGenerator`, and `/repoConsolidator`. The system is containerized using Docker for scalable deployment.

This project is intended for developers and teams requiring automated code generation, repository consolidation, and content aggregation, with robust error handling and database interactions.

## Project Structure
```
├── app.py                  # FastAPI application with API endpoints
├── controller.py           # Controller logic for routing and validation
├── services.py             # Business logic for query processing and code generation
├── repository.py           # Database ORM models and operations
├── Utility/
│   ├── dbUtility.py        # Database connection and CRUD utilities
│   ├── llmUtility.py       # AWS Bedrock LLM integration
│   ├── s3Utility.py        # AWS S3 file operations
│   ├── secretUtility.py    # AWS Secrets Manager integration
├── Dockerfile              # Docker configuration for containerization
├── requirements.txt        # Python dependencies
└── README.md               # This file
```


## Key Features

- **Query Processing**: Validates user queries and routes them to appropriate services (`/queryValidator`).
- **Code Chunking**: Splits large code files into manageable chunks for processing (`/chunkPopulator`).
- **Content Aggregation**: Consolidates chunk descriptions into a unified summary (`/contentAggregator`).
- **Instruction Generation**: Identifies user intent and generates development instructions (`/instructionGenerator`).
- **Code Generation**: Produces code based on user queries and instructions using AWS Bedrock LLM (`/codeGenerator`).
- **Repository Consolidation**: Stores and updates repository data (`/repoConsolidator`).
- **Database Management**: Uses SQLAlchemy ORM with PostgreSQL for structured data storage.
- **File Storage**: Integrates AWS S3 for managing prompt files and other resources.
- **Error Logging**: Comprehensive error tracking with database logging.

## Architecture

The application follows a microservices-inspired design with a central FastAPI server routing requests to specialized endpoints. Each endpoint interacts with controllers, services, and repositories, leveraging AWS Bedrock for LLM capabilities, PostgreSQL for data persistence, and S3 for file storage.

### Workflow
1. **User Input**: A request hits an endpoint (e.g., `/queryValidator`) with query, email, and optional repo/file data.
2. **Validation**: Input is validated using Pydantic models and custom logic.
3. **Routing**: The request is routed to subsequent endpoints (e.g., `/instructionGenerator`, `/codeGenerator`) via HTTP redirects.
4. **Processing**: LLM calls via Bedrock generate descriptions or code, while database operations store results.
5. **Response**: A JSON response is returned with status codes and data.

## Prerequisites
- Python 3.12
- Docker (optional for containerized deployment)
- AWS account with Bedrock, S3, and Secrets Manager access
- PostgreSQL database

## Endpoints

| Method | Endpoint              | Description                                      |
|--------|-----------------------|--------------------------------------------------|
| POST   | `/queryValidator`     | Validates user query and determines processing route. |
| POST   | `/instructionGenerator` | Generates instructions based on validated queries. |
| POST   | `/chunkPopulator`     | Splits and processes large code into chunks.     |
| POST   | `/contentAggregator`  | Aggregates and summarizes chunked content.       |
| POST   | `/codeGenerator`      | Generates AI-assisted code based on user instructions. |
| POST   | `/repoConsolidator`   | Consolidates generated code into the repository. |
