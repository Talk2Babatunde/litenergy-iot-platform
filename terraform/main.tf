resource "azurerm_resource_group" "rg" {}

resource "azurerm_storage_account" "storage" {}

resource "azurerm_eventhub_namespace" "namespace" {}

resource "azurerm_linux_function_app" "function" {}
