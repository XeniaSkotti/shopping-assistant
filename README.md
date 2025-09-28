# 🛍️ AI Shopping Assistant  

An **AI-powered shopping assistant** that helps users discover products based on natural language queries.  
The system demonstrates how to build an **enterprise-grade, agentic AI application** with retrieval, planning, observability, and governance features—without requiring a live cloud deployment.  

Example query:  

> “lightweight waterproof hiking jacket under £150, UK stock, eco-friendly brands”  

The assistant:  
1. Parses the request into structured constraints (category, price, region, brand features).  
2. Plans a tool-calling sequence (internal DB, external API).  
3. Retrieves and normalizes product data.  
4. Ranks results by relevance, constraints, availability, and diversity.  
5. Returns explainable recommendations with evidence and audit trail.

## 🏗️ Repository Structure

```
shopping-assistant/
├── services/              # Backend services
│   ├── core/             # Core orchestration service
│   ├── retrieval/        # Product data retrieval
│   ├── planning/         # AI planning and tool selection
│   ├── ranking/          # Product ranking algorithms
│   └── data/             # Data models and persistence
├── ui/                   # User interfaces
│   └── streamlit_app/    # Streamlit web application
├── infra/                # Infrastructure and deployment
│   ├── docker/           # Docker configurations
│   ├── k8s/              # Kubernetes manifests
│   ├── terraform/        # Infrastructure as Code
│   └── scripts/          # Deployment scripts
└── eval/                 # Evaluation and testing
```