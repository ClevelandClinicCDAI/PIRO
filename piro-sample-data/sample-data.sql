USE [PIRO];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @seedUser VARCHAR(100) = 'sample-seed';
DECLARE @now DATETIME = GETDATE();
DECLARE @sampleUserNuid NVARCHAR(150) = LTRIM(RTRIM('$(SAMPLE_USER_NUID)'));
DECLARE @sampleUserFirstName NVARCHAR(150) = NULLIF(LTRIM(RTRIM('$(SAMPLE_USER_FIRST_NAME)')), '');
DECLARE @sampleUserLastName NVARCHAR(150) = NULLIF(LTRIM(RTRIM('$(SAMPLE_USER_LAST_NAME)')), '');
DECLARE @sampleUserRoleCode NVARCHAR(50) = UPPER(NULLIF(LTRIM(RTRIM('$(SAMPLE_USER_ROLE)')), ''));

IF (
        @sampleUserNuid IS NULL
        OR @sampleUserNuid = ''
        OR @sampleUserNuid = '__unset__'
    )
    SET @sampleUserNuid = 'piro.user';

SET @sampleUserNuid = REPLACE(@sampleUserNuid, '''', '''''');

IF (@sampleUserFirstName IS NULL OR @sampleUserFirstName = '__unset__')
    SET @sampleUserFirstName = 'PIRO';

SET @sampleUserFirstName = REPLACE(@sampleUserFirstName, '''', '''''');

IF (@sampleUserLastName IS NULL OR @sampleUserLastName = '__unset__')
    SET @sampleUserLastName = 'User';

SET @sampleUserLastName = REPLACE(@sampleUserLastName, '''', '''''');

IF (
        @sampleUserRoleCode IS NULL
        OR @sampleUserRoleCode = ''
        OR @sampleUserRoleCode = '__UNSET__'
        OR @sampleUserRoleCode = '__unset__'
    )
    SET @sampleUserRoleCode = 'USER';

SET @sampleUserRoleCode = REPLACE(@sampleUserRoleCode, '''', '''''');

IF EXISTS (SELECT 1 FROM dbo.[User])
BEGIN
    PRINT 'Sample data already exists; skipping seed run.';
    RETURN;
END;

BEGIN TRY
    BEGIN TRAN;

    DECLARE @Region TABLE (RegionId INT, Code VARCHAR(50));
    INSERT INTO dbo.Region (ShortName, Code, DESCRIPTION, DataLabReference, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.RegionId, INSERTED.Code INTO @Region
    VALUES
        ('Main Campus', 'MAIN', 'Primary academic campus', 'REG-MAIN', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @Hospital TABLE (HospitalId INT, Code VARCHAR(50));
    INSERT INTO dbo.Hospital (RegionId, ShortName, Code, DESCRIPTION, DataLabReference, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.HospitalId, INSERTED.Code INTO @Hospital
    VALUES
        ((SELECT RegionId FROM @Region WHERE Code = 'MAIN'), 'Cleveland Clinic Main', 'CCF-MAIN', 'Flagship location', 'HOSP-MAIN', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @Specialty TABLE (SpecialtyId INT, Code VARCHAR(50));
    INSERT INTO dbo.Specialty (ShortName, Code, DESCRIPTION, DataLabReference, SpecialtyCategory, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.SpecialtyId, INSERTED.Code INTO @Specialty
    VALUES
        ('Breast Pathology', 'BREAST', 'Breast surgical pathology', 'SPEC-BREAST', 'Anatomic', 1, @now, @seedUser, @now, @seedUser),
        ('Neuropathology', 'NEURO', 'Neuropathology consultations', 'SPEC-NEURO', 'Anatomic', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @CaseStatus TABLE (CaseStatusId INT, Code VARCHAR(50));
    INSERT INTO dbo.CaseStatus (ShortName, Code, DESCRIPTION, DataLabReference, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.CaseStatusId, INSERTED.Code INTO @CaseStatus
    VALUES
        ('Pending Review', 'PENDING', 'Awaiting sign-out', 'CS-PENDING', 1, @now, @seedUser, @now, @seedUser),
        ('Signed Out', 'SIGNED', 'Final report complete', 'CS-SIGNED', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @CaseType TABLE (CaseTypeId INT, Code VARCHAR(50));
    INSERT INTO dbo.CaseType (ShortName, Code, DESCRIPTION, DataLabReference, CaseTypeCategory, ReviewType, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy, CaseTypeInfo, WorklistTypeInfo, DataLabReferenceCategory)
    OUTPUT INSERTED.CaseTypeId, INSERTED.Code INTO @CaseType
    VALUES
        ('Surgical Pathology', 'SURG', 'Routine surgical pathology case', 'CT-SURG', 'Diagnostic', 'Comprehensive', 1, @now, @seedUser, @now, @seedUser, 'Standard workflow', 'Resident', 'DIAG'),
        ('Consultation', 'CONSULT', 'External consultation', 'CT-CONSULT', 'Consult', 'Focused', 1, @now, @seedUser, @now, @seedUser, 'Consult workflow', 'Attending', 'CONSULT');

    DECLARE @Gender TABLE (GenderId INT, Code VARCHAR(10));
    INSERT INTO dbo.Gender (ShortName, Code, DESCRIPTION, DataLabReference, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.GenderId, INSERTED.Code INTO @Gender
    VALUES
        ('Female', 'F', 'Female sex', 'G-F', 1, @now, @seedUser, @now, @seedUser),
        ('Male', 'M', 'Male sex', 'G-M', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @Ethnicity TABLE (EthnicityId INT, Code VARCHAR(50));
    INSERT INTO dbo.Ethnicity (ShortName, Code, DESCRIPTION, DataLabReference, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.EthnicityId, INSERTED.Code INTO @Ethnicity
    VALUES
        ('Not Hispanic or Latino', 'NON-HISP', 'Not Hispanic or Latino', 'ETH-NONHISP', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @Race TABLE (RaceId INT, Code VARCHAR(50));
    INSERT INTO dbo.Race (ShortName, Code, DESCRIPTION, DataLabReference, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.RaceId, INSERTED.Code INTO @Race
    VALUES
        ('White', 'WHITE', 'White or Caucasian', 'RACE-WHITE', 1, @now, @seedUser, @now, @seedUser),
        ('Black or African American', 'BLACK', 'Black or African American', 'RACE-BLACK', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @MaritalStatus TABLE (MaritalStatusId INT, Code VARCHAR(50));
    INSERT INTO dbo.MaritalStatus (ShortName, Code, DESCRIPTION, DataLabReference, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.MaritalStatusId, INSERTED.Code INTO @MaritalStatus
    VALUES
        ('Married', 'MARRIED', 'Married', 'MS-M', 1, @now, @seedUser, @now, @seedUser),
        ('Single', 'SINGLE', 'Single', 'MS-S', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @Language TABLE (LanguageId INT, Code VARCHAR(50));
    INSERT INTO dbo.Language (ShortName, Code, DESCRIPTION, DataLabReference, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.LanguageId, INSERTED.Code INTO @Language
    VALUES
        ('English', 'EN', 'English', 'LANG-EN', 1, @now, @seedUser, @now, @seedUser),
        ('Spanish', 'ES', 'Spanish', 'LANG-ES', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @Role TABLE (RoleId INT, Code VARCHAR(50));
    INSERT INTO dbo.Role (ShortName, Code, DESCRIPTION, IsActive, DataLabReference, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.RoleId, INSERTED.Code INTO @Role
    VALUES
        ('Administrator', 'ADMIN', 'Full administrative access', 1, 'ROLE-ADMIN', @now, @seedUser, @now, @seedUser),
        ('Reviewer', 'REVIEW', 'Clinical reviewer', 1, 'ROLE-REVIEW', @now, @seedUser, @now, @seedUser),
        ('Researcher', 'RESEARCH', 'Research workspace access', 1, 'ROLE-RESEARCH', @now, @seedUser, @now, @seedUser),
        ('User', 'USER', 'Standard PIRO user', 1, 'ROLE-USER', @now, @seedUser, @now, @seedUser),
        ('Slide Room', 'SLIDEROOM', 'Slide room queue access only', 1, 'ROLE-SLIDEROOM', @now, @seedUser, @now, @seedUser);

    IF NOT EXISTS (SELECT 1 FROM @Role WHERE Code = @sampleUserRoleCode)
    BEGIN
        INSERT INTO dbo.Role (ShortName, Code, DESCRIPTION, IsActive, DataLabReference, CreateDate, CreateBy, UpdateDate, UpdateBy)
        OUTPUT INSERTED.RoleId, INSERTED.Code INTO @Role
        VALUES
            (@sampleUserRoleCode, @sampleUserRoleCode, CONCAT(@sampleUserRoleCode, ' role'), 1, CONCAT('ROLE-', @sampleUserRoleCode), @now, @seedUser, @now, @seedUser);
    END

    DECLARE @CommentType TABLE (CommentTypeId INT, Code VARCHAR(50));
    INSERT INTO dbo.CommentType (
        ShortName,
        Code,
        DESCRIPTION,
        DataLabReference,
        ETLSource,
        IsActive,
        CreateDate,
        CreateBy,
        UpdateDate,
        UpdateBy
    )
    OUTPUT INSERTED.CommentTypeId, INSERTED.Code INTO @CommentType
    VALUES
        ('Final Report', 'FINAL', 'Final diagnostic summary', 'COMMENT-FINAL', 'SampleData', 1, @now, @seedUser, @now, @seedUser),
        ('General Comment', 'COMMENT', 'Author comments and notes', 'COMMENT-GENERAL', 'SampleData', 1, @now, @seedUser, @now, @seedUser),
        ('Synoptic', 'SYNOPTIC', 'Structured synoptic section', 'COMMENT-SYNOPTIC', 'SampleData', 1, @now, @seedUser, @now, @seedUser),
        ('Microscopic', 'MICROSCOPIC', 'Microscopic description', 'COMMENT-MICROSCOPIC', 'SampleData', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @User TABLE (UserId INT, Email VARCHAR(100));
    INSERT INTO dbo.[User] (NUID, FirstName, LastName, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.UserId, INSERTED.NUID INTO @User
    VALUES
        ('judy.hart@piro.local', 'Judy', 'Hart', 1, @now, @seedUser, @now, @seedUser),
        ('marcus.hale@piro.local', 'Marcus', 'Hale', 1, @now, @seedUser, @now, @seedUser),
        ('elena.cole@piro.local', 'Elena', 'Cole', 1, @now, @seedUser, @now, @seedUser),
        (@sampleUserNuid, @sampleUserFirstName, @sampleUserLastName, 1, @now, @seedUser, @now, @seedUser);

    INSERT INTO dbo.UserRole (UserId, RoleId, isActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    VALUES
        ((SELECT UserId FROM @User WHERE Email = 'judy.hart@piro.local'), (SELECT RoleId FROM @Role WHERE Code = 'ADMIN'), 1, @now, @seedUser, @now, @seedUser),
        ((SELECT UserId FROM @User WHERE Email = 'marcus.hale@piro.local'), (SELECT RoleId FROM @Role WHERE Code = 'REVIEW'), 1, @now, @seedUser, @now, @seedUser),
        ((SELECT UserId FROM @User WHERE Email = 'elena.cole@piro.local'), (SELECT RoleId FROM @Role WHERE Code = 'RESEARCH'), 1, @now, @seedUser, @now, @seedUser),
        ((SELECT UserId FROM @User WHERE Email = @sampleUserNuid), (SELECT RoleId FROM @Role WHERE Code = @sampleUserRoleCode), 1, @now, @seedUser, @now, @seedUser);

    DECLARE @Staff TABLE (StaffId INT, RefEmployeeKey VARCHAR(50));
    INSERT INTO dbo.Staff (FullName, UserId, StartDate, EndDate, RefEmployeeKey, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.StaffId, INSERTED.RefEmployeeKey INTO @Staff
    VALUES
        ('Dr. Janet Price', 'U-1001', '2015-01-01', NULL, 'EMP-1001', 1, @now, @seedUser, @now, @seedUser),
        ('Dr. Omar French', 'U-1002', '2018-06-15', NULL, 'EMP-1002', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @Patient TABLE (PatientId INT, RefKey VARCHAR(50));
    INSERT INTO dbo.Patient (GenderId, EthnicityId, RaceId, MaritalStatusId, LanguageId, FirstName, LastName, MiddleName, DOB, MRN, PatId, EpiId, City, [State], Country, IsDeceased, DeathDate, IsActive, RefPatientKey, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.PatientId, INSERTED.RefPatientKey INTO @Patient
    VALUES
        ((SELECT GenderId FROM @Gender WHERE Code = 'F'), (SELECT EthnicityId FROM @Ethnicity), (SELECT RaceId FROM @Race WHERE Code = 'WHITE'), (SELECT MaritalStatusId FROM @MaritalStatus WHERE Code = 'MARRIED'), (SELECT LanguageId FROM @Language WHERE Code = 'EN'), 'Angela', 'Rivers', 'M', '1985-04-12', 'MRN-0001', 'PAT-0001', 'EPI-0001', 'Cleveland', 'OH', 'USA', 0, NULL, 1, 'PAT-0001', @now, @seedUser, @now, @seedUser),
        ((SELECT GenderId FROM @Gender WHERE Code = 'M'), (SELECT EthnicityId FROM @Ethnicity), (SELECT RaceId FROM @Race WHERE Code = 'BLACK'), (SELECT MaritalStatusId FROM @MaritalStatus WHERE Code = 'SINGLE'), (SELECT LanguageId FROM @Language WHERE Code = 'ES'), 'Isaac', 'Mendez', 'Q', '1990-11-03', 'MRN-0002', 'PAT-0002', 'EPI-0002', 'Akron', 'OH', 'USA', 0, NULL, 1, 'PAT-0002', @now, @seedUser, @now, @seedUser);

    DECLARE @Case TABLE (CaseId INT, CaseNumber VARCHAR(50));
    INSERT INTO dbo.[Case] (PatientId, HospitalId, CaseStatusId, CaseTypeId, SpecialtyId, SpecimenYear, CaseNumber, AccessionDate, ReceiveDate, OverdueDate, CollectionDate, SignoutDate, RefRequisitionKey, RefRequisitionId, RefPatientKey, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy, UploadDate)
    OUTPUT INSERTED.CaseId, INSERTED.CaseNumber INTO @Case
    VALUES
        ((SELECT PatientId FROM @Patient WHERE RefKey = 'PAT-0001'), (SELECT HospitalId FROM @Hospital WHERE Code = 'CCF-MAIN'), (SELECT CaseStatusId FROM @CaseStatus WHERE Code = 'SIGNED'), (SELECT CaseTypeId FROM @CaseType WHERE Code = 'SURG'), (SELECT SpecialtyId FROM @Specialty WHERE Code = 'BREAST'), 2024, 'S24-0001', '2024-08-01T09:00:00', '2024-08-01T08:15:00', '2024-08-15T17:00:00', '2024-07-30T10:00:00', '2024-08-05T14:22:00', 'REQ-2024-0001', CAST(20240010001 AS DECIMAL(38,0)), 'PAT-0001', 1, @now, @seedUser, @now, @seedUser, '2024-08-05T14:30:00'),
        ((SELECT PatientId FROM @Patient WHERE RefKey = 'PAT-0002'), (SELECT HospitalId FROM @Hospital WHERE Code = 'CCF-MAIN'), (SELECT CaseStatusId FROM @CaseStatus WHERE Code = 'PENDING'), (SELECT CaseTypeId FROM @CaseType WHERE Code = 'CONSULT'), (SELECT SpecialtyId FROM @Specialty WHERE Code = 'NEURO'), 2024, 'C24-0007', '2024-09-12T11:00:00', '2024-09-12T10:10:00', '2024-09-19T17:00:00', '2024-09-10T13:00:00', NULL, 'REQ-2024-0002', CAST(20240020007 AS DECIMAL(38,0)), 'PAT-0002', 1, @now, @seedUser, @now, @seedUser, NULL);

    INSERT INTO dbo.CaseCommentSourceInfo (RefRequisitionKey, CaseId, CaseNumber, IsEpic, IsCopath, IsEpicMigrated, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    VALUES
        ('REQ-2024-0001', (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'), 'S24-0001', 1, 0, 1, 1, @now, @seedUser, @now, @seedUser),
        ('REQ-2024-0002', (SELECT CaseId FROM @Case WHERE CaseNumber = 'C24-0007'), 'C24-0007', 1, 0, 0, 1, @now, @seedUser, @now, @seedUser);

    INSERT INTO dbo.CaseStaff (CaseId, StaffId, IsActive, RefRequisitionKey, RefEmployeeKey, CreateDate, CreateBy, UpdateDate, UpdateBy)
    VALUES
        ((SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'), (SELECT StaffId FROM @Staff WHERE RefEmployeeKey = 'EMP-1001'), 1, 'REQ-2024-0001', 'EMP-1001', @now, @seedUser, @now, @seedUser),
        ((SELECT CaseId FROM @Case WHERE CaseNumber = 'C24-0007'), (SELECT StaffId FROM @Staff WHERE RefEmployeeKey = 'EMP-1002'), 1, 'REQ-2024-0002', 'EMP-1002', @now, @seedUser, @now, @seedUser);

    ;WITH StaffNames AS (
        SELECT
            cs.CaseId,
            STRING_AGG(st.FullName, '; ') AS StaffList
        FROM dbo.CaseStaff cs
        JOIN dbo.Staff st ON cs.StaffId = st.StaffId
        GROUP BY cs.CaseId
    )
    INSERT INTO dbo.CaseSolr (
        CaseId,
        RefRequisitionKey,
        SpecimenYear,
        CaseNumber,
        AccessionDate,
        ReceiveDate,
        OverdueDate,
        CollectionDate,
        SignoutDate,
        PatientName,
        PatientDOB,
        PatientEpi,
        PatientMrn,
        PatientLanguage,
        PatientEthnicity,
        PatientGender,
        PatientDeathDate,
        PatientIsDeceased,
        PatientRace,
        PatientCity,
        PatientState,
        PatientCountry,
        Hospital,
        Region,
        CaseStatus,
        CaseType,
        CaseTypeCategory,
        ReviewType,
        Specialty,
        SpecialtyCode,
        SpecialtyCategory,
        ADDEND,
        ADDENDCount,
        COMMENT,
        COMMENTCount,
        FINAL,
        FINALCount,
        GROSS,
        GROSSCount,
        INTRAOP,
        INTRAOPCount,
        RESIDENT,
        RESIDENTCount,
        SYNOPTIC,
        SYNOPTICCount,
        CLINICAL,
        CLINICALCount,
        Interpreter,
        ProcedureCategory,
        StaffName,
        SpecimenNumber,
        CasePatientAge,
        CasePatientAgeYears,
        AnnotationMalignant,
        IsEpic,
        IsEpicMigrated,
        IsCopath,
        IsActive,
        CreateDate,
        CreateBy,
        UpdateDate,
        UpdateBy,
        IsSolrUpdate,
        IsConcentriq,
        CaseConcentriqId
    )
    SELECT
        C.CaseId,
        C.RefRequisitionKey,
        C.SpecimenYear,
        C.CaseNumber,
        C.AccessionDate,
        C.ReceiveDate,
        C.OverdueDate,
        C.CollectionDate,
        C.SignoutDate,
        dbo.F_FullName(P.FirstName, P.MiddleName, P.LastName),
        P.DOB,
        P.EpiId,
        P.MRN,
        L.ShortName,
        E.ShortName,
        G.ShortName,
        P.DeathDate,
        P.IsDeceased,
        R.ShortName,
        P.City,
        P.[State],
        P.Country,
        H.ShortName,
        REG.ShortName,
        CS.ShortName,
        CT.ShortName,
        CT.CaseTypeCategory,
        CT.ReviewType,
        S.ShortName,
        S.Code,
        S.SpecialtyCategory,
        '', 0,        -- ADDEND / ADDENDCount
        '', 0,        -- COMMENT / COMMENTCount
        '', 0,        -- FINAL / FINALCount
        '', 0,        -- GROSS / GROSSCount
        '', 0,        -- INTRAOP / INTRAOPCount
        '', 0,        -- RESIDENT / RESIDENTCount
        '', 0,        -- SYNOPTIC / SYNOPTICCount
        '', 0,        -- CLINICAL / CLINICALCount
        COALESCE(SN.StaffList, 'Demo Staff'),
        'General',
        COALESCE(SN.StaffList, 'Demo Staff'),
        C.CaseNumber,
        CAST(dbo.F_CasePatientAge(P.DOB, C.AccessionDate) AS VARCHAR(100)),
        CASE
            WHEN P.DOB = '1800-01-01' THEN 0
            ELSE ISNULL(DATEDIFF(YEAR, P.DOB, C.AccessionDate), 0)
        END,
        '-',
        CSI.IsEpic,
        CSI.IsEpicMigrated,
        CSI.IsCopath,
        1,
        @now,
        @seedUser,
        @now,
        @seedUser,
        1,
        0,
        -1
    FROM dbo.[Case] C
    JOIN dbo.Patient P ON C.PatientId = P.PatientId
    JOIN dbo.Gender G ON P.GenderId = G.GenderId
    JOIN dbo.Ethnicity E ON P.EthnicityId = E.EthnicityId
    JOIN dbo.Race R ON P.RaceId = R.RaceId
    JOIN dbo.[Language] L ON P.LanguageId = L.LanguageId
    JOIN dbo.Hospital H ON C.HospitalId = H.HospitalId
    JOIN dbo.Region REG ON H.RegionId = REG.RegionId
    JOIN dbo.CaseStatus CS ON C.CaseStatusId = CS.CaseStatusId
    JOIN dbo.CaseType CT ON C.CaseTypeId = CT.CaseTypeId
    JOIN dbo.Specialty S ON C.SpecialtyId = S.SpecialtyId
    JOIN dbo.CaseCommentSourceInfo CSI ON C.CaseId = CSI.CaseId
    LEFT JOIN StaffNames SN ON SN.CaseId = C.CaseId
    WHERE C.CaseNumber IN ('S24-0001', 'C24-0007');

    DECLARE @FinalCommentTypeId INT = (
        SELECT CommentTypeId FROM @CommentType WHERE Code = 'FINAL'
    );
    DECLARE @GeneralCommentTypeId INT = (
        SELECT CommentTypeId FROM @CommentType WHERE Code = 'COMMENT'
    );
    DECLARE @SynopticCommentTypeId INT = (
        SELECT CommentTypeId FROM @CommentType WHERE Code = 'SYNOPTIC'
    );
    DECLARE @MicroscopicCommentTypeId INT = (
        SELECT CommentTypeId FROM @CommentType WHERE Code = 'MICROSCOPIC'
    );

    INSERT INTO dbo.CaseComment (
        CaseId,
        CommentTypeId,
        [Text],
        RefRequistionKey,
        RefResultKey,
        RefLabCompName,
        RefCommentType,
        CreateDate,
        CreateBy,
        UpdateDate,
        UpdateBy,
        RefComponentDate
    )
    VALUES
        (
            (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'),
            @FinalCommentTypeId,
            'Final diagnosis: Invasive ductal carcinoma, Nottingham grade 2. Surgical margins negative (closest margin 4 mm). ER 95% positive, PR 80% positive, HER2 IHC 1+.',
            CAST(20240010001 AS DECIMAL(38, 0)),
            CAST(90010001 AS DECIMAL(38, 0)),
            'EPIC FINAL',
            'FINAL DIAGNOSIS',
            @now,
            @seedUser,
            @now,
            @seedUser,
            '2024-08-05T14:35:00'
        ),
        (
            (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'),
            @GeneralCommentTypeId,
            'Comment: Recommend multidisciplinary tumor board discussion. Imaging correlation reviewed; no residual calcifications noted.',
            CAST(20240010001 AS DECIMAL(38, 0)),
            CAST(90010002 AS DECIMAL(38, 0)),
            'EPIC COMMENT',
            'COMMENT',
            @now,
            @seedUser,
            @now,
            @seedUser,
            '2024-08-05T14:40:00'
        ),
        (
            (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'),
            @MicroscopicCommentTypeId,
            'Microscopic: Invasive ductal carcinoma with associated high-grade DCIS; lymphovascular invasion not identified.',
            CAST(20240010001 AS DECIMAL(38, 0)),
            CAST(90010003 AS DECIMAL(38, 0)),
            'EPIC MICROSCOPIC',
            'MICROSCOPIC',
            @now,
            @seedUser,
            @now,
            @seedUser,
            '2024-08-05T14:45:00'
        ),
        (
            (SELECT CaseId FROM @Case WHERE CaseNumber = 'C24-0007'),
            @FinalCommentTypeId,
            'Consultation pending: blocks pending deeper levels for neuropathology review.',
            CAST(20240020007 AS DECIMAL(38, 0)),
            CAST(90020007 AS DECIMAL(38, 0)),
            'EPIC FINAL',
            'FINAL DIAGNOSIS',
            @now,
            @seedUser,
            NULL,
            NULL,
            NULL
        );

    INSERT INTO dbo.CaseCommentCoPath (
        CaseId,
        CommentTypeId,
        [Text],
        RtfText,
        StatusDate,
        SpecYear,
        RefId,
        RefSpecimenId,
        RefCaseNum,
        RefSpecimenNum,
        RefTextType,
        CreateDate,
        CreateBy,
        UpdateDate,
        UpdateBy,
        IsTextUpdated
    )
    VALUES
        (
            (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'),
            @FinalCommentTypeId,
            'Final CoPath report confirms invasive ductal carcinoma with negative margins.',
            '{\rtf1\ansi\deff0 {\fonttbl {\f0 Arial;}} \f0\fs24 Final Diagnosis:\line Invasive ductal carcinoma, grade 2.\line Margins: Negative (closest 4 mm).}',
            '2024-08-05T15:05:00',
            2024,
            5001,
            'SPEC-A1',
            'S24-0001',
            'A1',
            'FINAL',
            @now,
            @seedUser,
            @now,
            @seedUser,
            0
        ),
        (
            (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'),
            @SynopticCommentTypeId,
            '#Synoptic Report#\nProcedure: Lumpectomy.\nHistologic Type: Invasive ductal carcinoma.\nNottingham Grade: II (tubule 2, nuclear 2, mitotic 2).\nTumor Size: 2.1 cm.',
            '{\rtf1\ansi\deff0 {\fonttbl {\f0 Arial;}} \f0\fs24 #Synoptic Report#\line Procedure: Lumpectomy\line Histologic Type: Invasive ductal carcinoma\line Nottingham Grade: II\line Tumor Size: 2.1 cm}',
            '2024-08-05T15:06:00',
            2024,
            5002,
            'SPEC-A1',
            'S24-0001',
            'A1',
            'SYNOPTIC',
            @now,
            @seedUser,
            @now,
            @seedUser,
            0
        );

    INSERT INTO dbo.CaseCommentEpic (
        CaseId,
        CommentTypeId,
        [Text],
        NumberOfLines,
        RefRequisitionKey,
        RefOrdKey,
        RefLabCompName,
        RefOrdResultDate,
        RefContactDate,
        RefRecNum,
        CreateDate,
        CreateBy,
        UpdateDate,
        UpdateBy
    )
    VALUES
        (
            (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'),
            @FinalCommentTypeId,
            'EPIC FINAL REPORT: Invasive ductal carcinoma, ER+/PR+, HER2-.',
            6,
            'REQ-2024-0001',
            'ORD-1001',
            'EPIC FINAL',
            '2024-08-05T15:00:00',
            CAST(20240805 AS DECIMAL(18, 2)),
            'EPIC-0001',
            @now,
            @seedUser,
            @now,
            @seedUser
        ),
        (
            (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'),
            @GeneralCommentTypeId,
            'EPIC COMMENT: Case discussed with surgical oncology.',
            3,
            'REQ-2024-0001',
            'ORD-1002',
            'EPIC COMMENT',
            '2024-08-05T15:10:00',
            CAST(20240805 AS DECIMAL(18, 2)),
            'EPIC-0002',
            @now,
            @seedUser,
            @now,
            @seedUser
        );

    DECLARE @SynopticId DECIMAL(38, 0) = CAST(1001 AS DECIMAL(38, 0));
    INSERT INTO dbo.CaseCommentSynopticSpecimen (
        CaseId,
        SpecimenId,
        SynopticId,
        SynopticLine,
        CaseNum,
        SpecimenNum,
        SpecimenList,
        RecordCreateDate,
        IsSpecimenLevel,
        RefSpecimenKey,
        RefRequisitionKey,
        IsParsed,
        CreateDate,
        CreateBy,
        UpdateDate,
        UpdateBy
    )
    VALUES
        (
            (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'),
            1001,
            @SynopticId,
            1,
            'S24-0001',
            'A1',
            'A1 - Left breast lumpectomy',
            @now,
            1,
            'SPEC-A1',
            'REQ-2024-0001',
            1,
            @now,
            @seedUser,
            @now,
            @seedUser
        );

    INSERT INTO dbo.CaseCommentSynopticText (
        SynopticId,
        Name,
        ResultId,
        HlvId,
        DataType,
        ContextName,
        ContexHierarchy,
        ValueLine,
        Level1,
        Level2,
        Level3,
        Level4,
        Level5,
        Level6,
        ElementName,
        ElementValue,
        SynopticKey,
        ElementComment,
        CommentLine,
        CommentSequence,
        RefSynopticKey,
        CreateDate,
        CreateBy,
        UpdateDate,
        UpdateBy
    )
    VALUES
        (
            @SynopticId,
            'Procedure',
            'RES-1001',
            101,
            'Text',
            'SYNOPTIC',
            'Breast|Procedure',
            '1',
            'Breast Cancer',
            'Procedure',
            'Specimen',
            'Procedure Detail',
            '',
            '',
            'Procedure Type',
            'Lumpectomy',
            'SYN-001',
            '',
            '1',
            1,
            'SYN-001',
            @now,
            @seedUser,
            @now,
            @seedUser
        ),
        (
            @SynopticId,
            'Tumor Size',
            'RES-1002',
            102,
            'Text',
            'SYNOPTIC',
            'Breast|Tumor',
            '2',
            'Breast Cancer',
            'Tumor Characteristics',
            'Greatest Dimension',
            '',
            '',
            '',
            'Greatest Dimension',
            '2.1 cm',
            'SYN-002',
            '',
            '2',
            2,
            'SYN-002',
            @now,
            @seedUser,
            @now,
            @seedUser
        ),
        (
            @SynopticId,
            'Nottingham Grade',
            'RES-1003',
            103,
            'Text',
            'SYNOPTIC',
            'Breast|Grade',
            '3',
            'Breast Cancer',
            'Tumor Characteristics',
            'Grading',
            '',
            '',
            '',
            'Grade Components',
            'II (tubule 2 / nuclear 2 / mitotic 2)',
            'SYN-003',
            '',
            '3',
            3,
            'SYN-003',
            @now,
            @seedUser,
            @now,
            @seedUser
        ),
        (
            @SynopticId,
            'Patient Metadata',
            'RES-1004',
            104,
            'Text',
            'PATIENT',
            'Patient|Demographics',
            '1',
            'Patient',
            'Demographics',
            'MRN',
            '',
            '',
            '',
            'MRN',
            'MRN-0001',
            'SYN-004',
            '',
            '4',
            4,
            'SYN-004',
            @now,
            @seedUser,
            @now,
            @seedUser
        );

    INSERT INTO dbo.CaseCommentSynopticTextComment (
        SynopticId,
        HlvId,
        [Line],
        Comment,
        CreateDate,
        CreateBy,
        UpdateDate,
        UpdateBy
    )
    VALUES
        (
            @SynopticId,
            101,
            1,
            'Lumpectomy – left breast, sentinel nodes not submitted.',
            @now,
            @seedUser,
            @now,
            @seedUser
        ),
        (
            @SynopticId,
            102,
            2,
            'Greatest invasive focus measures 2.1 cm.',
            @now,
            @seedUser,
            @now,
            @seedUser
        ),
        (
            @SynopticId,
            103,
            3,
            'Nottingham grade II (tubule score 2 / nuclear 2 / mitotic 2).',
            @now,
            @seedUser,
            @now,
            @seedUser
        ),
        (
            @SynopticId,
            104,
            4,
            'Patient MRN: MRN-0001.',
            @now,
            @seedUser,
            @now,
            @seedUser
        );

    DECLARE @Tag TABLE (TagId INT, Name VARCHAR(100));
    INSERT INTO dbo.Tag (UserId, Name, Description, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.TagId, INSERTED.Name INTO @Tag
    VALUES
        ((SELECT UserId FROM @User WHERE Email = 'judy.hart@piro.local'), 'Expedited', 'Cases needing expedited review', 1, @now, @seedUser, @now, @seedUser),
        ((SELECT UserId FROM @User WHERE Email = 'marcus.hale@piro.local'), 'Interesting', 'Teaching files', 1, @now, @seedUser, @now, @seedUser);

    INSERT INTO dbo.TagCase (TagId, CaseId, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    VALUES
        ((SELECT TagId FROM @Tag WHERE Name = 'Expedited'), (SELECT CaseId FROM @Case WHERE CaseNumber = 'C24-0007'), 1, @now, @seedUser, @now, @seedUser),
        ((SELECT TagId FROM @Tag WHERE Name = 'Interesting'), (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'), 1, @now, @seedUser, @now, @seedUser);

    DECLARE @Cohort TABLE (CohortId INT, Name VARCHAR(100));
    INSERT INTO dbo.Cohort (Name, Description, Disease, UserId, IsFacetDisplay, IsActive, LoadType, IsSolrUpdated, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.CohortId, INSERTED.Name INTO @Cohort
    VALUES
        ('Breast Demo Cohort', 'Signed-out breast cancer cases', 'Breast', (SELECT UserId FROM @User WHERE Email = 'judy.hart@piro.local'), 1, 1, 'M', 0, @now, @seedUser, @now, @seedUser),
        ('Neuro Consult Watch', 'Neuropathology consults awaiting sign-out', 'Neuro', (SELECT UserId FROM @User WHERE Email = 'marcus.hale@piro.local'), 1, 1, 'M', 0, @now, @seedUser, @now, @seedUser);

    INSERT INTO dbo.CohortPatient (CohortId, PatientId, PatientMrn, PatientEpi, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    VALUES
        ((SELECT CohortId FROM @Cohort WHERE Name = 'Breast Demo Cohort'), (SELECT PatientId FROM @Patient WHERE RefKey = 'PAT-0001'), 'MRN-0001', 'EPI-0001', 1, @now, @seedUser, @now, @seedUser),
        ((SELECT CohortId FROM @Cohort WHERE Name = 'Neuro Consult Watch'), (SELECT PatientId FROM @Patient WHERE RefKey = 'PAT-0002'), 'MRN-0002', 'EPI-0002', 1, @now, @seedUser, @now, @seedUser);

    INSERT INTO dbo.CohortCase (CohortId, PatientId, CaseNumber, CaseId, IsActive, LoadType, IsSolrUpdated, CreateDate, CreateBy, UpdateDate, UpdateBy)
    VALUES
        ((SELECT CohortId FROM @Cohort WHERE Name = 'Breast Demo Cohort'), (SELECT PatientId FROM @Patient WHERE RefKey = 'PAT-0001'), 'S24-0001', (SELECT CaseId FROM @Case WHERE CaseNumber = 'S24-0001'), 1, 'M', 0, @now, @seedUser, @now, @seedUser),
        ((SELECT CohortId FROM @Cohort WHERE Name = 'Neuro Consult Watch'), (SELECT PatientId FROM @Patient WHERE RefKey = 'PAT-0002'), 'C24-0007', (SELECT CaseId FROM @Case WHERE CaseNumber = 'C24-0007'), 1, 'M', 0, @now, @seedUser, @now, @seedUser);

    DECLARE @Search TABLE (SearchId INT, Name VARCHAR(200));
    INSERT INTO dbo.Search (UserId, Name, SearchQuery, AdvancedQuery, MRN, Description, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.SearchId, INSERTED.Name INTO @Search
    VALUES
        ((SELECT UserId FROM @User WHERE Email = 'elena.cole@piro.local'), 'ER Negative Breast', '{"filters":{"specialty":["BREAST"],"caseStatus":["SIGNED"]}}', 'Specialty:BREAST AND CaseStatus:SIGNED', NULL, 'Signed-out ER negative breast cases', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @SearchRequestReason TABLE (SearchRequestReasonId INT, Code VARCHAR(50));
    INSERT INTO dbo.SearchRequestReason (ShortName, Code, Description, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.SearchRequestReasonId, INSERTED.Code INTO @SearchRequestReason
    VALUES
        ('IRB Protocol', 'IRB', 'IRB-approved research request', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @SearchRequestStatus TABLE (SearchRequestStatusId INT, Code VARCHAR(50));
    INSERT INTO dbo.SearchRequestStatus (ShortName, Code, Description, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.SearchRequestStatusId, INSERTED.Code INTO @SearchRequestStatus
    VALUES
        ('Submitted', 'SUBMITTED', 'Request submitted', 1, @now, @seedUser, @now, @seedUser),
        ('Fulfilled', 'FULFILLED', 'Request fulfilled', 1, @now, @seedUser, @now, @seedUser);

    DECLARE @SearchRequest TABLE (SearchRequestId INT, Name VARCHAR(200));
    INSERT INTO dbo.SearchRequest (SearchId, RequesterId, SearchRequestReasonId, SearchRequestStatusId, RequestName, FromDate, ToDate, IRB, IsPediatric, RequestDocumentFile, RequestDocumentName, RequestDocumentSize, RequestDocumentType, RequestDocumentExtension, RequestComment, ResultDocumentFile, ResultDocumentName, ResultDocumentSize, ApprovedById, ApprovedDate, ApprovalComment, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.SearchRequestId, INSERTED.RequestName INTO @SearchRequest
    VALUES
        ((SELECT SearchId FROM @Search WHERE Name = 'ER Negative Breast'), (SELECT UserId FROM @User WHERE Email = 'elena.cole@piro.local'), (SELECT SearchRequestReasonId FROM @SearchRequestReason WHERE Code = 'IRB'), (SELECT SearchRequestStatusId FROM @SearchRequestStatus WHERE Code = 'SUBMITTED'), 'ER- Breast Study 2024', '2020-01-01', '2024-10-01', 'IRB-2024-001', 0, NULL, NULL, NULL, NULL, NULL, 'Need signed-out ER- cases for biomarker study.', NULL, NULL, NULL, NULL, NULL, NULL, 1, @now, @seedUser, @now, @seedUser);

    DECLARE @DataFieldCategory TABLE (DataFieldCategoryId INT, Code VARCHAR(50));
    INSERT INTO dbo.DataFieldCategory (DisplayName, Code, Sequence, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.DataFieldCategoryId, INSERTED.Code INTO @DataFieldCategory
    VALUES
        ('Clinical', 'CLIN', 1, 1, @now, @seedUser, @now, @seedUser);

    DECLARE @DataField TABLE (DataFieldId INT, Code VARCHAR(50));
    INSERT INTO dbo.DataField (DataFieldCategoryId, DisplayName, SolrField, Code, Sequence, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    OUTPUT INSERTED.DataFieldId, INSERTED.Code INTO @DataField
    VALUES
        ((SELECT DataFieldCategoryId FROM @DataFieldCategory WHERE Code = 'CLIN'), 'Patient Age', 'patient_age', 'AGE', 1, 1, @now, @seedUser, @now, @seedUser),
        ((SELECT DataFieldCategoryId FROM @DataFieldCategory WHERE Code = 'CLIN'), 'Diagnosis', 'diagnosis', 'DX', 2, 1, @now, @seedUser, @now, @seedUser);

    INSERT INTO dbo.SearchRequestDataField (SearchRequestId, DataFieldId, IsSelected, IsActive, CreateDate, CreateBy, UpdateDate, UpdateBy)
    VALUES
        ((SELECT SearchRequestId FROM @SearchRequest WHERE Name = 'ER- Breast Study 2024'), (SELECT DataFieldId FROM @DataField WHERE Code = 'AGE'), 1, 1, @now, @seedUser, @now, @seedUser),
        ((SELECT SearchRequestId FROM @SearchRequest WHERE Name = 'ER- Breast Study 2024'), (SELECT DataFieldId FROM @DataField WHERE Code = 'DX'), 1, 1, @now, @seedUser, @now, @seedUser);

    COMMIT;
    PRINT 'Sample data load completed successfully.';
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    DECLARE @err NVARCHAR(2048) = ERROR_MESSAGE();
    THROW 51000, @err, 1;
END CATCH;
