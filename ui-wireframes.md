# UI Wireframes & Component Specifications

## 1. Application Layout

### 1.1 Main Navigation
```
+------------------------------------------------------------------+
| [Logo] RFP RAG System          [Upload] [Query] [Help] [Profile] |
+------------------------------------------------------------------+
|                                                                  |
|                        [Main Content Area]                       |
|                                                                  |
+------------------------------------------------------------------+
| © 2025 Company Name | Privacy Policy | Terms of Service         |
+------------------------------------------------------------------+
```

## 2. Upload Page

### 2.1 Initial Upload View
```
+------------------------------------------------------------------+
| Upload Documents                                                 |
+------------------------------------------------------------------+
| Select Document Type:                                            |
| ( ) RFP Document                                                 |
| ( ) Application Documentation                                    |
|                                                                  |
| +------------------------------------------------------------+  |
| |                                                            |  |
| |           [Upload Icon]                                    |  |
| |                                                            |  |
| |     Drag and drop files here or click to browse           |  |
| |                                                            |  |
| |     Supported formats: Excel (.xlsx), PDF, DOCX           |  |
| |     Maximum file size: 50MB                                |  |
| |                                                            |  |
| +------------------------------------------------------------+  |
|                                                                  |
| Recent Uploads:                                                  |
| +------------------------------------------------------------+  |
| | File Name          | Type | Status      | Date    | Action |  |
| | ABC_Bank_RFP.xlsx  | RFP  | Completed   | 7/1/25  | View  |  |
| | Security_Guide.pdf | Doc  | Processing  | 7/1/25  | ---   |  |
| +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

### 2.2 RFP Column Mapping View
```
+------------------------------------------------------------------+
| Map Excel Columns - ABC_Bank_RFP.xlsx                           |
+------------------------------------------------------------------+
| Map your Excel columns to our standard fields:                  |
|                                                                  |
| Excel Column          →    Standard Field                       |
| +-----------------+       +------------------------+            |
| | Product Name    | ----> | Product               v|            |
| | Requirement Des | ----> | Requirement           v|            |
| | Priority        | ----> | Requirement Category  v|            |
| | Our Response    | ----> | Response Category     v|            |
| | Effort          | ----> | Effort Required       v|            |
| | Notes           | ----> | Comments              v|            |
| +-----------------+       +------------------------+            |
|                                                                  |
| □ Save this mapping as a template                               |
| Template Name: [_________________________]                      |
|                                                                  |
| Preview (first 5 rows):                                          |
| +------------------------------------------------------------+  |
| | Product | Requirement        | Response Category | ...     |  |
| | MLC     | Multi-factor auth  | Readily Available | ...     |  |
| | MLC     | SSO integration    | Configuration     | ...     |  |
| +------------------------------------------------------------+  |
|                                                                  |
| [Back] [Skip Preview] [Confirm & Process]                       |
+------------------------------------------------------------------+
```

### 2.3 Documentation Metadata Form
```
+------------------------------------------------------------------+
| Upload Documentation                                             |
+------------------------------------------------------------------+
| File: Security_Guidelines_v2.pdf                                |
|                                                                  |
| * Document Name: [Security Guidelines v2___________]            |
|                                                                  |
| * Related Product: [________________________] [+Add]            |
|   [EV7 x] [CEV6 x]                                             |
|                                                                  |
| Submodule: [GAPI_____________________]                          |
|                                                                  |
| * Document Type: [White Paper            v]                     |
|                                                                  |
| Tags (comma-separated):                                          |
| [security, authentication, best-practices__________]            |
|                                                                  |
| Description:                                                     |
| +--------------------------------------------------+            |
| | Comprehensive security guidelines for EV7        |            |
| | implementation including authentication...        |            |
| +--------------------------------------------------+            |
|                                                                  |
| [Cancel] [Upload Document]                                      |
+------------------------------------------------------------------+
```

## 3. Query Page

### 3.1 Search Interface
```
+------------------------------------------------------------------+
| Search RFP Knowledge Base                                        |
+------------------------------------------------------------------+
| +------------------------------------------------------------+  |
| | 🔍 What are the SLA requirements for MLC support?         |  |
| +------------------------------------------------------------+  |
|                                          [Search] [Clear]        |
|                                                                  |
| Filters: [Products ▼] [Response Category ▼] [Date Range ▼]     |
|                                                                  |
| Results (15 found):                              Show: [10 v]    |
| +------------------------------------------------------------+  |
| | 95% | MLC                                                  |  |
| |     | Support SLA within 4 hours for critical issues       |  |
| |     | Response: Readily Available | Effort: Low            |  |
| |     | RFP: XYZ Bank RFP 2025                              |  |
| |     | [Expand ▼]                                          |  |
| +------------------------------------------------------------+  |
| | 89% | MLC                                                  |  |
| |     | 24x7 support availability with dedicated team        |  |
| |     | Response: Configuration | Effort: Medium             |  |
| |     | RFP: ABC Bank RFP 2025                              |  |
| |     | [Expand ▼]                                          |  |
| +------------------------------------------------------------+  |
|                                                                  |
| [Load More Results]                                              |
+------------------------------------------------------------------+
```

### 3.2 Expanded Result View
```
+------------------------------------------------------------------+
| | 95% | MLC                                            [Copy] |  |
| +------------------------------------------------------------+  |
| | Full Requirement:                                          |  |
| | Support SLA within 4 hours for critical issues with       |  |
| | dedicated support team available 24x7. Must include        |  |
| | escalation matrix and quarterly review meetings.           |  |
| |                                                            |  |
| | Metadata:                                                  |  |
| | - Product: MLC                                            |  |
| | - Requirement Category: Must Have                         |  |
| | - Response Category: Readily Available                    |  |
| | - Effort Required: Low                                    |  |
| | - RFP Name: XYZ Bank RFP 2025                            |  |
| | - Bank Name: XYZ Bank                                    |  |
| | - Date: 2025-06-15                                       |  |
| | - Created By: john.doe@company.com                       |  |
| |                                                            |  |
| | Previous Remarks:                                          |  |
| | • Available from version 2.0 onwards                      |  |
| | • Standard SLA template can be customized                 |  |
| | • Quarterly reviews conducted via video conference        |  |
| |                                                            |  |
| | Related Documents:                                         |  |
| | • MLC Support Guidelines v2.1                            |  |
| | • SLA Template Document                                   |  |
| |                                                            |  |
| | [Export] [Edit] [Collapse ▲]                             |  |
| +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

