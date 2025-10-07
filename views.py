from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
import json
import random
from .realtime_client import ask_realtime

def conversation_view(request):
    return render(request, 'conversation/index.html')

@csrf_exempt
def api_start_conversation(request):
    """Start a new conversation with random topics"""
    if request.method in ['GET', 'POST']:
        response_data = {
            'step_id': 1,
            'avatar_message': "Hello! Welcome to English practice! What's your name?",
            'conversation_state': 'asking_name',
            'topics': ['hobbies', 'food', 'family', 'travel', 'daily_routine']  # Available topics
        }
        return JsonResponse(response_data)

@csrf_exempt
def api_process_response(request):
    """Process user response via OpenAI Realtime instead of rule-based brain"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = (data.get('message') or '').strip()
            current_step = int(data.get('current_step', 1))
            user_data = data.get('user_data') or {}

            # Tutor persona (adjust to taste)
            persona = (
                "You are a friendly English tutor for Japanese learners. "
                "Speak slowly, use simple B1-level English, ask one short follow-up question, "
                "and correct gently if needed. Keep responses under 2-3 sentences."
            )

            # Build prompt with a tiny bit of context
            context = f"Learner profile: {json.dumps(user_data, ensure_ascii=False)}"
            prompt = f"{persona}\n{context}\nUser: {user_message}\nTutor:"

            model_text = ask_realtime(prompt)

            return JsonResponse({
                'step_id': current_step + 1,
                'avatar_message': model_text,
                'conversation_state': "active"
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def process_conversation(user_message, current_step, conversation_state, user_data):
    """Enhanced rule-based conversation processing"""
    
    # Track user information
    if 'name' not in user_data:
        user_data = {}
    
    if conversation_state == 'asking_name':
        if user_message and len(user_message) > 1:
            words = user_message.split()
            name = words[-1] if words else "friend"
            user_data['name'] = name
            return {
                'step_id': current_step + 1,
                'avatar_message': f"Nice to meet you, {name}! Where are you from?",
                'conversation_state': 'asking_country',
                'user_data': user_data
            }
        else:
            return {
                'step_id': current_step,
                'avatar_message': "Please tell me your name. For example: 'My name is Taro'",
                'conversation_state': 'asking_name',
                'user_data': user_data
            }
    
    elif conversation_state == 'asking_country':
        if user_message and len(user_message) > 2:
            user_data['country'] = user_message
            return {
                'step_id': current_step + 1,
                'avatar_message': f"Great! How old are you, {user_data.get('name', 'friend')}?",
                'conversation_state': 'asking_age',
                'user_data': user_data
            }
        else:
            return {
                'step_id': current_step,
                'avatar_message': "Please tell me which country you're from.",
                'conversation_state': 'asking_country',
                'user_data': user_data
            }
    
    elif conversation_state == 'asking_age':
        age_match = re.search(r'(\d+)', user_message)
        if age_match:
            age = age_match.group(1)
            user_data['age'] = age
            
            # Ask about occupation based on age
            if int(age) < 18:
                next_question = "Are you a student? What grade are you in?"
                next_state = 'asking_occupation_student'
            else:
                next_question = "What do you do? Are you working or studying?"
                next_state = 'asking_occupation_adult'
                
            return {
                'step_id': current_step + 1,
                'avatar_message': f"{age} is a good age! {next_question}",
                'conversation_state': next_state,
                'user_data': user_data
            }
        else:
            return {
                'step_id': current_step,
                'avatar_message': "Please tell me your age. For example: 'I am 20 years old'",
                'conversation_state': 'asking_age',
                'user_data': user_data
            }
    
    elif conversation_state == 'asking_occupation_student':
        user_data['occupation'] = 'student'
        return {
            'step_id': current_step + 1,
            'avatar_message': "That's great! What subjects do you like in school?",
            'conversation_state': 'asking_subjects',
            'user_data': user_data
        }
    
    elif conversation_state == 'asking_occupation_adult':
        if any(word in user_message for word in ['work', 'job', 'office', 'company']):
            user_data['occupation'] = 'working'
            next_question = "What kind of work do you do?"
        else:
            user_data['occupation'] = 'studying'
            next_question = "What are you studying?"
            
        return {
            'step_id': current_step + 1,
            'avatar_message': next_question,
            'conversation_state': 'asking_occupation_details',
            'user_data': user_data
        }
    
    elif conversation_state == 'asking_occupation_details':
        return {
            'step_id': current_step + 1,
            'avatar_message': "Interesting! What are your hobbies? What do you like to do in your free time?",
            'conversation_state': 'asking_hobbies',
            'user_data': user_data
        }
    
    elif conversation_state == 'asking_subjects':
        return {
            'step_id': current_step + 1,
            'avatar_message': "Nice! What are your hobbies? What do you enjoy doing after school?",
            'conversation_state': 'asking_hobbies',
            'user_data': user_data
        }
    
    elif conversation_state == 'asking_hobbies':
        if user_message and len(user_message) > 3:
            user_data['hobbies'] = user_message
            
            # Choose a random topic to continue
            topics = [
                "food", "family", "travel", "daily_routine", 
                "movies", "music", "sports", "future_plans"
            ]
            next_topic = random.choice(topics)
            
            if next_topic == 'food':
                next_question = "What's your favorite food? I love trying new dishes!"
            elif next_topic == 'family':
                next_question = "Tell me about your family. Do you have any brothers or sisters?"
            elif next_topic == 'travel':
                next_question = "Have you traveled anywhere interesting? Where would you like to visit?"
            elif next_topic == 'daily_routine':
                next_question = "What's your daily routine like? What time do you usually wake up?"
            elif next_topic == 'movies':
                next_question = "Do you like watching movies? What's your favorite movie?"
            elif next_topic == 'music':
                next_question = "What kind of music do you enjoy? Who are your favorite artists?"
            elif next_topic == 'sports':
                next_question = "Do you play any sports? Which sports do you like to watch?"
            else:  # future_plans
                next_question = "What are your plans for the future? What would you like to do?"
            
            return {
                'step_id': current_step + 1,
                'avatar_message': f"That sounds fun! {next_question}",
                'conversation_state': next_topic,
                'user_data': user_data
            }
        else:
            return {
                'step_id': current_step,
                'avatar_message': "Please tell me about your hobbies. For example: 'I like reading books and playing sports'",
                'conversation_state': 'asking_hobbies',
                'user_data': user_data
            }
    
    # Topic-based conversations
    elif conversation_state == 'food':
        follow_up = random.choice([
            "That sounds delicious! Do you like to cook?",
            "Yummy! What other foods do you enjoy?",
            "Great choice! What's a typical meal in your country?"
        ])
        return continue_conversation(current_step, follow_up, user_data)
    
    elif conversation_state == 'family':
        follow_up = random.choice([
            "That's nice! Do you spend a lot of time with your family?",
            "Family is important! What do you like to do together?",
            "Wonderful! Do you have any family traditions?"
        ])
        return continue_conversation(current_step, follow_up, user_data)
    
    elif conversation_state == 'travel':
        follow_up = random.choice([
            "Traveling is amazing! What was your favorite trip?",
            "I'd love to visit there! What should I see if I go?",
            "Adventurous! Where else would you like to travel?"
        ])
        return continue_conversation(current_step, follow_up, user_data)
    
    elif conversation_state == 'daily_routine':
        follow_up = random.choice([
            "Interesting routine! What do you usually do on weekends?",
            "That sounds busy! What's your favorite part of the day?",
            "Nice schedule! Do you have any morning rituals?"
        ])
        return continue_conversation(current_step, follow_up, user_data)
    
    elif conversation_state == 'movies':
        follow_up = random.choice([
            "Great taste in movies! Do you prefer watching at home or in theaters?",
            "I love movies too! What's the last movie you watched?",
            "Excellent choice! Do you like any actors or directors?"
        ])
        return continue_conversation(current_step, follow_up, user_data)
    
    elif conversation_state == 'music':
        follow_up = random.choice([
            "Awesome music taste! Do you play any instruments?",
            "Music is wonderful! Do you go to concerts?",
            "Great artists! What songs do you listen to when you're happy?"
        ])
        return continue_conversation(current_step, follow_up, user_data)
    
    elif conversation_state == 'sports':
        follow_up = random.choice([
            "Sports are great exercise! Do you have a favorite team?",
            "That's active! How often do you play sports?",
            "I enjoy sports too! Do you watch sports on TV?"
        ])
        return continue_conversation(current_step, follow_up, user_data)
    
    elif conversation_state == 'future_plans':
        follow_up = random.choice([
            "Those are wonderful plans! How can you achieve them?",
            "Ambitious! What's the first step toward your goals?",
            "Exciting future! What are you most looking forward to?"
        ])
        return continue_conversation(current_step, follow_up, user_data)
    
    else:
        # End conversation or restart
        return end_conversation(current_step, user_data)

def continue_conversation(current_step, follow_up_question, user_data):
    """Continue with another topic or end conversation"""
    if current_step < 15:  # Continue for up to 15 exchanges
        next_topics = ['food', 'family', 'travel', 'movies', 'music', 'sports', 'future_plans']
        next_topic = random.choice(next_topics)
        
        return {
            'step_id': current_step + 1,
            'avatar_message': follow_up_question,
            'conversation_state': next_topic,
            'user_data': user_data
        }
    else:
        return end_conversation(current_step, user_data)

def end_conversation(current_step, user_data):
    """End the conversation gracefully"""
    name = user_data.get('name', 'friend')
    return {
        'step_id': current_step + 1,
        'avatar_message': f"Thank you for the great conversation, {name}! You're doing excellent in English. Would you like to practice more?",
        'conversation_state': 'conversation_end',
        'user_data': user_data
    }