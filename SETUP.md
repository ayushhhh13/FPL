# Quick Setup Guide

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.8+ installed
- ✅ Node.js 14+ installed
- ✅ GCP account with Speech-to-Text API enabled
- ✅ OpenAI API key

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
cd nodejs_backend
npm install
cd ..
```

### 2. Configure Environment

Create `.env` file:
```bash
OPENAI_API_KEY=your_key_here
GCP_PROJECT_ID=your_project_id
GCP_CREDENTIALS_PATH=./credentials/gcp-credentials.json
NODE_API_URL=http://localhost:3000
DATABASE_PATH=./database/credit_card.db
```

### 3. Initialize Database

```bash
python database/init_db.py
```

### 4. Start Services

**Terminal 1 - Node.js API:**
```bash
cd nodejs_backend
node server.js
```

**Terminal 2 - Python Backend:**
```bash
cd python_backend
python app.py
```

**Terminal 3 - Streamlit UI:**
```bash
streamlit run ui/app.py
```

### 5. Access Application

Open browser: http://localhost:8501

## Testing

### Test Chat
Type: "What's my account balance?"

### Test Voice
Click microphone icon and say: "Show my recent transactions"

### Test Action
Type: "I want to make a payment"
Then click "Approve" when prompted

## Troubleshooting

**Issue: Module not found**
- Ensure you're in the project root directory
- Check Python path includes python_backend

**Issue: Database error**
- Run `python database/init_db.py` again
- Check DATABASE_PATH in .env

**Issue: GCP error**
- Verify credentials file exists
- Check GCP_CREDENTIALS_PATH in .env
- Ensure Speech-to-Text API is enabled

**Issue: OpenAI error**
- Verify OPENAI_API_KEY is correct
- Check API quota

## Next Steps

- Read ARCHITECTURE.md for system design
- Read DOCUMENTATION.md for detailed docs
- Customize agents for your use case

