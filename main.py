import streamlit as st
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OPENAI_API_KEY not found in environment variables!")
    st.stop()

# Initialize Streamlit state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "language" not in st.session_state:
    st.session_state.language = "en"  # Default language: English

if "tool_logs" not in st.session_state:
    st.session_state.tool_logs = []

# Language toggle
st.sidebar.title("🌐 Language")
if st.sidebar.button("Switch to Russian" if st.session_state.language == "en" else "Переключить на английский"):
    st.session_state.language = "ru" if st.session_state.language == "en" else "en"
st.sidebar.markdown(f"**Current:** {'English' if st.session_state.language == 'en' else 'Русский'}")

# Helper for language-based strings
def get_text(key):
    texts = {
        "en": {
            "title": "🤖 LangChain Chatbot with Tools",
            "input": "Type your message...",
            "greeting_tool": "Useful for greeting a user",
            "calc_tool": "Useful for performing basic arithmetic calculations with numbers",
            "system": "You are a helpful assistant. You can use tools if needed.",
        },
        "ru": {
            "title": "🤖 Чат-бот LangChain с инструментами",
            "input": "Введите ваше сообщение...",
            "greeting_tool": "Полезно для приветствия пользователя",
            "calc_tool": "Полезно для выполнения арифметических вычислений с числами",
            "system": "Вы полезный помощник. Вы можете использовать инструменты при необходимости.",
        }
    }
    return texts[st.session_state.language][key]

# Display title
st.title(get_text("title"))

# Define tools with language-specific descriptions
@tool
def calculator(a: float, b: float) -> str:
    """Perform basic arithmetic"""
    log_tool_call(f"Calculator tool called with a={a}, b={b}")
    return f"The sum of {a} and {b} is {a + b}" if st.session_state.language == "en" else f"Сумма {a} и {b} равна {a + b}"

@tool
def say_hello(name: str) -> str:
    """Say hello"""
    log_tool_call(f"Say Hello tool called with name={name}")
    return f"Hello {name}, I hope you are well today" if st.session_state.language == "en" else f"Привет {name}, надеюсь, у тебя всё хорошо"

def log_tool_call(message: str):
    st.session_state.tool_logs.append(message)

tools = [calculator, say_hello]

# Chat model
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=openai_api_key
)

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", get_text("system")),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

# Agent setup
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Display chat messages using native UI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt_text := st.chat_input(get_text("input")):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    with st.chat_message("user"):
        st.markdown(prompt_text)

    # Build chat history for agent
    chat_history = []
    for m in st.session_state.messages[:-1]:
        if m["role"] == "user":
            chat_history.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            chat_history.append(AIMessage(content=m["content"]))

    # Get assistant reply
    try:
        result = agent_executor.invoke({
            "input": prompt_text,
            "chat_history": chat_history
        })
        reply = result["output"]
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    # Show assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# Show tool usage
if st.session_state.tool_logs:
    st.subheader("🔧 Tool Calls" if st.session_state.language == "en" else "🔧 Вызовы инструментов")
    for log in st.session_state.tool_logs:
        st.info(log)
