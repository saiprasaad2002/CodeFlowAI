# DesignDevTest Repository

![Python](https://img.shields.io/badge/Python-3.12-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115.7-green.svg) ![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20S3-orange.svg) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-SQLAlchemy-blue.svg)

## Overview

The **DesignDevTest** repository hosts a microservices-based application built with Python, FastAPI, and SQLAlchemy, designed to process user queries, manage code repositories, and generate code or content using AWS Bedrock's Large Language Model (LLM). It leverages a PostgreSQL database for persistent storage, AWS S3 for file management, and a modular architecture with endpoints like `/queryValidator`, `/chunkPopulator`, `/contentAggregator`, `/instructionGenerator`, `/codeGenerator`, and `/repoConsolidator`. The system is containerized using Docker for scalable deployment.

This project is intended for developers and teams requiring automated code generation, repository consolidation, and content aggregation, with robust error handling and database interactions.

## Project Structure
