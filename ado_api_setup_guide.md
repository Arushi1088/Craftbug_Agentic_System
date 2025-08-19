# Azure DevOps API Setup Guide

## Method 1: Using ADO "Run Query" Feature (Recommended)

### Step 1: Get Your Query ID
1. Go to your ADO dashboard: https://office.visualstudio.com/OC/_queries/query/6c1d07cd-a5d6-4483-9627-740d04b7fba8/
2. Click "Run Query" 
3. Look at the URL - the query ID is: `6c1d07cd-a5d6-4483-9627-740d04b7fba8`

### Step 2: Create Personal Access Token (PAT)
1. Go to: https://dev.azure.com/office/_usersSettings/tokens
2. Click "New Token"
3. Set:
   - Name: "Excel Bug Analysis"
   - Organization: office
   - Expiration: 1 year
   - Scopes: 
     - ✅ Work Items (Read)
     - ✅ Queries (Read)
4. Copy the generated token (you won't see it again!)

### Step 3: Update the Configuration
Edit `ado_bug_data_integration.py` and update these values:

```python
organization = "office"  # Your ADO organization
project = "OC"          # Your ADO project  
personal_access_token = "your_pat_here"  # The token you just created
query_id = "6c1d07cd-a5d6-4483-9627-740d04b7fba8"  # Your query ID
```

### Step 4: Run the Integration
```bash
python ado_bug_data_integration.py
```

## Method 2: Manual Data Collection (If API doesn't work)

If you can't get API access, you can manually collect detailed bug data:

### Step 1: Export Basic CSV
1. From your ADO dashboard, export as CSV
2. Save as `excel_bugs_basic.csv`

### Step 2: Manually Add Details
Create a new file `excel_bugs_detailed.csv` with these columns:
```csv
ID,Title,Description,State,Priority,Severity,Tags,ReproSteps,AreaPath,IterationPath
1,"Excel save dialog not appearing","When clicking save button, dialog doesn't show","Active","High","Critical","Excel;Save;UI","1. Open Excel Web\n2. Create new workbook\n3. Click save button\n4. Expected: Save dialog appears\n5. Actual: No dialog shows","Office/Excel/Web","Sprint 2024.1"
```

### Step 3: Use the Enhanced CSV
The integration module will automatically detect and use the detailed CSV format.

## Method 3: Direct WIQL Query

You can also use a direct WIQL (Work Item Query Language) query:

```sql
SELECT [System.Id], [System.Title], [System.Description], [System.State], 
       [System.CreatedBy], [System.CreatedDate], [System.Tags],
       [Microsoft.VSTS.Common.Priority], [Microsoft.VSTS.Common.Severity],
       [Microsoft.VSTS.TCM.ReproSteps], [System.AreaPath], [System.IterationPath]
FROM WorkItems 
WHERE [System.WorkItemType] = 'Bug' 
  AND [System.TeamProject] = 'OC'
  AND ([System.Title] CONTAINS 'Excel' OR [System.Description] CONTAINS 'Excel' OR [System.Tags] CONTAINS 'Excel')
ORDER BY [System.CreatedDate] DESC
```

## Testing Your Setup

Run the test script to verify everything works:

```bash
python test_ado_integration.py
```

This will:
1. Test CSV import with sample data
2. Test API integration (if you provide PAT)
3. Generate analysis and prompt templates
4. Save results to JSON files

## Expected Output

After successful integration, you'll get:
- `ado_bug_analysis.json` - Detailed bug analysis
- `prompt_templates.json` - Generated prompt templates
- Console output showing bug patterns and categories

## Troubleshooting

### API Access Issues
- Verify your PAT has correct permissions
- Check organization and project names
- Ensure query ID is correct

### CSV Format Issues
- Make sure CSV has proper headers
- Check for special characters in bug descriptions
- Verify file encoding is UTF-8

### No Bugs Found
- Check if your query actually returns results in ADO
- Verify Excel-related keywords in titles/descriptions
- Try broader search terms

