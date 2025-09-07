from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import json
import os # Import os to get environment variables
from dotenv import load_dotenv # Import load_dotenv
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware

# Import the Google Generative AI SDK
import google.generativeai as genai


# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost",
    "http://localhost:3000", # React frontend default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
# It's recommended to load the API key from environment variables for security
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
# You can choose a different model if needed, e.g., 'gemini-pro'
model = genai.GenerativeModel('gemini-2.5-flash')

# In-memory storage for user profiles and learning progress
user_profiles: Dict[str, Dict] = {}
current_learning_sessions: Dict[str, Dict] = {}

class UserProfile(BaseModel):
    name: str
    level: str
    goal: str

class Answer(BaseModel):
    user_name: str
    word: str
    user_answer: str # This will now be the selected meaning from options


def generate_words_with_ai(level: str, goal: str) -> List[Dict[str, str]]:
    """
    AI（Gemini）がユーザーのレベルと目標に基づいて単語リストを生成する関数
    Gemini APIを呼び出す
    """
    prompt = f"""
    あなたは英語教育の専門家です。
    ユーザーの英語レベルは「{level}」、学習目標は「{goal}」です。
    このユーザーに最適な英単語を5つ選んでください。
    各単語について、以下の情報を含めてJSON形式で出力してください。
    - word (英単語)
    - meaning (日本語の正しい意味)
    - explanation (簡単な日本語の解説)
    - options (正しい意味を含む4つの選択肢の配列。他の3つはもっともらしい誤った意味であること)

    JSON形式のデータのみを返してください。余計な説明やテキストは一切含めないでください。

    例:
    [
      {{"word": "ubiquitous", "meaning": "どこにでもある、偏在する", "explanation": "どこにでも存在すること。", "options": ["どこにでもある、偏在する", "珍しい、稀な", "特定の場所に限定された", "一時的な、はかない"]}},
      {{"word": "ephemeral", "meaning": "つかの間の、はかない", "explanation": "短命な、一時的な。", "options": ["つかの間の、はかない", "永遠の、不滅の", "巨大な、広大な", "複雑な、入り組んだ"]}}
    ]
    """
    try:
        response = model.generate_content(prompt)
        words_json_str = response.text
        if not words_json_str:
            raise ValueError("Gemini API returned empty response text.")
        print(f"DEBUG: Gemini API response text: {words_json_str}")
        
        # Remove markdown code block wrapping if present
        if words_json_str.startswith("```json") and words_json_str.endswith("```"):
            words_json_str = words_json_str[len("```json"): -len("```")].strip()

        words_list = json.loads(words_json_str)
        return words_list
    except Exception as e:
        print(f"Error generating words with Gemini API: {e}")
        # Fallback to a default list or raise an error
        return [
            {"word": "error", "meaning": "エラー", "explanation": "単語の生成に失敗しました。", "options": ["エラー", "成功", "警告", "情報"]},
            {"word": "default", "meaning": "デフォルト", "explanation": "初期設定の単語です。", "options": ["デフォルト", "カスタム", "オプション", "設定"]},
        ]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/user/setup")
def setup_user_profile(profile: UserProfile):
    user_profiles[profile.name] = profile.dict()
    return {"message": f"User {profile.name} profile set up successfully!", "profile": profile}

@app.post("/ai/generate_words")
def get_ai_generated_words(user_name: str):
    if user_name not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found. Please set up your profile first.")
    
    user_profile = user_profiles[user_name]
    generated_words = generate_words_with_ai(user_profile["level"], user_profile["goal"])
    return {"words": generated_words}

