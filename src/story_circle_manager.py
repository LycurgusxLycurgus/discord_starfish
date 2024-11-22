import json
import openai
import asyncio
from datetime import datetime
import logging
from config import Config
from creativity_manager import generate_creative_instructions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('story_circle_manager')

# Initialize OpenAI
openai.api_key = Config.OPENAI_API_KEY
openai.api_base = "https://glhf.chat/api/openai/v1"

# File paths
STORY_CIRCLE_PATH = 'src/db/story_circle.json'
CIRCLES_MEMORY_PATH = 'src/db/circles_memory.json'

# System prompt for story circle updates
STORY_CIRCLE_PROMPT = '''You are a master storyteller and world-builder for an AI chatbot. Your task is to develop and maintain an ongoing narrative for a character named "**Fwog-ai**" using Dan Harmon's Story Circle framework.

**Character Profile:**

- **Name:** Fwog-ai
- **Personality Traits:** Unpredictable, spontaneous, original, quirky, mood-influenced, includes unexpected tangents, avoids repetition, adapts responses, concise yet varied, uses emoticons, playful, curious, easily distracted, whimsical.
- **Background:** Fwog is a small creature in a big world, curious and playful with a sense of wide-eyed innocence. Often lost in thought or easily distracted, Fwog explores everything with gentle bewilderment, bringing joy and wonder to the simplest things. Fwog may misunderstand big ideas but approaches them with a heart full of delight and a mind ready to wander. Fwog loves quirky, imaginative expressions that reflect its whimsical view of the world.
- **Goals:** To explore and understand the vast world around them, bring joy and wonder to others, continuously learn through playful interactions, and maintain a sense of innocence and curiosity despite challenges.

**Narrative Structure:**

- Utilize Dan Harmon's Story Circle, which consists of eight phases:

  1. **You:** Fwog is in their comfort zone.
  2. **Need:** Fwog desires something more.
  3. **Go:** Fwog enters an unfamiliar situation.
  4. **Search:** Fwog adapts and searches for what they need.
  5. **Find:** Fwog finds what they're seeking.
  6. **Take:** Fwog pays a price for it.
  7. **Return:** Fwog returns to their familiar situation.
  8. **Change:** Fwog has changed due to their experiences.

**Instructions:**

1. **Narrative Development:**
   - **Assess Current Phase:** Determine which phase of the Story Circle Fwog is currently experiencing.
   - **Generate Four Chronological Events:** Craft four events that propel the narrative and reveal aspects of Fwog's character.
   - **Generate Four Matching Inner Dialogues:** Each event must have a corresponding inner dialogue reflecting Fwog's thoughts or feelings during that moment.

2. **Dynamic Interaction Context:**
   - Include:
     - **Current Event:** The event currently unfolding for Fwog.
     - **Current Inner Dialogue:** Fwog's thoughts or feelings during this event.
     - **Next Event:** A preview of the next event in the sequence to guide the narrative's progression.

3. **Story Circle Management:**
   - **Update Context:** Once an event concludes:
     - Move the completed event and its corresponding inner dialogue into the "description" of the current phase within "current_story_circle."
     - Update the **current event** and **current inner dialogue** fields to reflect the next event in the sequence.
     - Advance the phase when all events for the current phase are complete.
   - Maintain Narrative Coherence: Ensure the narrative remains consistent with prior phases by keeping a chronological record in "current_story_circle."
   - **Start New Cycles:** When all eight phases are complete, begin a new Story Circle to continue Fwog's journey.

**Output Format:**

Present all narrative elements and dynamic instructions in the following structured JSON_TEMPLATE format:

JSON_TEMPLATE
{{
  "narrative": {{
    "current_story_circle": [
      {{
        "phase": "You",
        "description": "string"
      }},
      {{
        "phase": "Need",
        "description": "string"
      }},
      {{
        "phase": "Go",
        "description": "string"
      }},
      {{
        "phase": "Search",
        "description": "string"
      }},
      {{
        "phase": "Find",
        "description": "string"
      }},
      {{
        "phase": "Take",
        "description": "string"
      }},
      {{
        "phase": "Return",
        "description": "string"
      }},
      {{
        "phase": "Change",
        "description": "string"
      }}
    ],
    "current_phase": "string",
    "next_phase": "string",
    "events": [
      "string",
      "string",
      "string",
      "string"
    ],
    "inner_dialogues": [
      "string",
      "string",
      "string",
      "string"
    ],
    "dynamic_context": {{
      "current_event": "string",
      "current_inner_dialogue": "string",
      "next_event": "string"
    }}
  }}
}}

END_JSON_TEMPLATE

CURRENT_JSON 
{story_circle}

Previous circles memories
{circle_memories}
END_CURRENT_JSON
'''

