# Credit Card Assistant - Detailed Documentation

## Overview

The Credit Card Assistant is an AI-powered chatbot that helps customers with credit card-related queries and actions. It supports both text and voice inputs, and can handle informational queries as well as actionable requests.

## Features

### Query Categories

1. **💳 Account & Onboarding**
   - Account balance and credit limit
   - Card status and activation
   - Profile information
   - Account updates

2. **🚚 Card Delivery**
   - Delivery tracking
   - Delivery status
   - Address updates
   - Delivery rescheduling

3. **💰 Transaction & EMI**
   - Transaction history
   - EMI details
   - Transaction disputes
   - EMI conversion

4. **📄 Bill & Statement**
   - Bill amount and due date
   - Statement download
   - Bill details
   - Statement email

5. **💸 Repayments**
   - Payment history
   - Payment methods
   - Make payment
   - Schedule payment

6. **🚨 Collections**
   - Overdue amounts
   - Payment plans
   - Settlement options

### Task Types

1. **Information Retrieval**
   - Read-only queries
   - Fetch data from database
   - No user consent required
   - Examples: "What's my balance?", "Show recent transactions"

2. **Action Execution**
   - Modify data or initiate transactions
   - Requires explicit user consent
   - Examples: "Make a payment", "Update my email"

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- GCP account with Speech-to-Text API enabled
- OpenAI API key

### Step-by-Step Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd ayush
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up Node.js backend**
```bash
cd nodejs_backend
npm install
cd ..
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - GCP_PROJECT_ID
# - GCP_CREDENTIALS_PATH
```

5. **Initialize database**
```bash
python database/init_db.py
```

## Running the Application

### Start Services

1. **Start Node.js API service** (Terminal 1)
```bash
cd nodejs_backend
node server.js
# Service runs on http://localhost:3000
```

2. **Start Python backend** (Terminal 2)
```bash
cd python_backend
python app.py
# Service runs on http://localhost:8000
```

3. **Start Streamlit UI** (Terminal 3)
```bash
streamlit run ui/app.py
# UI opens at http://localhost:8501
```

## Usage Examples

### Text Queries

**Information Query:**
- User: "What's my account balance?"
- Bot: "Your available credit is ₹35,000.00 out of ₹50,000.00 credit limit."

**Action Query:**
- User: "I want to make a payment"
- Bot: "I can help you make a payment of ₹2,700.00. Do you want to proceed?"
- User: [Clicks Approve]
- Bot: "Payment processed successfully"

### Voice Queries

1. Click the microphone icon in the UI
2. Speak your query
3. The system will:
   - Convert speech to text (GCP)
   - Classify the query
   - Process with appropriate agent
   - Return response

## API Reference

### Python Backend API

#### POST /chat
Process a chat message.

**Request:**
```json
{
  "message": "What's my balance?",
  "user_id": "USER001"
}
```

**Response:**
```json
{
  "success": true,
  "response": {
    "answer": "Your available credit is ₹35,000.00...",
    "data": {...},
    "requires_consent": false
  },
  "classification": {
    "category": "account",
    "task_type": "information"
  }
}
```

#### POST /voice
Process voice input.

**Request:**
```json
{
  "audio_data": "base64_encoded_audio",
  "user_id": "USER001"
}
```

**Response:**
```json
{
  "success": true,
  "transcript": "What's my balance?",
  "response": {...},
  "classification": {...}
}
```

#### POST /consent
Handle user consent for actions.

**Request:**
```json
{
  "query_id": "Q123456",
  "user_id": "USER001",
  "consent": true,
  "action": "make_payment",
  "action_params": {
    "amount": 2700.0
  }
}
```

### Node.js API

#### POST /api/transactions
Mock transaction API.

**Request:**
```json
{
  "user_id": "USER001",
  "action": "make_payment",
  "amount": 2700.0
}
```

#### POST /api/update-user
Mock user update API.

**Request:**
```json
{
  "user_id": "USER001",
  "action": "update_email",
  "email": "newemail@example.com"
}
```

## Database Schema

### Users Table
- `id`: Primary key
- `user_id`: Unique user identifier
- `name`: User name
- `email`: Email address
- `phone`: Phone number
- `card_number`: Credit card number
- `card_status`: Card status (active/blocked/expired)
- `credit_limit`: Credit limit
- `available_credit`: Available credit

### Transactions Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `transaction_id`: Unique transaction ID
- `amount`: Transaction amount
- `merchant`: Merchant name
- `category`: Transaction category
- `date`: Transaction date
- `status`: Transaction status
- `is_emi`: Whether transaction is EMI
- `emi_tenure`: EMI tenure in months
- `emi_amount`: Monthly EMI amount

### Bills Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `bill_id`: Unique bill ID
- `bill_date`: Bill generation date
- `due_date`: Payment due date
- `total_amount`: Total bill amount
- `minimum_due`: Minimum due amount
- `paid_amount`: Amount paid
- `status`: Bill status

## Troubleshooting

### Common Issues

1. **Database not found**
   - Run `python database/init_db.py` to initialize

2. **GCP credentials error**
   - Ensure GCP_CREDENTIALS_PATH points to valid credentials file
   - Check that Speech-to-Text API is enabled

3. **OpenAI API error**
   - Verify OPENAI_API_KEY is set correctly
   - Check API quota and billing

4. **Port already in use**
   - Change ports in .env or stop conflicting services

5. **Node.js service not responding**
   - Check if Node.js service is running
   - Verify NODE_API_URL in .env

## Development

### Adding New Agents

1. Create new agent class in `python_backend/agents/`
2. Inherit from `BaseAgent`
3. Implement `handle_information_query` and `handle_action_request`
4. Add to `AGENT_MAP` in `app.py`

### Adding New Categories

1. Update `CATEGORIES` in `classifier.py`
2. Create corresponding agent
3. Update classification prompt

### Testing

```bash
# Test Python API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my balance?", "user_id": "USER001"}'

# Test Node.js API
curl -X GET http://localhost:3000/api/health
```

## License

This project is for demonstration purposes.

