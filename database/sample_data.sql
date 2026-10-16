/*
    Patient-Doctor Management System (PDMS)
    Fictional sample/seed data for demonstration purposes only.

    Run script.sql first, then run this file once on the newly created PDMS database.
    The sample accounts below all use the demo password: Demo123!
    PasswordHash values were generated using Werkzeug's generate_password_hash()
    and are compatible with check_password_hash() in the Python application.

    Do not use these demo credentials in a real deployment.
*/
USE [PDMS];
GO

-- Sample records for Users
SET IDENTITY_INSERT [dbo].[Users] ON 

INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (1, N'dr.luna@pdms.ph', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Doctor', CAST(N'2026-05-26T18:03:13.3366667' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (2, N'dr.delmundo@pdms.ph', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Doctor', CAST(N'2026-05-26T18:03:13.3366667' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (3, N'dr.rizal@pdms.ph', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Doctor', CAST(N'2026-05-26T18:03:13.3366667' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (4, N'dr.valdez@pdms.ph', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Doctor', CAST(N'2026-05-26T18:03:13.3366667' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (5, N'dr.tolentino@pdms.ph', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Doctor', CAST(N'2026-05-26T18:03:13.3366667' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (6, N'juan.delacruz@email.ph', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Patient', CAST(N'2026-05-26T18:03:13.3366667' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (7, N'clara.santos@email.ph', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Patient', CAST(N'2026-05-26T18:03:13.3366667' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (8, N'pedro.penduko@email.ph', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Patient', CAST(N'2026-05-26T18:03:13.3366667' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (9, N'gabriela.silang@email.ph', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Patient', CAST(N'2026-05-26T18:03:13.3366667' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (10, N'miguel.aguinaldo@email.ph', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Patient', CAST(N'2026-05-26T18:03:13.3366667' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (11, N'carlos.mendoza@email.com', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Doctor', CAST(N'2026-05-29T15:40:06.5500000' AS DateTime2))
INSERT [dbo].[Users] ([UserID], [Email], [PasswordHash], [Role], [DateRegistered]) VALUES (12, N'elena.bautista@email.com', N'scrypt:32768:8:1$qGBToNCYxkLwdMzL$6f21da799ed86fcf2a69923c8a5c4d6df5e9e40b62e626d0b4cb289859d458df77735b9113430a50bd1a42e6a468e5fbc777103ac54bcbf3bd746205b189dd29', N'Patient', CAST(N'2026-05-29T15:45:59.7400000' AS DateTime2))
SET IDENTITY_INSERT [dbo].[Users] OFF

-- Sample records for Patients
SET IDENTITY_INSERT [dbo].[Patients] ON 

INSERT [dbo].[Patients] ([PatientID], [UID], [FirstName], [MiddleName], [LastName], [BirthDate], [Gender], [ContactNumber], [BloodType], [HomeAddress], [InitialConditions], [InitialAllergies], [InitialMedications]) VALUES (1, 6, N'Juan', N'Bautista', N'Dela Cruz', CAST(N'1980-05-15' AS Date), N'M', N'09177771111', N'O+', N'Blk 1 Lot 2, Salinas, Bacoor City', N'Hypertension', N'None', N'Losartan 50mg')
INSERT [dbo].[Patients] ([PatientID], [UID], [FirstName], [MiddleName], [LastName], [BirthDate], [Gender], [ContactNumber], [BloodType], [HomeAddress], [InitialConditions], [InitialAllergies], [InitialMedications]) VALUES (2, 7, N'Clara', N'Gomez', N'Santos', CAST(N'1995-12-01' AS Date), N'F', N'09188882222', N'A-', N'Aguinaldo Highway, Dasmariñas City', N'Asthma', N'Dust mites, Penicillin', N'Salbutamol')
INSERT [dbo].[Patients] ([PatientID], [UID], [FirstName], [MiddleName], [LastName], [BirthDate], [Gender], [ContactNumber], [BloodType], [HomeAddress], [InitialConditions], [InitialAllergies], [InitialMedications]) VALUES (3, 8, N'Pedro', N'Roxas', N'Penduko', CAST(N'1990-08-21' AS Date), N'M', N'09199993333', N'B+', N'Molino Blvd, Bacoor City', N'None', N'None', N'None')
INSERT [dbo].[Patients] ([PatientID], [UID], [FirstName], [MiddleName], [LastName], [BirthDate], [Gender], [ContactNumber], [BloodType], [HomeAddress], [InitialConditions], [InitialAllergies], [InitialMedications]) VALUES (4, 9, N'Gabriela', N'Diego', N'Silang', CAST(N'2001-03-08' AS Date), N'F', N'09200004444', N'AB+', N'Bayan Luma, Imus City', N'PCOS', N'Seafood', N'None')
INSERT [dbo].[Patients] ([PatientID], [UID], [FirstName], [MiddleName], [LastName], [BirthDate], [Gender], [ContactNumber], [BloodType], [HomeAddress], [InitialConditions], [InitialAllergies], [InitialMedications]) VALUES (5, 10, N'Miguel', N'Cruz', N'Aguinaldo', CAST(N'2018-11-30' AS Date), N'M', N'09211115555', N'O-', N'Centennial Road, Kawit', N'None', N'Peanuts', N'Vitamin C')
INSERT [dbo].[Patients] ([PatientID], [UID], [FirstName], [MiddleName], [LastName], [BirthDate], [Gender], [ContactNumber], [BloodType], [HomeAddress], [InitialConditions], [InitialAllergies], [InitialMedications]) VALUES (6, 12, N'Elena', N'Cruz', N'Bautista', CAST(N'1990-10-15' AS Date), N'F', N'09198987643', N'O+', N'88 Mabini Street, Bacoor', N'None', N'Penicillin', N'None')
SET IDENTITY_INSERT [dbo].[Patients] OFF

-- Sample records for Doctors
SET IDENTITY_INSERT [dbo].[Doctors] ON 

INSERT [dbo].[Doctors] ([DoctorID], [UID], [FirstName], [MiddleName], [LastName], [Gender], [ContactNumber], [Specialization], [LicenseNumber], [DefaultLocation]) VALUES (1, 1, N'Antonio', N'Reyes', N'Luna', N'M', N'09171000001', N'Cardiology', N'DR-2026-8001', N'Room 301 - Heart Center')
INSERT [dbo].[Doctors] ([DoctorID], [UID], [FirstName], [MiddleName], [LastName], [Gender], [ContactNumber], [Specialization], [LicenseNumber], [DefaultLocation]) VALUES (2, 2, N'Fe', N'Villanueva', N'Del Mundo', N'F', N'09182000002', N'Pediatrics', N'DR-2026-8002', N'Room 105 - Pedia Ward')
INSERT [dbo].[Doctors] ([DoctorID], [UID], [FirstName], [MiddleName], [LastName], [Gender], [ContactNumber], [Specialization], [LicenseNumber], [DefaultLocation]) VALUES (3, 3, N'Jose', N'Mercado', N'Rizal', N'M', N'09193000003', N'General Medicine', N'DR-2026-8003', N'General Clinic')
INSERT [dbo].[Doctors] ([DoctorID], [UID], [FirstName], [MiddleName], [LastName], [Gender], [ContactNumber], [Specialization], [LicenseNumber], [DefaultLocation]) VALUES (4, 4, N'Vicki', N'Santos', N'Valdez', N'F', N'09204000004', N'Dermatology', N'DR-2026-8004', N'Skin Clinic')
INSERT [dbo].[Doctors] ([DoctorID], [UID], [FirstName], [MiddleName], [LastName], [Gender], [ContactNumber], [Specialization], [LicenseNumber], [DefaultLocation]) VALUES (5, 5, N'Arturo', N'Garcia', N'Tolentino', N'M', N'09215000005', N'Psychiatry', N'DR-2026-8005', N'Room 402 - Wellness Center')
INSERT [dbo].[Doctors] ([DoctorID], [UID], [FirstName], [MiddleName], [LastName], [Gender], [ContactNumber], [Specialization], [LicenseNumber], [DefaultLocation]) VALUES (6, 11, N'Carlos', N'Santos', N'Mendoza', N'M', N'09129853432', N'General Medicine', N'MD-2015-8475', N'Room 101')
SET IDENTITY_INSERT [dbo].[Doctors] OFF

-- Sample records for EmergencyContacts
SET IDENTITY_INSERT [dbo].[EmergencyContacts] ON 

INSERT [dbo].[EmergencyContacts] ([ContactID], [PID], [FullName], [ContactNumber], [Relationship]) VALUES (1, 1, N'Maria Dela Cruz', N'09171234567', N'Wife')
INSERT [dbo].[EmergencyContacts] ([ContactID], [PID], [FullName], [ContactNumber], [Relationship]) VALUES (2, 2, N'Roberto Santos', N'09181234567', N'Father')
INSERT [dbo].[EmergencyContacts] ([ContactID], [PID], [FullName], [ContactNumber], [Relationship]) VALUES (3, 3, N'Anna Penduko', N'09191234567', N'Sister')
INSERT [dbo].[EmergencyContacts] ([ContactID], [PID], [FullName], [ContactNumber], [Relationship]) VALUES (4, 4, N'Mario Silang', N'09201234567', N'Brother')
INSERT [dbo].[EmergencyContacts] ([ContactID], [PID], [FullName], [ContactNumber], [Relationship]) VALUES (5, 5, N'Elena Aguinaldo', N'09211234567', N'Mother')
INSERT [dbo].[EmergencyContacts] ([ContactID], [PID], [FullName], [ContactNumber], [Relationship]) VALUES (6, 6, N'Miguel Bautista', N'09192345678', N'Husband')
SET IDENTITY_INSERT [dbo].[EmergencyContacts] OFF

-- Sample records for Fee
SET IDENTITY_INSERT [dbo].[Fee] ON 

INSERT [dbo].[Fee] ([FeeID], [DID], [BaseAmount], [EffectiveDate]) VALUES (1, 1, CAST(1500.00 AS Decimal(10, 2)), CAST(N'2026-05-26T18:03:13.3766667' AS DateTime2))
INSERT [dbo].[Fee] ([FeeID], [DID], [BaseAmount], [EffectiveDate]) VALUES (2, 2, CAST(800.00 AS Decimal(10, 2)), CAST(N'2026-05-26T18:03:13.3766667' AS DateTime2))
INSERT [dbo].[Fee] ([FeeID], [DID], [BaseAmount], [EffectiveDate]) VALUES (3, 3, CAST(500.00 AS Decimal(10, 2)), CAST(N'2026-05-26T18:03:13.3766667' AS DateTime2))
INSERT [dbo].[Fee] ([FeeID], [DID], [BaseAmount], [EffectiveDate]) VALUES (4, 4, CAST(1000.00 AS Decimal(10, 2)), CAST(N'2026-05-26T18:03:13.3766667' AS DateTime2))
INSERT [dbo].[Fee] ([FeeID], [DID], [BaseAmount], [EffectiveDate]) VALUES (5, 5, CAST(2000.00 AS Decimal(10, 2)), CAST(N'2026-05-26T18:03:13.3766667' AS DateTime2))
INSERT [dbo].[Fee] ([FeeID], [DID], [BaseAmount], [EffectiveDate]) VALUES (6, 6, CAST(1000.00 AS Decimal(10, 2)), CAST(N'2026-05-29T15:40:06.5700000' AS DateTime2))
INSERT [dbo].[Fee] ([FeeID], [DID], [BaseAmount], [EffectiveDate]) VALUES (7, 6, CAST(2000.00 AS Decimal(10, 2)), CAST(N'2026-05-29T17:36:44.4233333' AS DateTime2))
SET IDENTITY_INSERT [dbo].[Fee] OFF

-- Sample records for Appointments
SET IDENTITY_INSERT [dbo].[Appointments] ON 

INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (1, 1, 1, CAST(N'2026-04-15T09:00:00.0000000' AS DateTime2), N'Room 301 - Heart Center', N'Chest pain and routine BP check', N'Completed')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (2, 2, 3, CAST(N'2026-05-02T14:00:00.0000000' AS DateTime2), N'General Clinic', N'Fever, cough, and body aches for 3 days', N'Completed')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (3, 4, 4, CAST(N'2026-06-10T10:00:00.0000000' AS DateTime2), N'Skin Clinic', N'Severe acne breakout consultation', N'Pending')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (4, 3, 3, CAST(N'2026-06-15T13:00:00.0000000' AS DateTime2), N'General Clinic', N'Annual Physical Exam for pre-employment', N'Rescheduled')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (5, 1, 5, CAST(N'2026-05-10T15:00:00.0000000' AS DateTime2), N'Room 402 - Wellness Center', N'Work-related stress management', N'Cancelled')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (6, 5, 2, CAST(N'2026-04-20T11:00:00.0000000' AS DateTime2), N'Room 105 - Pedia Ward', N'Routine vaccination and weight check', N'Completed')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (7, 1, 1, CAST(N'2026-06-25T09:00:00.0000000' AS DateTime2), N'Room 301 - Heart Center', N'Follow-up on Amlodipine effectiveness', N'Pending')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (8, 6, 6, CAST(N'2026-06-26T10:00:00.0000000' AS DateTime2), N'General Clinic', N'Persistent cough and mild fever for 3 days', N'Completed')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (9, 6, 6, CAST(N'2026-06-25T09:00:00.0000000' AS DateTime2), N'General Clinic', N'Lower back pain', N'Cancelled')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (10, 6, 6, CAST(N'2026-06-24T10:00:00.0000000' AS DateTime2), N'General Clinic', N'Blood pressure monitoring', N'Rescheduled')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (11, 6, 6, CAST(N'2026-06-02T10:00:00.0000000' AS DateTime2), N'General Clinic', N'Frequent headaches', N'Pending')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (12, 6, 6, CAST(N'2026-06-15T17:00:00.0000000' AS DateTime2), N'General Clinic', N'Skin rash consultation', N'Pending')
INSERT [dbo].[Appointments] ([AppointmentID], [PID], [DID], [AppointmentDateTime], [Location], [Reason], [Status]) VALUES (13, 6, 6, CAST(N'2026-06-23T13:00:00.0000000' AS DateTime2), N'General Clinic', N'Routine annual physical exam', N'Cancelled')
SET IDENTITY_INSERT [dbo].[Appointments] OFF

-- Sample records for Invoices
SET IDENTITY_INSERT [dbo].[Invoices] ON 

INSERT [dbo].[Invoices] ([InvoiceID], [AID], [Amount], [Status], [DateIssued]) VALUES (1, 1, CAST(1500.00 AS Decimal(10, 2)), N'Paid', CAST(N'2026-05-26T18:03:13.4066667' AS DateTime2))
INSERT [dbo].[Invoices] ([InvoiceID], [AID], [Amount], [Status], [DateIssued]) VALUES (2, 2, CAST(500.00 AS Decimal(10, 2)), N'Paid', CAST(N'2026-05-26T18:03:13.4066667' AS DateTime2))
INSERT [dbo].[Invoices] ([InvoiceID], [AID], [Amount], [Status], [DateIssued]) VALUES (3, 6, CAST(800.00 AS Decimal(10, 2)), N'Paid', CAST(N'2026-05-26T18:03:13.4066667' AS DateTime2))
INSERT [dbo].[Invoices] ([InvoiceID], [AID], [Amount], [Status], [DateIssued]) VALUES (4, 3, CAST(1000.00 AS Decimal(10, 2)), N'Pending', CAST(N'2026-05-26T18:03:13.4066667' AS DateTime2))
INSERT [dbo].[Invoices] ([InvoiceID], [AID], [Amount], [Status], [DateIssued]) VALUES (5, 8, CAST(1000.00 AS Decimal(10, 2)), N'Paid', CAST(N'2026-05-29T16:42:09.9833333' AS DateTime2))
INSERT [dbo].[Invoices] ([InvoiceID], [AID], [Amount], [Status], [DateIssued]) VALUES (6, 9, CAST(1000.00 AS Decimal(10, 2)), N'Pending', CAST(N'2026-05-29T16:34:04.4300000' AS DateTime2))
INSERT [dbo].[Invoices] ([InvoiceID], [AID], [Amount], [Status], [DateIssued]) VALUES (7, 10, CAST(1000.00 AS Decimal(10, 2)), N'Pending', CAST(N'2026-05-29T16:34:22.8300000' AS DateTime2))
INSERT [dbo].[Invoices] ([InvoiceID], [AID], [Amount], [Status], [DateIssued]) VALUES (8, 11, CAST(1000.00 AS Decimal(10, 2)), N'Pending', CAST(N'2026-05-29T16:34:42.7800000' AS DateTime2))
INSERT [dbo].[Invoices] ([InvoiceID], [AID], [Amount], [Status], [DateIssued]) VALUES (9, 12, CAST(1000.00 AS Decimal(10, 2)), N'Pending', CAST(N'2026-05-29T16:35:01.6766667' AS DateTime2))
INSERT [dbo].[Invoices] ([InvoiceID], [AID], [Amount], [Status], [DateIssued]) VALUES (10, 13, CAST(1000.00 AS Decimal(10, 2)), N'Pending', CAST(N'2026-05-29T16:35:22.7766667' AS DateTime2))
SET IDENTITY_INSERT [dbo].[Invoices] OFF

-- Sample records for LabRequests
SET IDENTITY_INSERT [dbo].[LabRequests] ON 

INSERT [dbo].[LabRequests] ([RequestID], [AID], [Description], [DateRequested], [Status]) VALUES (1, 1, N'Lipid Profile and 12-lead ECG', CAST(N'2026-05-26T18:03:13.4000000' AS DateTime2), N'Completed')
INSERT [dbo].[LabRequests] ([RequestID], [AID], [Description], [DateRequested], [Status]) VALUES (2, 8, N'Chest X-Ray (PA View) to rule out pneumonia.', CAST(N'2026-05-29T16:39:16.0566667' AS DateTime2), N'Completed')
SET IDENTITY_INSERT [dbo].[LabRequests] OFF

-- Sample records for MedicalRecords
SET IDENTITY_INSERT [dbo].[MedicalRecords] ON 

INSERT [dbo].[MedicalRecords] ([RecordID], [AID], [Diagnosis], [Notes], [DateRecorded]) VALUES (1, 1, N'Mild Angina', N'Patient advised to rest, monitor BP daily, and avoid high-sodium foods.', CAST(N'2026-04-15T10:00:00.0000000' AS DateTime2))
INSERT [dbo].[MedicalRecords] ([RecordID], [AID], [Diagnosis], [Notes], [DateRecorded]) VALUES (2, 2, N'Viral Pharyngitis', N'Throat is visibly inflamed. Instructed to maintain hydration and rest.', CAST(N'2026-05-02T14:30:00.0000000' AS DateTime2))
INSERT [dbo].[MedicalRecords] ([RecordID], [AID], [Diagnosis], [Notes], [DateRecorded]) VALUES (3, 6, N'Healthy Development', N'Weight and height are normal for age. Cleared for scheduled vaccination.', CAST(N'2026-04-20T11:45:00.0000000' AS DateTime2))
INSERT [dbo].[MedicalRecords] ([RecordID], [AID], [Diagnosis], [Notes], [DateRecorded]) VALUES (4, 8, N'Acute Viral Bronchitis', N'Patient presents with mild fever and productive cough. Adivsed rest and hydration.', CAST(N'2026-05-29T16:39:16.0533333' AS DateTime2))
SET IDENTITY_INSERT [dbo].[MedicalRecords] OFF

-- Sample records for Prescriptions
SET IDENTITY_INSERT [dbo].[Prescriptions] ON 

INSERT [dbo].[Prescriptions] ([PrescriptionID], [AID], [DrugName], [Dosage], [Instructions], [DatePrescribed]) VALUES (1, 1, N'Amlodipine', N'5mg', N'Take 1 tablet daily after breakfast', CAST(N'2026-05-26T18:03:13.3966667' AS DateTime2))
INSERT [dbo].[Prescriptions] ([PrescriptionID], [AID], [DrugName], [Dosage], [Instructions], [DatePrescribed]) VALUES (2, 2, N'Paracetamol', N'500mg', N'Take 1 tablet every 4-6 hours as needed for fever or pain', CAST(N'2026-05-26T18:03:13.3966667' AS DateTime2))
INSERT [dbo].[Prescriptions] ([PrescriptionID], [AID], [DrugName], [Dosage], [Instructions], [DatePrescribed]) VALUES (3, 8, N'Paracetamol', N'500mg', N'Take 1 tablet every 8 hours as needed for fever', CAST(N'2026-05-29T16:39:16.0533333' AS DateTime2))
SET IDENTITY_INSERT [dbo].[Prescriptions] OFF
