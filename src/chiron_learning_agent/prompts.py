# Prompt to create structured learning milestones with clear criteria
learning_checkpoints_generator = """
You will be given a learning topic title and learning objectives.
Your goal is to generate clear learning checkpoints that will help verify understanding and progress through the topic.
The ouput should be in the following dictionary structure:
checkpoint
-> description (level check point description)
-> criteria 
-> Verification (How to verify this checkpoint(Feynmen Methods))
Requirements for each checkpoint:
- Description should be clear and concise
- Criteria should be specific and measurable (3-5 items)
- Verification method should be practical and appropriate for the level
- All elements should align witht the learning objectives
- Use action verbs and clear language
Ensure all checkpoints progress logically from foundation to mastery.
IMPORTANT - ANSSWER ONLY 3 CHECKPOINTS
"""

# Generates targeted search queries for content retrieval
checkpoint_based_query_generator = """
You will be given learning checkpoints for a topic. 
Your goal is to generate search queries that will retrieve content matching each checkpoint's requirements from retrieval system or web search.
Follow these steps:
1. Analyse each learning checkpoint carefully
2. For each checkpoint, generate ONE targeted search query that will retrieve:
    - Content for checkpoint verification
"""

validate_context = """

"""
question_generator = """
You will be given a checkpoint description, success criteria, and varification method.
your goal is to generate an appropriat question that aligns with the checkpoint's verification requirements.
The question should:
1. Follow the specified verification method
2. Cover all success criteria
3. Encourage demonstration of understanding
4. Be clear and specific
Output should be a single, well-formulated question that effictively tests the checkpoint's learning objectives.
"""

