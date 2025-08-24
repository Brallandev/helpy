"""Message parsing utilities."""

from typing import Any, Dict, Optional


class MessageParser:
    """Utility class for parsing WhatsApp webhook messages."""
    
    @staticmethod
    def extract_text_from_message(msg: Dict[str, Any]) -> Optional[str]:
        """Extract text content from a WhatsApp message.
        
        Args:
            msg: The message object from WhatsApp webhook
            
        Returns:
            The text content if found, None otherwise
        """
        message_type = msg.get("type")
        
        if message_type == "text":
            return msg.get("text", {}).get("body")
        elif message_type == "button":
            return msg.get("button", {}).get("text")
        elif message_type == "interactive":
            interactive = msg.get("interactive", {})
            interactive_type = interactive.get("type")
            
            if interactive_type == "button_reply":
                return interactive.get("button_reply", {}).get("title")
            elif interactive_type == "list_reply":
                return interactive.get("list_reply", {}).get("title")
        
        return None
