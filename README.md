# Patient-Doctor Management System (PDMS)

## About the Project

The Patient-Doctor Management System (PDMS) is a desktop application developed as an academic project by Amanda Ang, spanning November 2025 to June 2026 (See the [Thesis Paper](docs/pdms_thesis.pdf)). It is a prototype that is designed to help small clinics in the Philippines, especially in rural areas, manage patient information and organize basic clinic operations in one system.

The application was developed using Python, Tkinter, and Microsoft SQL Server.

## Features

- Patient and doctor accounts
- Appointment management
- Patient medical records
- Consultation and diagnosis records
- Prescription management
- Laboratory requests
- Billing and invoices
- Database storage using Microsoft SQL Server

## Technology Stack

- Programming Language: **Python**
- GUI Framework: **Tkinter**
- Database: **Microsoft SQL Server**
- Database Connectivity: **PyODBC**
- PDF Generation: **FPDF**
- Image Processing: **Pillow (PIL)**
- Authentication Security: **Werkzeug password hashing**
- Calendar Widget: **tkcalendar**

## Installation and Setup

Please refer to the following files for the setup instructions and system requirements:

- [Installation Guide](docs/installation_guide.md)
- [Minimum System Specifications](docs/min_system_specs.md)



## Project Files

- `main.py` – main application
- `data_access_layer.py` – database connection and query operations
- `PDMS_LOGO.png` – project logo

## Notes

This project was developed for academic purposes. The application requires a configured Microsoft SQL Server database to run.

Use fictional test data when testing the system. This project is not intended to replace a professionally validated clinical information system.
