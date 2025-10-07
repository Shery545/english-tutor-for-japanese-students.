import os
import openai

# Try to get API key from environment variable, or use the direct key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Set the API key for openai
openai.api_key = OPENAI_API_KEY

def ask_realtime(prompt):
    """
    Send prompt to OpenAI API and get response
    """
    try:
        # For newer OpenAI version (v1.0+)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o model
                messages=[
                    {"role": "system", "content": "You are a friendly English tutor for Japanese learners. Speak slowly, use simple B1-level English, ask one short follow-up question, and correct gently if needed. Keep responses under 2-3 sentences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
            
        except ImportError:
            # Fallback for older OpenAI version (0.28.x and below)
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a friendly English tutor for Japanese learners. Speak slowly, use simple B1-level English, ask one short follow-up question, and correct gently if needed. Keep responses under 2-3 sentences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
            
    except Exception as e:
        return f"I'm having trouble responding right now. Please try again. Error: {str(e)}"