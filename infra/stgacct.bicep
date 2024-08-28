@description('Storage Account type')
@allowed([
  'Premium_LRS'
  'Premium_ZRS'
  'Standard_GRS'
  'Standard_GZRS'
  'Standard_LRS'
  'Standard_RAGRS'
  'Standard_RAGZRS'
  'Standard_ZRS'
])
param storageAccountType string = 'Standard_LRS'

@description('The storage account location.')
param location string = resourceGroup().location

@description('The name of the storage account')
param storageAccountName string = 'store${uniqueString(resourceGroup().id)}'

@description('Index document name for static website')
param indexDocument string = 'index.html'

@description('Error document name for static website')
param errorDocument string = 'error.html'

resource sa 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: true
  }
}

resource staticWebsite 'Microsoft.Storage/storageAccounts/staticWebsite@2022-09-01' = {
  name: '${sa.name}-staticwebsite'
  parent: sa
  properties: {
    indexDocument: indexDocument
    error404Document: errorDocument
  }
}

output storageAccountName string = storageAccountName
output storageAccountId string = sa.id
output staticWebsiteUrl string = 'https://${storageAccountName}.z13.web.core.windows.net'
