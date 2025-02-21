import streamlit as st
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
import bleach
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set API keys (use environment variables or Streamlit secrets for better security)
PHI_API_KEY = "phi-ztoEHu1saAmMCnQ-6AYFa0HQrxMaWOis28sbi2crATE"
GROQ_API_KEY = "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"

# Initialize the agent
search_agent = Agent(
    name="Web Agent",
    description="Agent for searching content from the web.",
    model=Groq(
        id="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY
    ),
    tools=[DuckDuckGo()],
    instructions=["Always include the sources."],
    markdown=True,
    show_tool_calls=True
)

# Streamlit interface
st.title("Web Search Agent")

# Input from user
user_query = st.text_input("Enter your query:")

# Cache the search results for performance
@st.cache_data
def get_search_results(query):
    try:
        response = search_agent.run(query)
        return response
    except Exception as e:
        logging.error(f"Error during search: {e}")
        st.error("An error occurred while processing your request. Please try again.")
        return None

def extract_urls(text):
    """Extract all URLs from the given text."""
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.findall(text)

if user_query:
    if not user_query.strip():
        st.warning("Please enter a valid query.")
    else:
        with st.spinner("Processing..."):
            response = get_search_results(user_query)

            if response:
                # Extract the textual content from the RunResponse object
                response_text = response.content if hasattr(response, 'content') else str(response)

                # Sanitize the response to remove any potentially harmful HTML/JS
                cleaned_response = bleach.clean(response_text, tags=bleach.sanitizer.ALLOWED_TAGS,
                                                attributes=bleach.sanitizer.ALLOWED_ATTRIBUTES)

                # Display the sanitized response as Markdown
                st.markdown(cleaned_response)

                # Extract and display URLs as clickable links
                urls = extract_urls(cleaned_response)
                if urls:
                    st.subheader("Generated URLs:")
                    for url in urls:
                        st.markdown(f"- [{url}]({url})")

# Additional UI enhancements
