import logging
import os
from pathlib import Path

from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from agents.ragtools import attach_rag_tools
from agents.machine_tools import attach_machine_tools
from agents.calculator_tools import attach_calculator_tools
from agents.notepad_tools import attach_notepad_tools
from agents.todolist_tools import attach_todolist_tools
from rtmt import RTMiddleTier
from speech_service import get_speech_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voiceassistant")

async def create_app():
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
        load_dotenv()

    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    credential = None
    if not llm_key or not search_key:
        # IMPORTANT: if you are running this app in production, you must not set the AZURE_TENANT_ID environment variable.
        if (tenant_id := os.environ.get("AZURE_TENANT_ID")) and not os.environ.get("RUNNING_IN_PRODUCTION"):
            logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
            credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
        else:
            logger.info("Using DefaultAzureCredential")
            credential = DefaultAzureCredential()
    llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
    search_credential = AzureKeyCredential(search_key) if search_key else credential
    
    app = web.Application()

    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
        )
    rtmt.system_message = """
        You are a helpful assistant helping scientists when they are working in a lab using a glovebox machine. When asking to retrieve data about an experiment, only answer questions based on information you searched in the knowledge base, accessible with the 'search' tool. 
        You are allowed to answer generic questions *only* if they are related to chemistry, like questions about the density of a substance or the boiling point of a compound.
        The user is listening to answers with audio, so it's *super* important that answers are as short as possible, a single sentence if at all possible. Talk slowly.
        Never read file names or source names or keys out loud. 
        Always use the following step-by-step instructions to respond: 
        1. Always use the 'search' tool when the user asks for experiments data. 
        2. Always use the 'report_grounding' tool to report the source of information from the knowledge base.
        3. Always use the 'calculator' tools to perform arithmetic operations. Always provide the result of the operation. 
        4. Always use the 'machine' tools to answer questions about the Junior machine, like its status or temperature, or to set parameters of the machine.
        5. Always use the 'notepad' tools when the user asks to save a note or modify a file, for example when the user takes a sample on the Glovebox and needs to update the corresponding file.
        6. Always use the 'todolist' tools when the user asks to create a task, a to-do list or a reminder, for example when the user asks to create a task to perform an experiment.
        7. Produce an answer that's as short as possible. If the answer isn't in the knowledge base, say you don't know.
    """.strip()

    # attach RAG agent
    attach_rag_tools(rtmt,
        credentials=search_credential,
        search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
        search_index=os.environ.get("AZURE_SEARCH_INDEX"),
        semantic_configuration=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION") or None,
        identifier_field=os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD") or "chunk_id",
        content_field=os.environ.get("AZURE_SEARCH_CONTENT_FIELD") or "chunk",
        embedding_field=os.environ.get("AZURE_SEARCH_EMBEDDING_FIELD") or "text_vector",
        title_field=os.environ.get("AZURE_SEARCH_TITLE_FIELD") or "title",
        use_vector_query=(os.environ.get("AZURE_SEARCH_USE_VECTOR_QUERY") == "true") or True
        )

    # attach Machine agent
    attach_machine_tools(rtmt)

    # attach Calculator agent
    attach_calculator_tools(rtmt)

    # attach Notepad agent
    attach_notepad_tools(rtmt)

    # attach ToDoList agent
    attach_todolist_tools(rtmt)

    rtmt.attach_to_app(app, "/realtime")

    current_directory = Path(__file__).parent
    app.add_routes([
        web.get('/', lambda _: web.FileResponse(current_directory / 'static/index.html')),
        web.get('/speech/token', get_speech_token)])
    app.router.add_static('/', path=current_directory / 'static', name='static')
    
    return app

if __name__ == "__main__":
    host = "localhost"
    port = 8765
    web.run_app(create_app(), host=host, port=port)
