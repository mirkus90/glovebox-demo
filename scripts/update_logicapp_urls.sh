#!/bin/bash

# Script to retrieve Logic Apps trigger URLs and update Container App environment variables
# Run this script after deployment to populate the Logic Apps URLs in the container app

set -e

echo "Updating Logic Apps trigger URLs in Container App..."

# Get environment values
RESOURCE_GROUP_NAME=$(azd env get-values | grep "AZURE_RESOURCE_GROUP" | cut -d'=' -f2 | tr -d '"')
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

if [ -z "$RESOURCE_GROUP_NAME" ]; then
    echo "Error: Could not find AZURE_RESOURCE_GROUP in environment values"
    exit 1
fi

echo "Resource Group: $RESOURCE_GROUP_NAME"

# Get Logic Apps
LOGIC_APPS=$(az logicapp list --resource-group "$RESOURCE_GROUP_NAME" --query "[].{name:name, id:id}" -o json)

if [ "$(echo "$LOGIC_APPS" | jq 'length')" -eq 0 ]; then
    echo "Warning: No Logic Apps found in resource group $RESOURCE_GROUP_NAME"
    exit 0
fi

echo "Found Logic Apps:"
echo "$LOGIC_APPS" | jq -r '.[].name' | sed 's/^/  - /'

# Function to get trigger URL
get_trigger_url() {
    local logic_app_name="$1"
    local trigger_name="$2"
    local resource_group="$3"
    
    local url
    url=$(az rest --method post \
        --url "https://management.azure.com/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$resource_group/providers/Microsoft.Logic/workflows/$logic_app_name/triggers/$trigger_name/listCallbackUrl?api-version=2016-06-01" \
        --query "value" -o tsv 2>/dev/null || echo "")
    
    echo "$url"
}

# Get Container App name
CONTAINER_APP_NAME=$(az containerapp list --resource-group "$RESOURCE_GROUP_NAME" --query "[?contains(name, 'backend')].{name:name}" -o tsv)

if [ -z "$CONTAINER_APP_NAME" ]; then
    echo "Error: Could not find backend container app in resource group $RESOURCE_GROUP_NAME"
    exit 1
fi

echo "Container App: $CONTAINER_APP_NAME"

# Map Logic App names to trigger URLs
declare -A TRIGGER_URLS

while IFS= read -r app_info; do
    app_name=$(echo "$app_info" | jq -r '.name')
    
    # Determine trigger name and environment variable based on Logic App name
    if [[ "$app_name" == *"append-file-content"* ]]; then
        trigger_name="appendFileContent"
        env_var="NOTEPAD_APPEND_FILE_CONTENT_API_URL"
    elif [[ "$app_name" == *"get-file-name"* ]]; then
        trigger_name="getFileName"
        env_var="NOTEPAD_GET_FILE_NAME_API_URL"
    elif [[ "$app_name" == *"replace-file-content"* ]]; then
        trigger_name="replaceFileContent"
        env_var="NOTEPAD_REPLACE_FILE_CONTENT_API_URL"
    elif [[ "$app_name" == *"create-task"* ]]; then
        trigger_name="createTask"
        env_var="TODOLIST_CREATE_TASK_API_URL"
    else
        echo "Warning: Unknown Logic App: $app_name"
        continue
    fi
    
    echo "Getting trigger URL for $app_name/$trigger_name..."
    trigger_url=$(get_trigger_url "$app_name" "$trigger_name" "$RESOURCE_GROUP_NAME")
    
    if [ -n "$trigger_url" ]; then
        TRIGGER_URLS["$env_var"]="$trigger_url"
        echo "  $env_var = $trigger_url"
    else
        echo "Warning: Failed to get trigger URL for $app_name"
    fi
done < <(echo "$LOGIC_APPS" | jq -c '.[]')

if [ ${#TRIGGER_URLS[@]} -eq 0 ]; then
    echo "Warning: No trigger URLs were retrieved"
    exit 1
fi

# Update Container App environment variables
echo "Updating Container App environment variables..."

for env_var in "${!TRIGGER_URLS[@]}"; do
    url="${TRIGGER_URLS[$env_var]}"
    echo "Setting $env_var..."
    
    if az containerapp update --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP_NAME" --set-env-vars "$env_var=$url" --output none; then
        echo "Updated $env_var"
    else
        echo "Error: Failed to update $env_var"
    fi
done

echo "Logic Apps trigger URLs have been updated in the Container App!"
echo "The container app will restart automatically to pick up the new environment variables."
