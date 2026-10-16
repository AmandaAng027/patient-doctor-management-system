/*
    Patient-Doctor Management System (PDMS)
    Database schema setup

    Run this script first on a SQL Server instance where you have permission
    to create databases. It creates PDMS only if it does not already exist.
    For a clean install, use a new/empty PDMS database.
*/
USE [master];
GO
IF DB_ID(N'PDMS') IS NULL
BEGIN
    CREATE DATABASE [PDMS];
END;
GO
USE [PDMS];
GO

CREATE TABLE [dbo].[Appointments](
	[AppointmentID] [int] IDENTITY(1,1) NOT NULL,
	[PID] [int] NOT NULL,
	[DID] [int] NOT NULL,
	[AppointmentDateTime] [datetime2](7) NOT NULL,
	[Location] [nvarchar](100) NOT NULL,
	[Reason] [nvarchar](255) NOT NULL,
	[Status] [nvarchar](20) NOT NULL,
 CONSTRAINT [PK__Appointm__8ECDFCA29A882E4E] PRIMARY KEY CLUSTERED 
(
	[AppointmentID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Doctors]    Script Date: 29/05/2026 10:49:33 pm ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Doctors](
	[DoctorID] [int] IDENTITY(1,1) NOT NULL,
	[UID] [int] NOT NULL,
	[FirstName] [nvarchar](50) NOT NULL,
	[MiddleName] [nvarchar](50) NOT NULL,
	[LastName] [nvarchar](50) NOT NULL,
	[Gender] [char](1) NOT NULL,
	[ContactNumber] [varchar](11) NOT NULL,
	[Specialization] [nvarchar](100) NOT NULL,
	[LicenseNumber] [nvarchar](20) NOT NULL,
	[DefaultLocation] [nvarchar](100) NOT NULL,
 CONSTRAINT [PK__Doctors__2DC00EDF533D30C6] PRIMARY KEY CLUSTERED 
(
	[DoctorID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmergencyContacts]    Script Date: 29/05/2026 10:49:34 pm ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmergencyContacts](
	[ContactID] [int] IDENTITY(1,1) NOT NULL,
	[PID] [int] NOT NULL,
	[FullName] [nvarchar](150) NOT NULL,
	[ContactNumber] [varchar](11) NOT NULL,
	[Relationship] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK__Emergenc__5C6625BBCC1637A0] PRIMARY KEY CLUSTERED 
(
	[ContactID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Fee]    Script Date: 29/05/2026 10:49:34 pm ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Fee](
	[FeeID] [int] IDENTITY(1,1) NOT NULL,
	[DID] [int] NOT NULL,
	[BaseAmount] [decimal](10, 2) NOT NULL,
	[EffectiveDate] [datetime2](7) NOT NULL,
 CONSTRAINT [PK__Fee__B387B209FC878DD3] PRIMARY KEY CLUSTERED 
(
	[FeeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Invoices]    Script Date: 29/05/2026 10:49:34 pm ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Invoices](
	[InvoiceID] [int] IDENTITY(1,1) NOT NULL,
	[AID] [int] NOT NULL,
	[Amount] [decimal](10, 2) NOT NULL,
	[Status] [nvarchar](20) NOT NULL,
	[DateIssued] [datetime2](7) NOT NULL,
 CONSTRAINT [PK__Invoices__D796AAD5CAFC4143] PRIMARY KEY CLUSTERED 
(
	[InvoiceID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[LabRequests]    Script Date: 29/05/2026 10:49:34 pm ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[LabRequests](
	[RequestID] [int] IDENTITY(1,1) NOT NULL,
	[AID] [int] NOT NULL,
	[Description] [nvarchar](max) NULL,
	[DateRequested] [datetime2](7) NULL,
	[Status] [nvarchar](20) NULL,
 CONSTRAINT [PK__LabReque__33A8519A8D6A0506] PRIMARY KEY CLUSTERED 
(
	[RequestID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[MedicalRecords]    Script Date: 29/05/2026 10:49:34 pm ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[MedicalRecords](
	[RecordID] [int] IDENTITY(1,1) NOT NULL,
	[AID] [int] NOT NULL,
	[Diagnosis] [nvarchar](500) NULL,
	[Notes] [nvarchar](max) NULL,
	[DateRecorded] [datetime2](7) NOT NULL,
 CONSTRAINT [PK__MedicalR__FBDF78C93B20B074] PRIMARY KEY CLUSTERED 
(
	[RecordID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Patients]    Script Date: 29/05/2026 10:49:34 pm ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Patients](
	[PatientID] [int] IDENTITY(1,1) NOT NULL,
	[UID] [int] NOT NULL,
	[FirstName] [nvarchar](50) NOT NULL,
	[MiddleName] [nvarchar](50) NOT NULL,
	[LastName] [nvarchar](50) NOT NULL,
	[BirthDate] [date] NOT NULL,
	[Gender] [char](1) NOT NULL,
	[ContactNumber] [varchar](11) NOT NULL,
	[BloodType] [nvarchar](3) NOT NULL,
	[HomeAddress] [nvarchar](255) NOT NULL,
	[InitialConditions] [nvarchar](max) NULL,
	[InitialAllergies] [nvarchar](max) NULL,
	[InitialMedications] [nvarchar](max) NULL,
 CONSTRAINT [PK__Patients__970EC346E645FA6D] PRIMARY KEY CLUSTERED 
(
	[PatientID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Prescriptions]    Script Date: 29/05/2026 10:49:34 pm ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Prescriptions](
	[PrescriptionID] [int] IDENTITY(1,1) NOT NULL,
	[AID] [int] NOT NULL,
	[DrugName] [nvarchar](100) NULL,
	[Dosage] [nvarchar](50) NULL,
	[Instructions] [nvarchar](255) NULL,
	[DatePrescribed] [datetime2](7) NULL,
 CONSTRAINT [PK__Prescrip__40130812A598ECC1] PRIMARY KEY CLUSTERED 
(
	[PrescriptionID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Users]    Script Date: 29/05/2026 10:49:34 pm ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Users](
	[UserID] [int] IDENTITY(1,1) NOT NULL,
	[Email] [nvarchar](100) NOT NULL,
	[PasswordHash] [nvarchar](255) NOT NULL,
	[Role] [nvarchar](20) NOT NULL,
	[DateRegistered] [datetime2](7) NOT NULL,
 CONSTRAINT [PK__Users__1788CCAC92BE51B5] PRIMARY KEY CLUSTERED 
(
	[UserID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Doctors] ADD  CONSTRAINT [UQ__Doctors__C5B196035EBC4AB2] UNIQUE NONCLUSTERED 
(
	[UID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [UQ__Doctors__E8890166ADE87058]    Script Date: 29/05/2026 10:49:34 pm ******/
ALTER TABLE [dbo].[Doctors] ADD  CONSTRAINT [UQ__Doctors__E8890166ADE87058] UNIQUE NONCLUSTERED 
(
	[LicenseNumber] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [UQ__Emergenc__C57755218B188A81]    Script Date: 29/05/2026 10:49:34 pm ******/
ALTER TABLE [dbo].[EmergencyContacts] ADD  CONSTRAINT [UQ__Emergenc__C57755218B188A81] UNIQUE NONCLUSTERED 
(
	[PID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [UQ__Invoices__C69007C92029E28D]    Script Date: 29/05/2026 10:49:34 pm ******/
ALTER TABLE [dbo].[Invoices] ADD  CONSTRAINT [UQ__Invoices__C69007C92029E28D] UNIQUE NONCLUSTERED 
(
	[AID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [UQ__MedicalR__C69007C9263B6C68]    Script Date: 29/05/2026 10:49:34 pm ******/
ALTER TABLE [dbo].[MedicalRecords] ADD  CONSTRAINT [UQ__MedicalR__C69007C9263B6C68] UNIQUE NONCLUSTERED 
(
	[AID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [UQ__Patients__C5B196038DF50E45]    Script Date: 29/05/2026 10:49:34 pm ******/
ALTER TABLE [dbo].[Patients] ADD  CONSTRAINT [UQ__Patients__C5B196038DF50E45] UNIQUE NONCLUSTERED 
(
	[UID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [UQ__Users__A9D10534BC5E54DD]    Script Date: 29/05/2026 10:49:34 pm ******/
ALTER TABLE [dbo].[Users] ADD  CONSTRAINT [UQ__Users__A9D10534BC5E54DD] UNIQUE NONCLUSTERED 
(
	[Email] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Doctors] ADD  CONSTRAINT [DF__Doctors__Default__01142BA1]  DEFAULT ('General Clinic') FOR [DefaultLocation]
GO
ALTER TABLE [dbo].[Fee] ADD  CONSTRAINT [DF__Fee__EffectiveDa__4BAC3F29]  DEFAULT (getdate()) FOR [EffectiveDate]
GO
ALTER TABLE [dbo].[Invoices] ADD  CONSTRAINT [DF__Invoices__DateIs__5629CD9C]  DEFAULT (getdate()) FOR [DateIssued]
GO
ALTER TABLE [dbo].[LabRequests] ADD  CONSTRAINT [DF__LabReques__DateR__5EBF139D]  DEFAULT (getdate()) FOR [DateRequested]
GO
ALTER TABLE [dbo].[LabRequests] ADD  CONSTRAINT [DF__LabReques__Statu__60A75C0F]  DEFAULT ('Pending') FOR [Status]
GO
ALTER TABLE [dbo].[MedicalRecords] ADD  CONSTRAINT [DF__MedicalRe__DateR__5AEE82B9]  DEFAULT (getdate()) FOR [DateRecorded]
GO
ALTER TABLE [dbo].[Prescriptions] ADD  CONSTRAINT [DF__Prescript__DateP__6477ECF3]  DEFAULT (getdate()) FOR [DatePrescribed]
GO
ALTER TABLE [dbo].[Users] ADD  CONSTRAINT [DF__Users__DateRegis__398D8EEE]  DEFAULT (getdate()) FOR [DateRegistered]
GO
ALTER TABLE [dbo].[Appointments]  WITH CHECK ADD  CONSTRAINT [FK__Appointment__DID__4F7CD00D] FOREIGN KEY([DID])
REFERENCES [dbo].[Doctors] ([DoctorID])
GO
ALTER TABLE [dbo].[Appointments] CHECK CONSTRAINT [FK__Appointment__DID__4F7CD00D]
GO
ALTER TABLE [dbo].[Appointments]  WITH CHECK ADD  CONSTRAINT [FK__Appointment__PID__4E88ABD4] FOREIGN KEY([PID])
REFERENCES [dbo].[Patients] ([PatientID])
GO
ALTER TABLE [dbo].[Appointments] CHECK CONSTRAINT [FK__Appointment__PID__4E88ABD4]
GO
ALTER TABLE [dbo].[Doctors]  WITH CHECK ADD  CONSTRAINT [FK__Doctors__UID__4316F928] FOREIGN KEY([UID])
REFERENCES [dbo].[Users] ([UserID])
GO
ALTER TABLE [dbo].[Doctors] CHECK CONSTRAINT [FK__Doctors__UID__4316F928]
GO
ALTER TABLE [dbo].[EmergencyContacts]  WITH CHECK ADD  CONSTRAINT [FK__EmergencyCo__PID__47DBAE45] FOREIGN KEY([PID])
REFERENCES [dbo].[Patients] ([PatientID])
GO
ALTER TABLE [dbo].[EmergencyContacts] CHECK CONSTRAINT [FK__EmergencyCo__PID__47DBAE45]
GO
ALTER TABLE [dbo].[Fee]  WITH CHECK ADD  CONSTRAINT [FK__Fee__DID__4AB81AF0] FOREIGN KEY([DID])
REFERENCES [dbo].[Doctors] ([DoctorID])
GO
ALTER TABLE [dbo].[Fee] CHECK CONSTRAINT [FK__Fee__DID__4AB81AF0]
GO
ALTER TABLE [dbo].[Invoices]  WITH CHECK ADD  CONSTRAINT [FK__Invoices__AID__5441852A] FOREIGN KEY([AID])
REFERENCES [dbo].[Appointments] ([AppointmentID])
GO
ALTER TABLE [dbo].[Invoices] CHECK CONSTRAINT [FK__Invoices__AID__5441852A]
GO
ALTER TABLE [dbo].[LabRequests]  WITH CHECK ADD  CONSTRAINT [FK__LabRequests__AID__5DCAEF64] FOREIGN KEY([AID])
REFERENCES [dbo].[Appointments] ([AppointmentID])
GO
ALTER TABLE [dbo].[LabRequests] CHECK CONSTRAINT [FK__LabRequests__AID__5DCAEF64]
GO
ALTER TABLE [dbo].[MedicalRecords]  WITH CHECK ADD  CONSTRAINT [FK__MedicalReco__AID__59FA5E80] FOREIGN KEY([AID])
REFERENCES [dbo].[Appointments] ([AppointmentID])
GO
ALTER TABLE [dbo].[MedicalRecords] CHECK CONSTRAINT [FK__MedicalReco__AID__59FA5E80]
GO
ALTER TABLE [dbo].[Patients]  WITH CHECK ADD  CONSTRAINT [FK__Patients__UID__3D5E1FD2] FOREIGN KEY([UID])
REFERENCES [dbo].[Users] ([UserID])
GO
ALTER TABLE [dbo].[Patients] CHECK CONSTRAINT [FK__Patients__UID__3D5E1FD2]
GO
ALTER TABLE [dbo].[Prescriptions]  WITH CHECK ADD  CONSTRAINT [FK__Prescriptio__AID__6383C8BA] FOREIGN KEY([AID])
REFERENCES [dbo].[Appointments] ([AppointmentID])
GO
ALTER TABLE [dbo].[Prescriptions] CHECK CONSTRAINT [FK__Prescriptio__AID__6383C8BA]
GO
ALTER TABLE [dbo].[Appointments]  WITH CHECK ADD  CONSTRAINT [CK__Appointme__Statu__5070F446] CHECK  (([Status]='Rescheduled' OR [Status]='Cancelled' OR [Status]='Completed' OR [Status]='Pending'))
GO
ALTER TABLE [dbo].[Appointments] CHECK CONSTRAINT [CK__Appointme__Statu__5070F446]
GO
ALTER TABLE [dbo].[Doctors]  WITH CHECK ADD  CONSTRAINT [CHK_DoctorContact] CHECK  (([ContactNumber] like '09[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'))
GO
ALTER TABLE [dbo].[Doctors] CHECK CONSTRAINT [CHK_DoctorContact]
GO
ALTER TABLE [dbo].[Doctors]  WITH CHECK ADD  CONSTRAINT [CK__Doctors__Gender__440B1D61] CHECK  (([Gender]='F' OR [Gender]='M'))
GO
ALTER TABLE [dbo].[Doctors] CHECK CONSTRAINT [CK__Doctors__Gender__440B1D61]
GO
ALTER TABLE [dbo].[EmergencyContacts]  WITH CHECK ADD  CONSTRAINT [CHK_EmergencyContact] CHECK  (([ContactNumber] like '09[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'))
GO
ALTER TABLE [dbo].[EmergencyContacts] CHECK CONSTRAINT [CHK_EmergencyContact]
GO
ALTER TABLE [dbo].[Invoices]  WITH CHECK ADD  CONSTRAINT [CK_Invoices_Status] CHECK  (([Status]='Cancelled' OR [Status]='Paid' OR [Status]='Processing' OR [Status]='Pending'))
GO
ALTER TABLE [dbo].[Invoices] CHECK CONSTRAINT [CK_Invoices_Status]
GO
ALTER TABLE [dbo].[LabRequests]  WITH CHECK ADD  CONSTRAINT [CK__LabReques__Statu__5FB337D6] CHECK  (([Status]='Completed' OR [Status]='Pending'))
GO
ALTER TABLE [dbo].[LabRequests] CHECK CONSTRAINT [CK__LabReques__Statu__5FB337D6]
GO
ALTER TABLE [dbo].[Patients]  WITH CHECK ADD  CONSTRAINT [CK__Patients__Gender__3E52440B] CHECK  (([Gender]='F' OR [Gender]='M'))
GO
ALTER TABLE [dbo].[Patients] CHECK CONSTRAINT [CK__Patients__Gender__3E52440B]
GO
ALTER TABLE [dbo].[Users]  WITH CHECK ADD  CONSTRAINT [CK__Users__Role__38996AB5] CHECK  (([Role]='Doctor' OR [Role]='Patient'))
GO
ALTER TABLE [dbo].[Users] CHECK CONSTRAINT [CK__Users__Role__38996AB5]
GO
USE [master]
GO
ALTER DATABASE [PDMS] SET  READ_WRITE 
GO
