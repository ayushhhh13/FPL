# Pre-Run Checklist

Use this checklist before running the application to ensure everything is set up correctly.

## Prerequisites
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 14+ installed (`node --version`)
- [ ] pip installed and working
- [ ] npm installed and working

## Environment Setup
- [ ] `.env` file created from `.env.example`
- [ ] `OPENAI_API_KEY` set in `.env`
- [ ] `GCP_CREDENTIALS_PATH` set (optional, for voice)
- [ ] `GCP_PROJECT_ID` set (optional, for voice)
- [ ] `NODE_API_URL` set to `http://localhost:3000`
- [ ] `DATABASE_PATH` set (default: `./database/credit_card.db`)

## Dependencies
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Node.js dependencies installed (`cd nodejs_backend && npm install`)

## Database
- [ ] Database initialized (`python database/init_db.py`)
- [ ] Sample data created successfully
- [ ] Database file exists at specified path

## GCP Setup (for voice features)
- [ ] GCP account created
- [ ] Speech-to-Text API enabled
- [ ] Service account credentials downloaded
- [ ] Credentials file path correct in `.env`

## Testing
- [ ] Run test script: `python test_setup.py`
- [ ] All tests pass

## Services
- [ ] Node.js service starts without errors
- [ ] Python backend starts without errors
- [ ] Streamlit UI starts without errors
- [ ] All services accessible on expected ports

## Quick Test
- [ ] Can send text message in UI
- [ ] Can receive response
- [ ] Classification works
- [ ] Action consent flow works (if testing actions)

## Troubleshooting

If something doesn't work:

1. **Import errors**: Make sure you're in the project root directory
2. **Database errors**: Run `python database/init_db.py` again
3. **Port conflicts**: Check if ports 3000, 8000, 8501 are available
4. **API errors**: Verify API keys in `.env` file
5. **GCP errors**: Check credentials file path and API enablement

## Ready to Run!

Once all items are checked, you're ready to start the application:

```bash
# Option 1: Use start script
./start.sh  # Linux/Mac
start.bat   # Windows

# Option 2: Manual start (3 terminals)
# Terminal 1:
cd nodejs_backend && node server.js

# Terminal 2:
cd python_backend && python app.py

# Terminal 3:
streamlit run ui/app.py
```

