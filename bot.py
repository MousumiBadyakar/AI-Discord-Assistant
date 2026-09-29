from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

import discord
from agent import agent
from langchain.messages import HumanMessage


# -----------------------------
# Discord Setup
# -----------------------------

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# -----------------------------
# Send Long Messages
# -----------------------------

async def send_long_message(channel, content):
    for i in range(0, len(content), 1900):
        await channel.send(content[i:i + 1900])


# -----------------------------
# Message Event
# -----------------------------

@client.event
async def on_message(message):

    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    async with message.channel.typing():

        content = message.content

        # Remove old generated image before processing
        if os.path.exists("generated_image.png"):
            os.remove("generated_image.png")

        try:

            # Run the synchronous LangChain agent
            # in a separate thread so Discord doesn't freeze
            response = await asyncio.to_thread(
                agent.invoke,
                {
                    "messages": [
                        HumanMessage(content=content)
                    ]
                },
                config={
                    "configurable": {
                        "message": message
                    }
                }
            )

            # Check whether image was generated
            if os.path.exists("generated_image.png"):

                await message.channel.send(
                    file=discord.File("generated_image.png")
                )

                # Remove image after sending
                os.remove("generated_image.png")

            else:

                # Get final agent response
                agent_message = response["messages"][-1].content

                # Handle different LangChain content formats
                if isinstance(agent_message, list):

                    text_parts = []

                    for item in agent_message:
                        if isinstance(item, dict):
                            if "text" in item:
                                text_parts.append(item["text"])
                        elif isinstance(item, str):
                            text_parts.append(item)

                    agent_message = "\n".join(text_parts)

                # Send normal response
                await send_long_message(
                    message.channel,
                    agent_message
                )

        except Exception as e:

            print("Error:", repr(e))

            await message.channel.send(
                "Sorry, I couldn't process that request right now. Please try again."
            )


# -----------------------------
# Start Bot
# -----------------------------

client.run(
    token=os.getenv("DISCORD_API_KEY")
)