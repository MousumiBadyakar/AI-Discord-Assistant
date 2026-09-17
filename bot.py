from dotenv import load_dotenv
import os

load_dotenv()

import discord
from agent import agent
from langchain.messages import HumanMessage


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    async with message.channel.typing():
        content = message.content

        response = agent.invoke(
            {"messages":[HumanMessage(content)]},
            config={"configurable":{"message":message}}
            )

        agent_message = response["messages"][-1].content[0]["text"]

        if "generated_image.png" in agent_message:
             await message.channel.send(file=discord.File("generated_image.png"))
        else:
            await message.channel.send(agent_message)


client.run(token = os.getenv("DISCORD_API_KEY"))
