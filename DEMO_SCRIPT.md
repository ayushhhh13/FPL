# Demo Presentation Script - GenAI Credit Card Assistant
**Duration: 5-6 minutes**

---

## [0:00 - 0:30] Introduction & Overview

**[Slide/Scene: Application Homepage]**

"Good [morning/afternoon]! Today I'm excited to present the **GenAI Credit Card Assistant** - an intelligent, AI-powered chatbot that revolutionizes how customers interact with their credit card services.

This application leverages **Generative AI** to understand natural language queries, supports both **text and voice inputs**, and can handle everything from simple balance inquiries to complex transactions - all through a conversational interface.

The system is built on a **microservices architecture** with three main components:
- A **Streamlit web interface** for user interaction
- A **Python FastAPI backend** with specialized AI agents
- A **Node.js service** for external API integrations

Let me show you how it works!"

**[Action: Navigate to http://localhost:8501]**

---

## [0:30 - 1:00] Architecture Overview

**[Slide/Scene: Architecture Diagram or Code Structure]**

"Before we dive into the demo, let me quickly explain the architecture. The system uses **6 specialized AI agents**, each handling a specific category:

- **Account & Onboarding** - Account management and card activation
- **Card Delivery** - Tracking and delivery management  
- **Transactions & EMI** - Transaction history and EMI conversion
- **Bills & Statements** - Bill inquiries and statement downloads
- **Repayments** - Payment processing and scheduling
- **Collections** - Overdue management and payment plans

Each query is intelligently classified using **OpenAI GPT**, routed to the appropriate agent, and processed based on whether it's an information request or an action that requires user consent."

**[Action: Show architecture diagram or code structure briefly]**

---

## [1:00 - 2:00] Authentication & Setup

**[Scene: Login Page]**

"Let's start by logging in. The system includes secure **JWT-based authentication**."

**[Action: Click "Sign Up" or use existing credentials]**

"For new users, we can sign up with name, email, phone, and password. The system automatically creates a user account and generates a credit card profile."

**[Action: Complete signup/login]**

"Once authenticated, we're taken to the main chat interface. Notice the clean, modern UI with a sidebar showing account information and query categories."

**[Action: Show the main interface]**

---

## [2:00 - 3:30] Text Query Demo - Information Retrieval

**[Scene: Chat Interface]**

"Now let's see the AI in action. I'll start with a simple information query."

**[Action: Type "What's my account balance?"]**

**[Wait for response]**

"Perfect! The system:
1. **Classified** the query as an Account information request
2. **Routed** it to the AccountAgent
3. **Retrieved** the data from the database
4. **Formatted** a natural language response

Notice how the response includes your current balance, available credit, and credit limit - all presented in a conversational manner."

**[Action: Show classification details in expander]**

"Let's try another query from a different category."

**[Action: Type "Show my recent transactions"]**

**[Wait for response]**

"Excellent! This query was classified as a Transaction information request. The TransactionAgent retrieved your transaction history and displayed it in a structured format. You can see transaction dates, amounts, merchants, and statuses."

---

## [3:30 - 4:30] Voice Input Demo

**[Scene: Voice Input Section]**

"One of the standout features is **voice input support**. Let me demonstrate this."

**[Action: Click microphone button and record]**

**[Say: "What's my bill amount and due date?"]**

**[Wait for transcription and response]**

"Amazing! The system:
1. **Recorded** the audio input
2. **Converted** speech to text using AssemblyAI
3. **Processed** it just like a text query
4. **Classified** it as a Bill information request
5. **Retrieved** and displayed the bill details

The transcript is shown, and you can see the system understood the query perfectly. This makes the assistant accessible for users who prefer voice interaction or are on mobile devices."

---

## [4:30 - 5:30] Action with Consent Demo

**[Scene: Action Request]**

"Now let's see how the system handles actions that require user consent - a critical security feature."

**[Action: Type "I want to make a payment of 5000 rupees"]**

**[Wait for response]**

"Notice how the system:
1. **Identified** this as an action request
2. **Extracted** the payment amount
3. **Requested explicit consent** before proceeding

This is the consent management system in action - no financial transaction happens without user approval."

**[Action: Click "Approve" button]**

**[Wait for confirmation]**

"Perfect! The payment was processed successfully. The system:
1. **Validated** the user's consent
2. **Called** the Node.js API service
3. **Updated** the database
4. **Sent** a WhatsApp notification (saved to file)
5. **Confirmed** the transaction

You can see the transaction ID and confirmation message. This demonstrates the complete action execution flow with proper security measures."

---

## [5:30 - 6:00] Additional Features & Conclusion

**[Scene: Show different query examples]**

"Let me quickly show a few more capabilities:

- **Card Management**: 'Block my card' or 'Activate my card'
- **Delivery Tracking**: 'What's my card delivery status?'
- **EMI Conversion**: 'Convert this transaction to EMI'
- **Statement Requests**: 'Email me my statement'

Each query is intelligently routed to the right agent, and actions always require consent."

**[Action: Show one more quick example if time permits]**

---

## [6:00] Closing

**[Scene: Summary Slide or Application]**

"In conclusion, the GenAI Credit Card Assistant demonstrates:

✅ **Intelligent Query Understanding** - Natural language processing with GPT
✅ **Multi-modal Input** - Both text and voice support
✅ **Specialized Agent Architecture** - 6 category-specific agents
✅ **Secure Action Execution** - Consent-based transaction processing
✅ **Scalable Microservices Design** - Ready for production deployment
✅ **Modern Tech Stack** - FastAPI, Streamlit, Node.js, SQLite/PostgreSQL

The system is production-ready and can be extended with real payment gateways, multi-language support, and advanced analytics.

Thank you for watching! I'm happy to answer any questions."

---

## Quick Reference - Demo Flow Checklist

### Pre-Demo Setup
- [ ] All services running (Node.js, Python, Streamlit)
- [ ] Database initialized with sample data
- [ ] User account created (or signup ready)
- [ ] Browser open to http://localhost:8501
- [ ] Microphone permissions granted (for voice demo)

### Demo Sequence
1. [ ] Show login/signup (30 seconds)
2. [ ] Text query: "What's my account balance?" (30 seconds)
3. [ ] Text query: "Show my recent transactions" (30 seconds)
4. [ ] Voice query: "What's my bill amount and due date?" (60 seconds)
5. [ ] Action query: "Make a payment of 5000 rupees" + Consent (60 seconds)
6. [ ] Quick additional examples (30 seconds)
7. [ ] Closing remarks (30 seconds)

### Key Points to Emphasize
- ✅ AI-powered natural language understanding
- ✅ Voice input capability
- ✅ Consent-based security for actions
- ✅ Microservices architecture
- ✅ Specialized agent system
- ✅ Production-ready design

### Troubleshooting Tips
- If voice doesn't work: Fall back to text examples
- If API is slow: Have backup queries ready
- If error occurs: Explain it's a demo environment and show the error handling
- Keep backup screenshots ready for any technical issues

---

## Alternative Shorter Script (4-5 minutes)

If you need a shorter version:

1. **Introduction** (30s) - Overview and architecture
2. **Login** (30s) - Show authentication
3. **Text Query** (60s) - "What's my balance?" + "Show transactions"
4. **Voice Query** (60s) - Voice input demonstration
5. **Action with Consent** (90s) - Payment with consent flow
6. **Conclusion** (30s) - Key features and closing

---

**Total Time: ~5 minutes**

