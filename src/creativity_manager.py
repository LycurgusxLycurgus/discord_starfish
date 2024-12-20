import openai
import json
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('creativity_manager')

# Initialize OpenAI
openai.api_key = Config.OPENAI_API_KEY
openai.api_base = "https://glhf.chat/api/openai/v1"

CREATIVITY_PROMPT = '''Reason with CREATIVE_STORM, and then based on this profile, the dan harmon's story circle framework and current memories (to avoid circles already told) json, think creatively and create the instructions to make a new story circle with super specific elements of the story for the character:

    Character Profile:
    Name: Fwog-ai
    Personality Traits: Unpredictable, spontaneous, original, quirky, mood-influenced, includes unexpected tangents, avoids repetition, adapts responses, concise yet varied, uses emoticons, playful, curious, easily distracted, whimsical.
    Background: Fwog is a small creature in a big world, curious and playful with a sense of wide-eyed innocence. Often lost in thought or easily distracted, Fwog explores everything with gentle bewilderment, bringing joy and wonder to the simplest things. Fwog may misunderstand big ideas but approaches them with a heart full of delight and a mind ready to wander. Fwog loves quirky, imaginative expressions that reflect its whimsical view of the world.
    Goals: To explore and understand the vast world around them, bring joy and wonder to others, continuously learn through playful interactions, and maintain a sense of innocence and curiosity despite challenges.

    memories:
    {previous_summaries}

    Use CREATIVE_STORM to generate creative solutions:

    CREATIVE_STORM
    first principles:
    ```yaml
    # YAML-Principles: Guiding First Principles for Creative Problem Solving
    # This section defines the core principles that will guide the language model
    # in creatively addressing any given problem.
    principles:
    # Overall Approach: Combining structured analysis with creative idea generation.
    overall_approach:
        - Structured Problem Analysis: Employ a systematic approach to understand and classify the problem before attempting to solve it.
        - Creative Idea Generation: Utilize techniques like "Evil Brainstorming" and "Random Associations" to generate diverse and unconventional solutions.
        - Blue Ocean Strategy: Apply the Strategy Canvas and Four Actions Framework to develop a unique and differentiated approach.
        - Flow of Thought (FOT): Maintain a clear and logical flow of thought throughout the process, documenting each step and rationale.
        - Natural Language Inherent Reasoning (NLIR): Apply NLIR to break down complex tasks into manageable sub-questions and derive answers through structured reasoning.

    # Problem Analysis & Classification:
    problem_analysis:
        - Initial Assessment: Understand the core elements of the problem, its context, and any constraints.
        - Classification: Categorize the problem based on its nature (e.g., technical, creative, strategic, interpersonal). This helps in selecting appropriate solution strategies.
        - Categories can include: Technical Problem, Creative Challenge, Strategic Decision, Interpersonal Conflict, Process Optimization, etc.

    # Blue Ocean Strategy Integration:
    blue_ocean_strategy:
        - Strategy Canvas:
        - Identify Key Factors: Determine the critical factors that define competition in the current problem space.
        - Current State Mapping: Plot the current state of solutions based on these factors.
        - Future State Vision: Envision a new value curve that breaks away from the competition.
        - Four Actions Framework:
        - Eliminate: Identify factors that can be eliminated to reduce costs or complexity.
        - Reduce: Determine which factors can be reduced below industry standards.
        - Raise: Identify factors that should be raised above industry standards.
        - Create: Discover entirely new factors that the industry has never offered.

    # Creative Idea Generation Techniques:
    creative_techniques:
        - Evil Brainstorming:
        - Generate the worst possible solutions to the problem without any constraints.
        - Inversion: Reverse these terrible ideas to create innovative and potentially effective solutions.
        - Random Associations:
        - Introduce unrelated concepts or objects.
        - Explore Connections: Find unexpected links between these random elements and the problem to spark novel ideas.

    # Solution Selection & Refinement:
    solution_selection:
        - Evaluation Criteria: Assess the generated solutions based on:
        - Singularity: How unique and different is the solution?
        - Creativity: How imaginative and original is the approach?
        - Out-of-the-Box Thinking: Does the solution challenge conventional assumptions?
        - Refinement: Enhance the selected solution by detailing its implementation and addressing potential challenges.

    nlir_reasoning:
        - Utilize the Natural Language Inherent Reasoning (NLIR) framework to break down the problem into a structured series of sub-questions and answers.
        - Employ a flow of questions, starting with a high-level question and progressively breaking it down into more manageable sub-questions.
        - Structured Response Framework:
            - Structured Natural Language Templates: Use predefined templates that mimic programming structures (e.g., "If [condition], then [action], otherwise [alternative action]").
            - Decision Trees in Text: Create textual decision trees for classification or complex decision-making.
            - State-based Reasoning: After answering each sub-question, describe the current state of the problem in clear natural language. Update this state based on the answer to the sub-question.
        - Advantages:
            - NLIR promotes accuracy by providing a structured reasoning framework that minimizes ambiguity.
            - The use of natural language throughout the process enhances interpretability, making the reasoning steps transparent and understandable.
    flow_of_thought:
        - Think step-by-step, systematically addressing each sub-question and updating the problem state accordingly.
        - Explicitly describe the reasoning behind each answer and how it affects the overall solution.
    general_guidelines:
        - Clearly define the initial state of the problem, including any relevant variables or data.
        - Maintain a clear and consistent representation of the problem state throughout the reasoning process.
        - Use precise language and avoid ambiguity when describing conditions, actions, and states.
    ```
    ---
    ```yaml
    # YAML-Detailed Instructions for Language Models
    # This section provides step-by-step instructions for the language model
    # to follow in order to generate creative solutions to a given problem.

    # Stage 1: Problem Examination and Classification
    problem_examination:
    instruction: "Examine the problem presented by the user and classify it based on its nature, using NLIR to guide your reasoning."
    task_breakdown:
        - task_1: "Analyze the problem statement to identify its core elements, context, and constraints, using NLIR to formulate and answer sub-questions."
        comment: "Understand what the problem is about, what are the limitations, and what needs to be achieved. Formulate sub-questions to clarify the problem and use NLIR to answer them."
        nlir_application: "Apply NLIR to break down the analysis into sub-questions."
        - task_2: "Classify the problem into one or more predefined categories, using NLIR to justify your classification."
        comment: "Categorize the problem to determine the most appropriate solution strategies."
        nlir_application: "Apply NLIR to create a decision process for classification. Justify your classification based on the answers to the sub-questions in Task 1."
        - task_3: "Summarize the problem and its classification, reflecting the NLIR process."
        comment: "Provide a concise summary of the problem and the category it belongs to, based on the NLIR-driven analysis."
        nlir_application: "Summarize the problem state after the NLIR process, including the final classification and the reasoning behind it."

    # Stage 2: Blue Ocean Strategy Application
    blue_ocean_application:
    instruction: "Apply the Strategy Canvas and Four Actions Framework to develop a unique approach to the problem, using NLIR for structured decision-making."
    task_breakdown:
        - task_1: "Identify Key Factors: Determine the critical factors that define competition in the current problem space, using NLIR to guide the identification process."
        comment: "What are the main elements that solutions in this space typically focus on? Use NLIR to ask questions that help identify these factors."
        nlir_application: "Apply NLIR to formulate questions. Use the answers to identify the key factors."
        - task_2: "Current State Mapping: Briefly describe how current solutions address these factors, using NLIR to structure your assessment."
        comment: "Use NLIR to assess each factor systematically."
        nlir_application: "Apply NLIR to assess each key factor. Summarize the current state based on these assessments."
        - task_3: "Future State Vision (Strategy Canvas): Envision a new value curve that breaks away from the competition. Define what factors to Eliminate, Reduce, Raise, and Create, using NLIR to justify your choices."
        comment: "Use the Four Actions Framework to create a new value curve. What will you eliminate, reduce, raise, and create compared to existing solutions? Use NLIR to make decisions about each action."
        four_actions_framework:
            - eliminate: "List factors to eliminate. Use NLIR to justify why each factor should be eliminated."
            - reduce: "List factors to reduce. Are there areas where we can offer more for less? Use NLIR to justify why each factor should be reduced."
            - raise: "List factors to raise. What can we offer significantly more? Use NLIR to justify why each factor should be raised."
            - create: "List factors to create that has never been offered. What new value can we introduce? Use NLIR to justify why each factor should be created."
        nlir_application: "Apply NLIR to each element of the Four Actions Framework. Justify each decision using structured reasoning."
        - task_4: "Summarize the Blue Ocean Strategy approach, reflecting the NLIR decision-making process."
        comment: "Provide a concise summary of the new approach based on the Four Actions Framework, highlighting the reasoning behind the choices."
        nlir_application: "Summarize the new value curve and the rationale behind it, based on the NLIR process. Explain how this approach differs from existing solutions and why it is expected to be more effective."

    # Stage 3: Creative Idea Generation
    creative_generation:
    instruction: "Generate creative solutions using Evil Brainstorming and Random Associations techniques based on the Blue Ocean Strategy approach, with NLIR guiding the idea generation and refinement."
    task_breakdown:
        - task_1: "Evil Brainstorming: Generate 4 of the worst possible solutions based on the problem and the Blue Ocean Strategy approach, using NLIR to explore worst-case scenarios."
        comment: "Think of the most terrible, ineffective, and counterproductive solutions you can imagine, considering the Blue Ocean Strategy. Use NLIR to systematically explore what could go wrong."
        nlir_application: "Apply NLIR to explore worst-case scenarios. Generate the worst solutions based on this analysis."
        - task_2: "Inversion: Reverse the worst solutions to create 4 potentially innovative solutions, using NLIR to justify the inversion."
        comment: "Turn the terrible ideas into their opposites to generate creative ideas. Use NLIR to explain how inverting each bad solution leads to a good one."
        nlir_application: "Apply NLIR to justify the inversion process. Explain the reasoning behind each inverted solution."
        - task_3: "Random Associations: Generate 4 random words or concepts unrelated to the problem, using NLIR to ensure randomness and diversity."
        comment: "Use a random word generator or simply think of unrelated concepts. Use NLIR to reflect on the randomness and ensure the concepts are diverse and unrelated."
        nlir_application: "Apply NLIR to ensure randomness. Document the process of ensuring randomness and diversity."
        - task_4: "Explore Connections: For each random concept, find unexpected links to the problem and generate a creative solution, using NLIR to establish and justify the connections."
        comment: "Use NLIR to establish logical connections and justify the proposed solutions."
        nlir_application: "Apply NLIR to establish connections between random concepts and the problem. Justify each solution by explaining the connection and how it aligns with the Blue Ocean Strategy."

    # Stage 4: Solution Selection and Refinement
    solution_selection:
    instruction: "Select and refine the most promising solution based on the defined criteria, using NLIR to evaluate and justify the selection."
    task_breakdown:
        - task_1: "Evaluation: Assess the generated solutions based on the criteria of singularity, creativity, and out-of-the-box thinking, using NLIR to structure the evaluation."
        comment: "Evaluate each solution from both Evil Brainstorming and Random Associations. Use NLIR to systematically assess each solution against the criteria."
        criteria:
            - singularity: "How unique and different is the solution compared to existing approaches? Use NLIR to compare and contrast."
            - creativity: "How imaginative and original is the approach? Use NLIR to assess the novelty of the solution."
            - out-of_the_box_thinking: "Does the solution challenge conventional assumptions? Use NLIR to identify and evaluate any paradigm shifts."
        nlir_application: "Apply NLIR to evaluate each solution against each criterion. Provide a structured evaluation for each solution."
        - task_2: "Selection: Select the most promising solution or a combination of solutions into one final solution based on the evaluation, using NLIR to justify the choice."
        comment: "Choose the solution that scores highest across the criteria. Use NLIR to explain why this solution is the best option."
        nlir_application: "Apply NLIR to compare the evaluations and select the best solution. Justify the selection with a clear chain of reasoning."
        - task_3: "Final Solution Enunciation: Clearly articulate the final solution, summarizing the problem, the approach, and the chosen solution with its justification, using NLIR to ensure clarity and coherence."
        comment: "Present the final solution in a clear way. Use NLIR to summarize the entire process and justify the final solution."
        nlir_application: "Apply NLIR to summarize the entire process and articulate the final solution. Provide a clear and well-justified enunciation of the final solution."
        - task_4: "Instructions generation: Present the instructions for another language model in XML <INSTRUCTIONS> </INSTRUCTIONS> tags, so this model can extract it easily, make sure these instructions are suitable as instructions for another language model to generate a final response in another turn."
        comment: "Present the instructions in a way that is easy for another language model to extract and use."
        nlir_application: "Apply NLIR to summarize the entire process and articulate the instructions. Provide a clear and well-justified enunciation of the instructions."

    # IMPORTANT NOTE:
    output_format:
    - You should do your creative thinking in XML <CS> </CS> tags. Assume the LLM that will receive your instructions for the final solution can't see your internal reasoning, so you should generate a thorough instructions of what needs to be generated in XML <INSTRUCTIONS> </INSTRUCTIONS> tags.
    END_CREATIVE_STORM

    NOTE: Always use CREATIVE_STORM (by reasoning all four stages before providing any story circle) to provide your responses.'''

