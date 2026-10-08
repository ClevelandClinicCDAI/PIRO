-- SELECT-only extraction. No patient fields, case numbers, DDL, or DML.
-- Parameters: maximum cases, first specimen year, accession start, exclusive end,
-- exclusive signout end. Staff links are deduplicated before counting cases.
WITH recent AS (
    SELECT TOP (?) CaseId, SpecialtyId, HospitalId, AccessionDate, SignoutDate
    FROM dbo.[Case]
    WHERE IsActive = 1 AND SpecimenYear >= ?
      AND AccessionDate >= ? AND AccessionDate < ?
      AND SignoutDate IS NOT NULL AND SignoutDate < ?
    ORDER BY AccessionDate DESC, CaseId DESC
), staff_cases AS (
    SELECT DISTINCT c.CaseId, cs.StaffId, c.SpecialtyId, c.HospitalId
    FROM recent c
    JOIN dbo.CaseStaff cs ON cs.CaseId = c.CaseId AND cs.IsActive = 1
), pathologist_roles AS (
    -- The staging import retains responsibility roles that CaseStaff omits.
    -- Require positive STAFF PATHOLOGIST evidence on a case in this sample.
    SELECT cs.StaffId, COUNT(DISTINCT c.CaseId) AS RoleEvidenceCases
    FROM recent c
    JOIN dbo.CaseStaff cs ON cs.CaseId = c.CaseId AND cs.IsActive = 1
    JOIN dbo.SSIS_CaseStaff source
      ON source.K_REQUISITION_KEY = cs.RefRequisitionKey
     AND source.K_EMPLOYEE_KEY = cs.RefEmployeeKey
    WHERE source.RESPONSIBLE_ROLE_DESC = 'STAFF PATHOLOGIST'
    GROUP BY cs.StaffId
), sample AS (
    SELECT COUNT(*) AS SampleCases, MIN(AccessionDate) AS EarliestAccession,
           MAX(AccessionDate) AS LatestAccession, MAX(SignoutDate) AS LatestSignout
    FROM recent
)
SELECT s.StaffId, LTRIM(RTRIM(s.FullName)) AS FullName,
       sp.Code AS SpecialtyCode, sp.ShortName AS SpecialtyName,
       sp.SpecialtyCategory, r.ShortName AS CaseRegion,
       COUNT(*) AS CaseCount, roles.RoleEvidenceCases,
       sample.SampleCases, sample.EarliestAccession,
       sample.LatestAccession, sample.LatestSignout
FROM staff_cases c
JOIN dbo.Staff s ON s.StaffId = c.StaffId AND s.IsActive = 1
JOIN pathologist_roles roles ON roles.StaffId = s.StaffId
LEFT JOIN dbo.Specialty sp ON sp.SpecialtyId = c.SpecialtyId
LEFT JOIN dbo.Hospital h ON h.HospitalId = c.HospitalId
LEFT JOIN dbo.Region r ON r.RegionId = h.RegionId
CROSS JOIN sample
WHERE NULLIF(LTRIM(RTRIM(s.FullName)), '') IS NOT NULL
GROUP BY s.StaffId, LTRIM(RTRIM(s.FullName)), sp.Code, sp.ShortName,
         sp.SpecialtyCategory, r.ShortName, sample.SampleCases,
         sample.EarliestAccession, sample.LatestAccession, sample.LatestSignout, roles.RoleEvidenceCases
ORDER BY s.StaffId, CaseCount DESC, sp.Code, r.ShortName;
