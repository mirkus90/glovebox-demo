@description('The environment name prefix for resource naming')
param environmentName string

@description('The location for Logic Apps')
param location string = resourceGroup().location

@description('Tags to be applied to all resources')
param tags object = {}

@description('The resource token for unique naming')
param resourceToken string

// Load the Logic App definitions
var appendFileContentDefinition = loadJsonContent('../../logicapps/append_file_content.json')
var getFileNameDefinition = loadJsonContent('../../logicapps/get_file_name.json')
var replaceFileContentDefinition = loadJsonContent('../../logicapps/replace_file_content.json')
var createTaskDefinition = loadJsonContent('../../logicapps/create_task.json')

// Create OneDrive for Business connection
module oneDriveConnection 'logicapp-connection.bicep' = {
  name: 'onedrive-connection'
  params: {
    connectionName: 'onedriveforbusiness-${resourceToken}'
    location: location
    displayName: 'OneDrive for Business Connection'
    tags: tags
  }
}

// Create Google Tasks connection
module googleTasksConnection 'googletasks-connection.bicep' = {
  name: 'googletasks-connection'
  params: {
    connectionName: 'googletasks-${resourceToken}'
    location: location
    displayName: 'Google Tasks Connection'
    tags: tags
  }
}

// Create Logic Apps
module appendFileContentLogicApp 'logicapp-multi-connection.bicep' = {
  name: 'append-file-content-logicapp'
  params: {
    name: '${environmentName}-append-file-content-${resourceToken}'
    location: location
    definition: appendFileContentDefinition.definition
    oneDriveConnectionId: oneDriveConnection.outputs.connectionId
    oneDriveConnectionName: oneDriveConnection.outputs.connectionName
    triggerName: 'appendFileContent'
    tags: tags
  }
}

module getFileNameLogicApp 'logicapp-multi-connection.bicep' = {
  name: 'get-file-name-logicapp'
  params: {
    name: '${environmentName}-get-file-name-${resourceToken}'
    location: location
    definition: getFileNameDefinition.definition
    oneDriveConnectionId: oneDriveConnection.outputs.connectionId
    oneDriveConnectionName: oneDriveConnection.outputs.connectionName
    triggerName: 'getFileName'
    tags: tags
  }
}

module replaceFileContentLogicApp 'logicapp-multi-connection.bicep' = {
  name: 'replace-file-content-logicapp'
  params: {
    name: '${environmentName}-replace-file-content-${resourceToken}'
    location: location
    definition: replaceFileContentDefinition.definition
    oneDriveConnectionId: oneDriveConnection.outputs.connectionId
    oneDriveConnectionName: oneDriveConnection.outputs.connectionName
    triggerName: 'replaceFileContent'
    tags: tags
  }
}

module createTaskLogicApp 'logicapp-multi-connection.bicep' = {
  name: 'create-task-logicapp'
  params: {
    name: '${environmentName}-create-task-${resourceToken}'
    location: location
    definition: createTaskDefinition.definition
    googleTasksConnectionId: googleTasksConnection.outputs.connectionId
    googleTasksConnectionName: googleTasksConnection.outputs.connectionName
    triggerName: 'createTask'
    tags: tags
  }
}

// Outputs
@description('OneDrive connection information')
output oneDriveConnection object = {
  id: oneDriveConnection.outputs.connectionId
  name: oneDriveConnection.outputs.connectionName
}

@description('Google Tasks connection information')
output googleTasksConnection object = {
  id: googleTasksConnection.outputs.connectionId
  name: googleTasksConnection.outputs.connectionName
}

@description('Logic App information')
output logicApps object = {
  appendFileContent: {
    id: appendFileContentLogicApp.outputs.id
    name: appendFileContentLogicApp.outputs.name
    logicAppResource: appendFileContentLogicApp.outputs.logicAppResource
  }
  getFileName: {
    id: getFileNameLogicApp.outputs.id
    name: getFileNameLogicApp.outputs.name
    logicAppResource: getFileNameLogicApp.outputs.logicAppResource
  }
  replaceFileContent: {
    id: replaceFileContentLogicApp.outputs.id
    name: replaceFileContentLogicApp.outputs.name
    logicAppResource: replaceFileContentLogicApp.outputs.logicAppResource
  }
  createTask: {
    id: createTaskLogicApp.outputs.id
    name: createTaskLogicApp.outputs.name
    logicAppResource: createTaskLogicApp.outputs.logicAppResource
  }
}

@description('Logic App trigger URLs - these need to be retrieved post-deployment using Azure CLI')
output triggerUrls object = {
  appendFileContent: '${environment().resourceManager}${appendFileContentLogicApp.outputs.id}/triggers/appendFileContent/listCallbackUrl?api-version=2016-06-01'
  getFileName: '${environment().resourceManager}${getFileNameLogicApp.outputs.id}/triggers/getFileName/listCallbackUrl?api-version=2016-06-01'
  replaceFileContent: '${environment().resourceManager}${replaceFileContentLogicApp.outputs.id}/triggers/replaceFileContent/listCallbackUrl?api-version=2016-06-01'
  createTask: '${environment().resourceManager}${createTaskLogicApp.outputs.id}/triggers/createTask/listCallbackUrl?api-version=2016-06-01'
}
