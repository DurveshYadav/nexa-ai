# API Reference
Base URL:
/api//helth
# Response
{
  "status": "healthy"
}

# Authentication
POST /auth/register

# Creates a user.
POST /auth/login

# Returns a JWT access token.
# Conversations
POST /conversations

# Create a conversation.
GET /conversations

# List current user's conversations.
GET /conversations/{conversation_id}

# Get one conversation.
PATCH /conversations/{conversation_id}

# Update conversation title.
DELETE /conversations/{conversation_id}

# Delete conversation.
# Chat
POST /conversations/{conversation_id}/messages

