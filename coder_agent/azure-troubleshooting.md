# Alternative Azure Web App Settings
# Try these if the first attempt fails

## Option 1: Different Name
Name: github-agent-$(date +%s)  # This adds timestamp for uniqueness
Example: github-agent-1659312345

## Option 2: Different Region
Instead of East US, try:
- West US 2
- Central US
- West Europe

## Option 3: Different Runtime
Instead of Python 3.10, try:
- Python 3.9
- Python 3.11

## Option 4: Free Tier First
Start with Free F1 tier, then upgrade later:
- SKU: Free F1
- Memory: 1 GB
- Compute: Shared

## Option 5: Use Existing Resource Group
If creating new RG fails, try using an existing one from the dropdown.
