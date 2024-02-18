import chainlit as cl
import sys
import os
print(os.getcwd())
from ephemerear.EphemerEar import EphemerEar

BOT_PATH = '/Users/donalphipps/Documents/aiphoria/'
sys.path.append(BOT_PATH)

ee = EphemerEar('donbot.yaml')

@cl.on_message
async def main(message: cl.Message):
    response = ee.gpt_chat(message.content)
    # Send a response back to the user
    await cl.Message(
        content=response,
    ).send()
