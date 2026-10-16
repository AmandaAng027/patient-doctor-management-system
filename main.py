import tkinter as tk
from tkinter import ttk, messagebox
import re
import sys
import os
import platform
import subprocess
from datetime import datetime, date
from fpdf import FPDF
from PIL import Image, ImageTk, ImageDraw
from werkzeug.security import generate_password_hash, check_password_hash
from tkcalendar import Calendar


try:
    from data_access_layer import DataAccessLayer
except ImportError as err:
    DataAccessLayer = None
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Import Error", f"Could not import data_access_layer.py.\n\nError: {err}")
    sys.exit()


def resize_image(path, size):
    """resize an image to fit nicely and clear."""
    try:
        img = Image.open(path)
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as err:
        print(f"Error loading image {path}: {err}")
        return None


def generate_pdf(appointment_id):
    """generates PDF for a specific appointment, used in medical records tab"""
    dal = DataAccessLayer()
    try:
        dal.open()

        #fetch details from the database.
        query_info = """
            SELECT a.AppointmentDateTime,
                   p.FirstName AS PatFirst, p.LastName AS PatLast, p.BirthDate, p.Gender,
                   d.FirstName AS DocFirst, d.LastName AS DocLast, d.LicenseNumber, d.Specialization
            FROM Appointments a
            JOIN Patients p ON a.PID = p.PatientID
            JOIN Doctors d ON a.DID = d.DoctorID
            WHERE a.AppointmentID = ?
        """
        info = dal.execute_query(query_info, appointment_id)

        if not info:
            messagebox.showerror("Error", "Could not fetch details for PDF.")
            return

        record = info[0]
        consult_date = record[0].strftime("%B %d, %Y")
        pat_name = f"{record[1]} {record[2]}"
        dob = record[3]
        age = (datetime.now().date() - dob).days // 365 if dob else "N/A"
        gender = "Female" if record[4] == 'F' else "Male"
        doc_name = f"Dr. {record[5]} {record[6]}"
        doc_license = record[7]
        doc_spec = record[8]

        recs = dal.execute_query("SELECT Diagnosis, Notes FROM MedicalRecords WHERE AID=?", appointment_id)
        diag = recs[0][0] if recs and recs[0][0] else "No Diagnosis Provided"
        notes = recs[0][1] if recs and recs[0][1] else "No Consultation Notes"

        rx_rows = dal.execute_query("SELECT DrugName, Dosage, Instructions FROM Prescriptions WHERE AID=?",
                                    appointment_id)
        lab_rows = dal.execute_query("SELECT Description FROM LabRequests WHERE AID=?", appointment_id)

        pdf = FPDF()
        pdf.add_page()

        #render logo and header
        if os.path.exists("PDMS_LOGO.png"):
            pdf.image("PDMS_LOGO.png", x=10, y=8, w=25)

        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 10, "MEDICAL PRESCRIPTION & REQUEST", ln=True, align="R")
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"{doc_name} | {doc_spec}", ln=True, align="R")
        pdf.cell(0, 5, f"Lic No: {doc_license}", ln=True, align="R")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)

        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(100, 8, f" Patient: {pat_name}", border=1, fill=True)
        pdf.cell(45, 8, f" Age/Sex: {age} / {gender[0]}", border=1, fill=True)
        pdf.cell(45, 8, f" Date: {consult_date}", border=1, ln=True, fill=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Diagnosis:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, diag)
        pdf.ln(2)

        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Consultation Notes:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, notes)
        pdf.ln(10)

        if rx_rows:
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 8, "Rx", ln=True)
            for rx in rx_rows:
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 6, f"{rx[0]} ({rx[1]})", ln=True)
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(0, 6, f"Sig: {rx[2]}")
                pdf.ln(3)

        if lab_rows:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Laboratory / Diagnostic Requests:", ln=True)
            pdf.set_font("Arial", "", 11)
            for l in lab_rows:
                pdf.multi_cell(0, 6, f"[ ] {l[0]}")
            pdf.ln(10)

        pdf.ln(15)

        #render doctor signature
        sig_file = f"signature_AID_{appointment_id}.png"
        if os.path.exists(sig_file):
            pdf.image(sig_file, x=135, y=pdf.get_y() - 15, w=50)

        pdf.set_font("Arial", "B", 11)
        pdf.cell(130)
        pdf.cell(60, 5, "_______________________", ln=True, align="C")
        pdf.cell(130)
        pdf.cell(60, 6, doc_name, ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(130)
        pdf.cell(60, 5, f"Lic. No: {doc_license}", ln=True, align="C")

        #the pdf opens in Windows
        file_name = f"Medical_Document_{appointment_id}.pdf"
        pdf.output(file_name)

        if platform.system() == 'Darwin':
            subprocess.call(('open', file_name))
        elif platform.system() == 'Windows':
            os.startfile(file_name)
        else:
            subprocess.call(('xdg-open', file_name))

    except Exception as err:
        messagebox.showerror("PDF Error", f"Could not generate document: {err}")
    finally:
        dal.close()


def open_main_window(email, role):
    """send the user to the right portal for their role"""
    if role == "Patient":
        main_win = tk.Tk()
        PatientMainWindow(main_win, email)
        main_win.mainloop()
    elif role == "Doctor":
        main_win = tk.Tk()
        DoctorMainWindow(main_win, email)
        main_win.mainloop()


class RescheduleWindow:
    """a modal window that allows doctors to reschedule an appointment to a new date and time"""

    def __init__(self, parent_win, appointment_id, current_date_str, doctor_id, refresh_callback):
        self.win = tk.Toplevel(parent_win)
        self.win.title("Reschedule Appointment")
        self.win.geometry("400x450")
        self.win.configure(bg="white")
        self.win.grab_set()

        self.aid = appointment_id
        self.did = doctor_id
        self.refresh_callback = refresh_callback

        main_frame = ttk.Frame(self.win, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="Select New Date/Time", font=("Open Sans", 12, "bold"),
                  style="DataLabel.TLabel").pack(pady=(0, 20))

        ttk.Label(main_frame, text="New Date:", style="DataLabel.TLabel").pack(anchor="w")
        self.ent_date = ttk.Entry(main_frame, width=20, state='readonly')
        self.ent_date.insert(0, current_date_str.split(' ')[0])
        self.ent_date.pack(anchor="w", pady=(5, 15))

        ttk.Button(main_frame, text="Choose Date", command=self.open_calendar, style="Accent.TButton").pack(
            anchor="w", pady=(0, 15))

        ttk.Label(main_frame, text="New Time:", style="DataLabel.TLabel").pack(anchor="w")
        self.time_var = tk.StringVar()
        self.cb_time = ttk.Combobox(main_frame, textvariable=self.time_var, state="readonly", width=28)
        self.cb_time.pack(anchor="w", pady=(5, 20))

        ttk.Button(main_frame, text="Confirm Reschedule", style="Accent.TButton", command=self.save_reschedule).pack(
            fill="x", pady=5)
        ttk.Button(main_frame, text="Cancel", command=self.win.destroy).pack(fill="x", pady=5)

        self.check_timeslots()

    def open_calendar(self):
        """opens the Calendar pop-up for selecting date"""
        CalendarPopup(self.win, self.ent_date, self.check_timeslots)

    def check_timeslots(self, event=None):
        """query the database to find available time slots for the selected date"""
        date_str = self.ent_date.get()
        if not date_str or not self.did:
            self.cb_time['values'] = []
            return

        #clinic hours
        all_slots = [f"{h:02d}:00" for h in range(8, 18)]
        booked_times = set()

        dal = DataAccessLayer()
        try:
            dal.open()
            query = """
                SELECT FORMAT(AppointmentDateTime, 'HH:mm')
                FROM Appointments
                WHERE DID = ? AND AppointmentDateTime >= ? AND AppointmentDateTime < DATEADD(DAY, 1, ?)
                AND AppointmentID != ? AND Status IN ('Pending', 'Rescheduled')
            """
            rows = dal.execute_query(query, self.did, date_str, date_str, self.aid)
            for row in rows:
                booked_times.add(row[0])
        except Exception as err:
            print(f"Failed to check time slots: {err}")
        finally:
            dal.close()

        display_slots = []
        first_available = -1

        for i, time in enumerate(all_slots):
            if time in booked_times:
                display_slots.append(f"{time} (Booked)")
            else:
                display_slots.append(f"{time} (Available)")
                if first_available == -1:
                    first_available = i

        self.cb_time['values'] = display_slots
        if first_available != -1:
            self.cb_time.current(first_available)
        else:
            self.cb_time.set("No slots available")

    def save_reschedule(self):
        """update the appointment with the new time"""
        date_str = self.ent_date.get().strip()
        time_display = self.cb_time.get().strip()

        if "Booked" in time_display or "No slots" in time_display:
            messagebox.showerror("Error", "Selected time slot is not available.")
            return

        try:
            time_str = time_display.split(' ')[0]
        except IndexError:
            return

        dal = DataAccessLayer()
        try:
            dal.open()
            query = "UPDATE Appointments SET AppointmentDateTime = ?, Status='Rescheduled' WHERE AppointmentID = ?"
            dal.execute(query, f"{date_str} {time_str}:00", self.aid)
            dal.commit()

            messagebox.showinfo("Success", "Rescheduled successfully.")
            self.refresh_callback()
            self.win.destroy()
        except Exception as err:
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()


class EditProfileWindow:
    """a modal window that allows a patient to edit their personal details"""

    def __init__(self, parent_win, patient_data, refresh_callback):
        self.win = tk.Toplevel(parent_win)
        self.win.title("Edit Profile")
        self.win.geometry("600x700")
        self.win.configure(bg="white")
        self.win.grab_set()

        self.data = patient_data
        self.refresh_callback = refresh_callback

        style = ttk.Style()
        style.configure("Edit.TLabel", background="white", font=("Open Sans", 10, "bold"), foreground="#333")

        main_frame = ttk.Frame(self.win, style="Card.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        #makes the window scrollable
        canvas = tk.Canvas(main_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Card.TFrame")

        scroll_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(scroll_frame, text="Edit Contact & History", font=("Open Sans", 14, "bold"), background="white",
                  foreground="#0078d7").pack(anchor="w", padx=20, pady=(20, 5))
        ttk.Separator(scroll_frame, orient="horizontal").pack(fill="x", padx=20, pady=10)

        def create_entry(label, current_val):
            ttk.Label(scroll_frame, text=label, style="Edit.TLabel").pack(anchor="w", padx=20, pady=(10, 2))
            entry = ttk.Entry(scroll_frame, width=50)
            entry.insert(0, current_val)
            entry.pack(anchor="w", padx=20, pady=0)
            return entry

        def create_text_area(label, current_val):
            ttk.Label(scroll_frame, text=label, style="Edit.TLabel").pack(anchor="w", padx=20, pady=(10, 2))
            txt = tk.Text(scroll_frame, height=4, width=58, font=("Open Sans", 9), relief="solid", bd=1)
            txt.insert("1.0", current_val)
            txt.pack(anchor="w", padx=20, pady=0)
            return txt

        #The form fields
        self.ent_phone = create_entry("My Contact Number:", self.data["Phone"])
        self.ent_address = create_entry("Home Address:", self.data["Address"])

        ttk.Separator(scroll_frame, orient="horizontal").pack(fill="x", padx=20, pady=20)

        self.ent_em_name = create_entry("Emergency Contact Name:", self.data["EmergencyName"])
        self.ent_em_phone = create_entry("Emergency Contact Number:", self.data["EmergencyPhone"])
        self.ent_em_rel = create_entry("Relationship:", self.data["Relation"])

        ttk.Separator(scroll_frame, orient="horizontal").pack(fill="x", padx=20, pady=20)

        self.txt_cond = create_text_area("Known Medical Conditions:", self.data["Conditions"])
        self.txt_alg = create_text_area("Allergies:", self.data["Allergies"])
        self.txt_meds = create_text_area("Current Medications:", self.data["Medications"])

        btn_frame = ttk.Frame(scroll_frame, style="Card.TFrame")
        btn_frame.pack(fill="x", padx=20, pady=30)
        ttk.Button(btn_frame, text="Save Changes", style="Accent.TButton", command=self.save_changes).pack(fill="x",
                                                                                                           ipady=5)

    def save_changes(self):
        """save the updated patient profile in the database"""
        phone = self.ent_phone.get().strip()
        address = self.ent_address.get().strip()
        em_name = self.ent_em_name.get().strip()
        em_phone = self.ent_em_phone.get().strip()
        em_rel = self.ent_em_rel.get().strip()
        cond = self.txt_cond.get("1.0", tk.END).strip()
        alg = self.txt_alg.get("1.0", tk.END).strip()
        meds = self.txt_meds.get("1.0", tk.END).strip()

        #data validations
        if not all([phone, address, em_name, em_phone, em_rel]):
            messagebox.showerror("Error", "Fields cannot be empty.")
            return

        if len(em_name) > 50 or len(em_rel) > 50:
            messagebox.showerror("Invalid Input",
                                 "Emergency Contact Name and Relationship must be 50 characters or less.")
            return

        if address and len(address) > 255:
            messagebox.showerror("Invalid Input", "Home address is too long. Please keep it under 255 characters.")
            return

        if not re.match(r'^09\d{9}$', phone):
            messagebox.showerror("Invalid Input",
                                 "Your contact number must be exactly 11 digits, start with '09', "
                                 "and contain no dashes or spaces.")
            return

        if not re.match(r'^09\d{9}$', em_phone):
            messagebox.showerror("Invalid Input",
                                 "Emergency contact number must be exactly 11 digits, start with '09', "
                                 "and contain no dashes or spaces.")
            return

        dal = DataAccessLayer()
        try:
            dal.open()

            sql_patient = ("UPDATE Patients SET ContactNumber=?, HomeAddress=?, InitialConditions=?, "
                           "InitialAllergies=?, InitialMedications=? WHERE PatientID=?")
            dal.execute(sql_patient, phone, address, cond, alg, meds, self.data["ID"])

            sql_em = "UPDATE EmergencyContacts SET FullName=?, ContactNumber=?, Relationship=? WHERE PID=?"
            dal.execute(sql_em, em_name, em_phone, em_rel, self.data["ID"])

            dal.commit()

            messagebox.showinfo("Success", "Profile updated successfully.")
            self.refresh_callback()
            self.win.destroy()
        except Exception as err:
            dal.rollback()
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()


class CalendarPopup:
    """Calendar popup for appointment tabs"""
    def __init__(self, parent, entry_widget, callback):
        self.entry = entry_widget
        self.callback = callback

        self.top = tk.Toplevel(parent)
        self.top.title("Select Date")
        self.top.configure(bg="white")
        self.top.grab_set()

        self.cal = Calendar(self.top, selectmode='day', date_pattern='yyyy-mm-dd', font="Arial 10", locale='en_US',
                            mindate=date.today())
        self.cal.pack(padx=10, pady=10)
        ttk.Button(self.top, text="Confirm", style="Accent.TButton", command=self.select_date).pack(pady=10)

    def select_date(self):
        selected_date = self.cal.get_date()
        self.entry.config(state='normal')
        self.entry.delete(0, tk.END)
        self.entry.insert(0, selected_date)
        self.entry.config(state='readonly')

        self.callback()
        self.top.destroy()

class PatientMainWindow:
    """The portal for Patient users. It handles viewing profile, appointments, records, and billing."""

    def __init__(self, root, email):
        self.details_wrapper = None
        self.root = root
        self.email = email
        self.patient_data = {}
        self.doctor_map = {}
        self.doc_locations = {}

        self.root.title("PDMS — Patient Portal")
        try:
            self.root.state('zoomed')
        except tk.TclError:
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        self.root.configure(bg="#f4f4f4")

        if not self.fetch_patient():
            self.root.destroy()
            return

        self.setup_styles()
        self.build_header()
        self.build_footer()
        self.build_navigation()

    def setup_styles(self):
        """set up the styles for the patient portal"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", font=("Open Sans", 10), background="#f4f4f4")
        style.configure("Header.TFrame", background="#0078d7")
        style.configure("HeaderTitle.TLabel", background="#0078d7", foreground="white", font=("Open Sans", 16, "bold"))
        style.configure("HeaderSlogan.TLabel", background="#0078d7", foreground="white",
                        font=("Open Sans", 11, "italic"))
        style.configure("HeaderUser.TLabel", background="#0078d7", foreground="#e0e0e0", font=("Open Sans", 10, "bold"))
        style.configure("TNotebook", background="#f4f4f4", borderwidth=0)
        style.configure("TNotebook.Tab", padding=[20, 5], font=("Open Sans", 10), background="#d9d9d9",
                        foreground="#003366", borderwidth=1, relief="solid")
        style.map("TNotebook.Tab", background=[("selected", "#f4f4f4")], foreground=[("selected", "#0078d7")],
                  expand=[("selected", [1, 1, 1, 0])])
        style.configure("Card.TFrame", background="white", relief="solid", bordercolor="#e0e0e0", borderwidth=1)
        style.configure("Section.TLabel", background="white", font=("Open Sans", 12, "bold"), foreground="#0078d7")
        style.configure("DataLabel.TLabel", background="white", font=("Open Sans", 10, "bold"), foreground="#333")
        style.configure("ValueLabel.TLabel", background="white", font=("Open Sans", 10), foreground="#555")
        style.configure("Quote.TLabel", background="white", font=("Open Sans", 10, "italic"), foreground="#0078d7")
        style.configure("Desc.TLabel", background="white", font=("Open Sans", 9), foreground="#777")
        style.configure("Accent.TButton", font=("Open Sans", 10, "bold"), background="#0078d7", foreground="white",
                        borderwidth=0)
        style.map("Accent.TButton", background=[('active', '#005fa3')])
        style.configure("Success.TButton", font=("Open Sans", 9, "bold"), background="#28a745", foreground="white",
                        borderwidth=0)
        style.map("Success.TButton", background=[('active', '#218838')])
        style.configure("Danger.TButton", font=("Open Sans", 9), background="#d9534f", foreground="white",
                        borderwidth=0)
        style.map("Danger.TButton", background=[('active', '#c9302c')])
        style.configure("Warn.TButton", font=("Open Sans", 9), background="#ffc107", foreground="black", borderwidth=0)
        style.map("Warn.TButton", background=[('active', '#e0a800')])
        style.configure("Treeview.Heading", font=("Open Sans", 10, "bold"), background="#e0e0e0")
        style.configure("Treeview", font=("Open Sans", 10), rowheight=30)

    def fetch_patient(self):
        """get the patient's profile from the database"""
        dal = DataAccessLayer()
        try:
            dal.open()
            query = """
                SELECT p.PatientID, p.FirstName, p.MiddleName, p.LastName, p.BirthDate, p.Gender, p.BloodType, 
                       p.HomeAddress, p.ContactNumber, p.InitialConditions, p.InitialAllergies, p.InitialMedications,
                       ec.FullName, ec.ContactNumber, ec.Relationship
                FROM Users u JOIN Patients p ON u.UserID = p.UID LEFT JOIN EmergencyContacts ec ON p.PatientID = ec.PID 
                WHERE u.Email = ?
            """
            rows = dal.execute_query(query, self.email)
            if rows:
                record = rows[0]
                mid_str = f"{record[2]} " if record[2] else ""

                self.patient_data = {
                    "ID": record[0],
                    "FullName": f"{record[1]} {mid_str}{record[3]}",
                    "FirstName": record[1],
                    "DOB": record[4],
                    "Gender": record[5],
                    "BloodType": record[6] if record[6] else "N/A",
                    "Address": record[7],
                    "Phone": record[8],
                    "Conditions": record[9] if record[9] else "None",
                    "Allergies": record[10] if record[10] else "None",
                    "Medications": record[11] if record[11] else "None",
                    "EmergencyName": record[12] if record[12] else "Not set",
                    "EmergencyPhone": record[13] if record[13] else "N/A",
                    "Relation": record[14] if record[14] else "N/A"
                }
                return True
            return False
        except Exception as err:
            messagebox.showerror("Data Error", str(err))
            return False
        finally:
            dal.close()

    def build_header(self):
        """creates the top header"""
        header_frame = ttk.Frame(self.root, style="Header.TFrame", padding=(15, 10))
        header_frame.pack(fill="x")

        left_frame = ttk.Frame(header_frame, style="Header.TFrame")
        left_frame.pack(side="left")

        self.logo_img = resize_image("PDMS_LOGO.png", (50, 50))
        if self.logo_img:
            lbl_logo = tk.Label(left_frame, image=self.logo_img, bg="#0078d7", bd=0)
            lbl_logo.pack(side="left", padx=(0, 10))

        title_frame = ttk.Frame(left_frame, style="Header.TFrame")
        title_frame.pack(side="left")
        ttk.Label(title_frame, text="Patient", style="HeaderTitle.TLabel").pack(anchor="w")
        ttk.Label(title_frame, text="Portal", style="HeaderTitle.TLabel").pack(anchor="w")

        center_frame = ttk.Frame(header_frame, style="Header.TFrame")
        center_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(center_frame, text='"Patients are our priority, your health is our mission."',
                  style="HeaderSlogan.TLabel").pack(anchor="center")

        right_frame = ttk.Frame(header_frame, style="Header.TFrame")
        right_frame.pack(side="right")
        ttk.Label(right_frame, text=f"Hi, {self.patient_data.get('FullName', 'User')}", style="HeaderUser.TLabel").pack(
            side="left", padx=(0, 15))
        ttk.Button(right_frame, text="Logout", style="Danger.TButton", command=self.logout).pack(side="left")

    def build_footer(self):
        """creates the footer"""
        footer_frame = tk.Frame(self.root, bg="#f4f4f4")
        footer_frame.pack(side="bottom", fill="x", pady=(0, 10))
        tk.Label(footer_frame,
                 text="📞 Need assistance or have clinic inquiries? Contact our support desk at (02) 8123-4567.",
                 font=("Open Sans", 9, "italic"), bg="#f4f4f4", fg="#777777").pack(anchor="center")

    def build_navigation(self):
        """build the main tabbed interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_profile = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_profile, text="  My Profile  ")
        self.build_profile()

        self.tab_appointments = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_appointments, text="  Appointments  ")
        self.build_appointments()

        self.tab_records = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_records, text="  Medical Records  ")
        self.build_records()

        self.tab_billing = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_billing, text="  Billing  ")
        self.build_billing()

    def build_profile(self):
        """fill the profile tab with the user's details"""
        main_frame = ttk.Frame(self.tab_profile, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)

        header_row = ttk.Frame(main_frame, style="Card.TFrame")
        header_row.pack(fill="x", pady=(0, 10))
        ttk.Label(header_row, text="My Profile Information", font=("Open Sans", 18, "bold"),
                  style="DataLabel.TLabel").pack(anchor="w")
        ttk.Label(header_row, text="View your personal details and self-reported medical history.",
                  style="Desc.TLabel").pack(anchor="w")

        import random
        ttk.Label(header_row, text=random.choice(
            ["🌿 Drink plenty of water today!", "🍎 Health is wealth.", "💤 Rest is productive."]),
                  style="Quote.TLabel").pack(anchor="w", pady=(5, 0))
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=15)

        content_grid = ttk.Frame(main_frame, style="Card.TFrame")
        content_grid.pack(fill="both", expand=True)
        content_grid.columnconfigure(0, weight=1)
        content_grid.columnconfigure(1, weight=1)

        left_col = ttk.Frame(content_grid, style="Card.TFrame")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        self.create_grid(left_col, "Personal Details", [
            ("Full Name:", self.patient_data["FullName"]),
            ("Date of Birth:", str(self.patient_data["DOB"])),
            ("Gender:", "Female" if self.patient_data["Gender"] == 'F' else "Male"),
            ("Blood Type:", self.patient_data["BloodType"]),
            ("Address:", self.patient_data["Address"]),
            ("Phone:", self.patient_data["Phone"])
        ])

        ttk.Separator(left_col, orient="horizontal").pack(fill="x", pady=15)

        self.create_grid(left_col, "Emergency Contact", [
            ("Name:", self.patient_data["EmergencyName"]),
            ("Phone:", self.patient_data["EmergencyPhone"]),
            ("Relation:", self.patient_data["Relation"])
        ])

        right_col = ttk.Frame(content_grid, style="Card.TFrame")
        right_col.grid(row=0, column=1, sticky="nsew")
        ttk.Label(right_col, text="Self-Reported History", style="Section.TLabel").pack(anchor="w", pady=(0, 10))

        def create_med_box(parent, title, text, bg_color, border_color):
            frame = tk.Frame(parent, bg=bg_color, bd=1, relief="solid", highlightbackground=border_color,
                             highlightthickness=1)
            frame.pack(fill="x", pady=5)
            tk.Label(frame, text=title, font=("Open Sans", 10, "bold"), bg=bg_color, fg="#0056b3", anchor="w").pack(
                fill="x", padx=10, pady=5)
            tk.Label(frame, text=text, font=("Open Sans", 10), bg=bg_color, fg="#333", wraplength=400, anchor="w").pack(
                fill="x", padx=10, pady=(0, 8))

        create_med_box(right_col, "Conditions", self.patient_data["Conditions"], "#fff3cd", "#ffeeba")
        create_med_box(right_col, "Allergies", self.patient_data["Allergies"], "#f8d7da", "#f5c6cb")
        create_med_box(right_col, "Medications", self.patient_data["Medications"], "#d4edda", "#c3e6cb")

        ttk.Button(main_frame, text="Edit Profile Info", style="Accent.TButton", command=self.edit_profile).pack(
            side="right", pady=20)

    def create_grid(self, parent, title, fields):
        """helper to create a grid for personal details"""
        ttk.Label(parent, text=title, style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        grid = ttk.Frame(parent, style="Card.TFrame")
        grid.pack(fill="x")

        for index, (lbl, val) in enumerate(fields):
            ttk.Label(grid, text=lbl, style="DataLabel.TLabel").grid(row=index, column=0, sticky="w", pady=3)
            ttk.Label(grid, text=val, style="ValueLabel.TLabel").grid(row=index, column=1, sticky="w", padx=10, pady=3)

    def build_appointments(self):
        """build the appointment scheduling and viewing interface"""
        top_frame = ttk.Frame(self.tab_appointments, style="Card.TFrame", padding=20)
        top_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(top_frame, text="Appointment Schedule", font=("Open Sans", 18, "bold"),
                  style="DataLabel.TLabel").pack(anchor="w")
        ttk.Label(top_frame,
                  text="Track your upcoming visits, reschedule if necessary, or book a new consultation below.",
                  style="Desc.TLabel").pack(anchor="w", pady=(0, 15))

        #sorting dropdown
        filter_frame = ttk.Frame(top_frame, style="Card.TFrame")
        filter_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(filter_frame, text="Sort by Date:", style="DataLabel.TLabel").pack(side="left")
        self.sort_var = tk.StringVar()
        self.cb_sort = ttk.Combobox(filter_frame, textvariable=self.sort_var, state="readonly", width=15)
        self.cb_sort['values'] = ("Ascending", "Descending")
        self.cb_sort.current(0)
        self.cb_sort.pack(side="left", padx=10)
        self.cb_sort.bind("<<ComboboxSelected>>", lambda e: self.refresh_appointments())

        cols = ("ID", "Date", "Time", "Doctor", "Location", "Reason", "Status")
        self.tree = ttk.Treeview(top_frame, columns=cols, show="headings", height=6)

        for col in cols:
            self.tree.heading(col, text=col)

        self.tree.column("ID", width=0, stretch=False)
        self.tree.column("Date", width=90)
        self.tree.column("Time", width=80)
        self.tree.column("Doctor", width=150)
        self.tree.column("Location", width=100)
        self.tree.column("Reason", width=150)
        self.tree.column("Status", width=90)
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.tag_configure('Completed', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('Cancelled', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('Rescheduled', background='#fff3cd', foreground='#856404')
        self.tree.tag_configure('Pending', background='#cce5ff', foreground='#004085')

        self.tree.bind("<Button-1>",
                       lambda event: self.tree.selection_remove(self.tree.selection()) if not self.tree.identify_row(
                           event.y) else None)

        btn_frame = ttk.Frame(self.tab_appointments, style="Card.TFrame", padding=(20, 5))
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Cancel Appt", style="Danger.TButton", command=self.cancel_appointment).pack(
            side="right", padx=5)

        ttk.Button(btn_frame, text="Reschedule", style="Warn.TButton", command=self.open_reschedule).pack(
            side="right", padx=5)

        bottom_frame = ttk.LabelFrame(self.tab_appointments, text=" Book New Appointment ", padding=20)
        bottom_frame.pack(fill="x", padx=30, pady=20)

        ttk.Label(bottom_frame, text="Choose Doctor:", style="DataLabel.TLabel").grid(row=0, column=0, sticky="w",
                                                                                      pady=5)
        self.cb_doctor = ttk.Combobox(bottom_frame, state="readonly", width=35)
        self.cb_doctor.grid(row=0, column=1, sticky="w", pady=5)
        self.cb_doctor.bind("<<ComboboxSelected>>", lambda event: [self.check_timeslots(), self.update_fee_display()])

        ttk.Label(bottom_frame, text="Select Date:", style="DataLabel.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        date_cont = ttk.Frame(bottom_frame)
        date_cont.grid(row=1, column=1, sticky="w", pady=5)
        self.ent_book_date = ttk.Entry(date_cont, width=15, state='readonly')
        self.ent_book_date.pack(side="left", padx=(0, 5))
        self.ent_book_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ttk.Button(date_cont, text="📅", width=3, command=self.open_calendar, style="Accent.TButton").pack(
            side="left")

        ttk.Label(bottom_frame, text="Select Time:", style="DataLabel.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        self.cb_book_time = ttk.Combobox(bottom_frame, state="readonly", width=25)
        self.cb_book_time.grid(row=2, column=1, sticky="w")
        self.cb_book_time.bind("<<ComboboxSelected>>", self.validate_time)

        ttk.Label(bottom_frame, text="Reason:", style="DataLabel.TLabel").grid(row=3, column=0, sticky="nw", pady=5)
        self.ent_reason = ttk.Entry(bottom_frame, width=50)
        self.ent_reason.grid(row=3, column=1, sticky="w", pady=5)

        self.lbl_fee = ttk.Label(bottom_frame, text="Fee: -", font=("Open Sans", 11, "bold"), foreground="#0078d7")
        self.lbl_fee.grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))

        ttk.Button(bottom_frame, text="Book Appointment", style="Accent.TButton",
                   command=self.book_appointment).grid(row=4, column=1, sticky="e", pady=(10, 0))

        self.load_doctors()
        self.refresh_appointments()
        self.check_timeslots()
        self.update_fee_display()

    def update_fee_display(self):
        """Update the UI element that shows the doctor's base fee."""
        doc = self.cb_doctor.get()
        if not doc:
            self.lbl_fee.config(text="Fee: -")
            return

        did = self.doctor_map.get(doc)
        fee = 1000.00
        dal = DataAccessLayer()
        try:
            dal.open()
            rows = dal.execute_query("SELECT TOP 1 BaseAmount FROM Fee WHERE DID=? "
                                     "ORDER BY EffectiveDate DESC", did)
            if rows:
                fee = float(rows[0][0])
        except Exception as err:
            print(f"Fee fetch error: {err}")
        finally:
            dal.close()

        self.lbl_fee.config(text=f"Fee: ₱{fee:,.2f}")

    def build_records(self):
        """construct the medical records viewer."""
        main_frame = ttk.Frame(self.tab_records, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="My Medical History", font=("Open Sans", 18, "bold"), style="DataLabel.TLabel").pack(
            anchor="w")
        ttk.Label(main_frame, text="Select a visit on the left to view full consultation details.",
                  style="Desc.TLabel").pack(anchor="w", pady=(0, 15))
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(0, 15))

        paned = ttk.PanedWindow(main_frame, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left_frame = ttk.Frame(paned, width=300, relief="solid", borderwidth=1)
        paned.add(left_frame, weight=1)
        ttk.Label(left_frame, text="  Past Visits", font=("Open Sans", 11, "bold"), background="#e0e0e0",
                  padding=5).pack(fill="x")

        cols = ("ID", "Date", "Doctor")
        self.history_tree = ttk.Treeview(left_frame, columns=cols, show="headings", height=15)
        self.history_tree.heading("ID", text="ID")
        self.history_tree.column("ID", width=0, stretch=False)
        self.history_tree.heading("Date", text="Date")
        self.history_tree.column("Date", width=100)
        self.history_tree.heading("Doctor", text="Doctor")
        self.history_tree.column("Doctor", width=150)
        self.history_tree.pack(side="left", fill="both", expand=True)
        self.history_tree.bind("<<TreeviewSelect>>", self.load_visit)
        self.history_tree.bind("<Button-1>", lambda event: self.history_tree.selection_remove(
            self.history_tree.selection()) if not self.history_tree.identify_row(event.y) else None)

        self.details_wrapper = ttk.Frame(paned, style="Card.TFrame")
        paned.add(self.details_wrapper, weight=3)
        self.details_canvas = tk.Canvas(self.details_wrapper, bg="white", highlightthickness=0)
        self.details_scrollbar = ttk.Scrollbar(self.details_wrapper, orient="vertical",
                                               command=self.details_canvas.yview)
        self.details_frame = ttk.Frame(self.details_canvas, style="Card.TFrame", padding=20)
        self.details_window_id = self.details_canvas.create_window((0, 0), window=self.details_frame, anchor="nw")

        self.details_canvas.configure(yscrollcommand=self.details_scrollbar.set)
        self.details_canvas.pack(side="left", fill="both", expand=True)
        self.details_scrollbar.pack(side="right", fill="y")

        self.details_frame.bind("<Configure>", lambda event: self.details_canvas.configure(
            scrollregion=self.details_canvas.bbox("all")))
        self.details_canvas.bind("<Configure>", lambda event: self.details_canvas.itemconfig(self.details_window_id,
                                                                                             width=event.width))
        self.details_canvas.bind("<Enter>",
                                 lambda _: self.details_canvas.bind_all("<MouseWheel>", self.mousewheel))
        self.details_canvas.bind("<Leave>", lambda _: self.details_canvas.unbind_all("<MouseWheel>"))

        self.lbl_select_msg = ttk.Label(self.details_frame, text="👈 Select a visit from the list.",
                                        font=("Open Sans", 12), foreground="#888")
        self.lbl_select_msg.pack(expand=True, pady=100)

        self.refresh_history()

    def mousewheel(self, event):
        """The mousewheel scrolling."""
        self.details_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def refresh_history(self):
        """Fetch and populate the patient's past completed appointments."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        dal = DataAccessLayer()
        try:
            dal.open()
            query = """
                SELECT a.AppointmentID, a.AppointmentDateTime, d.FirstName, d.LastName
                FROM Appointments a JOIN Doctors d ON a.DID = d.DoctorID
                WHERE a.PID = ? AND a.Status = 'Completed' ORDER BY a.AppointmentDateTime DESC
            """
            rows = dal.execute_query(query, self.patient_data["ID"])
            for row in rows:
                self.history_tree.insert("", "end",
                                         values=(row[0], row[1].strftime("%Y-%m-%d"), f"Dr. {row[2]} {row[3]}"))
        except Exception as err:
            print(f"Error fetching history: {err}")
        finally:
            dal.close()

    def load_visit(self, event):
        """show the medical records for the selected visit"""
        sel = self.history_tree.selection()
        if not sel:
            return

        appointment_id = self.history_tree.item(sel[0])['values'][0]

        for widget in self.details_frame.winfo_children():
            widget.destroy()

        dal = DataAccessLayer()
        try:
            dal.open()
            visit_rows = dal.execute_query(
                "SELECT AppointmentDateTime, Location, Reason FROM Appointments "
                "WHERE AppointmentID=?", appointment_id)

            if visit_rows:
                visit = visit_rows[0]
                header_frame = ttk.Frame(self.details_frame)
                header_frame.pack(fill="x")
                ttk.Label(header_frame, text="Visit Details", style="Section.TLabel").pack(side="left")
                ttk.Button(header_frame, text="Download Rx & Lab PDF", style="Accent.TButton",
                           command=lambda: generate_pdf(appointment_id)).pack(side="right")

                info_frame = ttk.Frame(self.details_frame)
                info_frame.pack(fill="x", pady=5)
                ttk.Label(info_frame, text=f"Time: {visit[0].strftime('%B %d, %Y at %I:%M %p')}",
                          style="DataLabel.TLabel").pack(anchor="w")
                ttk.Label(info_frame, text=f"Location: {visit[1]}", style="DataLabel.TLabel").pack(anchor="w")
                ttk.Label(info_frame, text=f"Reason: {visit[2]}", style="ValueLabel.TLabel", wraplength=450).pack(
                    anchor="w")
                ttk.Separator(self.details_frame, orient="horizontal").pack(fill="x", pady=10)

            #diagnosis block
            recs = dal.execute_query("SELECT Diagnosis, Notes FROM MedicalRecords WHERE AID=?", appointment_id)
            diag_frame = ttk.LabelFrame(self.details_frame, text=" 🩺 Diagnosis ", padding=10)
            diag_frame.pack(fill="x", pady=5)

            if recs:
                ttk.Label(diag_frame, text=f"Condition: {recs[0][0]}", style="DataLabel.TLabel",
                          font=("Open Sans", 11, "bold")).pack(anchor="w")
                ttk.Label(diag_frame, text=f"Notes: {recs[0][1]}", style="ValueLabel.TLabel", wraplength=450).pack(
                    anchor="w")
            else:
                ttk.Label(diag_frame, text="No notes.", foreground="#777").pack(anchor="w")

            #prescription block
            rx = dal.execute_query("SELECT DrugName, Dosage, Instructions FROM Prescriptions WHERE AID=?",
                                   appointment_id)
            rx_frame = ttk.LabelFrame(self.details_frame, text=" 💊 Prescriptions ", padding=10)
            rx_frame.pack(fill="x", pady=5)

            if rx:
                for p in rx:
                    r_frame = ttk.Frame(rx_frame)
                    r_frame.pack(fill="x", pady=4)
                    ttk.Label(r_frame, text=f"• {p[0]} ({p[1]})", foreground="#0078d7",
                              font=("Open Sans", 10, "bold")).pack(anchor="w")
                    ttk.Label(r_frame, text=f"Instructions: {p[2]}", foreground="#555", wraplength=450).pack(anchor="w",
                                                                                                             padx=(
                                                                                                             15, 0))
            else:
                ttk.Label(rx_frame, text="No medications.", foreground="#777").pack(anchor="w")

            #lab block
            labs = dal.execute_query("SELECT Description, Status FROM LabRequests WHERE AID=?", appointment_id)
            lab_frame = ttk.LabelFrame(self.details_frame, text=" 🧪 Lab Requests ", padding=10)
            lab_frame.pack(fill="x", pady=5)

            if labs:
                for l in labs:
                    l_frame = ttk.Frame(lab_frame)
                    l_frame.pack(fill="x", pady=2)
                    ttk.Label(l_frame, text=f"• {l[0]}", width=40, wraplength=300).pack(side="left")
                    tk.Label(l_frame, text=f" {l[1]} ", bg="#28a745" if l[1] == 'Completed' else "#ffc107",
                             fg="white" if l[1] == 'Completed' else "black", font=("Arial", 8, "bold")).pack(
                        side="right")
            else:
                ttk.Label(lab_frame, text="No lab requests.", foreground="#777").pack(anchor="w")

        except Exception as err:
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()

    def build_billing(self):
        """builds billing and payments interface"""
        for widget in self.tab_billing.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.tab_billing, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Billing & Payments", font=("Open Sans", 18, "bold"), style="DataLabel.TLabel").pack(
            anchor="w")
        ttk.Label(main_frame, text="View outstanding balances. Select an invoice to pay or download as PDF.",
                  style="Desc.TLabel").pack(anchor="w", pady=(0, 15))

        cols = ("ID", "Date", "Time", "Doctor", "Reason", "Amount", "Status")
        self.bill_tree = ttk.Treeview(main_frame, columns=cols, show="headings", height=10)

        self.bill_tree.heading("ID", text="Invoice #")
        self.bill_tree.heading("Date", text="Date")
        self.bill_tree.heading("Time", text="Time")
        self.bill_tree.heading("Doctor", text="Doctor")
        self.bill_tree.heading("Reason", text="Reason")
        self.bill_tree.heading("Amount", text="Amount")
        self.bill_tree.heading("Status", text="Status")

        self.bill_tree.column("ID", width=80)
        self.bill_tree.column("Date", width=90)
        self.bill_tree.column("Time", width=80)
        self.bill_tree.column("Doctor", width=130)
        self.bill_tree.column("Reason", width=150)
        self.bill_tree.column("Amount", width=90, anchor="e")
        self.bill_tree.column("Status", width=90, anchor="center")
        self.bill_tree.pack(fill="both", expand=True)

        self.bill_tree.bind("<Button-1>", lambda event: self.bill_tree.selection_remove(
            self.bill_tree.selection()) if not self.bill_tree.identify_row(event.y) else None)

        dal = DataAccessLayer()
        try:
            dal.open()
            query = """
                SELECT i.InvoiceID, a.AppointmentDateTime, d.LastName, a.Reason, i.Amount, i.Status
                FROM Invoices i JOIN Appointments a ON i.AID = a.AppointmentID JOIN Doctors d ON a.DID = d.DoctorID
                WHERE a.PID = ?
            """
            rows = dal.execute_query(query, self.patient_data["ID"])
            total_due = 0.0

            for row in rows:
                if row[5] in ('Processing'):
                    total_due += float(row[4])
                self.bill_tree.insert("", "end", values=(
                f"INV-{row[0]:04d}", row[1].strftime("%Y-%m-%d"), row[1].strftime("%I:%M %p"), f"Dr. {row[2]}", row[3],
                f"₱{row[4]:,.2f}", row[5]))

            btn_frame = ttk.Frame(main_frame, padding=20)
            btn_frame.pack(fill="x")

            ttk.Button(btn_frame, text="Download Invoice PDF", style="Accent.TButton", command=self.download_invoice).pack(
                side="right", padx=10)
            ttk.Label(btn_frame, text=f"Total Pending: ₱{total_due:,.2f}", font=("Open Sans", 14, "bold"),
                      foreground="#d9534f").pack(side="right", padx=20)
        except Exception as err:
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()


    def download_invoice(self):
        """make and download a pdf receipt for a paid invoice"""
        sel = self.bill_tree.selection()
        if not sel:
            messagebox.showwarning("Select Bill", "Please select an invoice.")
            return

        item = self.bill_tree.item(sel[0])['values']
        if item[6] != 'Paid':
            messagebox.showwarning("Payment Required",
                                   "This invoice has not been paid yet.\n"
                                   "You can only download invoices that are marked as PAID.")
            return

        inv_id_raw = int(item[0].split('-')[1])
        dal = DataAccessLayer()
        try:
            dal.open()
            query = """
                SELECT i.InvoiceID, i.DateIssued, i.Amount, i.Status, p.FirstName AS PatFirst, p.LastName AS PatLast,
                       d.FirstName AS DocFirst, d.LastName AS DocLast, a.Location, a.AppointmentDateTime, a.Reason
                FROM Invoices i JOIN Appointments a ON i.AID = a.AppointmentID JOIN Patients p ON a.PID = p.PatientID
                JOIN Doctors d ON a.DID = d.DoctorID WHERE i.InvoiceID = ?
            """
            rows = dal.execute_query(query, inv_id_raw)

            if not rows:
                return

            record = rows[0]

            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", "B", 110)
            pdf.set_text_color(230, 255, 230)
            pdf.set_xy(0, 130)
            pdf.cell(0, 0, "P A I D", align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(10, 10)

            if os.path.exists("PDMS_LOGO.png"):
                pdf.image("PDMS_LOGO.png", x=10, y=8, w=35)

            pdf.set_font("Arial", "B", 24)
            pdf.cell(0, 15, "INVOICE", ln=True, align="R")
            pdf.set_font("Arial", "", 12)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 8, f"Invoice Number: INV-{record[0]:04d}", ln=True, align="R")
            pdf.cell(0, 8, f"Date Issued: {record[1].strftime('%B %d, %Y') if record[1] else 'N/A'}", ln=True,
                     align="R")
            pdf.set_text_color(40, 167, 69)
            pdf.cell(0, 8, "Status: PAID", ln=True, align="R")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(20)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(95, 10, "Billed To:", 0, 0)
            pdf.cell(95, 10, "Service Provider:", 0, 1)
            pdf.set_font("Arial", "", 12)
            pdf.cell(95, 8, f"{record[4]} {record[5]}", 0, 0)
            pdf.cell(95, 8, f"Dr. {record[6]} {record[7]}", 0, 1)
            pdf.cell(95, 8, f"Patient ID: P{self.patient_data['ID']}", 0, 0)
            pdf.cell(95, 8, record[8] if record[8] else "General Clinic", 0, 1)
            pdf.ln(20)

            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(90, 10, "Description", border=1, fill=True)
            pdf.cell(40, 10, "Consultation Date", border=1, align="C", fill=True)
            pdf.cell(60, 10, "Amount", border=1, align="R", fill=True)
            pdf.ln(10)

            pdf.set_font("Arial", "", 11)
            reason_str = record[10] if record[10] else "Medical Consultation"
            desc_text = f"Consultation: {reason_str}"

            x_start = pdf.get_x()
            y_start = pdf.get_y()

            pdf.multi_cell(90, 7.5, desc_text, border=1)
            row_height = pdf.get_y() - y_start

            pdf.set_xy(x_start + 90, y_start)
            pdf.cell(40, row_height, f"{record[9].strftime('%b %d, %Y')}", border=1, align="C")
            pdf.cell(60, row_height, f"PHP {float(record[2]):,.2f}", border=1, align="R")
            pdf.ln(row_height)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(130, 15, "TOTAL PAID:", border=0, align="R")
            pdf.cell(60, 15, f"PHP {float(record[2]):,.2f}", border=0, align="R")
            pdf.ln(30)

            pdf.set_font("Arial", "I", 10)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 10, "Patients are our priority, your health is our mission.", align="C", ln=True)

            file_name = f"Invoice_INV{record[0]:04d}.pdf"
            pdf.output(file_name)

            if platform.system() == 'Darwin':
                subprocess.call(('open', file_name))
            elif platform.system() == 'Windows':
                os.startfile(file_name)
            else:
                subprocess.call(('xdg-open', file_name))

        except Exception as err:
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()

    def open_calendar(self):
        """calendar pop-up for date selection"""
        CalendarPopup(self.root, self.ent_book_date, self.check_timeslots)

    def check_timeslots(self, event=None):
        """check available booking slots for the selected doctor and date"""
        doc = self.cb_doctor.get()
        date_val = self.ent_book_date.get()

        if not doc or not date_val:
            return

        did = self.doctor_map.get(doc)
        slots = [f"{h:02d}:00" for h in range(8, 18)]
        booked = set()
        dal = DataAccessLayer()

        try:
            dal.open()
            query = """
                SELECT FORMAT(AppointmentDateTime, 'HH:mm') 
                FROM Appointments 
                WHERE DID=? AND AppointmentDateTime >= ? 
                AND AppointmentDateTime < DATEADD(DAY, 1, ?) 
                AND Status IN ('Pending','Rescheduled')
            """
            rows = dal.execute_query(query, did, date_val, date_val)
            for row in rows:
                booked.add(row[0])
        except Exception as err:
            print(f"Error checking time slots: {err}")
        finally:
            dal.close()

        final_slots = []
        for slot in slots:
            if slot in booked:
                final_slots.append(f"{slot} (Booked)")
            else:
                final_slots.append(f"{slot} (Available)")

        self.cb_book_time['values'] = final_slots
        if final_slots:
            self.cb_book_time.current(0)

    def validate_time(self, event):
        """ensure the user cannot select a booked time slot"""
        if "(Booked)" in self.cb_book_time.get():
            messagebox.showwarning("Unavailable", "Slot booked.")
            self.cb_book_time.set("")

    def load_doctors(self):
        """fetch all doctors to populate the booking combobox"""
        dal = DataAccessLayer()
        try:
            dal.open()
            rows = dal.execute_query(
                "SELECT DoctorID, FirstName, LastName, Specialization, DefaultLocation FROM Doctors")

            self.doctor_map = {}
            self.doc_locations = {}
            display_list = []

            for row in rows:
                name = f"Dr. {row[1]} {row[2]} ({row[3]})"
                self.doctor_map[name] = row[0]
                self.doc_locations[row[0]] = row[4] if row[4] else "General Clinic"
                display_list.append(name)

            self.cb_doctor['values'] = display_list
            if display_list:
                self.cb_doctor.current(0)
        except Exception as err:
            print(f"Error loading doctors: {err}")
        finally:
            dal.close()

    def refresh_appointments(self):
        """display patient's upcoming and previous appointments"""
        for i in self.tree.get_children(): self.tree.delete(i)
        order_dir = "DESC" if hasattr(self, 'sort_var') and self.sort_var.get() == "Descending" else "ASC"
        dal = DataAccessLayer()
        try:
            dal.open()
            query = f"""
                        SELECT a.AppointmentID, a.AppointmentDateTime, d.FirstName, d.LastName, a.Location, a.Reason, a.Status 
                        FROM Appointments a JOIN Doctors d ON a.DID=d.DoctorID WHERE a.PID=? 
                        ORDER BY a.AppointmentDateTime {order_dir}
                    """
            rows = dal.execute_query(query, self.patient_data["ID"])
            for r in rows:
                self.tree.insert("", "end", values=(
                r[0], r[1].strftime("%Y-%m-%d"), r[1].strftime("%I:%M %p"), f"Dr. {r[2]} {r[3]}", r[4], r[5], r[6]),
                                 tags=(r[6],))
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            dal.close()

    def book_appointment(self):
        """saves a new appointment request into the database and create a pending invoice"""
        doc = self.cb_doctor.get()
        date_val = self.ent_book_date.get()
        time_display = self.cb_book_time.get()
        reason = self.ent_reason.get().strip()

        if not doc or not date_val or not time_display or not reason:
            messagebox.showerror("Error", "Fill all fields.")
            return

        if len(reason) > 255:
            messagebox.showerror("Invalid Input", "Reason is too long. Please summarize in under 255 characters.")
            return

        time_val = time_display.split(' ')[0]
        did = self.doctor_map.get(doc)
        dt = f"{date_val} {time_val}:00"
        loc = self.doc_locations.get(did, "Clinic Room 1")
        fee = 1000.00

        dal = DataAccessLayer()
        try:
            dal.open()
            rows = dal.execute_query("SELECT TOP 1 BaseAmount FROM Fee WHERE DID=? "
                                     "ORDER BY EffectiveDate DESC", did)
            if rows:
                fee = float(rows[0][0])

            dal.execute(
                "INSERT INTO Appointments (PID, DID, AppointmentDateTime, Location, Reason, Status) "
                "VALUES (?, ?, ?, ?, ?, 'Pending')",
                self.patient_data["ID"], did, dt, loc, reason
            )

            appointment_id = dal.fetch_one("SELECT @@IDENTITY")

            if appointment_id:
                dal.execute(
                    "INSERT INTO Invoices (AID, Amount, Status, DateIssued) VALUES (?, ?, 'Pending', GETDATE())",
                    appointment_id, fee)

            dal.commit()
            messagebox.showinfo("Success", f"Booked at {loc}!")

            self.refresh_appointments()
            self.build_billing()
            self.cb_doctor.set('')

            self.ent_book_date.config(state='normal')
            self.ent_book_date.delete(0, tk.END)
            self.ent_book_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.ent_book_date.config(state='readonly')

            self.cb_book_time.set('')
            self.ent_reason.delete(0, tk.END)
            self.lbl_fee.config(text="Fee: -")
            self.check_timeslots()

        except Exception as err:
            dal.rollback()
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()

    def cancel_appointment(self):
        """patient can cancel an appointment and drop the corresponding pending invoice"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select Appointment", "Please select an appointment to cancel.")
            return

        item = self.tree.item(sel[0])['values']
        status = item[6]
        appointment_id = item[0]

        if status == 'Cancelled':
            messagebox.showinfo("Info", "This appointment is already cancelled.")
            return
        if status == 'Completed':
            messagebox.showerror("Error", "Cannot cancel a completed appointment.")
            return

        if messagebox.askyesno("Cancel Appointment",
                               "Are you sure you want to cancel this appointment?\n\n"
                               "This action cannot be undone."):
            dal = DataAccessLayer()
            try:
                dal.open()
                dal.execute("UPDATE Appointments SET Status='Cancelled' WHERE AppointmentID=?", appointment_id)
                dal.execute("DELETE FROM Invoices WHERE AID=? AND Status='Processing'", appointment_id)
                dal.commit()
                messagebox.showinfo("Success", "Appointment cancelled successfully.")

                self.refresh_appointments()
                self.build_billing()
            except Exception as err:
                dal.rollback()
                messagebox.showerror("Error", f"Could not cancel appointment: {err}")
            finally:
                dal.close()

    def open_reschedule(self):
        """it allows the patient to reschedule a pending appointment"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select Appointment", "Please select an appointment to reschedule.",
                                   parent=self.root)
            return

        item = self.tree.item(sel[0])['values']
        appointment_id = item[0]
        current_date_str = str(item[1])
        status = item[6]

        if status == 'Cancelled':
            messagebox.showerror("Error", "You cannot reschedule a cancelled appointment.", parent=self.root)
            return
        if status == 'Completed':
            messagebox.showerror("Error", "You cannot reschedule a completed appointment. Please book a new visit.",
                                 parent=self.root)
            return
        if status not in ('Pending', 'Rescheduled'):
            messagebox.showerror("Error", "Only active/pending appointments can be rescheduled.", parent=self.root)
            return

        dal = DataAccessLayer()
        try:
            dal.open()
            did_rows = dal.execute_query("SELECT DID FROM Appointments WHERE AppointmentID=?", appointment_id)
            if not did_rows:
                messagebox.showerror("Error", "Could not locate doctor schedule.", parent=self.root)
                return
            did = did_rows[0][0]
        except Exception as err:
            messagebox.showerror("Error", f"Database error: {err}", parent=self.root)
            return
        finally:
            dal.close()

        RescheduleWindow(self.root, appointment_id, current_date_str, did, self.refresh_appointments)

    def edit_profile(self):
        """launch the edit profile window"""
        EditProfileWindow(self.root, self.patient_data, self.refresh_profile)

    def refresh_profile(self):
        """reload the data and rebuild the profile page"""
        if self.fetch_patient():
            for widget in self.tab_profile.winfo_children():
                widget.destroy()
            self.build_profile()

    def logout(self):
        """close the application and return to the login window"""
        self.root.destroy()
        open_login_window()

def open_login_window():
    login_win = tk.Tk()
    LoginWindow(login_win)
    login_win.mainloop()

class LoginWindow:
    """The authentication gateway for both Doctors and Patients users"""

    def __init__(self, login_win):
        self.login_win = login_win
        self.login_win.title("Patient-Doctor Portal")
        self.login_win.geometry("500x500")
        self.login_win.resizable(False, False)
        self.login_win.configure(bg="white")

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure(".", font=("Open Sans", 10), background="white")
        style.configure("TEntry", borderwidth=1, relief="solid", bordercolor="#cccccc", padding=5)
        style.map("TEntry", bordercolor=[('focus', '#0078d7')], relief=[('focus', 'solid')])
        style.configure("TCombobox", borderwidth=1, relief="solid", bordercolor="#cccccc", padding=5)
        style.map("TCombobox", bordercolor=[('focus', '#0078d7')])
        style.configure("Bold.TLabel", font=("Open Sans", 10, "bold"), background="white")
        style.configure("Sub.TLabel", font=("Open Sans", 10), foreground="#6e6e6e", background="white")
        style.configure("Small.TButton", font=("Open Sans", 9), background="#f0f0f0", bordercolor="#cccccc",
                        relief="solid")
        style.configure("Accent.TButton", font=("Open Sans", 10, "bold"), background="#0078d7", foreground="white",
                        borderwidth=0)
        style.map("Accent.TButton", background=[('active', '#005fa3')])

        header_frame = ttk.Frame(self.login_win)
        header_frame.pack(pady=(20, 10))

        self.logo_img = resize_image("PDMS_LOGO.png", (60, 60))
        if self.logo_img:
            lbl_logo = tk.Label(header_frame, image=self.logo_img, bg="white", bd=0)
            lbl_logo.pack(side="left", padx=(0, 10))

        text_frame = ttk.Frame(header_frame)
        text_frame.pack(side="left")
        ttk.Label(text_frame, text="Patient-Doctor", font=("Open Sans", 16, "bold"), foreground="#0078d7").pack(
            anchor="w")
        ttk.Label(text_frame, text="Management System", font=("Open Sans", 16, "bold"), foreground="#333").pack(
            anchor="w")
        ttk.Label(self.login_win, text="Sign in to access your dashboard.", style="Sub.TLabel").pack(pady=(0, 20))

        frame_main = ttk.Frame(self.login_win)
        frame_main.pack(pady=5, padx=40, fill="x")

        ttk.Label(frame_main, text="Login Role:", style="Bold.TLabel").pack(fill="x", pady=(5, 0))
        self.role_var = tk.StringVar()
        self.role_combo = ttk.Combobox(frame_main, textvariable=self.role_var, state="readonly", width=25,
                                       font=("Open Sans", 10))
        self.role_combo['values'] = ("Patient", "Doctor")
        self.role_combo.current(0)
        self.role_combo.pack(fill="x", ipady=4, pady=(5, 10))

        ttk.Label(frame_main, text="Email:", style="Bold.TLabel").pack(fill="x", pady=(5, 0))
        self.email = ttk.Entry(frame_main, width=28, font=("Open Sans", 10))
        self.email.pack(fill="x", pady=(5, 10))

        ttk.Label(frame_main, text="Password:", style="Bold.TLabel").pack(fill="x", pady=(5, 0))
        password_frame = ttk.Frame(frame_main)
        password_frame.pack(fill="x", pady=(5, 10))
        self.entry_password = ttk.Entry(password_frame, width=28, show="*", font=("Open Sans", 10))
        self.entry_password.pack(side=tk.LEFT, fill="x", expand=True)
        self.btn_show = ttk.Button(password_frame, text="Show", style="Small.TButton",
                                   command=self.toggle_password_visibility, width=6)
        self.btn_show.pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(frame_main, text="Log In", command=self.login_process, style="Accent.TButton").pack(fill="x",
                                                                                                       pady=10)

        ttk.Label(self.login_win, text="New user? Register here:", style="Sub.TLabel").pack(pady=(10, 0))
        frame_links = ttk.Frame(self.login_win)
        frame_links.pack()
        lbl_patient = ttk.Label(frame_links, text="Patient", font=("Open Sans", 9, "underline"), foreground="blue",
                                cursor="hand2")
        lbl_doctor = ttk.Label(frame_links, text="Doctor", font=("Open Sans", 9, "underline"), foreground="blue",
                               cursor="hand2")
        lbl_patient.grid(row=0, column=0, padx=5)
        lbl_doctor.grid(row=0, column=1, padx=5)

        lbl_patient.bind("<Button-1>", lambda event: self.open_registration("Patient"))
        lbl_doctor.bind("<Button-1>", lambda event: self.open_registration("Doctor"))
        self.login_win.bind('<Return>', self.login_process)

    def toggle_password_visibility(self):
        """toggle the password entry mask"""
        if self.entry_password.cget("show") == "*":
            self.entry_password.config(show="")
            self.btn_show.config(text="Hide")
        else:
            self.entry_password.config(show="*")
            self.btn_show.config(text="Show")

    def login_process(self, event=None):
        """validate login and open the user's portal"""
        email = self.email.get().strip()
        password = self.entry_password.get().strip()
        role = self.role_var.get()

        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password.")
            return

        dal = DataAccessLayer()
        try:
            dal.open()
            query = """
                SELECT UserID, Email, Role, PasswordHash
                FROM dbo.Users
                WHERE Email=? AND Role=?
            """
            records = dal.execute_query(query, email, role)

            if records and check_password_hash(records[0][3], password):
                self.login_win.destroy()
                open_main_window(email, role)
            else:
                messagebox.showerror(
                    "Error",
                    "Invalid credentials. Please try again."
                )
        except Exception as err:
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()

    def open_registration(self, user_type):
        """Route to the registration portal"""
        self.login_win.destroy()
        if user_type == "Patient":
            open_patient_registration()
        else:
            open_doctor_registration()


def open_patient_registration():
    """Loads the Patient Registration Window"""
    reg_win = tk.Tk()
    PatientRegistrationWindow(reg_win)
    reg_win.mainloop()


class PatientRegistrationWindow:
    """It inserts new patient profiles into the database"""

    def __init__(self, reg_win):
        self.reg_win = reg_win
        self.reg_win.title("Patient Registration")
        self.reg_win.geometry("570x670")
        self.reg_win.configure(bg="white")
        self.reg_win.resizable(False, False)

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure(".", font=("Open Sans", 10), background="white", fieldbackground="white", borderwidth=0,
                        focusthickness=0)
        style.configure("TEntry", borderwidth=1, relief="solid", bordercolor="#cccccc", padding=5)
        style.map("TEntry", bordercolor=[('focus', '#0078d7')], relief=[('focus', 'solid')])
        style.configure("TCombobox", borderwidth=1, relief="solid", bordercolor="#cccccc", padding=5)
        style.map("TCombobox", bordercolor=[('focus', '#0078d7')], selectbackground=[('!focus', 'white')],
                  selectforeground=[('!focus', 'black')])
        style.configure("TLabel", background="white")
        style.configure("Bold.TLabel", font=("Open Sans", 10, "bold"), background="white")
        style.configure("Sub.TLabel", font=("Open Sans", 10), foreground="#6e6e6e", background="white")
        style.configure("Small.TButton", font=("Open Sans", 9), padding=(5, 2), background="#f0f0f0",
                        bordercolor="#cccccc", relief="solid")
        style.map("Small.TButton", background=[('active', '#e0e0e0')])
        style.configure("Accent.TButton", font=("Open Sans", 10, "bold"), padding=(10, 5), background="#0078d7",
                        foreground="white", borderwidth=0)
        style.map("Accent.TButton", background=[('active', '#005fa3')])

        ttk.Label(self.reg_win, text="Create Account", font=("Open Sans", 16, "bold")).pack(pady=(20, 0))
        ttk.Label(self.reg_win, text="Join the Patient-Doctor Portal.", style="Sub.TLabel").pack(pady=(0, 15))

        main_scroll_frame = ttk.Frame(self.reg_win)
        main_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        canvas = tk.Canvas(main_scroll_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        self.reg_win.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        def create_field(parent, label, widget, row, sticky=tk.W + tk.E):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
            widget.grid(row=row, column=1, sticky=sticky, padx=10, pady=5)

        account_frame = ttk.LabelFrame(self.scrollable_frame, text="Account & Personal Information")
        account_frame.pack(fill="x", expand=True, padx=10, pady=10)
        account_frame.columnconfigure(1, weight=1)

        ttk.Label(account_frame, text="Patient ID:", style="Bold.TLabel").grid(row=0, column=0, sticky=tk.W, padx=10,
                                                                               pady=5)
        ttk.Label(account_frame, text="Auto-generated", style="Sub.TLabel").grid(row=0, column=1, sticky=tk.W, padx=10,
                                                                                 pady=5)

        self.email = ttk.Entry(account_frame, width=40)
        create_field(account_frame, "Email:", self.email, 1)

        ttk.Label(account_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        password_frame = ttk.Frame(account_frame)
        password_frame.grid(row=2, column=1, sticky=tk.W + tk.E, padx=10, pady=5)
        password_frame.columnconfigure(0, weight=1)
        self.password = ttk.Entry(password_frame, show="*", width=35)
        self.password.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.btn_show_pass = ttk.Button(password_frame, text="Show", style="Small.TButton",
                                        command=self.password_visibility, width=6)
        self.btn_show_pass.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

        self.first = ttk.Entry(account_frame, width=40)
        create_field(account_frame, "First Name:", self.first, 3)
        self.middle = ttk.Entry(account_frame, width=40)
        create_field(account_frame, "Middle Name:", self.middle, 4)
        self.last = ttk.Entry(account_frame, width=40)
        create_field(account_frame, "Last Name:", self.last, 5)
        self.birth = ttk.Entry(account_frame, width=40)
        create_field(account_frame, "Date of Birth (MM/DD/YYYY):", self.birth, 6)

        self.gender = ttk.Combobox(account_frame, values=["Male", "Female"], width=38, state="readonly")
        create_field(account_frame, "Gender:", self.gender, 7, sticky=tk.W)
        self.contact = ttk.Entry(account_frame, width=40)
        create_field(account_frame, "Contact Number (+63):", self.contact, 8)
        self.blood = ttk.Combobox(account_frame, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"],
                                  width=38, state="readonly")
        create_field(account_frame, "Blood Type:", self.blood, 9, sticky=tk.W)

        contact_frame = ttk.LabelFrame(self.scrollable_frame, text="Address & Emergency Contact")
        contact_frame.pack(fill="x", expand=True, padx=10, pady=10)
        contact_frame.columnconfigure(1, weight=1)

        self.address = ttk.Entry(contact_frame, width=40)
        create_field(contact_frame, "Home Address:", self.address, 0)
        self.em_name = ttk.Entry(contact_frame, width=40)
        create_field(contact_frame, "Emergency Contact Name:", self.em_name, 1)
        self.em_num = ttk.Entry(contact_frame, width=40)
        create_field(contact_frame, "Emergency Contact Number (+63):", self.em_num, 2)
        self.em_rel = ttk.Entry(contact_frame, width=40)
        create_field(contact_frame, "Relationship to Patient:", self.em_rel, 3)

        #medical frame
        medical_frame = ttk.LabelFrame(self.scrollable_frame, text="Medical Information (Optional)")
        medical_frame.pack(fill="x", expand=True, padx=10, pady=10)
        medical_frame.columnconfigure(1, weight=1)

        ttk.Label(medical_frame, text="Medical Conditions:").grid(row=0, column=0, sticky=tk.NW, padx=10, pady=5)
        self.med_cond = tk.Text(medical_frame, width=35, height=3, relief="solid", borderwidth=1)
        self.med_cond.grid(row=0, column=1, sticky=tk.W + tk.E, padx=10, pady=5)

        ttk.Label(medical_frame, text="Current Medications:").grid(row=1, column=0, sticky=tk.NW, padx=10, pady=5)
        self.medications = tk.Text(medical_frame, width=35, height=3, relief="solid", borderwidth=1)
        self.medications.grid(row=1, column=1, sticky=tk.W + tk.E, padx=10, pady=5)

        ttk.Label(medical_frame, text="Allergies:").grid(row=2, column=0, sticky=tk.NW, padx=10, pady=5)
        self.allergies = tk.Text(medical_frame, width=35, height=3, relief="solid", borderwidth=1)
        self.allergies.grid(row=2, column=1, sticky=tk.W + tk.E, padx=10, pady=5)

        btn_frame = ttk.Frame(self.reg_win)
        btn_frame.pack(pady=15, fill="x")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).grid(row=0, column=0, sticky=tk.E, padx=(0, 5))
        ttk.Button(btn_frame, text="Submit", style="Accent.TButton", command=self.save_patient).grid(row=0,
                                                                                                          column=1,
                                                                                                          sticky=tk.W,
                                                                                                          padx=(5, 0))

    def password_visibility(self):
        """toggles the password entry mask"""
        if self.password.cget("show") == "*":
            self.password.config(show="")
            self.btn_show_pass.config(text="Hide")
        else:
            self.password.config(show="*")
            self.btn_show_pass.config(text="Show")

    def cancel(self):
        """close registration and return to login"""
        self.reg_win.destroy()
        open_login_window()

    def save_patient(self):
        """validates the data and add the new patient"""
        med_cond_text = self.med_cond.get("1.0", tk.END).strip() or None
        medications_text = self.medications.get("1.0", tk.END).strip() or None
        allergies_text = self.allergies.get("1.0", tk.END).strip() or None

        email = self.email.get().strip()
        password = self.password.get().strip()
        first_name = self.first.get().strip()
        middle_name = self.middle.get().strip() or None
        last_name = self.last.get().strip()
        birth_date = self.birth.get().strip()
        gender_full = self.gender.get().strip()
        gender = gender_full[0] if gender_full else ''
        contact_number = self.contact.get().strip()
        blood_type = self.blood.get().strip() or None
        address = self.address.get().strip()
        em_name = self.em_name.get().strip()
        em_num = self.em_num.get().strip()
        em_rel = self.em_rel.get().strip()

        required_fields = [email, password, first_name, last_name, birth_date, gender, contact_number, address, em_name,
                           em_num, em_rel]
        #data validations
        if not all(required_fields):
            messagebox.showerror("Error", "Please fill in all required fields. Blank spaces are not allowed.")
            return

        if len(first_name) > 50 or len(last_name) > 50:
            messagebox.showerror("Invalid Input", "First and Last names must be 50 characters or less.")
            return

        if middle_name and len(middle_name) > 50:
            messagebox.showerror("Invalid Input", "Middle name must be 50 characters or less.")
            return

        if len(em_name) > 50 or len(em_rel) > 50:
            messagebox.showerror("Invalid Input",
                                 "Emergency Contact Name and Relationship must be 50 characters or less.")
            return

        if address and len(address) > 255:
            messagebox.showerror("Invalid Input", "Home address is too long. Please keep it under 255 characters.")
            return

        if not re.match(r'^09\d{9}$', contact_number):
            messagebox.showerror("Invalid Input",
                                 "Contact number must be exactly 11 digits, start with '09', "
                                 "and contain no dashes or spaces (e.g., 09157034318).")
            return

        if not re.match(r'^09\d{9}$', em_num):
            messagebox.showerror("Invalid Input",
                                 "Emergency contact number must be exactly 11 digits, start with '09', "
                                 "and contain no dashes or spaces (e.g., 09157034318).")
            return

        email_regex = r"^[\w.-]+@[\w.-]+\.\w+$"
        if not re.match(email_regex, email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        dal_check = DataAccessLayer()
        try:
            dal_check.open()
            if dal_check.fetch_one("SELECT COUNT(*) FROM Users WHERE Email=?", email) > 0:
                messagebox.showerror("Error", "Email used already.")
                return
        except Exception as err:
            print(f"Validation error: {err}")
            return
        finally:
            dal_check.close()

        try:
            parsed_dob = datetime.strptime(birth_date, "%m/%d/%Y")
            if parsed_dob.date() > date.today():
                messagebox.showerror("Invalid Input", "Date of Birth cannot be in the future.")
                return
        except ValueError:
            messagebox.showerror("Error", "Birth date must be in MM/DD/YYYY format.")
            return

        if len(password) < 12 or not any(c.isupper() for c in password) or not any(
                c.isdigit() for c in password) or not any(c in "!@#$%^&*()-_+=~`[]{}|:;\"'<>,.?/" for c in password):
            messagebox.showerror("Error",
                                 "Password must be at least 12 chars and contain Upper, Number, and Special character.")
            return

        dal = DataAccessLayer()
        try:
            dal.open()
            user_id = dal.fetch_one(
                "INSERT INTO Users (Email, PasswordHash, Role, DateRegistered) OUTPUT INSERTED.UserID "
                "VALUES (?, ?, 'Patient', GETDATE())",
                email, generate_password_hash(password)
            )

            if not user_id:
                raise Exception("Failed to retrieve new UserID.")

            patient_id = dal.fetch_one(
                "INSERT INTO Patients (UID, FirstName, MiddleName, LastName, BirthDate, Gender, ContactNumber, "
                "BloodType, HomeAddress, InitialConditions, InitialMedications, InitialAllergies) OUTPUT INSERTED.PatientID "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                user_id, first_name, middle_name, last_name, birth_date, gender, contact_number, blood_type, address,
                med_cond_text, medications_text, allergies_text
            )

            dal.execute(
                "INSERT INTO EmergencyContacts (PID, FullName, ContactNumber, Relationship) VALUES (?, ?, ?, ?)",
                patient_id, em_name, em_num, em_rel
            )

            dal.commit()
            messagebox.showinfo("Success", "Patient account created successfully!")
            self.reg_win.destroy()
            open_login_window()
        except Exception as err:
            dal.rollback()
            messagebox.showerror("Database Error", str(err))
        finally:
            dal.close()


def open_doctor_registration():
    """Loads the Doctor Registration Window."""
    reg_win = tk.Tk()
    DoctorRegistrationWindow(reg_win)
    reg_win.mainloop()


class DoctorRegistrationWindow:
    """This handles inserting new doctor profiles into the database."""

    def __init__(self, reg_win):
        self.reg_win = reg_win
        self.reg_win.title("Doctor Registration")
        self.reg_win.geometry("500x600")
        self.reg_win.configure(bg="white")
        self.reg_win.resizable(False, False)

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure(".", font=("Open Sans", 10), background="white", fieldbackground="white", borderwidth=0,
                        focusthickness=0)
        style.configure("TEntry", borderwidth=1, relief="solid", bordercolor="#cccccc")
        style.map("TEntry", bordercolor=[('focus', '#0078d7')], relief=[('focus', 'solid')])
        style.configure("TCombobox", borderwidth=1, relief="solid", bordercolor="#cccccc")
        style.map("TCombobox", bordercolor=[('focus', '#0078d7')], selectbackground=[('!focus', 'white')],
                  selectforeground=[('!focus', 'black')])
        style.configure("TLabelFrame", background="white", borderwidth=1, relief="solid", bordercolor="#e0e0e0")
        style.configure("TLabelFrame.Label", font=("Open Sans", 12, "bold"), background="white", foreground="#333333")
        style.configure("TLabel", background="white")
        style.configure("Bold.TLabel", font=("Open Sans", 10, "bold"), background="white")
        style.configure("Sub.TLabel", font=("Open Sans", 10), foreground="#6e6e6e", background="white")
        style.configure("Small.TButton", font=("Open Sans", 9), padding=(5, 2), background="#f0f0f0",
                        bordercolor="#cccccc", relief="solid")
        style.map("Small.TButton", background=[('active', '#e0e0e0')])
        style.configure("Accent.TButton", font=("Open Sans", 10, "bold"), background="#0078d7", foreground="white",
                        borderwidth=0)
        style.map("Accent.TButton", background=[('active', '#005fa3')])

        ttk.Label(self.reg_win, text="Create Account", font=("Open Sans", 16, "bold"), style="TLabel").pack(
            pady=(20, 0))
        ttk.Label(self.reg_win, text="Join the Patient-Doctor Portal.", style="Sub.TLabel").pack(pady=(0, 15))

        main_scroll_frame = ttk.Frame(self.reg_win)
        main_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        canvas = tk.Canvas(main_scroll_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        self.reg_win.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        self.scrollable_frame.columnconfigure(0, weight=1)

        def create_field(parent, label, widget, row, sticky=tk.W + tk.E):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
            widget.grid(row=row, column=1, sticky=sticky, padx=10, pady=5)

        account_frame = ttk.LabelFrame(self.scrollable_frame, text="Account & Personal Information")
        account_frame.grid(row=0, column=0, sticky=tk.W + tk.E, pady=5)
        account_frame.columnconfigure(1, weight=1)

        ttk.Label(account_frame, text="Doctor ID:", style="Bold.TLabel").grid(row=0, column=0, sticky=tk.W, padx=10,
                                                                              pady=5)
        ttk.Label(account_frame, text="Auto-generated", style="Sub.TLabel").grid(row=0, column=1, sticky=tk.W, padx=10,
                                                                                 pady=5)

        self.email = ttk.Entry(account_frame, width=35)
        create_field(account_frame, "Email:", self.email, 1)

        ttk.Label(account_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        password_frame = ttk.Frame(account_frame)
        password_frame.grid(row=2, column=1, sticky=tk.W + tk.E, padx=10, pady=5)
        password_frame.columnconfigure(0, weight=1)

        self.password = ttk.Entry(password_frame, show="*", width=30)
        self.password.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.btn_show_pass = ttk.Button(password_frame, text="Show", style="Small.TButton",
                                        command=self.password_visibility, width=6)
        self.btn_show_pass.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

        self.first = ttk.Entry(account_frame, width=35)
        create_field(account_frame, "First Name:", self.first, 3)
        self.middle = ttk.Entry(account_frame, width=35)
        create_field(account_frame, "Middle Name:", self.middle, 4)
        self.last = ttk.Entry(account_frame, width=35)
        create_field(account_frame, "Last Name:", self.last, 5)

        self.gender = ttk.Combobox(account_frame, values=["Male", "Female"], width=32, state="readonly")
        create_field(account_frame, "Gender:", self.gender, 6, sticky=tk.W)
        self.contact = ttk.Entry(account_frame, width=35)
        create_field(account_frame, "Contact Number (+63):", self.contact, 7)

        prof_frame = ttk.LabelFrame(self.scrollable_frame, text="Professional Information")
        prof_frame.grid(row=1, column=0, sticky=tk.W + tk.E, pady=10)
        prof_frame.columnconfigure(1, weight=1)

        specializations = ["General Medicine", "Pediatrics", "Cardiology", "Dermatology", "Neurology", "Orthopedics",
                           "Psychiatry"]
        self.spec = ttk.Combobox(prof_frame, values=specializations, width=32, state="readonly")
        create_field(prof_frame, "Specialization:", self.spec, 0, sticky=tk.W)

        self.license = ttk.Entry(prof_frame, width=35)
        create_field(prof_frame, "License Number:", self.license, 1)

        btn_frame = ttk.Frame(self.reg_win)
        btn_frame.pack(pady=15, fill="x")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        ttk.Button(btn_frame, text="Cancel", command=self.cancel).grid(row=0, column=0, sticky=tk.E, padx=(0, 5))
        ttk.Button(btn_frame, text="Submit", style="Accent.TButton", command=self.save_doctor).grid(row=0,
                                                                                                         column=1,
                                                                                                         sticky=tk.W,
                                                                                     padx=(5, 0))

    def password_visibility(self):
        """show or hide the password entry"""
        if self.password.cget("show") == "*":
            self.password.config(show="")
            self.btn_show_pass.config(text="Hide")
        else:
            self.password.config(show="*")
            self.btn_show_pass.config(text="Show")

    def cancel(self):
        """close registration and go back to login"""
        self.reg_win.destroy()
        open_login_window()

    def save_doctor(self):
        """it saves a new doctor upon registration"""
        email = self.email.get().strip()
        password = self.password.get().strip()
        first_name = self.first.get().strip()
        middle_name = self.middle.get().strip() or None
        last_name = self.last.get().strip()
        gender_full = self.gender.get().strip()
        gender = gender_full[0] if gender_full else ''
        contact_number = self.contact.get().strip()
        specialization = self.spec.get().strip()
        license_number = self.license.get().strip()

        #data validations
        if not all([email, password, first_name, last_name, gender, contact_number, specialization, license_number]):
            messagebox.showerror("Error", "Please fill in all required fields. Blank spaces are not allowed.")
            return

        if len(first_name) > 50 or len(last_name) > 50:
            messagebox.showerror("Invalid Input", "First and Last names must be 50 characters or less.")
            return

        if middle_name and len(middle_name) > 50:
            messagebox.showerror("Invalid Input", "Middle name must be 50 characters or less.")
            return

        if not re.match(r'^09\d{9}$', contact_number):
            messagebox.showerror("Invalid Input",
                                 "Contact number must be exactly 11 digits, start with '09', "
                                 "and contain no dashes or spaces.")
            return

        if not re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
            messagebox.showerror("Error", "Invalid email format.")
            return

        dal_check = DataAccessLayer()
        try:
            dal_check.open()
            if dal_check.fetch_one("SELECT COUNT(*) FROM Users WHERE Email=?", email) > 0:
                messagebox.showerror("Error", "This email has been used already.")
                return
        except Exception as err:
            print(f"Validation error: {err}")
            return
        finally:
            dal_check.close()

        if len(password) < 12 or not any(c.isupper() for c in password) or not any(
                c.isdigit() for c in password) or not any(c in "!@#$%^&*()-_+=~`[]{}|:;\"'<>,.?/" for c in password):
            messagebox.showerror("Error",
                                 "Password must be at least 12 characters and contain upper, number, and special character.")
            return

        if not re.match(r'^[A-Z]{2}-\d{4}-\d{4}$', license_number):
            messagebox.showerror("Error", "License number must follow the format XX-YYYY-XXXX "
                                          "(e.g., DR-2025-0001).")
            return

        dal = DataAccessLayer()
        try:
            dal.open()
            user_id = dal.fetch_one(
                "INSERT INTO Users (Email, PasswordHash, Role, DateRegistered) OUTPUT INSERTED.UserID "
                "VALUES (?, ?, 'Doctor', GETDATE())",
                email, generate_password_hash(password)
            )

            if not user_id:
                raise Exception("Failed to retrieve new UserID after Users insert.")

            doc_id = dal.fetch_one(
                "INSERT INTO Doctors (UID, FirstName, MiddleName, LastName, Gender, ContactNumber, Specialization, "
                "LicenseNumber) OUTPUT INSERTED.DoctorID VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                user_id, first_name, middle_name, last_name, gender, contact_number, specialization, license_number
            )

            dal.execute("INSERT INTO Fee (DID, BaseAmount, EffectiveDate) VALUES (?, 1000.00, GETDATE())", doc_id)
            dal.commit()

            messagebox.showinfo("Success", "Doctor account created successfully!")
            self.reg_win.destroy()
            open_login_window()
        except Exception as err:
            dal.rollback()
            messagebox.showerror("Database Error", str(err))
        finally:
            dal.close()


class DoctorEditProfileWindow:
    """Open a window to edit the doctor's personal details"""

    def __init__(self, parent_win, doctor_data, refresh_callback):
        self.win = tk.Toplevel(parent_win)
        self.win.title("Edit Profile")
        self.win.geometry("450x450")
        self.win.configure(bg="white")
        self.win.grab_set()

        self.data = doctor_data
        self.refresh_callback = refresh_callback

        style = ttk.Style()
        style.configure("Edit.TLabel", background="white", font=("Open Sans", 10, "bold"), foreground="#333")

        main_frame = ttk.Frame(self.win, style="Card.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="Edit Personal Details", font=("Open Sans", 14, "bold"), background="white",
                  foreground="#2E7D32").pack(anchor="w", padx=20, pady=(20, 5))
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", padx=20, pady=10)

        def create_entry(label, current_val):
            ttk.Label(main_frame, text=label, style="Edit.TLabel").pack(anchor="w", padx=20, pady=(5, 2))
            entry = ttk.Entry(main_frame, width=45)
            entry.insert(0, current_val if current_val else "")
            entry.pack(anchor="w", padx=20, pady=(0, 10))
            return entry

        self.ent_first = create_entry("First Name:", self.data.get("FirstName", ""))
        self.ent_mid = create_entry("Middle Name:", self.data.get("MiddleName", ""))
        self.ent_last = create_entry("Last Name:", self.data.get("LastName", ""))
        self.ent_contact = create_entry("Contact Number (+63):", self.data.get("ContactNumber", ""))

        btn_frame = ttk.Frame(main_frame, style="Card.TFrame")
        btn_frame.pack(fill="x", padx=20, pady=20)
        ttk.Button(btn_frame, text="Save Changes", style="Accent.TButton", command=self.save_changes).pack(fill="x",
                                                                                                           ipady=5)

    def save_changes(self):
        """save the updated doctor profile in the database"""
        first = self.ent_first.get().strip()
        mid = self.ent_mid.get().strip()
        last = self.ent_last.get().strip()
        contact = self.ent_contact.get().strip()

        if not first or not last or not contact:
            messagebox.showerror("Error", "Fields cannot be empty.")
            return

        if len(first) > 50 or len(last) > 50:
            messagebox.showerror("Invalid Input", "First and Last names must be 50 characters or less.")
            return

        if mid and len(mid) > 50:
            messagebox.showerror("Invalid Input", "Middle name must be 50 characters or less.")
            return

        if not re.match(r'^09\d{9}$', contact):
            messagebox.showerror("Invalid Input",
                                 "Contact number must be exactly 11 digits, start with '09', "
                                 "and contain no dashes or spaces (e.g., 09157034318).")
            return

        dal = DataAccessLayer()
        try:
            dal.open()
            query = "UPDATE Doctors SET FirstName=?, MiddleName=?, LastName=?, ContactNumber=? WHERE DoctorID=?"
            dal.execute(query, first, mid if mid else None, last, contact, self.data["ID"])
            dal.commit()

            self.data["FirstName"] = first
            self.data["MiddleName"] = mid
            self.data["LastName"] = last
            self.data["ContactNumber"] = contact

            mid_str = f"{mid} " if mid else ""
            self.data["FullName"] = f"Dr. {first} {mid_str}{last}"

            messagebox.showinfo("Success", "Profile updated successfully.")
            self.refresh_callback()
            self.win.destroy()
        except Exception as err:
            dal.rollback()
            messagebox.showerror("Error", f"Failed to save: {err}")
        finally:
            dal.close()


class DoctorMainWindow:
    """The portal for Doctor users. Handles appointments, patient records, prescriptions, and billing verification."""

    def __init__(self, root, email):
        self.root = root
        self.email = email
        self.doctor_data = {}
        self.selected_appointment_id = None

        self.root.title("PDMS — Doctor Portal")
        try:
            self.root.state('zoomed')
        except tk.TclError:
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        self.root.configure(bg="#f4f4f4")

        if not self.fetch_doctor():
            self.root.destroy()
            return

        self.setup_styles()
        self.build_header()
        self.build_footer()
        self.build_navigation()
        self.notebook.bind("<<NotebookTabChanged>>", self.refresh)

    def setup_styles(self):
        """set up the styles for the doctor window"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", font=("Open Sans", 10), background="#f4f4f4")
        style.configure("Header.TFrame", background="#2E7D32")
        style.configure("Header.TLabel", background="#2E7D32", foreground="white", font=("Open Sans", 14, "bold"))
        style.configure("HeaderSub.TLabel", background="#2E7D32", foreground="#e0e0e0", font=("Open Sans", 10))
        style.configure("HeaderTitle.TLabel", background="#2E7D32", foreground="white", font=("Open Sans", 16, "bold"))
        style.configure("HeaderSlogan.TLabel", background="#2E7D32", foreground="white",
                        font=("Open Sans", 11, "italic"))
        style.configure("HeaderUser.TLabel", background="#2E7D32", foreground="#e0e0e0", font=("Open Sans", 10, "bold"))
        style.configure("Card.TFrame", background="white", relief="solid", bordercolor="#e0e0e0", borderwidth=1)
        style.configure("Section.TLabel", background="white", font=("Open Sans", 12, "bold"), foreground="#2E7D32")
        style.configure("DataLabel.TLabel", background="white", font=("Open Sans", 10, "bold"), foreground="#333")
        style.configure("ValueLabel.TLabel", background="white", font=("Open Sans", 10), foreground="#555")
        style.configure("Desc.TLabel", background="white", font=("Open Sans", 9), foreground="#777")
        style.configure("TNotebook", background="#f4f4f4", borderwidth=0)
        style.configure("TNotebook.Tab", padding=[20, 5], font=("Open Sans", 10), background="#d9d9d9",
                        foreground="#003366", borderwidth=1, relief="solid")
        style.map("TNotebook.Tab", background=[("selected", "#f4f4f4")], foreground=[("selected", "#2E7D32")],
                  expand=[("selected", [1, 1, 1, 0])])
        style.configure("Accent.TButton", font=("Open Sans", 10, "bold"), background="#2E7D32", foreground="white",
                        borderwidth=0)
        style.map("Accent.TButton", background=[('active', '#1B5E20')])
        style.configure("Success.TButton", font=("Open Sans", 9, "bold"), background="#28a745", foreground="white",
                        borderwidth=0)
        style.map("Success.TButton", background=[('active', '#218838')])
        style.configure("Warn.TButton", font=("Open Sans", 9), background="#ffc107", foreground="black", borderwidth=0)
        style.map("Warn.TButton", background=[('active', '#e0a800')])
        style.configure("Danger.TButton", font=("Open Sans", 9), background="#d9534f", foreground="white",
                        borderwidth=0)
        style.map("Danger.TButton", background=[('active', '#c9302c')])
        style.configure("Treeview.Heading", font=("Open Sans", 10, "bold"), background="#e0e0e0")
        style.configure("Treeview", font=("Open Sans", 10), rowheight=25)

    def fetch_doctor(self):
        """get the doctor's profile from the database"""
        dal = DataAccessLayer()
        try:
            dal.open()
            query = """
                SELECT d.DoctorID, d.FirstName, d.LastName, d.Specialization, d.LicenseNumber, d.DefaultLocation, 
                d.MiddleName, d.ContactNumber FROM Users u JOIN Doctors d ON u.UserID = d.UID WHERE u.Email = ?
            """
            rows = dal.execute_query(query, self.email)
            if rows:
                record = rows[0]
                mid_str = f"{record[6]} " if record[6] else ""

                self.doctor_data = {
                    "ID": record[0],
                    "FullName": f"Dr. {record[1]} {mid_str}{record[2]}",
                    "FirstName": record[1],
                    "LastName": record[2],
                    "Specialty": record[3],
                    "License": record[4],
                    "Location": record[5] if record[5] else "General Clinic",
                    "MiddleName": record[6] if record[6] else "",
                    "ContactNumber": record[7] if record[7] else ""
                }
                return True
            return False
        except Exception as err:
            messagebox.showerror("Error", str(err))
            return False
        finally:
            dal.close()

    def build_header(self):
        """creates the header."""
        header_frame = ttk.Frame(self.root, style="Header.TFrame", padding=(15, 10))
        header_frame.pack(fill="x")

        left_frame = ttk.Frame(header_frame, style="Header.TFrame")
        left_frame.pack(side="left")

        self.logo_img = resize_image("PDMS_LOGO.png", (50, 50))
        if self.logo_img:
            lbl_logo = tk.Label(left_frame, image=self.logo_img, bg="#2E7D32", bd=0)
            lbl_logo.pack(side="left", padx=(0, 10))

        title_frame = ttk.Frame(left_frame, style="Header.TFrame")
        title_frame.pack(side="left")
        ttk.Label(title_frame, text="Doctor", style="HeaderTitle.TLabel").pack(anchor="w")
        ttk.Label(title_frame, text="Portal", style="HeaderTitle.TLabel").pack(anchor="w")

        center_frame = ttk.Frame(header_frame, style="Header.TFrame")
        center_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(center_frame, text='"Patients are our priority, your health is our mission."',
                  style="HeaderSlogan.TLabel").pack(anchor="center")

        right_frame = ttk.Frame(header_frame, style="Header.TFrame")
        right_frame.pack(side="right")
        self.lbl_greeting = ttk.Label(right_frame, text=f"Hi, {self.doctor_data.get('FullName', 'Doc')}",
                                      style="HeaderUser.TLabel")
        self.lbl_greeting.pack(side="left", padx=(0, 15))
        ttk.Button(right_frame, text="Logout", style="Danger.TButton", command=self.logout).pack(side="left")

    def build_footer(self):
        """contructs the footer"""
        footer_frame = tk.Frame(self.root, bg="#f4f4f4")
        footer_frame.pack(side="bottom", fill="x", pady=(0, 10))
        tk.Label(footer_frame,
                 text="📞 Need assistance or IT support? Contact the clinic administration at (02) 8123-4567.",
                 font=("Open Sans", 9, "italic"), bg="#f4f4f4", fg="#777777").pack(anchor="center")

    def build_navigation(self):
        """construct the tabs"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_appointments = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_appointments, text="  Appointments  ")
        self.build_appointments()

        self.tab_records = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_records, text="  Patient Records  ")
        self.build_records()

        self.tab_prescriptions = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_prescriptions, text="  Prescriptions  ")
        self.build_prescription()

        self.tab_billing = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_billing, text="  Billing  ")
        self.build_billing()

    def refresh(self, event):
        """clear the consultation if leaving the prescription page"""
        if self.notebook.index(self.notebook.select()) != 2:
            self.selected_appointment_id = None
            self.clear_form(full=True)
            self.lbl_active_patient.config(text="No active consultation selected.", foreground="#d9534f")

    def clear_form(self, full=True):
        """clear the inputs in the prescription tab"""
        if full:
            self.txt_diag.delete("1.0", tk.END)
            if hasattr(self, 'txt_consult_notes'):
                self.txt_consult_notes.delete("1.0", tk.END)

        if hasattr(self, 'ent_med'):
            self.ent_med.delete(0, tk.END)
            self.ent_dose.delete(0, tk.END)
            self.txt_instructions.delete("1.0", tk.END)
            self.txt_lab.delete("1.0", tk.END)
            self.chk_lab.set(0)

    def build_appointments(self):
        """make the interface for booking and checking appointments"""
        main_frame = ttk.Frame(self.tab_appointments, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Appointment Schedule", font=("Open Sans", 18, "bold"),
                  style="DataLabel.TLabel").pack(anchor="w")
        ttk.Label(main_frame, text="Manage your schedule, start consultations, or update appointment status.",
                  style="Desc.TLabel").pack(anchor="w", pady=(0, 15))
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(0, 15))

        search_frame = ttk.Frame(main_frame, style="Card.TFrame")
        search_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(search_frame, text="Search Patient:", style="DataLabel.TLabel").pack(side="left")
        self.ent_search = ttk.Entry(search_frame, width=40)
        self.ent_search.pack(side="left", padx=10)
        ttk.Button(search_frame, text="Search", style="Accent.TButton", command=self.refresh_appointments).pack(
            side="left")
        ttk.Button(search_frame, text="Show All", style="Small.TButton",
                   command=lambda: [self.ent_search.delete(0, tk.END), self.refresh_appointments()]).pack(side="left",
                                                                                                          padx=5)

        ttk.Label(search_frame, text="Sort by Date:", style="DataLabel.TLabel").pack(side="left", padx=(30, 5))
        self.sort_var = tk.StringVar()
        self.cb_sort = ttk.Combobox(search_frame, textvariable=self.sort_var, state="readonly", width=15)
        self.cb_sort['values'] = ("Ascending", "Descending")
        self.cb_sort.current(0)
        self.cb_sort.pack(side="left")
        self.cb_sort.bind("<<ComboboxSelected>>", lambda e: self.refresh_appointments())

        cols = ("AID", "Date", "Time", "Patient", "Location", "Reason", "Status")
        self.appt_tree = ttk.Treeview(main_frame, columns=cols, show="headings", height=10)

        for col in cols:
            self.appt_tree.heading(col, text=col)

        self.appt_tree.column("AID", width=0, stretch=False)
        self.appt_tree.pack(fill="both", expand=True)

        self.appt_tree.tag_configure('Completed', background='#d4edda', foreground='#155724')
        self.appt_tree.tag_configure('Cancelled', background='#f8d7da', foreground='#721c24')
        self.appt_tree.tag_configure('Rescheduled', background='#fff3cd', foreground='#856404')
        self.appt_tree.tag_configure('Pending', background='#cce5ff', foreground='#004085')
        self.appt_tree.bind("<Button-1>", lambda event: self.appt_tree.selection_remove(
            self.appt_tree.selection()) if not self.appt_tree.identify_row(event.y) else None)

        btn_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=(0, 10))
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Start Consult", style="Success.TButton", command=self.start_consult).pack(
            side="right", padx=5)
        ttk.Button(btn_frame, text="Reschedule", style="Warn.TButton", command=self.open_reschedule).pack(
            side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel Appointment", style="Danger.TButton", command=self.cancel_appointment).pack(
            side="right", padx=5)

        footer = ttk.LabelFrame(main_frame, text=" Practice Details ", padding=10)
        footer.pack(fill="x", pady=20)

        info_text = (f"Doctor: {self.doctor_data.get('FullName')}   |   Contact: {self.doctor_data.get('ContactNumber')}\n"
                     f"Specialty: {self.doctor_data.get('Specialty')}   |   License No: {self.doctor_data.get('License')}")

        self.lbl_practice_details = ttk.Label(footer, text=info_text, font=("Open Sans", 10), foreground="#333")
        self.lbl_practice_details.pack(anchor="w", pady=(0, 10))

        loc_frame = ttk.Frame(footer)
        loc_frame.pack(fill="x", pady=(0, 0))
        ttk.Label(loc_frame, text="Current Clinic/Room:", style="DataLabel.TLabel").pack(side="left")

        self.loc_var = tk.StringVar(value=self.doctor_data["Location"])
        self.cb_loc = ttk.Combobox(loc_frame, textvariable=self.loc_var, width=25)
        self.cb_loc['values'] = ["General Clinic", "Room 101", "Room 102", "Room 201", "ER", "Online Consult"]
        self.cb_loc.pack(side="left", padx=10)

        ttk.Button(loc_frame, text="Update Location", style="Small.TButton", command=self.update_location).pack(
            side="left")
        ttk.Button(loc_frame, text="Edit Profile", style="Accent.TButton", command=self.open_edit_profile).pack(
            side="right", padx=10)

        self.refresh_appointments()

    def update_location(self):
        """save the doctor's main clinic location to the database"""
        new_loc = self.loc_var.get().strip()
        if not new_loc:
            return

        if len(new_loc) > 100:
            messagebox.showerror("Invalid Input", "Clinic location name must be 100 characters or less.")
            return

        dal = DataAccessLayer()
        try:
            dal.open()
            dal.execute("UPDATE Doctors SET DefaultLocation=? WHERE DoctorID=?", new_loc, self.doctor_data["ID"])
            dal.commit()

            self.doctor_data["Location"] = new_loc
            messagebox.showinfo("Success", "Default location updated.")
        except Exception as err:
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()

    def open_edit_profile(self):
        """opens the edit profile modal"""
        DoctorEditProfileWindow(self.root, self.doctor_data, self.refresh_profile)

    def refresh_profile(self):
        """change the headers when the profile info updates"""
        if hasattr(self, 'lbl_greeting'):
            self.lbl_greeting.config(text=f"Hi, {self.doctor_data['FullName']}")

        if hasattr(self, 'lbl_practice_details'):
            info_text = (f"Doctor: {self.doctor_data.get('FullName')}   |   "
                         f"Contact: {self.doctor_data.get('ContactNumber')}\n"
                         f"Specialty: {self.doctor_data.get('Specialty')}   |   "
                         f"License No: {self.doctor_data.get('License')}")
            self.lbl_practice_details.config(text=info_text)

    def refresh_appointments(self):
        """filter the doctor's schedule"""
        for item in self.appt_tree.get_children(): self.appt_tree.delete(item)
        search_txt = self.ent_search.get().strip().lower()
        order_dir = "DESC" if hasattr(self, 'sort_var') and self.sort_var.get() == "Descending" else "ASC"
        dal = DataAccessLayer()
        try:
            dal.open()
            query = f"""
                        SELECT a.AppointmentID, a.AppointmentDateTime, p.FirstName, p.LastName, a.Location, a.Reason, a.Status 
                        FROM Appointments a JOIN Patients p ON a.PID = p.PatientID WHERE a.DID = ? 
                        ORDER BY a.AppointmentDateTime {order_dir}
                    """
            rows = dal.execute_query(query, self.doctor_data["ID"])
            for r in rows:
                dt = r[1]
                pat_name = f"{r[2]} {r[3]}"
                if search_txt and (
                        search_txt not in pat_name.lower() and search_txt not in dt.strftime("%Y-%m-%d")): continue
                self.appt_tree.insert("", "end", values=(
                r[0], dt.strftime("%Y-%m-%d"), dt.strftime("%I:%M %p"), pat_name, r[4], r[5], r[6]), tags=(r[6],))
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            dal.close()

    def start_consult(self):
        """move the appointment to active and automatically go to the prescription tab"""
        sel = self.appt_tree.selection()
        if not sel:
            return

        item = self.appt_tree.item(sel[0])['values']
        if item[6] == 'Cancelled':
            messagebox.showerror("Error", "Cannot start a cancelled appointment.")
            return
        if item[6] == 'Completed':
            messagebox.showerror("Error", "Appointment already completed.")
            return

        self.clear_form()
        self.selected_appointment_id = item[0]
        self.notebook.select(self.tab_prescriptions)
        self.lbl_active_patient.config(text=f"Active Patient: {item[3]} (ID: {self.selected_appointment_id})",
                                       foreground="#333")

    def cancel_appointment(self):
        """cancel an appointment and update its status."""
        sel = self.appt_tree.selection()
        if not sel:
            return

        if self.appt_tree.item(sel[0])['values'][6] == 'Completed':
            messagebox.showerror("Error", "Cannot cancel a completed appointment.")
            return

        if messagebox.askyesno("Cancel", "Cancel this appointment?"):
            dal = DataAccessLayer()
            try:
                dal.open()
                dal.execute("UPDATE Appointments SET Status='Cancelled' WHERE AppointmentID=?",
                            self.appt_tree.item(sel[0])['values'][0])
                dal.commit()
                self.refresh_appointments()
            finally:
                dal.close()

    def open_reschedule(self):
        """launches the rescheduling modal"""
        sel = self.appt_tree.selection()
        if not sel:
            return

        item = self.appt_tree.item(sel[0])['values']
        if item[6] == 'Cancelled':
            messagebox.showerror("Error", "Cannot reschedule a cancelled appointment.")
            return
        if item[6] == 'Completed':
            messagebox.showerror("Error", "Cannot reschedule a completed appointment.")
            return

        RescheduleWindow(self.root, item[0], f"{item[1]} {item[2]}", self.doctor_data["ID"], self.refresh_appointments)

    def build_records(self):
        """this builds the patient records viewer."""
        main_frame = ttk.Frame(self.tab_records, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Patient Records", font=("Open Sans", 18, "bold"), style="DataLabel.TLabel").pack(
            anchor="w")
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(10, 15))

        search_row = ttk.Frame(main_frame)
        search_row.pack(fill="x", pady=(0, 10))
        ttk.Label(search_row, text="Search Patient:", style="DataLabel.TLabel").pack(side="left")
        self.rec_search = ttk.Entry(search_row, width=40)
        self.rec_search.pack(side="left", padx=10)
        ttk.Button(search_row, text="Search", style="Accent.TButton", command=self.search_patients).pack(side="left")

        paned = ttk.PanedWindow(main_frame, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left_frame = ttk.Frame(paned, width=300, relief="solid", borderwidth=1)
        paned.add(left_frame, weight=1)
        self.rec_tree = ttk.Treeview(left_frame, columns=("PID", "Name", "LastVisit"), show="headings")
        self.rec_tree.heading("PID", text="ID")
        self.rec_tree.column("PID", width=60)
        self.rec_tree.heading("Name", text="Name")
        self.rec_tree.column("Name", width=120)
        self.rec_tree.heading("LastVisit", text="Last Visit")
        self.rec_tree.column("LastVisit", width=100)
        self.rec_tree.pack(fill="both", expand=True)
        self.rec_tree.bind("<<TreeviewSelect>>", self.load_patient)

        self.rec_tree.bind("<Button-1>", lambda event: self.rec_tree.selection_remove(
            self.rec_tree.selection()) if not self.rec_tree.identify_row(event.y) else None)

        self.rec_detail_frame = ttk.Frame(paned, style="Card.TFrame", padding=20)
        paned.add(self.rec_detail_frame, weight=3)
        self.search_patients()

    def search_patients(self):
        """filter patients that have visited this doctor."""
        for item in self.rec_tree.get_children():
            self.rec_tree.delete(item)

        txt = self.rec_search.get().strip().lower()
        dal = DataAccessLayer()

        try:
            dal.open()
            query = ("SELECT p.PatientID, p.FirstName, p.LastName, MAX(a.AppointmentDateTime) as LastVisit "
                     "FROM Patients p JOIN Appointments a ON p.PatientID = a.PID WHERE a.DID = ? "
                     "GROUP BY p.PatientID, p.FirstName, p.LastName")
            rows = dal.execute_query(query, self.doctor_data["ID"])

            for row in rows:
                if txt and (txt not in f"{row[1]} {row[2]}".lower() and str(row[0]) != txt):
                    continue
                self.rec_tree.insert("", "end", values=(
                row[0], f"{row[1]} {row[2]}", row[3].strftime("%Y-%m-%d") if row[3] else "No visits"))
        except Exception as err:
            print(f"Error fetching patients: {err}")
        finally:
            dal.close()

    def load_patient(self, event):
        """populate with patient's historical medical records."""
        sel = self.rec_tree.selection()
        if not sel:
            return

        patient_id = self.rec_tree.item(sel[0])['values'][0]

        for widget in self.rec_detail_frame.winfo_children():
            widget.destroy()

        dal = DataAccessLayer()
        try:
            dal.open()
            query = """
                SELECT FirstName, LastName, BirthDate, Gender, BloodType, InitialConditions, 
                InitialAllergies, InitialMedications FROM Patients WHERE PatientID=?
            """
            p_record = dal.execute_query(query, patient_id)[0]

            header = ttk.Frame(self.rec_detail_frame)
            header.pack(fill="x", pady=(0, 10))
            ttk.Label(header, text=f"Patient: {p_record[0]} {p_record[1]}", font=("Open Sans", 16, "bold"),
                      foreground="#2E7D32").pack(side="left")

            info = ttk.Frame(self.rec_detail_frame)
            info.pack(fill="x", pady=(0, 15))
            ttk.Label(info,
                      text=f"DOB: {p_record[2].strftime('%m/%d/%Y')}   |   "
                           f"Gender: {'Female' if p_record[3] == 'F' else 'Male'}",
                      style="ValueLabel.TLabel").pack(anchor="w")

            ov_frame = ttk.Frame(self.rec_detail_frame)
            ov_frame.pack(fill="x", pady=(0, 10))

            def make_box(col, title, text, bg_color, border_color):
                frame = tk.Frame(ov_frame, bg=bg_color, bd=1, relief="solid", highlightbackground=border_color,
                                 highlightthickness=1)
                frame.grid(row=0, column=col, sticky="nsew", padx=5)
                tk.Label(frame, text=title, bg=bg_color, font=("Open Sans", 9, "bold")).pack(anchor="w", padx=5, pady=2)
                tk.Label(frame, text=text if text else "None", bg=bg_color, wraplength=150, justify="left").pack(
                    anchor="w", padx=5, pady=2)

            make_box(0, "Conditions", p_record[5], "#fff3cd", "#ffeeba")
            make_box(1, "Allergies", p_record[6], "#f8d7da", "#f5c6cb")
            make_box(2, "Meds", p_record[7], "#d4edda", "#c3e6cb")

            bot_paned = ttk.PanedWindow(self.rec_detail_frame, orient="vertical")
            bot_paned.pack(fill="both", expand=True)

            self.hist_tree = ttk.Treeview(bot_paned, columns=("AID", "Date", "Reason"), show="headings", height=5)
            self.hist_tree.heading("AID", text="ID")
            self.hist_tree.column("AID", width=0, stretch=False)
            self.hist_tree.heading("Date", text="Date")
            self.hist_tree.column("Date", width=100)
            self.hist_tree.heading("Reason", text="Reason for Visit")
            self.hist_tree.column("Reason", width=300)
            bot_paned.add(self.hist_tree, weight=1)

            self.hist_tree.bind("<<TreeviewSelect>>", self.load_consult)
            self.scroll_container = ttk.Frame(bot_paned)
            bot_paned.add(self.scroll_container, weight=2)

            self.visit_canvas = tk.Canvas(self.scroll_container, bg="white", highlightthickness=0)
            self.visit_scroll = ttk.Scrollbar(self.scroll_container, orient="vertical", command=self.visit_canvas.yview)
            self.visit_frame = ttk.Frame(self.visit_canvas, style="Card.TFrame")
            self.visit_window_id = self.visit_canvas.create_window((0, 0), window=self.visit_frame, anchor="nw")

            self.visit_frame.bind("<Configure>",
                                  lambda event: self.visit_canvas.configure(scrollregion=self.visit_canvas.bbox("all")))
            self.visit_canvas.bind("<Configure>",
                                   lambda event: self.visit_canvas.itemconfig(self.visit_window_id, width=event.width))
            self.visit_canvas.configure(yscrollcommand=self.visit_scroll.set)
            self.visit_canvas.pack(side="left", fill="both", expand=True)
            self.visit_scroll.pack(side="right", fill="y")

            h_rows = dal.execute_query(
                "SELECT AppointmentID, AppointmentDateTime, Reason FROM Appointments WHERE PID=? AND DID=? "
                "ORDER BY AppointmentDateTime DESC",
                patient_id, self.doctor_data["ID"])
            for hist in h_rows:
                self.hist_tree.insert("", "end", values=(hist[0], hist[1].strftime("%Y-%m-%d"), hist[2]))

        except Exception as err:
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()

    def load_consult(self, event):
        """display the specifics of a past consultation."""
        sel = self.hist_tree.selection()
        if not sel:
            return

        appointment_id = self.hist_tree.item(sel[0])['values'][0]

        for widget in self.visit_frame.winfo_children():
            widget.destroy()

        dal = DataAccessLayer()
        try:
            dal.open()
            recs = dal.execute_query("SELECT Diagnosis, Notes FROM MedicalRecords WHERE AID=?", appointment_id)

            btn_frame = ttk.Frame(self.visit_frame)
            btn_frame.pack(fill="x", pady=5, padx=10)

            ttk.Button(btn_frame, text="Download Rx & Lab PDF", style="Accent.TButton",
                       command=lambda: generate_pdf(appointment_id)).pack(side="right")

            d_frame = ttk.Frame(self.visit_frame)
            d_frame.pack(fill="x", pady=5, padx=10)
            ttk.Label(d_frame, text=f"Diagnosis: {recs[0][0] if recs else 'N/A'}", style="DataLabel.TLabel",
                      foreground="#2E7D32", wraplength=450).pack(anchor="w")
            ttk.Label(d_frame, text=f"Notes: {recs[0][1] if recs else 'N/A'}", style="ValueLabel.TLabel",
                      wraplength=450).pack(anchor="w", pady=(5, 0))
            ttk.Separator(self.visit_frame, orient="horizontal").pack(fill="x", pady=10, padx=10)

            rx_rows = dal.execute_query("SELECT DrugName, Dosage, Instructions FROM Prescriptions WHERE AID=?",
                                        appointment_id)
            if rx_rows:
                ttk.Label(self.visit_frame, text="Prescriptions:", style="DataLabel.TLabel").pack(anchor="w", padx=10)
                for rx in rx_rows:
                    r_frame = ttk.Frame(self.visit_frame)
                    r_frame.pack(fill="x", padx=20, pady=4)
                    ttk.Label(r_frame, text=f"• {rx[0]} ({rx[1]})", foreground="#2E7D32",
                              font=("Open Sans", 10, "bold")).pack(anchor="w")
                    ttk.Label(r_frame, text=f"Instructions: {rx[2]}", foreground="#555", wraplength=450).pack(
                        anchor="w", padx=(15, 0))

            lab_rows = dal.execute_query("SELECT RequestID, Description, Status FROM LabRequests WHERE AID=?",
                                         appointment_id)
            if lab_rows:
                ttk.Label(self.visit_frame, text="Lab Requests:", style="DataLabel.TLabel").pack(anchor="w",
                                                                                                 pady=(10, 0), padx=10)
                for l in lab_rows:
                    l_frame = ttk.Frame(self.visit_frame)
                    l_frame.pack(fill="x", padx=20, pady=4)
                    text_frame = ttk.Frame(l_frame)
                    text_frame.pack(side="left", fill="x", expand=True)
                    ttk.Label(text_frame, text=f"• {l[1]}", wraplength=350).pack(anchor="w")

                    if l[2] == 'Pending':
                        ttk.Button(l_frame, text="✓ Done", style="Small.TButton",
                                   command=lambda r=l[0]: self.mark_lab(r, event)).pack(side="right", padx=10)
                    else:
                        tk.Label(l_frame, text=f" {l[2]} ", bg="#28a745", fg="white", font=("Arial", 8, "bold")).pack(
                            side="right", padx=10)
        except Exception as err:
            print(f"Error loading consult details: {err}")
        finally:
            dal.close()

    def mark_lab(self, request_id, event):
        """this marks the lab request as completed"""
        dal = DataAccessLayer()
        try:
            dal.open()
            dal.execute("UPDATE LabRequests SET Status='Completed' WHERE RequestID=?", request_id)
            dal.commit()
            self.load_consult(event)
        finally:
            dal.close()

    def build_prescription(self):
        """the form for writing the prescriptions and diagnosis for patients"""
        main_frame = ttk.Frame(self.tab_prescriptions, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Prescribe Medication & Diagnosis", style="Section.TLabel").pack(anchor="w")
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(10, 15))

        self.lbl_active_patient = ttk.Label(main_frame, text="No active consultation selected.",
                                            font=("Open Sans", 11, "bold"), foreground="#d9534f")
        self.lbl_active_patient.pack(anchor="w", pady=(0, 10))

        paned = ttk.PanedWindow(main_frame, orient="horizontal")
        paned.pack(fill="both", expand=True)
        left_frame = ttk.Frame(paned, padding=(0, 0, 20, 0))
        paned.add(left_frame, weight=3)
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        def add_field(label_text, widget, height=None):
            ttk.Label(left_frame, text=label_text, style="DataLabel.TLabel").pack(anchor="w", pady=(5, 0))
            if height:
                widget.config(height=height)
            widget.pack(fill="x", pady=(0, 10))

        self.txt_diag = tk.Text(left_frame, height=2, font=("Open Sans", 10), bd=1, relief="solid")
        add_field("Diagnosis:", self.txt_diag)

        self.txt_consult_notes = tk.Text(left_frame, height=3, font=("Open Sans", 10), bd=1, relief="solid")
        add_field("Consultation Notes:", self.txt_consult_notes)

        ttk.Separator(left_frame, orient="horizontal").pack(fill="x", pady=(10, 5))

        self.ent_med = ttk.Entry(left_frame)
        add_field("Medication Name:", self.ent_med)

        self.ent_dose = ttk.Entry(left_frame)
        add_field("Dosage:", self.ent_dose)

        self.txt_instructions = tk.Text(left_frame, height=2, font=("Open Sans", 10), bd=1, relief="solid")
        add_field("Medication Instructions:", self.txt_instructions)

        self.chk_lab = tk.IntVar()
        ttk.Checkbutton(left_frame, text="Include Lab Request", variable=self.chk_lab).pack(anchor="w", pady=(5, 0))

        self.txt_lab = tk.Text(left_frame, height=2, font=("Open Sans", 10), bd=1, relief="solid")
        add_field("Lab Details:", self.txt_lab)

        #signature canvas
        self.sig_canvas = tk.Canvas(right_frame, width=300, height=150, bg="white", cursor="crosshair", bd=1,
                                    relief="solid")
        self.sig_canvas.pack(anchor="w", pady=(0, 10))
        self.sig_img = Image.new("RGB", (300, 150), "white")
        self.sig_draw = ImageDraw.Draw(self.sig_img)

        self.sig_canvas.bind("<Button-1>", self.start_draw)
        self.sig_canvas.bind("<B1-Motion>", self.draw_lines)
        self.last_x, self.last_y = None, None

        ttk.Button(right_frame, text="Clear Signature", style="Small.TButton", command=self.clear_signature).pack(
            anchor="w", pady=(0, 20))
        ttk.Button(right_frame, text="Save & Add to Record", style="Accent.TButton",
                   command=self.submit_prescription).pack(fill="x", ipady=5)

    def start_draw(self, event):
        """allows drawing in the signature pad"""
        self.last_x, self.last_y = event.x, event.y

    def draw_lines(self, event):
        """be able to draw lines"""
        if self.last_x and self.last_y:
            self.sig_canvas.create_line((self.last_x, self.last_y, event.x, event.y), width=2, fill="black",
                                        capstyle=tk.ROUND, smooth=tk.TRUE)
            self.sig_draw.line([self.last_x, self.last_y, event.x, event.y], fill="black", width=2)
            self.last_x, self.last_y = event.x, event.y

    def clear_signature(self):
        """clears the signature pad"""
        self.sig_canvas.delete("all")
        self.sig_img = Image.new("RGB", (300, 150), "white")
        self.sig_draw = ImageDraw.Draw(self.sig_img)

    def submit_prescription(self):
        """this saves the prescription to the database"""
        if not self.selected_appointment_id:
            messagebox.showerror("Error", "Start consult first.")
            return

        diag = self.txt_diag.get("1.0", tk.END).strip() or None
        consult_notes = self.txt_consult_notes.get("1.0", tk.END).strip() or None
        med = self.ent_med.get().strip() or None
        dose = self.ent_dose.get().strip() or None
        instructions = self.txt_instructions.get("1.0", tk.END).strip() or None
        lab_details = self.txt_lab.get("1.0", tk.END).strip() or None

        if not self.sig_canvas.find_all():
            messagebox.showerror("Signature Required",
                                 "A doctor's signature is strictly required to save and complete this consultation.")
            return

        #check if some clinical fields are completely blank
        if not any([diag, consult_notes, med, dose, instructions, lab_details]):
            proceed = messagebox.askyesno(
                "Confirm Blank Record",
                "Some clinical fields are empty. \n\nAre you sure you want to save this record? "
                "It will appear blank on the patient's medical history and PDF."
            )
            if not proceed:
                return

        #text length validations
        if diag and len(diag) > 500:
            messagebox.showerror("Text Too Long",
                                 "The diagnosis is too long (maximum 500 characters). Please summarize.")
            return

        if med and len(med) > 100:
            messagebox.showerror("Text Too Long",
                                 "The Medication Name exceeds the 100-character limit. Please abbreviate.")
            return

        if dose and len(dose) > 50:
            messagebox.showerror("Text Too Long", "The Dosage text is too long (maximum 50 characters).")
            return

        if instructions and len(instructions) > 255:
            messagebox.showerror("Text Too Long",
                                 "The Medication Instructions are too long. Please keep them under 255 characters.")
            return

        if lab_details and len(lab_details) > 255:
            messagebox.showerror("Text Too Long",
                                 "The Lab Details are too long. Please keep them under 255 characters.")
            return

        dal = DataAccessLayer()
        try:
            dal.open()

            #upsert medical record
            if dal.fetch_one("SELECT RecordID FROM MedicalRecords WHERE AID=?", self.selected_appointment_id):
                dal.execute("UPDATE MedicalRecords SET Diagnosis=?, Notes=?, DateRecorded=GETDATE() "
                            "WHERE AID=?", diag, consult_notes, self.selected_appointment_id)
            else:
                dal.execute(
                    "INSERT INTO MedicalRecords (AID, Diagnosis, Notes, DateRecorded) VALUES (?, ?, ?, GETDATE())",
                    self.selected_appointment_id, diag, consult_notes)

            if med or dose or instructions:
                dal.execute(
                    "INSERT INTO Prescriptions (AID, DrugName, Dosage, Instructions, DatePrescribed) "
                    "VALUES (?, ?, ?, ?, GETDATE())",
                    self.selected_appointment_id, med, dose, instructions)

            if self.chk_lab.get() and lab_details:
                dal.execute(
                    "INSERT INTO LabRequests (AID, Description, Status, DateRequested) "
                    "VALUES (?, ?, 'Pending', GETDATE())",
                    self.selected_appointment_id, lab_details)

            dal.execute("UPDATE Appointments SET Status='Completed' WHERE AppointmentID=?",
                        self.selected_appointment_id)

            dal.execute("UPDATE Invoices SET Status='Processing' WHERE AID=?",
                        self.selected_appointment_id)

            dal.commit()

            messagebox.showinfo("Success", "Record saved successfully!")
            self.refresh_appointments()

            self.sig_img.save(f"signature_AID_{self.selected_appointment_id}.png")

            self.clear_form(full=False)

        except Exception as err:
            dal.rollback()
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()

    def build_billing(self):
        """this builds the billing interface"""
        main_frame = ttk.Frame(self.tab_billing, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Billing Administration", font=("Open Sans", 18, "bold"),
                  style="DataLabel.TLabel").pack(anchor="w")
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(10, 15))
        ttk.Label(main_frame, text="Unresolved Patient Balances",
                  style="Section.TLabel").pack(anchor="w", pady=(0, 5))

        cols = ("InvID", "Patient", "ConsultDate", "Status", "Amount")
        self.bal_tree = ttk.Treeview(main_frame, columns=cols, show="headings", height=6)

        self.bal_tree.heading("InvID", text="Invoice #")
        self.bal_tree.heading("Patient", text="Patient Name (ID)")
        self.bal_tree.heading("ConsultDate", text="Consult Date")
        self.bal_tree.heading("Status", text="Status")
        self.bal_tree.heading("Amount", text="Amount Due")

        self.bal_tree.column("InvID", width=80)
        self.bal_tree.column("Patient", width=180)
        self.bal_tree.column("ConsultDate", width=100)
        self.bal_tree.column("Status", width=90, anchor="center")
        self.bal_tree.column("Amount", width=90, anchor="e")
        self.bal_tree.pack(fill="x", pady=(0, 20))

        self.bal_tree.bind("<Button-1>", lambda event: self.bal_tree.selection_remove(
            self.bal_tree.selection()) if not self.bal_tree.identify_row(event.y) else None)
        self.bal_tree.bind("<Double-1>", self.confirm_payment)

        ttk.Label(main_frame, text="Payment History (Paid)", style="Section.TLabel").pack(anchor="w", pady=(0, 5))
        cols_paid = ("InvID", "Patient", "DatePaid", "Reason", "Amount", "ConsultDate")
        self.paid_tree = ttk.Treeview(main_frame, columns=cols_paid, show="headings", height=6)

        self.paid_tree.heading("InvID", text="Invoice #")
        self.paid_tree.heading("Patient", text="Patient Name (ID)")
        self.paid_tree.heading("DatePaid", text="Date Paid")
        self.paid_tree.heading("Reason", text="Reason")
        self.paid_tree.heading("Amount", text="Amount Paid")
        self.paid_tree.heading("ConsultDate", text="Consult Date")

        self.paid_tree.column("InvID", width=80)
        self.paid_tree.column("Patient", width=180)
        self.paid_tree.column("DatePaid", width=90)
        self.paid_tree.column("Reason", width=150)
        self.paid_tree.column("Amount", width=90, anchor="e")
        self.paid_tree.column("ConsultDate", width=90)
        self.paid_tree.pack(fill="x")

        self.paid_tree.bind("<Button-1>", lambda event: self.paid_tree.selection_remove(
            self.paid_tree.selection()) if not self.paid_tree.identify_row(event.y) else None)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=5)

        self.lbl_total_paid = ttk.Label(action_frame, text="Total Collected: ₱0.00", font=("Open Sans", 11, "bold"),
                                        foreground="#2E7D32")
        self.lbl_total_paid.pack(side="left")

        ttk.Button(action_frame, text="Download Invoice PDF", style="Accent.TButton",
                   command=self.download_invoice).pack(side="right")

        fee_frame = ttk.LabelFrame(main_frame, text=" Consultation Fee ", padding=10)
        fee_frame.pack(fill="x", pady=20)

        self.lbl_current_fee = ttk.Label(fee_frame, text="Current Fee: ₱0.00", font=("Open Sans", 12))
        self.lbl_current_fee.pack(side="left", padx=20)

        self.ent_new_fee = ttk.Entry(fee_frame, width=10)
        self.ent_new_fee.pack(side="left", padx=5)

        ttk.Button(fee_frame, text="Update", style="Accent.TButton", command=self.update_fee).pack(side="left")

        self.refresh_billing()

    def refresh_billing(self):
        """populate both the unresolved balances and paid tables."""
        for item in self.bal_tree.get_children():
            self.bal_tree.delete(item)

        for item in self.paid_tree.get_children():
            self.paid_tree.delete(item)

        dal = DataAccessLayer()
        try:
            dal.open()

            #fetch unresolved
            q_unresolved = """
                SELECT i.InvoiceID, p.FirstName, p.LastName, p.PatientID, a.AppointmentDateTime, i.Status, i.Amount 
                FROM Invoices i JOIN Appointments a ON i.AID = a.AppointmentID JOIN Patients p ON a.PID = p.PatientID 
                WHERE a.DID = ? AND i.Status = 'Processing'
            """
            for record in dal.execute_query(q_unresolved, self.doctor_data["ID"]):
                self.bal_tree.insert("", "end", values=(
                f"INV-{record[0]:04d}", f"{record[1]} {record[2]} (P{record[3]})", record[4].strftime("%Y-%m-%d"),
                record[5], f"₱{record[6]:,.2f}"))

            #fetch paid
            q_paid = """
                SELECT i.InvoiceID, p.FirstName, p.LastName, p.PatientID, i.DateIssued, a.Reason, i.Amount, a.AppointmentDateTime 
                FROM Invoices i JOIN Appointments a ON i.AID = a.AppointmentID JOIN Patients p ON a.PID = p.PatientID 
                WHERE a.DID = ? AND i.Status = 'Paid'
            """
            total = 0.0
            for record in dal.execute_query(q_paid, self.doctor_data["ID"]):
                total += float(record[6])
                self.paid_tree.insert("", "end", values=(
                f"INV-{record[0]:04d}", f"{record[1]} {record[2]} (P{record[3]})", record[4].strftime("%Y-%m-%d"),
                record[5], f"₱{record[6]:,.2f}", record[7].strftime("%Y-%m-%d")))

            self.lbl_total_paid.config(text=f"Total Collected: ₱{total:,.2f}")

            #fetch current fee
            fee_query = "SELECT TOP 1 BaseAmount FROM Fee WHERE DID=? ORDER BY EffectiveDate DESC"
            fee_records = dal.execute_query(fee_query, self.doctor_data["ID"])
            self.lbl_current_fee.config(
                text=f"Current Fee: ₱{fee_records[0][0]:,.2f}" if fee_records else "Current Fee: ₱1,000.00")

        except Exception as err:
            print(f"Billing refresh error: {err}")
        finally:
            dal.close()

    def confirm_payment(self, event):
        """this allows the clinic staff to verify or reject a processing payment."""
        sel = self.bal_tree.selection()
        if not sel: return
        item = self.bal_tree.item(sel[0])['values']

        status = item[3]
        if status != 'Processing':
            messagebox.showinfo("Verification", "Only invoices marked as 'Processing' require your confirmation.")
            return

        inv_id_raw = int(item[0].split('-')[1])
        amount = item[4]

        msg = (f"Has the payment of {amount} for {item[0]} been successfully received by the clinic?\n\n"
               f"YES = Confirm and mark as Paid\nNO = Cancel Verification")
        response = messagebox.askyesno("Verify Payment", msg)

        if response:
            dal = DataAccessLayer()
            try:
                dal.open()
                dal.execute("UPDATE Invoices SET Status='Paid', DateIssued=GETDATE() "
                            "WHERE InvoiceID=?", inv_id_raw)
                messagebox.showinfo("Success", f"{item[0]} has been verified and marked as PAID.")
                dal.commit()
                self.refresh_billing()
            except Exception as e:
                dal.rollback()
                messagebox.showerror("Error", str(e))
            finally:
                dal.close()

    def update_fee(self):
        """this updates the base consultation fee for the doctor who logged in"""
        try:
            new_fee_amount = float(self.ent_new_fee.get().strip())

            if new_fee_amount < 0:
                messagebox.showerror("Invalid Input", "Consultation fee cannot be a negative number.")
                return

            dal = DataAccessLayer()
            try:
                dal.open()
                query = "INSERT INTO Fee (DID, BaseAmount, EffectiveDate) VALUES (?, ?, GETDATE())"
                dal.execute(query, self.doctor_data["ID"], new_fee_amount)
                dal.commit()

                messagebox.showinfo("Success", "Updated.")
                self.refresh_billing()
            finally:
                dal.close()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount. Please enter a valid number.")

    def download_invoice(self):
        """similar to the patient window on generating PDF invoice"""
        sel = self.paid_tree.selection()
        if not sel:
            messagebox.showwarning("Select Bill", "Please select a paid invoice from the history list.")
            return

        item = self.paid_tree.item(sel[0])['values']
        inv_id_raw = int(item[0].split('-')[1])

        dal = DataAccessLayer()
        try:
            dal.open()
            query = """
                SELECT i.InvoiceID, i.DateIssued, i.Amount, i.Status, p.FirstName AS PatFirst, p.LastName AS PatLast, p.PatientID,
                       d.FirstName AS DocFirst, d.LastName AS DocLast, a.Location, a.AppointmentDateTime, a.Reason
                FROM Invoices i JOIN Appointments a ON i.AID = a.AppointmentID JOIN Patients p ON a.PID = p.PatientID
                JOIN Doctors d ON a.DID = d.DoctorID WHERE i.InvoiceID = ?
            """
            rows = dal.execute_query(query, inv_id_raw)
            if not rows:
                return

            record = rows[0]

            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", "B", 110)
            pdf.set_text_color(230, 255, 230)
            pdf.set_xy(0, 130)
            pdf.cell(0, 0, "P A I D", align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(10, 10)

            if os.path.exists("PDMS_LOGO.png"):
                pdf.image("PDMS_LOGO.png", x=10, y=8, w=35)

            pdf.set_font("Arial", "B", 24)
            pdf.cell(0, 15, "INVOICE", ln=True, align="R")
            pdf.set_font("Arial", "", 12)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 8, f"Invoice Number: INV-{record[0]:04d}", ln=True, align="R")
            pdf.cell(0, 8, f"Date Issued: {record[1].strftime('%B %d, %Y') if record[1] else 'N/A'}", ln=True,
                     align="R")
            pdf.set_text_color(40, 167, 69)
            pdf.cell(0, 8, "Status: PAID", ln=True, align="R")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(20)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(95, 10, "Billed To:", 0, 0)
            pdf.cell(95, 10, "Service Provider:", 0, 1)
            pdf.set_font("Arial", "", 12)
            pdf.cell(95, 8, f"{record[4]} {record[5]}", 0, 0)
            pdf.cell(95, 8, f"Dr. {record[7]} {record[8]}", 0, 1)
            pdf.cell(95, 8, f"Patient ID: P{record[6]}", 0, 0)
            pdf.cell(95, 8, record[9] if record[9] else "General Clinic", 0, 1)
            pdf.ln(20)

            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(90, 10, "Description", border=1, fill=True)
            pdf.cell(40, 10, "Consultation Date", border=1, align="C", fill=True)
            pdf.cell(60, 10, "Amount", border=1, align="R", fill=True)
            pdf.ln(10)

            pdf.set_font("Arial", "", 11)
            reason_str = record[11] if record[11] else "Medical Consultation"
            desc_text = f"Consultation: {reason_str}"

            x_start = pdf.get_x()
            y_start = pdf.get_y()

            pdf.multi_cell(90, 7.5, desc_text, border=1)
            row_height = pdf.get_y() - y_start

            pdf.set_xy(x_start + 90, y_start)
            pdf.cell(40, row_height, f"{record[10].strftime('%b %d, %Y')}", border=1, align="C")
            pdf.cell(60, row_height, f"PHP {float(record[2]):,.2f}", border=1, align="R")
            pdf.ln(row_height)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(130, 15, "TOTAL PAID:", border=0, align="R")
            pdf.cell(60, 15, f"PHP {float(record[2]):,.2f}", border=0, align="R")
            pdf.ln(30)

            pdf.set_font("Arial", "I", 10)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 10, "Patients are our priority, your health is our mission.", align="C", ln=True)

            file_name = f"Invoice_INV{record[0]:04d}.pdf"
            pdf.output(file_name)

            if platform.system() == 'Darwin':
                subprocess.call(('open', file_name))
            elif platform.system() == 'Windows':
                os.startfile(file_name)
            else:
                subprocess.call(('xdg-open', file_name))

        except Exception as err:
            messagebox.showerror("Error", str(err))
        finally:
            dal.close()

    def logout(self):
        """close the application and return to the login window."""
        self.root.destroy()
        open_login_window()


if __name__ == "__main__":
    open_login_window()