# Define the .env file path
$envFilePath = "app\backend\.env"

# Clear the contents of the .env file
Set-Content -Path $envFilePath -Value ""

# Append new values to the .env file
$azureOpenAiEndpoint = azd env get-value AZURE_OPENAI_ENDPOINT
$azureOpenAiRealtimeDeployment = azd env get-value AZURE_OPENAI_REALTIME_DEPLOYMENT
$azureOpenAiRealtimeVoiceChoice = azd env get-value AZURE_OPENAI_REALTIME_VOICE_CHOICE
$azureSearchEndpoint = azd env get-value AZURE_SEARCH_ENDPOINT
$azureSearchIndex = azd env get-value AZURE_SEARCH_INDEX
$azureTenantId = azd env get-value AZURE_TENANT_ID
$azureSearchSemanticConfiguration = azd env get-value AZURE_SEARCH_SEMANTIC_CONFIGURATION
$azureSearchIdentifierField = azd env get-value AZURE_SEARCH_IDENTIFIER_FIELD
$azureSearchTitleField = azd env get-value AZURE_SEARCH_TITLE_FIELD
$azureSearchContentField = azd env get-value AZURE_SEARCH_CONTENT_FIELD
$azureSearchEmbeddingField = azd env get-value AZURE_SEARCH_EMBEDDING_FIELD
$azureSearchUseVectorQuery = azd env get-value AZURE_SEARCH_USE_VECTOR_QUERY
$azureSpeechRegion = azd env get-value AZURE_SPEECH_REGION
$azureSpeechResourceId = azd env get-value AZURE_SPEECH_RESOURCE_ID
$keywordDeactivation = azd env get-value KEYWORD_DEACTIVATION
$notepadBaseUrl = azd env get-value NOTEPAD_BASE_URL

Add-Content -Path $envFilePath -Value "AZURE_OPENAI_ENDPOINT=$azureOpenAiEndpoint"
Add-Content -Path $envFilePath -Value "AZURE_OPENAI_REALTIME_DEPLOYMENT=$azureOpenAiRealtimeDeployment"
Add-Content -Path $envFilePath -Value "AZURE_OPENAI_REALTIME_VOICE_CHOICE=$azureOpenAiRealtimeVoiceChoice"
Add-Content -Path $envFilePath -Value "AZURE_SEARCH_ENDPOINT=$azureSearchEndpoint"
Add-Content -Path $envFilePath -Value "AZURE_SEARCH_INDEX=$azureSearchIndex"
Add-Content -Path $envFilePath -Value "AZURE_SEARCH_SEMANTIC_CONFIGURATION=$azureSearchSemanticConfiguration"
Add-Content -Path $envFilePath -Value "AZURE_SEARCH_IDENTIFIER_FIELD=$azureSearchIdentifierField"
Add-Content -Path $envFilePath -Value "AZURE_SEARCH_TITLE_FIELD=$azureSearchTitleField"
Add-Content -Path $envFilePath -Value "AZURE_SEARCH_CONTENT_FIELD=$azureSearchContentField"
Add-Content -Path $envFilePath -Value "AZURE_SEARCH_EMBEDDING_FIELD=$azureSearchEmbeddingField"
Add-Content -Path $envFilePath -Value "AZURE_SEARCH_USE_VECTOR_QUERY=$azureSearchUseVectorQuery"
Add-Content -Path $envFilePath -Value "AZURE_TENANT_ID=$azureTenantId"
Add-Content -Path $envFilePath -Value "AZURE_SPEECH_REGION=$azureSpeechRegion"
Add-Content -Path $envFilePath -Value "AZURE_SPEECH_RESOURCE_ID=$azureSpeechResourceId"
Add-Content -Path $envFilePath -Value "KEYWORD_DEACTIVATION=$keywordDeactivation"
Add-Content -Path $envFilePath -Value "NOTEPAD_BASE_URL=$notepadBaseUrl"

# Note: Logic Apps trigger URLs need to be manually retrieved and added after deployment
# You can get them from the Azure portal or use Azure CLI to retrieve the callback URLs
Add-Content -Path $envFilePath -Value "NOTEPAD_REPLACE_FILE_CONTENT_API_URL="
Add-Content -Path $envFilePath -Value "NOTEPAD_GET_FILE_NAME_API_URL="
Add-Content -Path $envFilePath -Value "NOTEPAD_APPEND_FILE_CONTENT_API_URL="
Add-Content -Path $envFilePath -Value "TODOLIST_CREATE_TASK_API_URL="