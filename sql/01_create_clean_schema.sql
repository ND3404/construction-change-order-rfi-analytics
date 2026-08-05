CREATE TABLE projects (
    Project_ID TEXT PRIMARY KEY,
    Project_Name TEXT NOT NULL,
    Project_Type TEXT NOT NULL,
    City TEXT NOT NULL,
    State TEXT NOT NULL,
    Region TEXT NOT NULL,
    Client_Type TEXT NOT NULL,
    Contract_Type TEXT NOT NULL,
    Delivery_Method TEXT NOT NULL,
    Complexity_Level TEXT NOT NULL,
    Digital_Coordination_Level TEXT NOT NULL,
    Owner_Decision_Profile TEXT NOT NULL,
    Original_Budget REAL NOT NULL,
    Original_Contingency REAL NOT NULL,
    Planned_Start_Date TEXT NOT NULL,
    Planned_End_Date TEXT NOT NULL,
    Actual_Start_Date TEXT NOT NULL,
    Forecast_End_Date TEXT NOT NULL,
    Project_Status TEXT NOT NULL,
    Current_Phase TEXT NOT NULL,
    Project_Manager_ID TEXT NOT NULL,
    Design_Manager_ID TEXT NOT NULL,
    Change_Manager_ID TEXT NOT NULL
);

CREATE TABLE rfi_log (
    RFI_ID TEXT PRIMARY KEY,
    Project_ID TEXT NOT NULL REFERENCES projects(Project_ID),
    RFI_Number TEXT NOT NULL,
    RFI_Title TEXT NOT NULL,
    Discipline TEXT NOT NULL,
    Priority TEXT NOT NULL,
    RFI_Type TEXT NOT NULL,
    Submitted_Date TEXT NOT NULL,
    Required_Response_Date TEXT NOT NULL,
    First_Response_Date TEXT,
    Final_Response_Date TEXT,
    Closed_Date TEXT,
    RFI_Status TEXT NOT NULL,
    Submitted_By_Role TEXT NOT NULL,
    Responsible_Role TEXT NOT NULL,
    Revision_Count INTEGER NOT NULL,
    Reopen_Count INTEGER NOT NULL,
    Cost_Impact_Flag TEXT NOT NULL,
    Estimated_Cost_Impact REAL NOT NULL,
    Actual_Cost_Impact REAL NOT NULL,
    Schedule_Impact_Flag TEXT NOT NULL,
    Estimated_Schedule_Days INTEGER NOT NULL,
    Actual_Schedule_Days INTEGER NOT NULL,
    Field_Work_Affected TEXT NOT NULL,
    Drawing_Reference_Count INTEGER NOT NULL,
    Response_Quality_Rating INTEGER NOT NULL
);

CREATE TABLE change_orders (
    Change_Order_ID TEXT PRIMARY KEY,
    Project_ID TEXT NOT NULL REFERENCES projects(Project_ID),
    Change_Number TEXT NOT NULL,
    Change_Title TEXT NOT NULL,
    Change_Category TEXT NOT NULL,
    Initiating_Party TEXT NOT NULL,
    Discipline TEXT NOT NULL,
    Change_Type TEXT NOT NULL,
    Originating_Source TEXT NOT NULL,
    Identified_Date TEXT NOT NULL,
    Submitted_Date TEXT NOT NULL,
    Required_Decision_Date TEXT NOT NULL,
    First_Decision_Date TEXT,
    Approved_Date TEXT,
    Closed_Date TEXT,
    Change_Status TEXT NOT NULL,
    Submitted_Value REAL NOT NULL,
    Negotiated_Value REAL,
    Approved_Value REAL,
    Requested_Schedule_Days INTEGER NOT NULL,
    Approved_Schedule_Days INTEGER NOT NULL,
    Revision_Count INTEGER NOT NULL,
    Pricing_Status TEXT NOT NULL,
    Authorization_Type TEXT NOT NULL,
    Forecast_Incorporated_Date TEXT,
    Cost_Code_Group TEXT NOT NULL
);

CREATE TABLE workflow_events (
    Event_ID TEXT PRIMARY KEY,
    Project_ID TEXT NOT NULL REFERENCES projects(Project_ID),
    Item_Type TEXT NOT NULL,
    Item_ID TEXT NOT NULL,
    Event_Sequence INTEGER NOT NULL,
    Event_Timestamp TEXT NOT NULL,
    From_Status TEXT,
    To_Status TEXT NOT NULL,
    Action_By_Role TEXT NOT NULL,
    Assigned_To_Role TEXT,
    Event_Action TEXT NOT NULL,
    Revision_Number INTEGER NOT NULL,
    Decision_Required_Flag TEXT NOT NULL,
    Comment_Category TEXT NOT NULL
);

CREATE TABLE rfi_change_links (
    Link_ID TEXT PRIMARY KEY,
    Project_ID TEXT NOT NULL REFERENCES projects(Project_ID),
    RFI_ID TEXT NOT NULL REFERENCES rfi_log(RFI_ID),
    Change_Order_ID TEXT NOT NULL REFERENCES change_orders(Change_Order_ID),
    Link_Type TEXT NOT NULL,
    Link_Confidence TEXT NOT NULL,
    Relationship_Date TEXT NOT NULL,
    Relationship_Notes_Category TEXT NOT NULL
);

CREATE TABLE cleaning_log (
    Action_ID TEXT PRIMARY KEY,
    Table_Name TEXT NOT NULL,
    Record_ID TEXT NOT NULL,
    Field_Name TEXT NOT NULL,
    Issue_Type TEXT NOT NULL,
    Raw_Value TEXT,
    Clean_Value TEXT,
    Action TEXT NOT NULL,
    Evidence TEXT,
    Disposition TEXT NOT NULL
);

CREATE TABLE quarantine_records (
    Quarantine_ID TEXT PRIMARY KEY,
    Table_Name TEXT NOT NULL,
    Record_ID TEXT NOT NULL,
    Reason TEXT NOT NULL,
    Source_Issue TEXT NOT NULL,
    Raw_Record_JSON TEXT NOT NULL
);
