#!/bin/bash

# Azure prerequisites and deployment script for Cosmos DB billing archive

echo "Logging into Azure..."
az login

echo "Creating resource group..."
az group create --name billing-rg --location eastus

echo "Deploying Bicep template (Storage + Cosmos DB)..."
az deployment group create \
  --resource-group billing-rg \
  --template-file bicep/main.bicep

echo "Creating Azure Function App..."
az functionapp create \
  --resource-group billing-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --functions-version 4 \
  --name billing-archive-func \
  --storage-account Vijay

echo "Setting application settings (sample connection strings)..."
az functionapp config appsettings set \
  --name billing-archive-func \
  --resource-group billing-rg \
  --settings \
  COSMOS_CONN='*****' \
  BLOB_CONN='*****'

echo "Setup complete. You can now publish your functions using Azure Functions Core Tools."
