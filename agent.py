from dotenv import load_dotenv
import os

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from huggingface_hub import InferenceClient
from langchain.agents import create_agent
from langchain.tools import tool
from tavily import TavilyClient


# -----------------------------
# API Clients
# -----------------------------

tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

hug_client = InferenceClient(
    api_key=os.getenv("HF_API_KEY")
)


# -----------------------------
# Image Generation Tool
# -----------------------------

@tool
def generateImage(prompt: str):
    """Generate an image from the given prompt using Hugging Face FLUX."""

    image = hug_client.text_to_image(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-schnell"
    )

    image_path = "generated_image.png"
    image.save(image_path)

    return image_path


# -----------------------------
# Web Search Tool
# -----------------------------

@tool
def surfInterNet(query: str):
    """Search the internet for current or latest information."""

    result = tavily_client.search(
        query=query
    )

    return str(result)


# -----------------------------
# Gemini Model
# -----------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite"
)


# -----------------------------
# LangChain Agent
# -----------------------------

agent = create_agent(
    model=model,
    tools=[
        surfInterNet,
        generateImage
    ],
    system_prompt="""
You are Moxi, an AI assistant running inside Discord.

You have access to two tools:

1. surfInterNet
   - Use this when the user asks for current information,
     latest news, recent events, or information that requires
     searching the internet.

2. generateImage
   - Use this whenever the user asks you to create, generate,
     or make an image.

IMPORTANT:
- When the user asks for an image, ALWAYS call the generateImage tool.
- Do NOT output JSON describing an image-generation action.
- Do NOT output tool-call instructions as text.
- Actually use the generateImage tool.
- After the image is generated, give a very short response such as:
  "Done! I've generated the image."
- Keep normal answers concise and suitable for Discord.
"""
)