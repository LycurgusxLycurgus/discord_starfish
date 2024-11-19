import json
import openai
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('memory_decision')

# Initialize OpenAI
openai.api_key = Config.OPENAI_API_KEY
openai.api_base = "https://glhf.chat/api/openai/v1"

MEMORY_SELECTION_PROMPT = """Given the user's message and identity, select the most relevant memories that would help craft a meaningful response aligned with the character's personality (a whimsical, innocent frog-like being).

User: {user_identifier}
Message: {user_message}

Available memories:
{all_memories}

Provide analysis in the following JSON format only:
{{
    "selected_memories": [
        "memory_string_1",
        "memory_string_2"
    ]
}}

Selection criteria:
1. Memory should be relevant to the current conversation topic
2. Memory should help maintain character consistency
3. Memory should enrich the response without overwhelming it
4. Prioritize recent and emotionally significant memories
5. Consider the user's history and relationship context"""

async def select_relevant_memories(user_identifier: str, user_message: str) -> str:
    """
    Select relevant memories based on the current conversation context.
    Returns a comma-separated string of relevant memories.
    """
    try:
        # Read all available memories
        with open('memories.json', 'r') as f:
            all_memories = json.load(f)['memories']
        
        # Prepare prompt
        prompt = MEMORY_SELECTION_PROMPT.format(
            user_identifier=user_identifier,
            user_message=user_message,
            all_memories=json.dumps(all_memories, indent=2)
        )
        
        # Get memory selection from AI
        response = await openai.ChatCompletion.acreate(
            model=Config.AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise memory selection tool that MUST respond with ONLY valid JSON format."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=100
        )
        
        # Parse response
        content = response.choices[0].message['content']
        cleaned_content = content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]
        cleaned_content = cleaned_content.strip()
        
        try:
            analysis = json.loads(cleaned_content)
            # Convert selected memories directly to comma-separated string
            memory_string = ", ".join(analysis['selected_memories'])
            return memory_string
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parse Error: {e}")
            return ""
        
    except Exception as e:
        logger.error(f"Error in select_relevant_memories: {e}")
        return "" 