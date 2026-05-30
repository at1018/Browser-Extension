# AI Visual Copilot — Product Requirements

## Product Vision

AI Visual Copilot is an AI-first platform that transforms screenshots into persona-aware outcomes. Users receive tailored assistance based on their role, context, and the screenshot content.

## Target Personas

- **Developer**: debug errors, explain code, search docs, generate fixes
- **QA Engineer**: create Jira tickets, generate test cases, create repro steps, assign severity
- **Student**: explain concepts, summarize, generate notes, create quizzes
- **Designer**: detect fonts, extract colors, generate HTML/CSS, find similar designs
- **Shopper**: compare prices, find similar products, analyze reviews, recommend affiliates
- **Analyst**: analyze charts, generate insights, export reports

## Core Product Capabilities

- Screenshot capture and automatic detection
- OCR and vision understanding pipeline
- Persona identification and action routing
- Intent detection classification
- Provider-agnostic AI model orchestration
- Modular workflows using LangGraph and LangChain
- Structured data extraction for text, code, UI, charts, errors, and products

## Major System Components

- Chrome Extension frontend
- FastAPI backend API and orchestration services
- Multi-model provider abstraction layer
- Persona engine with role-specific workflows
- Intent detection and action router
- Supabase-powered authentication, database, and storage
- Stripe billing and subscription management

## Data and User Flows

1. User captures or uploads a screenshot.
2. Backend ingests the image.
3. OCR and vision pipeline extracts structured information.
4. Intent and persona engines determine best workflow.
5. Model router selects the optimal AI provider.
6. Specialized agents generate results and actions.
7. Results persist in history and workflow logs.

## Constraints

- Build with Chrome Extension Manifest V3
- Use React + TypeScript + TailwindCSS for frontend
- Use FastAPI and Python for backend
- Keep the provider layer abstract and extensible
- Generate documentation before implementing business logic
- Design for a scalable SaaS architecture from day one
