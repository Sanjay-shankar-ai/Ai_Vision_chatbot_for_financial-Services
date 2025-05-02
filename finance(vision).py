import streamlit as st
import base64
from groq import Groq

st.set_page_config(layout="wide")

# Function to encode the image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Initialize Groq client
client = Groq()

# Define the prompt template
PROMPT_TEMPLATE = """
You are an expert at reading ATM receipts and transaction slips.
The uploaded image contains a bank transaction response code or error code.
Your job is:
- Carefully read the code from the receipt image.
- Identify the meaning of the code.
- Provide a simple explanation that a normal customer can understand.
- If the code is unknown, say "This code is not recognized commonly, please contact your bank."

Here are some examples of common ATM response codes:
- 000: Transaction Successful
- 051: Insufficient Funds
- 055: Incorrect PIN
- 089: Authorization Declined
- 097: Cash dispenser error, cash not dispensed properly
- 123: Card expired
- 902: Bank network unavailable

Always prioritize explaining clearly and in simple language.
Now based on the uploaded receipt, help the user.
"""

# Streamlit application
st.title("AI Vision Chatbot for ATM Response")
st.caption("Visionary AI Assistant - Powered by Llama 3.1")

# Session state to store conversation history and base64 image
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'base64_image' not in st.session_state:
    st.session_state.base64_image = None  # To store the image

# File uploader for image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# Handle image upload or removal
if uploaded_file is not None:
    # Encode the uploaded image and store it in session state
    st.session_state.base64_image = encode_image(uploaded_file)
    # Display the uploaded image in small size
    st.image(uploaded_file, width=200)  # Adjust width as needed
else:
    # If no image is uploaded or the image is removed, reset image and conversation history
    st.session_state.base64_image = None
    st.session_state.conversation_history = []
    st.info("No image uploaded. Upload an image to start a conversation.")

# Input box for user message
user_message = st.text_input("Enter your message:")

# Only proceed if there's a user message and an image in session state
if user_message and st.session_state.base64_image:
    # Prepare chat message with system prompt + user query + image
    messages = [
        {"role": "system", "content": PROMPT_TEMPLATE},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_message},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{st.session_state.base64_image}",
                    },
                },
            ],
        }
    ]

    # Get the chat completion response
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )

    # Store user message and bot response in conversation history
    bot_response = chat_completion.choices[0].message.content
    st.session_state.conversation_history.append({"user": user_message, "bot": bot_response})

    # Display the response
    st.subheader("Response:")
    st.write(bot_response)

# Display past conversations with custom styling if there's any
if st.session_state.conversation_history:
    st.subheader("Conversation History:")
    for conversation in st.session_state.conversation_history:
        # Display the user's message
        st.markdown(f"<div style='background-color: #DCF8C6; color: black; padding: 10px; border-radius: 10px; margin-bottom: 5px;'>"
                    f"<strong>You:</strong> {conversation['user']}</div>", unsafe_allow_html=True)

        # Display the AI's response
        st.markdown(f"<div style='background-color: #E3F2FD; color: black; padding: 10px; border-radius: 10px; margin-bottom: 5px;'>"
                    f"<strong>AI:</strong> {conversation['bot']}</div>", unsafe_allow_html=True)
