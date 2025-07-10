#!/usr/bin/env pwsh

# Script to retrieve Logic Apps trigger URLs and update Container App environment variables
# Run this script after deployment to populate the Logic Apps URLs in the container app

# Load required assemblies for URL encoding
Add-Type -AssemblyName System.Web

Write-Host "Updating Logic Apps trigger URLs in Container App..." -ForegroundColor Green

# Get environment values
Write-Host "Getting environment values..." -ForegroundColor Cyan
$envValues = azd env get-values
$envHash = @{}
foreach ($line in $envValues) {
    if ($line -match '^([^=]+)=(.*)$') {
        $envHash[$Matches[1]] = $Matches[2].Trim('"')
    }
}

$resourceGroupName = $envHash["AZURE_RESOURCE_GROUP"]
$subscriptionId = az account show --query id -o tsv

Write-Host "Resource Group: $resourceGroupName" -ForegroundColor Yellow
Write-Host "Subscription ID: $subscriptionId" -ForegroundColor Yellow

if (-not $resourceGroupName) {
    Write-Error "Could not find AZURE_RESOURCE_GROUP in environment values"
    exit 1
}

Write-Host "Resource Group: $resourceGroupName" -ForegroundColor Yellow

# Get Logic Apps (workflows)
$logicApps = az logic workflow list --resource-group $resourceGroupName --query "[].{name:name, id:id}" -o json | ConvertFrom-Json

if (-not $logicApps -or $logicApps.Count -eq 0) {
    Write-Warning "No Logic Apps found in resource group $resourceGroupName"
    exit 0
}

Write-Host "Found $($logicApps.Count) Logic Apps:" -ForegroundColor Yellow
foreach ($app in $logicApps) {
    Write-Host "  - $($app.name)" -ForegroundColor Cyan
}

# Function to get trigger URL
function Get-LogicAppTriggerUrl {
    param(
        [string]$LogicAppName,
        [string]$TriggerName,
        [string]$ResourceGroupName
    )
    
    try {
        # Get the trigger callback URL
        $url = az rest --method post --url "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Logic/workflows/$LogicAppName/triggers/$TriggerName/listCallbackUrl?api-version=2016-06-01" --query "value" -o tsv
        return $url
    }
    catch {
        Write-Warning "Failed to get trigger URL for $LogicAppName/$TriggerName : $_"
        return $null
    }
}

# Get Container App name
$containerApps = az containerapp list --resource-group $resourceGroupName --query "[?contains(name, 'backend')].{name:name}" -o json | ConvertFrom-Json

if (-not $containerApps -or $containerApps.Count -eq 0) {
    Write-Error "Could not find backend container app in resource group $resourceGroupName"
    exit 1
}

$containerAppName = $containerApps[0].name
Write-Host "Container App: $containerAppName" -ForegroundColor Yellow

# Map Logic App names to trigger URLs
$triggerUrls = @{}

foreach ($app in $logicApps) {
    $appName = $app.name
    $triggerName = ""
      # Determine trigger name based on Logic App name
    if ($appName -like "*append-file-content*") {
        $triggerName = "appendFileContent"
        $envVar = "NOTEPAD_APPEND_FILE_CONTENT_API_URL"
    }
    elseif ($appName -like "*get-file-name*") {
        $triggerName = "getFileName" 
        $envVar = "NOTEPAD_GET_FILE_NAME_API_URL"
    }
    elseif ($appName -like "*replace-file-content*") {
        $triggerName = "replaceFileContent"
        $envVar = "NOTEPAD_REPLACE_FILE_CONTENT_API_URL"
    }
    elseif ($appName -like "*create-task*") {
        $triggerName = "createTask"
        $envVar = "TODOLIST_CREATE_TASK_API_URL"
    }
    else {
        Write-Warning "Unknown Logic App: $appName"
        continue
    }
    
    Write-Host "Getting trigger URL for $appName/$triggerName..." -ForegroundColor Cyan
    $triggerUrl = Get-LogicAppTriggerUrl -LogicAppName $appName -TriggerName $triggerName -ResourceGroupName $resourceGroupName
    
    if ($triggerUrl) {
        $triggerUrls[$envVar] = $triggerUrl
        Write-Host "  $envVar = $triggerUrl" -ForegroundColor Green
    }
    else {
        Write-Warning "Failed to get trigger URL for $appName"
    }
}

if ($triggerUrls.Count -eq 0) {
    Write-Warning "No trigger URLs were retrieved"
    exit 1
}

# Update Container App environment variables
Write-Host "Updating Container App environment variables..." -ForegroundColor Green

# Update each environment variable individually
$successCount = 0
foreach ($envVar in $triggerUrls.Keys) {
    $url = $triggerUrls[$envVar]
    # URL encode the URL to handle query string parameters safely
    $encodedUrl = [System.Web.HttpUtility]::UrlEncode($url)
    Write-Host "Setting $envVar..." -ForegroundColor Cyan
    Write-Host "Encoded URL: $encodedUrl" -ForegroundColor Gray
    
    try {
        # Update the environment variable
        $result = az containerapp update --name $containerAppName --resource-group $resourceGroupName --set-env-vars "$envVar=$encodedUrl" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Updated $envVar successfully" -ForegroundColor Green
            $successCount++
        }
        else {
            Write-Error "Failed to update $envVar. Output: $result"
        }
    }
    catch {
        Write-Error "Failed to update $envVar : $_"
    }
}

if ($successCount -eq $triggerUrls.Count) {
    Write-Host "All Logic Apps trigger URLs have been updated in the Container App" -ForegroundColor Green
    Write-Host "The container app will restart automatically to pick up the new environment variables." -ForegroundColor Yellow
    
    # Verify the update by checking the environment variables
    Write-Host "Verifying environment variables..." -ForegroundColor Cyan
    $containerAppDetails = az containerapp show --name $containerAppName --resource-group $resourceGroupName | ConvertFrom-Json
    $envVars = $containerAppDetails.properties.template.containers[0].env
    
    foreach ($envVar in $triggerUrls.Keys) {
        $foundVar = $envVars | Where-Object { $_.name -eq $envVar }
        if ($foundVar) {
            $currentValue = $foundVar.value
            if ($currentValue -like "https://prod-*") {
                Write-Host "$envVar is properly set" -ForegroundColor Green
            }
            else {
                Write-Warning "$envVar may not be properly set. Current value: $currentValue"
            }
        }
        else {
            Write-Warning "$envVar not found in container app environment variables"
        }
    }
}
else {
    Write-Warning "Only $successCount out of $($triggerUrls.Count) environment variables were updated successfully"
    exit 1
}