@app.post("/learn/start")
def start_learning_session(user_name: str, mode: str = "learning"): # Added mode parameter
    if user_name not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found. Please set up your profile first.")

    user_profile = user_profiles[user_name]
    
    if mode == "test":
        TEST_QUESTION_COUNT = 10 # Fixed number of questions for test mode
        words_for_session = []
        # Generate words until we have enough for the test
        while len(words_for_session) < TEST_QUESTION_COUNT:
            new_words = generate_words_with_ai(user_profile["level"], user_profile["goal"])
            words_for_session.extend(new_words)
            # Ensure we don't exceed the test question count
            words_for_session = words_for_session[:TEST_QUESTION_COUNT]
        total_questions = TEST_QUESTION_COUNT
    else: # learning mode
        words_for_session = generate_words_with_ai(user_profile["level"], user_profile["goal"])
        total_questions = 0 # Dynamic for learning mode

    if not words_for_session:
        raise HTTPException(status_code=500, detail="Could not generate words for the session.")

    # Initialize session
    current_learning_sessions[user_name] = {
        "word_index": 0,
        "correct_answers": 0,
        "total_questions": total_questions, # Set based on mode
        "words_for_session": words_for_session,
        "mode": mode # Store the mode
    }

    first_word = current_learning_sessions[user_name]["words_for_session"][0]
    return {"message": "Learning session started!", "word": first_word["word"], "options": first_word["options"], "mode": mode, "total_questions": total_questions}

@app.post("/learn/submit_answer")
def submit_answer(answer: Answer):
    user_name = answer.user_name
    if user_name not in current_learning_sessions:
        raise HTTPException(status_code=400, detail="No active learning session for this user.")

    session = current_learning_sessions[user_name]
    current_word_index = session["word_index"]
    mode = session["mode"]

    if mode == "test" and current_word_index >= session["total_questions"]:
        raise HTTPException(status_code=400, detail="No more words in this test session.")
    
    # For learning mode, we might generate new words if needed
    expected_word = session["words_for_session"][current_word_index]

    is_correct = (answer.user_answer == expected_word["meaning"])
    if is_correct:
        session["correct_answers"] += 1

    session["word_index"] += 1

    # Check if more words need to be generated for learning mode
    if mode == "learning" and session["word_index"] >= len(session["words_for_session"]):
        user_profile = user_profiles[user_name]
        new_words = generate_words_with_ai(user_profile["level"], user_profile["goal"])
        session["words_for_session"].extend(new_words)
        session["total_questions"] += len(new_words) # Update total questions for learning mode

    response = {
        "is_correct": is_correct,
        "correct_meaning": expected_word["meaning"],
        "feedback": "正解！" if is_correct else f"不正解。正解は「{expected_word['meaning']}」でした。",
        "explanation": expected_word.get("explanation", "解説はありません。"), # AIによる解説を追加
        "current_score": f"{session['correct_answers']}/{session['total_questions']}"
    }

    session_finished = False
    if mode == "test" and session["word_index"] >= session["total_questions"]:
        session_finished = True
    elif mode == "learning" and session["word_index"] >= len(session["words_for_session"]):
        # In learning mode, we continuously generate words, so session only finishes if explicitly ended
        # If we reach here, it means new words were not generated, or there are no more words to generate.
        # This case should ideally not be reached if generate_words_with_ai always provides words.
        # However, to prevent IndexError, we should ensure session_finished is True if no more words.
        session_finished = True # This will prevent the IndexError if no new words are added.

    if session_finished:
        accuracy_percentage = (session["correct_answers"] / session["total_questions"]) * 100
        response["session_finished"] = True
        response["final_accuracy"] = accuracy_percentage
        response["message"] = "学習セッションが終了しました！"
    else:
        next_word = session["words_for_session"][session["word_index"]]
        response["next_word"] = next_word["word"]
        response["next_options"] = next_word["options"] # Pass options for the next word

    return response

@app.post("/learn/end_learning_session")
def end_learning_session(user_name: str):
    if user_name not in current_learning_sessions:
        raise HTTPException(status_code=400, detail="No active learning session for this user.")
    
    session = current_learning_sessions[user_name]
    if session["mode"] != "learning":
        raise HTTPException(status_code=400, detail="This endpoint is only for learning mode sessions.")

    accuracy_percentage = 0
    if session["total_questions"] > 0: # Avoid division by zero if no questions were answered
        accuracy_percentage = (session["correct_answers"] / session["total_questions"]) * 100

    del current_learning_sessions[user_name] # Clear the session

    return {
        "message": "学習セッションを終了しました。",
        "final_accuracy": accuracy_percentage,
        "correct_answers": session["correct_answers"],
        "total_questions": session["total_questions"]
    }
