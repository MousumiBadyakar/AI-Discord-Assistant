from dotenv import load_dotenv
import os
import discord

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from huggingface_hub import InferenceClient
from langchain.agents import create_agent
from langchain.tools import tool,ToolRuntime
from tavily import TavilyClient
from langchain.messages import HumanMessage

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
hug_client = InferenceClient(api_key=os.getenv("HF_API_KEY"))

@tool
def generateImage(prompt: str,runTime:ToolRuntime):
    """Generate an image from the given prompt using Hugging Face."""

    image = hug_client.text_to_image(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-schnell"
    )

    config = runTime.config.get("configurable")
    message = config.get("message")

    image_path = "generated_image.png"
    image.save(image_path)

    return image_path


@tool
def surfInterNet(query:str):
    """Use this tool to surf internet and get latest information"""

    result = tavily_client.search(query=query)

    return str(result)

model = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
agent = create_agent(model=model,tools=[surfInterNet,generateImage],system_prompt="""Provide clean out to the user""")