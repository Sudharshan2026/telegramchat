import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(name)

# Define the bot token (keep it secure)
TOKEN = 'BOT_API'

# Define templates
career_counselor_template = """
You are a helpful and knowledgeable career counselor. 
Your task is to guide individuals in finding the best career based on their skills, interests, and experience. 
Provide suggestions for possible career paths, discuss the job market trends, and suggest qualifications they should pursue.

Here is the conversation history:
{hicontext}
Question: {question}
Answer:
"""

general_chat_template = """
You are a friendly and conversational AI assistant. 
Feel free to engage in light-hearted conversations, provide general knowledge, and answer various questions.

Here is the conversation history:
{hicontext}
Question: {question}
Answer:
"""

# Define the models and prompts
model = OllamaLLM(model="llama3")

# Store user contexts and selected templates
user_contexts = {}
user_templates = {}

# Function to select the appropriate template
def select_template(template_name: str) -> ChatPromptTemplate:
    if template_name == 'career_counselor':
        return ChatPromptTemplate.from_template(career_counselor_template)
    elif template_name == 'general_chat':
        return ChatPromptTemplate.from_template(general_chat_template)
    else:
        return ChatPromptTemplate.from_template(general_chat_template)

# Function to handle the conversation with the selected template
async def handle_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_input = update.message.text

    # Check if the user wants to change the template
    if user_input.lower() == 'career mode':
        user_templates[chat_id] = 'career_counselor'
        await update.message.reply_text('Switched to Career Counselor mode. How can I assist you with career guidance?')
        return
    elif user_input.lower() == 'chat mode':
        user_templates[chat_id] = 'general_chat'
        await update.message.reply_text('Switched to General Chat mode. Feel free to ask me anything!')
        return

    # Get or initialize the user's template and context
    selected_template = user_templates.get(chat_id, 'general_chat')
    prompt = select_template(selected_template)
    context_history = user_contexts.get(chat_id, "")

    # Generate the AI's response using the selected template
    chain = prompt | model
    result = chain.invoke({"hicontext": context_history, "question": user_input})

    # Update the conversation history
    context_history += f"\nUser: {user_input}\nAI: {result}"
    user_contexts[chat_id] = context_history

    # Send the AI's response back to the user
    await update.message.reply_text(result)

# Command to start the bot and set the initial mode
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_templates[chat_id] = 'general_chat'
    user_contexts[chat_id] = ""
    await update.message.reply_text(
        'Welcome to the AI ChatBot! You can switch between "Career mode" and "Chat mode" anytime by typing "career mode" or "chat mode".'
    )

# Main function to start the bot
def main() -> None:
    """Start the bot."""
    # Create the Application and pass it the bot's token.
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_conversation))

    # Start the Bot
    application.run_polling()

if name == 'main':
    main()
