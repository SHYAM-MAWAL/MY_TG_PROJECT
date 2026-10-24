# n8n Airtable Course Records Workflow Setup Guide

## Overview
This workflow fetches course records from Airtable one by one and processes them.

## Prerequisites
- Access to your n8n instance at https://n8n.shyamai.xyz
- Airtable Personal Access Token
- Airtable Base ID and Table Name

## Your Airtable Credentials
Set these in n8n credentials (do **not** commit real tokens to git):
- **Token**: your Airtable personal access token
- **Base ID**: your Airtable base ID
- **Table Name**: e.g. `Premium_Course`

## Setup Steps

### Step 1: Create Airtable Credentials in n8n

1. Log in to your n8n instance
2. Go to **Credentials** (top menu)
3. Click **Add Credential**
4. Search for **Airtable**
5. Select **Airtable Personal Access Token API**
6. Enter your Airtable personal access token
7. Name it: `Airtable Personal Access Token`
8. Click **Save**

### Step 2: Import the Workflow

1. In n8n, click **Workflows** → **Import from File**
2. Select the file: `n8n_airtable_workflow.json`
3. The workflow will be imported with all nodes

### Step 3: Configure the Workflow

1. Open the imported workflow
2. Click on the **"List All Courses"** node
3. Verify the credentials are selected (should use the credential you created)
4. Verify the settings:
   - **Base**: `appAkDWxYZHZDYvXx`
   - **Table**: `Premium_Course`
   - **Operation**: `List`
   - **Return All**: `Yes`
5. The fields to retrieve are already configured:
   - `course_title`
   - `target_url`
   - `created_at`
   - `image`

### Step 4: Test the Workflow

1. Click **Execute Workflow** button (top right)
2. The workflow will:
   - Trigger manually
   - Fetch all records from Airtable
   - Split them into individual items
   - Process each record one by one
   - Filter valid records (those with target_url)
   - Output the course data

## Workflow Structure

```
Manual Trigger
    ↓
List All Courses (Airtable)
    ↓
Split Records (Split into individual items)
    ↓
Process Each Record (Code node - extracts fields)
    ↓
Filter Valid Records (Only records with target_url)
    ↓
Output Course Data (Set node - formats output)
```

## Customization

### To Process Records Automatically on Schedule:
1. Replace **Manual Trigger** with **Schedule Trigger**
2. Set your desired schedule (e.g., daily, hourly)

### To Add More Processing:
1. Add nodes after **"Process Each Record"** to:
   - Send notifications
   - Update other systems
   - Transform data
   - etc.

### To Modify Fields Retrieved:
1. Click on **"List All Courses"** node
2. In **Options** → **Fields**, add or remove field names

## Troubleshooting

### Error: "Invalid credentials"
- Verify your Airtable token is correct
- Check that the token has access to the base and table

### Error: "Base not found"
- Verify the Base ID: `appAkDWxYZHZDYvXx`
- Ensure your token has access to this base

### Error: "Table not found"
- Verify the Table Name: `Premium_Course`
- Check for typos (case-sensitive)

### No Records Returned
- Check if there are records in your Airtable table
- Verify the table name matches exactly

## Next Steps

After the workflow is working, you can:
1. Add webhook triggers to process records on-demand
2. Add email notifications for new courses
3. Integrate with other services
4. Add data transformation logic
5. Set up error handling and retries
