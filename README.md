# GenAI Credit Card Assistant

A microservices-based AI assistant for handling credit card customer queries and actions.

## Architecture

The application follows a microservices architecture with:
- **Python Backend**: Main logic, classification, and agent orchestration
- **Node.js API Service**: External API integrations and mock services
- **SQLite Database**: Local data storage
- **Streamlit UI**: Web interface for chat and voice interactions
<img width="853" height="621" alt="Screenshot 2025-12-07 at 11 49 28 PM" src="https://github.com/user-attachments/assets/36d6ca0b-3362-4477-b269-87a4c17f3082" />

## Project Structure

```
ayush/
├── python_backend/
│   ├── app.py                 # Main FastAPI application
│   ├── classifier.py          # LLM-based query classifier
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py      # Base agent class
│   │   ├── account_agent.py   # Account & Onboarding
│   │   ├── delivery_agent.py  # Card Delivery
│   │   ├── transaction_agent.py # Transaction & EMI
│   │   ├── bill_agent.py      # Bill & Statement
│   │   ├── repayment_agent.py # Repayments
│   │   └── collections_agent.py # Collections
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py          # Database models
│   │   └── db.py              # Database connection
│   └── utils/
│       ├── __init__.py
│       └── speech_to_text.py  # GCP Speech-to-Text integration
├── nodejs_backend/
│   ├── server.js              # Express server
│   ├── routes/
│   │   └── api.js             # API routes
│   └── package.json
├── ui/
│   └── app.py                 # Streamlit UI
├── database/
│   └── init_db.py             # Database initialization script
├── requirements.txt
├── .env.example
└── README.md
```
## Testing and Screenshots

### Login Page
<img width="1425" height="563" alt="Screenshot 2025-12-07 at 11 54 08 PM" src="https://github.com/user-attachments/assets/8403daa8-81d9-4ea5-a043-d72178cb0d40" />

### Home Page
<img width="1457" height="793" alt="Screenshot 2025-12-07 at 11 54 25 PM" src="https://github.com/user-attachments/assets/1ba5f5cf-d73e-40ff-9218-b29e0e33e084" />

### Sample Inputs
<img width="1434" height="791" alt="Screenshot 2025-12-07 at 11 55 25 PM" src="https://github.com/user-attachments/assets/43bf9978-0a01-419d-83ca-abab651221be" />

### Voice Input
<img width="1109" height="356" alt="Screenshot 2025-12-07 at 11 56 17 PM" src="https://github.com/user-attachments/assets/bd918d91-e8df-4161-9822-a85e8c9f9451" />

<img width="1092" height="488" alt="Screenshot 2025-12-07 at 11 56 48 PM" src="https://github.com/user-attachments/assets/21cfc980-b934-43af-8ac6-01e6c9fc12fc" />

<img width="1057" height="303" alt="Screenshot 2025-12-07 at 11 57 05 PM" src="https://github.com/user-attachments/assets/cd538699-f04e-4bf0-a981-965de5149663" />

### Notification Broadcast to Whatsapp
<img width="966" height="737" alt="Screenshot 2025-12-07 at 11 57 31 PM" src="https://github.com/user-attachments/assets/342c318a-ede1-4661-a8e1-1a91b1170b5f" />


## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- GCP account with Speech-to-Text API enabled
- OpenAI API key (or compatible LLM service)

### Installation

1. **Clone the repository**
```bash
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
# Edit .env with your API keys
```

5. **Initialize database**
```bash
python database/init_db.py
```

### Running the Application

1. **Start Node.js API service** (Terminal 1)
```bash
cd nodejs_backend
node server.js
```

2. **Start Python backend** (Terminal 2)
```bash
cd python_backend
python app.py
```

3. **Start Streamlit UI** (Terminal 3)
```bash
streamlit run ui/app.py
```

The UI will be available at `http://localhost:8501`

## Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_key
GCP_PROJECT_ID=your_gcp_project_id
GCP_CREDENTIALS_PATH=path/to/credentials.json
NODE_API_URL=http://localhost:3000
```

## Features

### Query Categories
- 💳 Account & Onboarding
- 🚚 Card Delivery
- 💰 Transaction & EMI
- 📄 Bill & Statement
- 💸 Repayments
- 🚨 Collections

### Task Types
1. **Information Retrieval**: Read-only queries that fetch data
2. **Action Execution**: Tasks requiring user consent (e.g., transactions, updates)

## API Endpoints

### Python Backend (Port 8000)
- `POST /classify` - Classify user query
- `POST /chat` - Process chat message
- `POST /voice` - Process voice input

### Node.js Backend (Port 3000)
- `POST /api/transactions` - Mock transaction API
- `POST /api/update-user` - Mock user update API
- `GET /api/health` - Health check

## Development Notes

- Follows Single Responsibility Principle
- Each agent handles one category
- Classification uses low-token LLM calls
- Action execution requires explicit user consent
- Database uses SQLite for simplicity

## Documentation

- **README.md** - This file, project overview
- **ARCHITECTURE.md** - Detailed system architecture
- **DOCUMENTATION.md** - Complete API and usage documentation
- **SETUP.md** - Quick setup guide
- **AI_COPILOT_REPORT.md** - AI tools usage report

## Quick Start

See [SETUP.md](SETUP.md) for quick start instructions.

For detailed documentation, see [DOCUMENTATION.md](DOCUMENTATION.md).

For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md).

