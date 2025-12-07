"""WhatsApp message service using Meta WhatsApp Business Platform API."""
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class WhatsAppService:
    """Service for sending WhatsApp messages via Meta WhatsApp Business Platform API."""
    
    def __init__(self):
        # Create whatsapp directory for storing messages
        self.whatsapp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "whatsapp_messages")
        os.makedirs(self.whatsapp_dir, exist_ok=True)
        
        # Meta WhatsApp Business Platform API credentials
        # Support both naming conventions for backward compatibility
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("PHONE_NUMBER_ID")
        self.app_id = os.getenv("WHATSAPP_APP_ID") or os.getenv("APP_ID")
        self.app_secret = os.getenv("WHATSAPP_APP_SECRET") or os.getenv("APP_SECRET")
        self.version = os.getenv("WHATSAPP_API_VERSION") or os.getenv("VERSION", "v21.0")
        
        # Graph API base URL
        self.graph_api_url = "https://graph.facebook.com"
        
        # Check if API is configured
        self.use_api = bool(self.access_token and self.phone_number_id)
    
    async def send_message(self, phone_number: str, message: str, preview_url: bool = False) -> dict:
        """
        Send a WhatsApp text message using Meta WhatsApp Business Platform API.
        
        Args:
            phone_number: Recipient phone number (with country code, e.g., +919876543210)
            message: Message content
            preview_url: Whether to enable URL preview (default: False)
            
        Returns:
            dict with success status and message
        """
        # Always save message to file
        self._save_message_to_file(phone_number, message)
        
        if not self.use_api:
            print(f"📱 [FILE] WhatsApp message saved to file")
            print(f"   To: {phone_number}")
            print(f"   Message: {message[:100]}...")
            return {
                "success": True,
                "message": f"WhatsApp message saved to file (check whatsapp_messages/ directory). To send via API, configure WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID in .env",
                "to": phone_number,
                "saved_to_file": True
            }
        
        # Format phone number (ensure it starts with +)
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number.lstrip('0')
        
        # Prepare message data
        message_data = self._get_text_message_input(phone_number, message, preview_url)
        
        # Send via API
        try:
            result = await self._send_message_async(message_data)
            print(f"📱 [API] WhatsApp message sent successfully to {phone_number}")
            return result
        except Exception as e:
            print(f"⚠️ WhatsApp API error (message saved to file): {str(e)}")
            return {
                "success": True,  # Still success because saved to file
                "message": f"WhatsApp message saved to file. API error: {str(e)}",
                "to": phone_number,
                "saved_to_file": True,
                "api_error": str(e)
            }
    
    def _get_text_message_input(self, recipient: str, text: str, preview_url: bool = False) -> str:
        """
        Get text message input in the format required by WhatsApp Business Platform API.
        
        Args:
            recipient: Recipient phone number
            text: Message text
            preview_url: Whether to enable URL preview
            
        Returns:
            JSON string with message data
        """
        return json.dumps({
            "messaging_product": "whatsapp",
            "preview_url": preview_url,
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "body": text
            }
        })
    
    async def _send_message_async(self, data: str) -> dict:
        """
        Send message to WhatsApp Business Platform API asynchronously.
        
        Args:
            data: JSON string with message data
            
        Returns:
            dict with response data
        """
        try:
            import aiohttp
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }
            
            url = f"{self.graph_api_url}/{self.version}/{self.phone_number_id}/messages"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "message": "WhatsApp message sent successfully via API",
                            "to": json.loads(data).get("to"),
                            "message_id": result.get("messages", [{}])[0].get("id"),
                            "sent_via_api": True
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"API returned status {response.status}: {error_text}")
        except ImportError:
            # Fallback to requests if aiohttp is not available
            import requests
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }
            url = f"{self.graph_api_url}/{self.version}/{self.phone_number_id}/messages"
            response = requests.post(url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "message": "WhatsApp message sent successfully via API",
                "to": json.loads(data).get("to"),
                "message_id": result.get("messages", [{}])[0].get("id"),
                "sent_via_api": True
            }
    
    def _save_message_to_file(self, phone_number: str, message: str):
        """Save WhatsApp message to a file for record keeping."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")
            filename = f"{timestamp}_{safe_phone}.txt"
            filepath = os.path.join(self.whatsapp_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"To: {phone_number}\n")
                f.write(f"Date: {datetime.now().isoformat()}\n")
                f.write(f"{'='*50}\n\n")
                f.write(message)
            
            print(f"💾 WhatsApp message saved to: {filepath}")
        except Exception as e:
            print(f"⚠️ Failed to save WhatsApp message to file: {str(e)}")
    
    async def send_action_notification(self, phone_number: str, action: str, action_details: dict) -> dict:
        """
        Send an action execution notification via WhatsApp.
        
        Args:
            phone_number: User's phone number
            action: Action that was executed (e.g., 'block_card', 'make_transaction')
            action_details: Details about the action
            
        Returns:
            dict with success status
        """
        # Format notification message
        action_names = {
            "block_card": "Card Blocked",
            "unblock_card": "Card Unblocked",
            "make_transaction": "Transaction Completed",
            "make_payment": "Payment Processed",
            "activate_card": "Card Activated",
            "update_email": "Email Updated",
            "update_phone": "Phone Updated"
        }
        
        action_name = action_names.get(action, action.replace("_", " ").title())
        
        message = f"🔔 *Credit Card Assistant Notification*\n\n"
        message += f"Action: *{action_name}*\n"
        
        if action == "make_transaction":
            amount = action_details.get("amount", 0)
            merchant = action_details.get("merchant", "Unknown")
            transaction_id = action_details.get("transaction_id", "N/A")
            message += f"Amount: ₹{amount:,.2f}\n"
            message += f"Merchant: {merchant}\n"
            message += f"Transaction ID: {transaction_id}\n"
        elif action in ["block_card", "unblock_card", "activate_card"]:
            card_status = action_details.get("card_status", "N/A")
            message += f"Card Status: {card_status}\n"
        elif action == "make_payment":
            amount = action_details.get("amount", 0)
            message += f"Payment Amount: ₹{amount:,.2f}\n"
        
        message += f"\nStatus: ✅ Success\n"
        message += f"Time: {action_details.get('timestamp', 'N/A')}\n"
        message += f"\nThank you for using our service!"
        
        return await self.send_message(phone_number, message)
    
    def get_templated_message_input(
        self, 
        recipient: str, 
        template_name: str, 
        language_code: str = "en_US",
        header_params: Optional[list] = None,
        body_params: Optional[list] = None,
        button_params: Optional[list] = None
    ) -> str:
        """
        Get templated message input in the format required by WhatsApp Business Platform API.
        
        Args:
            recipient: Recipient phone number
            template_name: Name of the approved message template
            language_code: Language code (default: en_US)
            header_params: Optional list of header parameters
            body_params: Optional list of body parameters
            button_params: Optional list of button parameters
            
        Returns:
            JSON string with template message data
        """
        components = []
        
        # Add header component if parameters provided
        if header_params:
            components.append({
                "type": "header",
                "parameters": header_params
            })
        
        # Add body component if parameters provided
        if body_params:
            components.append({
                "type": "body",
                "parameters": body_params
            })
        
        # Add button component if parameters provided
        if button_params:
            components.append({
                "type": "button",
                "sub_type": "url",  # or "quick_reply"
                "index": "0",
                "parameters": button_params
            })
        
        template_data = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            template_data["template"]["components"] = components
        
        return json.dumps(template_data)
    
    async def send_template_message(
        self,
        phone_number: str,
        template_name: str,
        language_code: str = "en_US",
        header_params: Optional[list] = None,
        body_params: Optional[list] = None,
        button_params: Optional[list] = None
    ) -> dict:
        """
        Send a templated WhatsApp message using Meta WhatsApp Business Platform API.
        
        Args:
            phone_number: Recipient phone number
            template_name: Name of the approved message template
            language_code: Language code (default: en_US)
            header_params: Optional list of header parameters
            body_params: Optional list of body parameters
            button_params: Optional list of button parameters
            
        Returns:
            dict with success status
        """
        # Format phone number
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number.lstrip('0')
        
        # Get template message data
        message_data = self.get_templated_message_input(
            phone_number,
            template_name,
            language_code,
            header_params,
            body_params,
            button_params
        )
        
        # Save template info to file
        self._save_message_to_file(
            phone_number, 
            f"Template: {template_name}\n{json.dumps(json.loads(message_data), indent=2)}"
        )
        
        if not self.use_api:
            print(f"📱 [FILE] WhatsApp template message saved to file")
            print(f"   To: {phone_number}")
            print(f"   Template: {template_name}")
            return {
                "success": True,
                "message": f"WhatsApp template message saved to file. To send via API, configure WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID in .env",
                "to": phone_number,
                "template_name": template_name,
                "saved_to_file": True
            }
        
        # Send via API
        try:
            result = await self._send_message_async(message_data)
            print(f"📱 [API] WhatsApp template message sent successfully to {phone_number}")
            result["template_name"] = template_name
            return result
        except Exception as e:
            print(f"⚠️ WhatsApp API error (template message saved to file): {str(e)}")
            return {
                "success": True,
                "message": f"WhatsApp template message saved to file. API error: {str(e)}",
                "to": phone_number,
                "template_name": template_name,
                "saved_to_file": True,
                "api_error": str(e)
            }

