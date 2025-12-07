/**
 * Node.js API Service for Credit Card Assistant
 * Handles mock API calls for action execution
 */

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'Credit Card API Service',
    timestamp: new Date().toISOString()
  });
});

// Mock transaction API
app.post('/api/transactions', (req, res) => {
  const { user_id, action, transaction_id, amount, emi_tenure } = req.body;
  
  console.log('Transaction API called:', { user_id, action, transaction_id, amount });
  
  // Simulate API processing delay
  setTimeout(() => {
    if (action === 'make_payment') {
      res.json({
        success: true,
        message: 'Payment processed successfully',
        transaction_id: `TXN${Date.now()}`,
        amount: amount,
        status: 'completed',
        timestamp: new Date().toISOString()
      });
    } else if (action === 'dispute_transaction') {
      res.json({
        success: true,
        message: 'Dispute filed successfully',
        dispute_id: `DSP${Date.now()}`,
        transaction_id: transaction_id,
        status: 'under_review',
        timestamp: new Date().toISOString()
      });
    } else if (action === 'convert_to_emi') {
      res.json({
        success: true,
        message: 'Transaction converted to EMI',
        emi_id: `EMI${Date.now()}`,
        transaction_id: transaction_id,
        emi_tenure: emi_tenure || 6,
        status: 'active',
        timestamp: new Date().toISOString()
      });
    } else {
      res.json({
        success: true,
        message: 'Transaction processed',
        data: req.body,
        timestamp: new Date().toISOString()
      });
    }
  }, 500); // 500ms delay to simulate real API
});

// Mock user update API
app.post('/api/update-user', (req, res) => {
  const { user_id, action, email, phone, name } = req.body;
  
  console.log('User Update API called:', { user_id, action, email, phone });
  
  // Simulate API processing delay
  setTimeout(() => {
    if (action === 'update_email' || email) {
      res.json({
        success: true,
        message: 'Email updated successfully',
        user_id: user_id,
        email: email,
        status: 'updated',
        timestamp: new Date().toISOString()
      });
    } else if (action === 'update_phone' || phone) {
      res.json({
        success: true,
        message: 'Phone number updated successfully',
        user_id: user_id,
        phone: phone,
        status: 'updated',
        timestamp: new Date().toISOString()
      });
    } else if (action === 'activate_card') {
      res.json({
        success: true,
        message: 'Card activated successfully',
        user_id: user_id,
        card_status: 'active',
        timestamp: new Date().toISOString()
      });
    } else if (action === 'block_card') {
      res.json({
        success: true,
        message: 'Card blocked successfully. All transactions are now prevented.',
        user_id: user_id,
        card_status: 'blocked',
        timestamp: new Date().toISOString()
      });
    } else if (action === 'unblock_card') {
      res.json({
        success: true,
        message: 'Card unblocked successfully. Normal card functionality has been restored.',
        user_id: user_id,
        card_status: 'active',
        timestamp: new Date().toISOString()
      });
    } else {
      res.json({
        success: true,
        message: 'User profile updated successfully',
        user_id: user_id,
        data: req.body,
        timestamp: new Date().toISOString()
      });
    }
  }, 500);
});

// Mock delivery update API
app.post('/api/delivery', (req, res) => {
  const { user_id, action, address } = req.body;
  
  console.log('Delivery API called:', { user_id, action, address });
  
  setTimeout(() => {
    res.json({
      success: true,
      message: 'Delivery information updated',
      user_id: user_id,
      tracking_number: `TRACK${Date.now()}`,
      status: 'updated',
      timestamp: new Date().toISOString()
    });
  }, 500);
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    message: err.message
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Not found',
    message: `Route ${req.method} ${req.path} not found`
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Node.js API Service running on http://localhost:${PORT}`);
  console.log(`📡 Health check: http://localhost:${PORT}/api/health`);
});

