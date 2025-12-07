# System Architecture

## Overview

The GenAI Credit Card Assistant is a microservices-based AI application that handles credit card customer queries and actions through natural language processing, supporting both text and voice inputs.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (Port 8501)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Chat Interface                                        │  │
│  │  • Voice Input (Audio Recorder)                          │  │
│  │  • Authentication (Login/Signup)                         │  │
│  │  • Consent Management UI                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Python Backend - FastAPI (Port 8000)               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Authentication Layer                                    │  │
│  │  • JWT Token Management                                 │  │
│  │  • User Authentication                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Query Processing Pipeline                               │  │
│  │  1. Speech-to-Text (AssemblyAI)                          │  │
│  │  2. Query Classifier (OpenAI GPT)                       │  │
│  │  3. Agent Router                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Specialized Agents (6 Categories)                      │  │
│  │  • AccountAgent      - Account & Onboarding             │  │
│  │  • DeliveryAgent     - Card Delivery                    │  │
│  │  • TransactionAgent  - Transactions & EMI                │  │
│  │  • BillAgent         - Bills & Statements               │  │
│  │  • RepaymentAgent    - Repayments                       │  │
│  │  • CollectionsAgent  - Collections                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Notification Services                                   │  │
│  │  • Email Service (Gmail API / File-based)               │  │
│  │  • WhatsApp Service (File-based)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────────┬────────────────────┘
             │                              │
             │                              │
    ┌────────▼────────┐          ┌────────▼────────┐
    │  SQLite Database │          │  Node.js API    │
    │   (Port N/A)     │          │  (Port 3000)    │
    │                  │          │                  │
    │ • Users          │          │ • Mock APIs      │
    │ • Transactions   │          │ • Transactions  │
    │ • Bills          │          │ • User Updates  │
    │ • Deliveries     │          │ • Card Actions  │
    │ • Repayments     │          │                  │
    │ • Collections    │          │                  │
    └──────────────────┘          └──────────────────┘
```

## Component Details

### 1. Streamlit UI (Frontend)
- **Technology**: Streamlit
- **Port**: 8501
- **Features**:
  - Real-time chat interface
  - Voice recording and playback
  - User authentication UI
  - Consent approval interface
  - Response visualization

### 2. Python Backend (Core Logic)
- **Technology**: FastAPI
- **Port**: 8000
- **Components**:
  - **Authentication**: JWT-based user authentication
  - **Speech-to-Text**: AssemblyAI integration for voice processing
  - **Query Classifier**: OpenAI GPT for intelligent query routing
  - **Agent System**: 6 specialized agents following Single Responsibility Principle
  - **Database Layer**: SQLAlchemy ORM with SQLite

### 3. Node.js Backend (API Service)
- **Technology**: Express.js
- **Port**: 3000
- **Purpose**: Mock external API services
- **Endpoints**:
  - Transaction processing
  - User profile updates
  - Card management (block/unblock/activate)
  - Delivery tracking updates

### 4. Database (Data Persistence)
- **Technology**: SQLite
- **Schema**:
  - Users (authentication, profile, card info)
  - Transactions (payment history)
  - Bills (statements, due dates)
  - Card Deliveries (tracking, addresses)
  - Repayments (payment history)
  - Collections (overdue management)

## Data Flow

### Text Query Flow
```
User Input (Text)
    ↓
Streamlit UI
    ↓
POST /chat (FastAPI)
    ↓
JWT Authentication
    ↓
Query Classifier (OpenAI)
    ↓
Agent Selection (Based on Category)
    ↓
Agent Processing
    ├─ Information Query → Database Query → Response
    └─ Action Query → Consent Request → User Approval → Node.js API → Response
    ↓
Email/WhatsApp Notification (Async)
    ↓
Response to UI
```

### Voice Query Flow
```
User Voice Input
    ↓
Streamlit UI (Audio Recording)
    ↓
POST /voice (FastAPI)
    ↓
JWT Authentication
    ↓
Speech-to-Text (AssemblyAI)
    ↓
Query Classifier (OpenAI)
    ↓
[Same as Text Query Flow]
```

## Agent Architecture

### Base Agent Pattern
All agents inherit from `BaseAgent` and implement:
- `process(query, user_id, task_type)` - Main processing method
- `handle_information(query, user_id)` - Information retrieval
- `handle_action(query, user_id)` - Action execution with consent

### Agent Categories

1. **AccountAgent**
   - Information: Balance, credit limit, card status, profile
   - Actions: Update email/phone, activate/block/unblock card

2. **DeliveryAgent**
   - Information: Delivery status, tracking number, address
   - Actions: Update delivery address, reschedule delivery

3. **TransactionAgent**
   - Information: Transaction history, EMI details, disputes
   - Actions: Make transaction, dispute transaction, convert to EMI

4. **BillAgent**
   - Information: Bill amount, due date, statements
   - Actions: Download statement, email statement

5. **RepaymentAgent**
   - Information: Payment history, payment methods
   - Actions: Make payment, schedule payment

6. **CollectionsAgent**
   - Information: Overdue amounts, payment plans
   - Actions: Setup payment plan, pay overdue amount

## Design Principles

### 1. Single Responsibility Principle
- Each agent handles one specific category
- Classifier only classifies queries
- Speech-to-Text only converts audio
- Database layer only handles data persistence

### 2. Separation of Concerns
- **UI Layer**: User interaction and presentation
- **Business Logic**: Python backend with agents
- **External APIs**: Node.js backend for mock services
- **Data Layer**: SQLite database

### 3. Consent Management
- All actions require explicit user consent
- Consent is requested before execution
- User can approve or cancel any action
- Actions are logged for audit purposes

### 4. Scalability
- Microservices architecture allows independent scaling
- Database can be upgraded to PostgreSQL/MySQL
- Agents can be distributed across services
- Stateless design enables horizontal scaling

## Security Features

1. **Authentication**: JWT-based token authentication
2. **Password Hashing**: bcrypt for secure password storage
3. **Authorization**: User-specific data access
4. **Input Validation**: Pydantic models for request validation
5. **CORS**: Configured for secure cross-origin requests

## Technology Stack

### Backend
- **Python 3.8+**: FastAPI, SQLAlchemy, OpenAI, AssemblyAI
- **Node.js 14+**: Express.js
- **Database**: SQLite (production-ready for PostgreSQL)

### Frontend
- **Streamlit**: Web UI framework
- **Audio Recorder**: Streamlit audio recorder component

### AI/ML
- **OpenAI GPT**: Query classification
- **AssemblyAI**: Speech-to-Text conversion

### External Services
- **Gmail API**: Email notifications (optional)
- **WhatsApp API**: WhatsApp notifications (optional, file-based fallback)

## Deployment Architecture

### Development
- All services run locally
- SQLite for database
- File-based notifications

### Production (Recommended)
- **UI**: Streamlit Cloud or Docker container
- **Python Backend**: Docker container or cloud service (AWS/GCP)
- **Node.js Backend**: Docker container or cloud service
- **Database**: PostgreSQL or MySQL
- **Load Balancer**: For horizontal scaling
- **Message Queue**: For async notifications

## Future Enhancements

1. **Multi-language Support**: Internationalization
2. **Text-to-Speech**: Voice responses
3. **Real Payment Integration**: Actual payment gateways
4. **Analytics Dashboard**: Usage metrics and insights
5. **Caching Layer**: Redis for performance
6. **Rate Limiting**: API protection
7. **Monitoring**: Logging and error tracking
8. **CI/CD Pipeline**: Automated deployment