## 4. Component Specifications

### 4.1 File Upload Component
- Drag-and-drop support with visual feedback
- Progress bar during upload
- File validation (type, size) before upload
- Multiple file selection support
- Cancel upload functionality

### 4.2 Column Mapping Component
- Dropdown menus for target field selection
- Visual connection lines between source and target
- Auto-suggestion based on column names
- Validation to ensure all required fields are mapped
- Template management (save/load)

### 4.3 Search Results Component
- Relevance score indicator (percentage or stars)
- Color-coded response categories
- Truncated text with "..." for long content
- Smooth expand/collapse animations
- Batch operations (export multiple)

### 4.4 Filter Component
- Multi-select dropdowns
- Date range picker
- Clear all filters option
- Show active filter count
- Save filter combinations

### 4.5 Responsive Design Breakpoints
- Desktop: 1200px and above
- Tablet: 768px to 1199px
- Mobile: Below 768px

## 5. UI States & Interactions

### 5.1 Loading States
- Skeleton screens for content loading
- Progress indicators for long operations
- Disable interactive elements during processing

### 5.2 Error States
- Inline validation messages
- Toast notifications for system errors
- Clear error recovery actions

### 5.3 Empty States
- Helpful messages when no results found
- Suggestions for improving search
- Quick actions to get started

### 5.4 Success States
- Confirmation messages for completed actions
- Visual feedback (checkmarks, color changes)
- Next step suggestions