@description('The name of the API connection')
param connectionName string

@description('The location of the API connection')
param location string = resourceGroup().location

@description('The display name of the API connection')
param displayName string = 'Google Tasks'

@description('Tags to be applied to the resource')
param tags object = {}

resource googleTasksConnection 'Microsoft.Web/connections@2016-06-01' = {
  name: connectionName
  location: location
  tags: tags
  properties: {
    displayName: displayName
    api: {
      id: subscriptionResourceId('Microsoft.Web/locations/managedApis', location, 'googletasks')
    }
    parameterValues: {}
  }
}

@description('The resource ID of the API connection')
output connectionId string = googleTasksConnection.id

@description('The name of the API connection')
output connectionName string = googleTasksConnection.name
