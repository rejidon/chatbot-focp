import tkinter as tk
from tkinter import scrolledtext, messagebox
import random
import json
import logging
from datetime import datetime
from threading import Timer

# Initialize logging
logging.basicConfig(
    filename="chat_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Load data from JSON files
def load_jsonfile(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{file_path}' not found.")
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("Error", f"File '{file_path}' contains invalid JSON.")
        return {}

responses = load_jsonfile("responses.json")
questions = load_jsonfile("questions.json")

# Generate random agent name
def generate_agent_name():
    agent_names = ["Ruchi", "bnee", "Prasun", "shubham", "Pushpa"]
    return random.choice(agent_names)

agent_name = generate_agent_name()

# Time-based greeting
def timestamped_greeting():
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

response_timer = None

def re_timer():
    global response_timer
    if response_timer:
        response_timer.cancel()
    response_timer = Timer(20, auto_ask_question)
    response_timer.start()

def auto_ask_question():
    chat_type = chattype_var.get()
    if chat_type:
        question = ask_question(chat_type)
        chat_window.insert(tk.END, f"{agent_name}: {question}\n")
        logging.info(f"{agent_name}: {question}")

current_context = None

def get_response(user_input, chat_type):
    global current_context

    user_input = user_input.lower().strip()

    # Handle follow-up responses for "yes" or "no"
    if current_context:
        follow_up_responses = responses.get("follow_ups", {}).get(current_context, {})
        if user_input in ["yes", "y", "no", "n"]: # Modified to include 'y' and 'n'
            suggestions = follow_up_responses.get(user_input, []) # Use user_input as key directly
            if suggestions:
                if user_input in ["no", "n"]: # Modified to include 'n'
                    current_context = None  # Reset context for "no"
                return random.choice(suggestions)

    # Handle normal responses
    chat_responses = responses.get("keywords", {}).get(chat_type, {})
    for keyword, reply in chat_responses.items():
        if keyword in user_input:
            # Set context if the response requires follow-ups
            if "Would you like to" in reply:
                if "relaxation relief" in reply: 
                    current_context = "relaxation_technique"
                elif "dietary advice" in reply:
                    current_context = "healthy_eating" 
                elif "managing stress" in reply:
                    current_context = "stress_manage" 
                elif"mental health"in reply:
                    current_context = "mental_health_tips"
                elif "admission requirements" in reply:
                    current_context = "admission_require"
                elif "library resources" in reply:
                    current_context = "library_re"
                elif "event details " in reply:
                    current_context ="event_det"
            return reply

    # Return fallback if no keywords match
    return random.choice(responses.get("fallbacks", ["I'm not sure about that."]))

def ask_question(chat_type):
    question_list = questions.get(chat_type, [])
    if question_list:
        return random.choice(question_list)
    return "I don't have any predefined questions for this category."

# Tkinter GUI Functions
def send_message():
    global response_timer
    user_message = input_box.get()
    if not user_message.strip():
        return

    chat_type = chattype_var.get()
    if not chat_type:
        messagebox.showerror("Error", "Please select a chat type!")
        return

    # Display user message
    chat_window.insert(tk.END, f"You: {user_message}\n")
    input_box.delete(0, tk.END)

    if user_message.lower() in ["bye", "quit", "exit"]:
        bot_message = "It was nice chatting with you. Goodbye!"
        chat_window.insert(tk.END, f"{agent_name}: {bot_message}\n")
        logging.info("User ended the chat.")
        root.after(1000, root.quit)  # Wait 1 seconds before closing the application
        return

    # Get chatbot response
    bot_message = get_response(user_message, chat_type)
    chat_window.insert(tk.END, f"{agent_name}: {bot_message}\n")

    # Log conversation
    logging.info(f"User: {user_message}")
    logging.info(f"{agent_name}: {bot_message}")

    # it Reset the response timer
    re_timer()

def clear_chat():
    chat_window.delete('1.0', tk.END)
    re_timer()

def display_question():
    chat_type = chattype_var.get()
    if not chat_type:
        messagebox.showerror("Error", "Please select a chat type!")
        return

    question = ask_question(chat_type)
    chat_window.insert(tk.END, f"{agent_name}: {question}\n")
    logging.info(f"{agent_name}: {question}")
    re_timer()

# Tkinter GUI Setup
root = tk.Tk()
root.title("AI Chatbot")

# Style configurations
root.configure(bg="#f5f5f5")
root.geometry("500x600")
root.resizable(False, False)

# Header
tk.Label(root, text="AI Chatbot", font=("Helvetica", 18, "bold"), bg="#f5f5f5", fg="#333").pack(pady=10)
tk.Label(root, text=f"{timestamped_greeting()}! I'm {agent_name}. How can I assist you today?",
         font=("Helvetica", 12), wraplength=450, bg="#f5f5f5", fg="#555").pack(pady=5)

# Chat type selection
chattype_var = tk.StringVar(value="")
frame_options = tk.Frame(root, bg="#f5f5f5")
frame_options.pack(pady=5)
tk.Label(frame_options, text="Select Chat Type:", font=("Helvetica", 10), bg="#f5f5f5", fg="#333").pack(side=tk.LEFT, padx=5)
tk.Radiobutton(frame_options, text="Healthcare", variable=chattype_var, value="healthcare_advisor",
               bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
tk.Radiobutton(frame_options, text="Psychologist", variable=chattype_var, value="psychologist",
               bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
tk.Radiobutton(frame_options, text="General Inquiry", variable=chattype_var, value="general",
               bg="#f5f5f5").pack(side=tk.LEFT, padx=5)

# Chat display window
chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='normal', height=20, width=55, bg="#ffffff", fg="#333")
chat_window.pack(pady=10)
chat_window.insert(tk.END, f"{agent_name}: {timestamped_greeting()}! How can I help?\n")

# User input and buttons
input_frame = tk.Frame(root, bg="#f5f5f5")
input_frame.pack(pady=5)

input_box = tk.Entry(input_frame, width=40, font=("Arial", 12))
input_box.pack(side=tk.LEFT, padx=5)

send_button = tk.Button(input_frame, text="Send", command=send_message, bg="#4CAF50", fg="#fff", font=("Times new roman", 10, "bold"))
send_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(root, text="Clear Chat", command=clear_chat, bg="#f44336", fg="#fff", font=("Times new roman", 10, "bold"))
clear_button.pack(pady=10)

question_button = tk.Button(root, text="Ask Predefined Question", command=display_question,
                             bg="#008CBA", fg="#fff", font=("Times new roman", 11, "bold"))
question_button.pack(pady=5)

re_timer()
root.mainloop()