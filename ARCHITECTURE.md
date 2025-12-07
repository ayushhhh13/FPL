# Architecture Documentation

## System Architecture

The Credit Card Assistant follows a microservices architecture with clear separation of concerns.

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI                           │
│              (Chat & Voice Interface)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Python Backend (FastAPI)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Classifier   │  │ Speech-to-   │  │   Agents     │     │
│  │   (LLM)      │  │    Text      │  │  (6 types)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   SQLite     │ │  Node.js     │ │   GCP        │
│  Database    │ │  API Service │ │  Speech API  │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Data Flow

1. **User Input (Text/Voice)**
   - User sends message via Streamlit UI
   - Voice input is converted to text using GCP Speech-to-Text

2. **Classification**
   - Query is classified using low-token LLM call
   - Returns category and task type (information/action)

3. **Agent Selection**
   - Appropriate agent is selected based on category
   - Agent processes query based on task type

4. **Response Generation**
   - Information queries: Read from database and return data
   - Action queries: Return action details and request consent

5. **Action Execution**
   - If user consents, action is sent to Node.js API
   - Node.js API simulates external service calls
   - Result is returned to user

### Agent Categories

1. **AccountAgent** - Account & Onboarding
   - Information: Account balance, card status, profile
   - Actions: Update email/phone, activate card

2. **DeliveryAgent** - Card Delivery
   - Information: Tracking status, delivery address
   - Actions: Update address, reschedule delivery

3. **TransactionAgent** - Transaction & EMI
   - Information: Transaction history, EMI details
   - Actions: Dispute transaction, convert to EMI

4. **BillAgent** - Bill & Statement
   - Information: Bill amount, due date, statements
   - Actions: Download statement, email statement

5. **RepaymentAgent** - Repayments
   - Information: Payment history, payment methods
   - Actions: Make payment, schedule payment

6. **CollectionsAgent** - Collections
   - Information: Overdue amounts, payment plans
   - Actions: Setup payment plan, pay overdue

### Design Principles

1. **Single Responsibility Principle**
   - Each agent handles one category
   - Classifier only classifies
   - Speech-to-text only converts audio

2. **Separation of Concerns**
   - Python backend: Business logic
   - Node.js backend: External API simulation
   - Database: Data persistence
   - UI: User interaction

3. **Consent Management**
   - All actions require explicit user consent
   - Consent is requested before execution
   - User can approve or cancel

### Database Schema

- **users**: User account information
- **card_deliveries**: Card delivery tracking
- **transactions**: Transaction records
- **bills**: Bill and statement records
- **repayments**: Repayment history
- **collections**: Collections information

### API Endpoints

#### Python Backend (Port 8000)
- `POST /chat` - Process chat message
- `POST /voice` - Process voice input
- `POST /classify` - Classify query
- `POST /consent` - Handle user consent

#### Node.js Backend (Port 3000)
- `POST /api/transactions` - Mock transaction API
- `POST /api/update-user` - Mock user update API
- `POST /api/delivery` - Mock delivery API
- `GET /api/health` - Health check

### Scalability Considerations

1. **Horizontal Scaling**
   - Python backend can be replicated
   - Node.js backend can be load balanced
   - Database can be moved to PostgreSQL/MySQL

2. **Interface Agnostic**
   - Architecture supports multiple interfaces
   - Can add WhatsApp, RCS, mobile app channels
   - Voice and text handled uniformly

3. **Medium Agnostic**
   - Text and voice processed similarly
   - Voice converted to text before processing
   - Response can be converted to speech if needed

### Security Considerations

1. **Authentication**: Add user authentication
2. **Authorization**: Verify user permissions
3. **Data Encryption**: Encrypt sensitive data
4. **API Security**: Add API keys/tokens
5. **Input Validation**: Validate all inputs

### Future Enhancements

1. Add authentication and authorization
2. Support multiple languages
3. Add voice response (text-to-speech)
4. Integrate with real payment gateways
5. Add analytics and monitoring
6. Implement caching for better performance
7. Add rate limiting
8. Support file uploads for statements

