@description('The name of the Logic App')
param name string

@description('The location of the Logic App')
param location string = resourceGroup().location

@description('The Logic App definition')
param definition object

@description('The connection ID for OneDrive for Business')
param oneDriveConnectionId string

@description('The connection name for OneDrive for Business')
param oneDriveConnectionName string

@description('Tags to be applied to the resource')
param tags object = {}

@description('The state of the Logic App (Enabled or Disabled)')
@allowed(['Enabled', 'Disabled'])
param state string = 'Enabled'

@description('The trigger name for callback URL generation')
param triggerName string

resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    definition: definition
    parameters: {
      '$connections': {
        value: {
          onedriveforbusiness: {
            id: subscriptionResourceId('Microsoft.Web/locations/managedApis', location, 'onedriveforbusiness')
            connectionId: oneDriveConnectionId
            connectionName: oneDriveConnectionName
          }
        }
      }
    }
    state: state
  }
}

@description('The resource ID of the Logic App')
output id string = logicApp.id

@description('The name of the Logic App')
output name string = logicApp.name

@description('The Logic App resource for reference')
output logicAppResource object = {
  id: logicApp.id
  name: logicApp.name
  triggerName: triggerName
}
