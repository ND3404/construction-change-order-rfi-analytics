-- Process-phase validation queries
SELECT 'Projects duplicate IDs' AS check_name, COUNT(*) AS failures
FROM (SELECT Project_ID FROM projects GROUP BY Project_ID HAVING COUNT(*) > 1)
UNION ALL
SELECT 'RFI orphan projects', COUNT(*) FROM rfi_log r LEFT JOIN projects p ON p.Project_ID=r.Project_ID WHERE p.Project_ID IS NULL
UNION ALL
SELECT 'Change orphan projects', COUNT(*) FROM change_orders c LEFT JOIN projects p ON p.Project_ID=c.Project_ID WHERE p.Project_ID IS NULL
UNION ALL
SELECT 'Link orphan RFIs', COUNT(*) FROM rfi_change_links l LEFT JOIN rfi_log r ON r.RFI_ID=l.RFI_ID WHERE r.RFI_ID IS NULL
UNION ALL
SELECT 'Link orphan changes', COUNT(*) FROM rfi_change_links l LEFT JOIN change_orders c ON c.Change_Order_ID=l.Change_Order_ID WHERE c.Change_Order_ID IS NULL
UNION ALL
SELECT 'Answered/closed RFIs missing final response', COUNT(*) FROM rfi_log WHERE RFI_Status IN ('Answered','Closed') AND Final_Response_Date IS NULL
UNION ALL
SELECT 'Approved changes missing approval date/value', COUNT(*) FROM change_orders WHERE Change_Status='Approved' AND (Approved_Date IS NULL OR Approved_Value IS NULL);