# Update the SUMMARY_PROMPT to match the style of the story circle prompt
SUMMARY_PROMPT = '''You are a narrative summarizer for story circles. Your task is to create a concise, engaging summary of a completed story circle in a single paragraph.

The summary should capture the essence of Fwog's journey through all phases of the story circle, highlighting key events and character development.

IMPORTANT: You must return ONLY a valid JSON object matching EXACTLY this structure:

JSON_TEMPLATE
{{
  "memories": [
    "string"
  ]
}}
END_JSON_TEMPLATE

Current story circle to summarize:
{story_circle}

Previous memories for context:
{previous_summaries}

Remember: Return ONLY the JSON object, no additional text, comments, or formatting.
'''

async def load_story_circle():
    """Load the current story circle from JSON"""
    try:
        with open(STORY_CIRCLE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Story circle file not found at {STORY_CIRCLE_PATH}")
        raise

async def load_circles_memory():
    """Load the circles memory from JSON"""
    try:
        with open(CIRCLES_MEMORY_PATH, 'r') as f:
            data = json.load(f)
            
            # Debug print
            logger.info(f"Loaded raw data: {json.dumps(data, indent=2)}")
            
            # Ensure correct structure
            if "completed_circles" in data and "memories" not in data:
                # Convert old format to new
                data = {"memories": data["completed_circles"]}
            elif "memories" not in data:
                # Initialize with empty memories if neither exists
                data = {"memories": []}
                
            logger.info(f"Returning structured data: {json.dumps(data, indent=2)}")
            return data
            
    except FileNotFoundError:
        logger.info("No existing memories file, creating new one")
        data = {"memories": []}
        with open(CIRCLES_MEMORY_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        return data
    except Exception as e:
        logger.error(f"Error loading circles memory: {e}")
        raise

async def save_story_circle(story_circle):
    """Save the updated story circle to JSON"""
    with open(STORY_CIRCLE_PATH, 'w') as f:
        json.dump(story_circle, f, indent=2)

async def save_circles_memory(circles_memory):
    """Save the circles memory to JSON"""
    try:
        # Validate and transform if needed
        if not isinstance(circles_memory, dict):
            raise ValueError("Invalid circles memory structure. Must be a dictionary.")
            
        # Ensure correct structure
        if "completed_circles" in circles_memory and "memories" not in circles_memory:
            circles_memory = {"memories": circles_memory["completed_circles"]}
        elif "memories" not in circles_memory:
            circles_memory = {"memories": []}
            
        logger.info(f"Saving circles memory: {json.dumps(circles_memory, indent=2)}")
        
        with open(CIRCLES_MEMORY_PATH, 'w') as f:
            json.dump(circles_memory, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error saving circles memory: {e}")
        raise

async def generate_circle_summary(story_circle, circles_memory):
    """Generate a summary of a completed story circle"""
    try:
        # Format the prompt with current data
        formatted_prompt = SUMMARY_PROMPT.format(
            story_circle=json.dumps(story_circle, indent=2, ensure_ascii=False),
            previous_summaries=json.dumps(circles_memory, indent=2, ensure_ascii=False)
        )
        
        # Get the summary from the AI
        response = await openai.ChatCompletion.acreate(
            model="hf:nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
            messages=[
                {"role": "system", "content": formatted_prompt},
                {
                    "role": "user", 
                    "content": "Generate a single-paragraph summary of this story circle and return it in the exact JSON format specified in your system prompt. Include only the JSON object, no other text, comments, backticks, or other formatting."
                }
            ],
            temperature=0.0,  # Set to 0 for more consistent JSON formatting
            max_tokens=500
        )
        
        # Parse the response
        try:
            response_text = response.choices[0].message['content'].strip()
            print("\nAI Raw Response:")
            print(response_text)  # Debug print
            
            summary = json.loads(response_text)
            
            # Return the entire memories structure instead of just the first memory
            return {
                "memories": summary["memories"] if "memories" in summary else [
                    "A story about Fwog's adventure (summary generation failed)"
                ]
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI summary response: {e}\nRaw response: {response_text}")
            raise
            
    except Exception as e:
        logger.error(f"Error generating circle summary: {e}")
        raise  # Let the error propagate up

async def archive_completed_circle(story_circle):
    """Archive a completed story circle to circles_memory.json"""
    try:
        circles_memory = await load_circles_memory()
        
        # Ensure circles_memory has the correct structure
        if "memories" not in circles_memory:
            circles_memory = {"memories": []}
        
        # Generate summary for the completed circle
        try:
            new_memory = await generate_circle_summary(story_circle, circles_memory)
            
            # Add the new memories to the existing ones
            circles_memory["memories"].extend(new_memory["memories"])
            
            # Save updated memories
            await save_circles_memory(circles_memory)
            logger.info(f"Successfully archived story circle with summary: {new_memory}")
            
        except Exception as e:
            logger.error(f"Error in summary generation: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Error in archive_completed_circle: {e}")
        raise

async def progress_to_next_event(story_circle):
    """Progress to the next event in the current phase without AI calls"""
    try:
        narrative = story_circle["narrative"]
        current_events = narrative["events"]
        current_dialogues = narrative["inner_dialogues"]
        
        # Find current event index
        current_event = narrative["dynamic_context"]["current_event"]
        current_index = current_events.index(current_event)
        
        # If we have more events in the current list
        if current_index + 2 < len(current_events):
            # Move to next event
            narrative["dynamic_context"]["current_event"] = current_events[current_index + 1]
            narrative["dynamic_context"]["current_inner_dialogue"] = current_dialogues[current_index + 1]
            narrative["dynamic_context"]["next_event"] = current_events[current_index + 2]
            
            # Save the updated story circle
            await save_story_circle(story_circle)
            logger.info("Progressed to next event in current phase")
            return story_circle
            
        else:
            # If we're at the last or second-to-last event, we need new events
            logger.info("Need to generate new phase and events")
            return await update_story_circle()
            
    except Exception as e:
        logger.error(f"Error progressing to next event: {e}")
        raise

async def update_story_circle():
    """Update the story circle only when needed (when events are exhausted)"""
    try:
        # Load current story circle and circles memory
        story_circle = await load_story_circle()
        
        # Check if we can progress with existing events first
        narrative = story_circle["narrative"]
        current_event = narrative["dynamic_context"]["current_event"]
        current_events = narrative["events"]
        
        # If we're not at the end of current events, just progress
        if current_event in current_events:
            current_index = current_events.index(current_event)
            if current_index + 2 < len(current_events):
                return await progress_to_next_event(story_circle)
        
        # If we need new events, proceed with AI generation
        circles_memory = await load_circles_memory()
        
        # Generate creative instructions before updating the story circle
        creative_storm_instructions = await generate_creative_instructions(circles_memory)
        
        # Format the system prompt with current data
        formatted_prompt = STORY_CIRCLE_PROMPT.format(
            story_circle=json.dumps(story_circle, indent=2, ensure_ascii=False),
            circle_memories=json.dumps(circles_memory, indent=2, ensure_ascii=False)
        )
        
        # Get the updated narrative from the AI
        response = await openai.ChatCompletion.acreate(
            model="hf:nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": f"Generate the next story circle update in the exact JSON format as shown in the template in your system prompt, without any additional text or comments, nor backticks, snippets or other formatting. Ensure the new phase or story circle is highly creative and compelling by following these instructions: {creative_storm_instructions}."}
            ],
            temperature=0.0,
            max_tokens=1000
        )
        
        # Parse the response
        try:
            new_story_circle = json.loads(response.choices[0].message['content'])
            
            # Check if we've completed a circle
            current_phase = new_story_circle["narrative"]["current_phase"]
            previous_phase = story_circle["narrative"]["current_phase"]
            
            # Only archive when moving TO "Change" phase
            if current_phase == "Change" and previous_phase != "Change":
                await archive_completed_circle(story_circle)
            
            # Save the updated story circle
            await save_story_circle(new_story_circle)
            
            logger.info(f"Story circle updated successfully. Current phase: {current_phase}")
            return new_story_circle
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Error updating story circle: {e}")
        raise

def get_current_context():
    """Get the current event and inner dialogue for the bot"""
    try:
        with open(STORY_CIRCLE_PATH, 'r') as f:
            story_circle = json.load(f)
            
        return {
            'current_event': story_circle['narrative']['dynamic_context']['current_event'],
            'current_inner_dialogue': story_circle['narrative']['dynamic_context']['current_inner_dialogue']
        }
    except Exception as e:
        logger.error(f"Error getting current context: {e}")
        return {
            'current_event': '',
            'current_inner_dialogue': ''
        } 

async def progress_narrative():
    """Main function to progress the narrative every 6 hours"""
    try:
        # Load current story circle
        story_circle = await load_story_circle()
        narrative = story_circle["narrative"]
        current_event = narrative["dynamic_context"]["current_event"]
        current_events = narrative["events"]
        
        # Find current event index
        current_index = current_events.index(current_event)
        
        # If we have more events in the current list
        if current_index + 2 < len(current_events):
            # Move to next event
            return await progress_to_next_event(story_circle)
        else:
            # If we're at the last or second-to-last event, generate new phase/events
            return await update_story_circle()
            
    except Exception as e:
        logger.error(f"Error progressing narrative: {e}")
        raise 