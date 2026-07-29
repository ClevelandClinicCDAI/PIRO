/* Seeds CytologyTerminology with the authoritative values from temp/terminologies.xlsx.
   Safe to re-run: only inserts rows that do not already exist. */
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ProcedureType' AND [Value] = 'Bronch')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ProcedureType', 'Bronch', 0, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ProcedureType' AND [Value] = 'Superficial/Peripheral FNA')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ProcedureType', 'Superficial/Peripheral FNA', 1, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ProcedureType' AND [Value] = 'EUS')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ProcedureType', 'EUS', 2, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ProcedureType' AND [Value] = 'IR')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ProcedureType', 'IR', 3, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ReadLocation' AND [Value] = 'Main Campus')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ReadLocation', 'Main Campus', 0, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ReadLocation' AND [Value] = 'Marymount')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ReadLocation', 'Marymount', 1, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ReadLocation' AND [Value] = 'Fairview')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ReadLocation', 'Fairview', 2, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ReadLocation' AND [Value] = 'Hillcrest')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ReadLocation', 'Hillcrest', 3, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ProcedureLocation' AND [Value] = 'Main Campus')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ProcedureLocation', 'Main Campus', 0, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ProcedureLocation' AND [Value] = 'Marymount')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ProcedureLocation', 'Marymount', 1, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ProcedureLocation' AND [Value] = 'Fairview')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ProcedureLocation', 'Fairview', 2, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'ProcedureLocation' AND [Value] = 'Hillcrest')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('ProcedureLocation', 'Hillcrest', 3, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Lung, right')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Lung, right', 0, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Lung right upper lobe')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Lung right upper lobe', 1, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Lung , right middle lobe')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Lung , right middle lobe', 2, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Lung, right lower lobe')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Lung, right lower lobe', 3, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Lung, Left')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Lung, Left', 4, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Lung, left upper lobe')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Lung, left upper lobe', 5, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Lung, left lower lobe')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Lung, left lower lobe', 6, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Lung, lingula')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Lung, lingula', 7, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Lung, hilar')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Lung, hilar', 8, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Pancreas, NOS')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Pancreas, NOS', 9, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Pancreas, head')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Pancreas, head', 10, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Pancreas, body/tail')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Pancreas, body/tail', 11, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Pancreas, body')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Pancreas, body', 12, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Pancreas, tail')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Pancreas, tail', 13, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Pancreas, uncinate')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Pancreas, uncinate', 14, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Pancreas, peripancreatic')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Pancreas, peripancreatic', 15, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Thyroid')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Thyroid', 16, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Thyroid, left')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Thyroid, left', 17, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Thyroid, left upper')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Thyroid, left upper', 18, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Thyroid, left mid')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Thyroid, left mid', 19, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Thyroid, left lower')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Thyroid, left lower', 20, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Thyroid, right')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Thyroid, right', 21, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Thyroid, right upper')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Thyroid, right upper', 22, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Thyroid, right mid')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Thyroid, right mid', 23, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Thyroid, right lower')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Thyroid, right lower', 24, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Salivary gland, NOS')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Salivary gland, NOS', 25, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Parotid, left')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Parotid, left', 26, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Parotid, right')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Parotid, right', 27, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Submandibular')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Submandibular', 28, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Submandibular, right')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Submandibular, right', 29, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Submandibular, left')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Submandibular, left', 30, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Submental')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Submental', 31, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = '2R')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', '2R', 32, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = '4R')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', '4R', 33, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = '4L')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', '4L', 34, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Station 7')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Station 7', 35, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = '10R')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', '10R', 36, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = '10L')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', '10L', 37, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = '11L')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', '11L', 38, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Site' AND [Value] = 'Other (please type)')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Site', 'Other (please type)', 39, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Non-diagnostic')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Non-diagnostic', 0, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Benign')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Benign', 1, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Lymphoid sample')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Lymphoid sample', 2, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Limited lymphoid sample')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Limited lymphoid sample', 3, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Lymphoid sample with granulomas')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Lymphoid sample with granulomas', 4, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Granulomas with necrosis')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Granulomas with necrosis', 5, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Necrosis')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Necrosis', 6, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Necrotic debris')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Necrotic debris', 7, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Acute inflammation')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Acute inflammation', 8, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Suppurative acute inflammation')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Suppurative acute inflammation', 9, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Atypical')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Atypical', 10, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Atypical cells present')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Atypical cells present', 11, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Atypical lymphocytes present')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Atypical lymphocytes present', 12, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Atypical spindle cells present')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Atypical spindle cells present', 13, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Suspicious')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Suspicious', 14, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Atypical cells, suspicious for malignancy')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Atypical cells, suspicious for malignancy', 15, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Atypical cells suspicious for non small cell carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Atypical cells suspicious for non small cell carcinoma', 16, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Atypical cells suspicious for carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Atypical cells suspicious for carcinoma', 17, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Atypical lymphocytes, suspicious for lymphoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Atypical lymphocytes, suspicious for lymphoma', 18, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive', 19, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive for malignant cells')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive for malignant cells', 20, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive for Non-small cell carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive for Non-small cell carcinoma', 21, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive for malignant cells, favor small cell carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive for malignant cells, favor small cell carcinoma', 22, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Large cell malignant neoplasm')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Large cell malignant neoplasm', 23, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'poorly differentiated malignant neoplasm')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'poorly differentiated malignant neoplasm', 24, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive for carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive for carcinoma', 25, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive for malignant cells, favorxxxxx')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive for malignant cells, favorxxxxx', 26, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Neoplastic cells present')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Neoplastic cells present', 27, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Lesional cells present')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Lesional cells present', 28, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Low grade neoplasm')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Low grade neoplasm', 29, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Adequate')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Adequate', 30, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Inadequate')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Inadequate', 31, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Other (please type)')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Other (please type)', 32, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive for adenocarcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive for adenocarcinoma', 33, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive for squamous cell carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive for squamous cell carcinoma', 34, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Suspicious for adenocarcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Suspicious for adenocarcinoma', 35, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Suspicious for squamous cell carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Suspicious for squamous cell carcinoma', 36, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive for metastatic carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive for metastatic carcinoma', 37, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive for carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive for carcinoma', 38, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Small cell carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Small cell carcinoma', 39, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Positive for lymphoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Positive for lymphoma', 40, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Suspicious for lymphoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Suspicious for lymphoma', 41, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Papillary thyroid carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Papillary thyroid carcinoma', 42, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Suspicious for papillary thyroid carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Suspicious for papillary thyroid carcinoma', 43, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'AUS')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'AUS', 44, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Benign')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Benign', 45, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Favor mucoepidermoid carcinoma')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Favor mucoepidermoid carcinoma', 46, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Salivary gland neoplasm')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Salivary gland neoplasm', 47, 1, 'System');
IF NOT EXISTS (SELECT 1 FROM [CytologyTerminology] WHERE [Category] = 'Adequacy' AND [Value] = 'Polymorphous lymphoid population')
    INSERT INTO [CytologyTerminology] ([Category],[Value],[SortOrder],[IsActive],[CreateBy]) VALUES ('Adequacy', 'Polymorphous lymphoid population', 48, 1, 'System');