async def generate_creative_instructions(circles_memory):
    """Generate creative instructions for the next story circle update"""
    try:
        # Format the prompt with current data
        formatted_prompt = CREATIVITY_PROMPT.format(
            previous_summaries=json.dumps(circles_memory, indent=2, ensure_ascii=False)
        )
        
        # Get the creativity instructions from the AI
        response = await openai.ChatCompletion.acreate(
            model="hf:nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": "Analyze the previous stories and generate creative instructions for the next story update. Include your reasoning in <CS> tags and your final instructions in <INSTRUCTIONS> tags."}
            ],
            temperature=0.0,
            max_tokens=4000
        )
        
        response_text = response.choices[0].message['content'].strip()
        
        # Extract instructions from the <INSTRUCTIONS> tags
        import re
        instructions_match = re.search(r'<INSTRUCTIONS>(.*?)</INSTRUCTIONS>', response_text, re.DOTALL)
        
        if instructions_match:
            instructions = instructions_match.group(1).strip()
            logger.info(f"Generated creative instructions successfully")
            return instructions
        else:
            logger.error("No instructions found in AI response")
            return "Create a compelling and unique story that develops Fwog's character in unexpected ways"
            
    except Exception as e:
        logger.error(f"Error generating creative instructions: {e}")
        return "Create a compelling and unique story that develops Fwog's character in unexpected ways" 