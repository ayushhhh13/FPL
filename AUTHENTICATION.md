# Authentication & Authorization Guide

## Overview

The Credit Card Assistant now includes:
- **User Authentication**: Signup and login with JWT tokens
- **Gmail Integration**: Chat conversations are automatically sent to user's email
- **WhatsApp Integration**: Action execution notifications are sent to user's WhatsApp

## Features

### 1. Authentication
- **Signup**: Users can create accounts with name, email, phone, and password
- **Login**: Secure login with JWT token-based authentication
- **Password Security**: Passwords are hashed using bcrypt
- **Session Management**: JWT tokens expire after 7 days

### 2. Gmail Integration
- **Chat Summaries**: Every chat conversation is automatically sent to the user's registered email
- **HTML Format**: Emails are sent in HTML format with formatted chat history
- **Automatic**: No user action required - emails are sent in the background

### 3. WhatsApp Integration
- **Action Notifications**: When users execute actions (block card, make transaction, etc.), notifications are sent to WhatsApp
- **Detailed Information**: Notifications include action details, amounts, transaction IDs, etc.
- **Real-time**: Notifications are sent immediately after action execution

## API Endpoints

### Authentication Endpoints

#### POST `/auth/signup`
Create a new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+919876543210",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "user_id": "USER12345678",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+919876543210"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST `/auth/login`
Login with email and password.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "user_id": "USER12345678",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+919876543210"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Protected Endpoints

All chat, voice, and consent endpoints now require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

#### POST `/chat`
Send a chat message (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```
GET /chat?message=What is my account balance?
```

**Response:**
```json
{
  "success": true,
  "response": {
    "answer": "Your available credit is ₹95,000.00...",
    "data": {...}
  },
  "classification": {...}
}
```

**Note:** Chat messages are automatically sent to the user's email.

#### POST `/voice`
Send voice input (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "audio_data": "base64_encoded_audio_data"
}
```

**Note:** Voice transcripts are automatically sent to the user's email.

#### POST `/consent`
Execute an action with user consent (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "query_id": "Q1234567890",
  "user_id": "USER12345678",
  "consent": true,
  "action": "make_transaction",
  "action_params": {
    "amount": 1000,
    "merchant": "Amazon"
  }
}
```

**Note:** Action execution notifications are automatically sent to the user's WhatsApp.

## Environment Variables

Add these to your `.env` file:

```bash
# JWT Secret Key (change in production)
JWT_SECRET_KEY=your-secret-key-change-in-production

# Gmail API Configuration
GMAIL_API_KEY=your-gmail-api-key
GMAIL_OAUTH_TOKEN=your-gmail-oauth-token
GMAIL_SENDER_EMAIL=noreply@creditcardassistant.com

# WhatsApp API Configuration
WHATSAPP_API_KEY=your-whatsapp-api-key
WHATSAPP_API_URL=https://api.whatsapp.com/v1/messages
WHATSAPP_PHONE_ID=your-whatsapp-phone-id
```

## Setup Instructions

### 1. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Get access token and add to `.env`:
   - `GMAIL_API_KEY`: Your API key
   - `GMAIL_OAUTH_TOKEN`: OAuth access token
   - `GMAIL_SENDER_EMAIL`: Email address to send from

### 2. WhatsApp API Setup

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a WhatsApp Business Account
3. Get API credentials:
   - `WHATSAPP_API_KEY`: Your API access token
   - `WHATSAPP_PHONE_ID`: Your WhatsApp Business Phone Number ID
   - `WHATSAPP_API_URL`: API endpoint (default: `https://api.whatsapp.com/v1/messages`)

### 3. JWT Secret Key

Generate a secure random key for JWT signing:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add the output to `.env` as `JWT_SECRET_KEY`.

## Usage

### UI Flow

1. **Signup/Login**: Users must sign up or login before accessing the chat
2. **Chat**: All chat messages are automatically sent to email
3. **Actions**: When users approve actions, notifications are sent to WhatsApp

### Mock Mode

If Gmail or WhatsApp APIs are not configured, the system runs in "mock mode":
- Email sending is logged to console
- WhatsApp messages are logged to console
- No actual emails/messages are sent

This allows development and testing without API credentials.

## Security Notes

1. **Password Hashing**: All passwords are hashed using bcrypt
2. **JWT Tokens**: Tokens expire after 7 days
3. **HTTPS**: Use HTTPS in production
4. **Secret Key**: Change `JWT_SECRET_KEY` in production
5. **API Keys**: Never commit API keys to version control

## Database Changes

The `User` model has been updated with:
- `password_hash`: Hashed password
- `is_active`: Account status
- `last_login`: Last login timestamp

Existing users will need to sign up again or update their accounts.

