# Services

This directory contains the backend services for the AI shopping assistant.

## Structure

- `core/` - Core business logic and orchestration
- `retrieval/` - Product data retrieval and search services
- `planning/` - AI planning and tool selection logic
- `ranking/` - Product ranking and recommendation algorithms
- `data/` - Data models, schemas, and database interactions

## Architecture

The services follow a microservices architecture where each service handles a specific aspect of the shopping assistant functionality:

1. **Core Service**: Orchestrates the entire shopping assistant workflow
2. **Retrieval Service**: Handles product data fetching from various sources
3. **Planning Service**: Uses AI to plan tool-calling sequences based on user queries
4. **Ranking Service**: Ranks and filters products based on relevance and constraints
5. **Data Service**: Manages product data persistence and normalization

Each service can be developed, tested, and deployed independently.