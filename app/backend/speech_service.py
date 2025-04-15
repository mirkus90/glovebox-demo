import os
import azure.cognitiveservices.speech as speechsdk
from azure.identity import DefaultAzureCredential
from aiohttp import web

async def get_speech_token(request):
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        return web.json_response({"token": token.token, "region": os.environ["AZURE_SPEECH_REGION"], "resource_id": os.environ["AZURE_SPEECH_RESOURCE_ID"]})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)