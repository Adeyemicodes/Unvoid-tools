#!/usr/bin/env python3
"""
Patient Unvoid Tool - CCFN OpenMRS
===================================
Secure tool for unvoiding patient records in OpenMRS database

Features:
- Password-protected (Administrator only)
- Patient lookup by ART Identifier
- Confirmation step before unvoiding
- Comprehensive audit trail
- Real-time feedback

Author: Adeyemi
Date: January 2026
Python: 3.6+
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import pymysql as mysql_connector
from pymysql import Error
import configparser
from datetime import datetime
from pathlib import Path
import traceback


class UnvoidPatientApp:
    """Patient Unvoid Application with Security"""

    def __init__(self, root):
        self.root = root
        self.root.title("Patient Unvoid Tool - CCFN")
        self.root.geometry("800x700")
        self.root.resizable(False, False)

        # Security
        self.authenticated = False
        self.admin_password = "pibtib"

        # Database
        self.connection = None
        self.config = None

        # Patient data
        self.current_patient = None

        # Show login screen
        self.show_login_screen()

    def show_login_screen(self):
        """Display login/password screen"""

        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Center frame
        login_frame = tk.Frame(self.root, bg="#f0f0f0")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        tk.Label(
            login_frame,
            text="🔒 ADMINISTRATOR ACCESS REQUIRED",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#d32f2f"
        ).pack(pady=(0, 30))

        # Organization
        tk.Label(
            login_frame,
            text="Catholic Caritas Foundation of Nigeria",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#333"
        ).pack(pady=(0, 5))

        tk.Label(
            login_frame,
            text="Patient Unvoid Tool",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        ).pack(pady=(0, 30))

        # Password field
        tk.Label(
            login_frame,
            text="Administrator Password:",
            font=("Arial", 11),
            bg="#f0f0f0"
        ).pack(pady=(0, 5))

        self.password_entry = tk.Entry(
            login_frame,
            width=30,
            font=("Arial", 12),
            show="*",
            bd=2,
            relief="solid"
        )
        self.password_entry.pack(pady=(0, 20))
        self.password_entry.focus()

        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.check_password())

        # Login button
        tk.Button(
            login_frame,
            text="LOGIN",
            command=self.check_password,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=40,
            pady=10,
            cursor="hand2"
        ).pack()

        # Warning
        tk.Label(
            login_frame,
            text="⚠ WARNING: This tool unvoids patient records.\nUse with extreme caution.",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#d32f2f",
            justify="center"
        ).pack(pady=(30, 0))

    def check_password(self):
        """Verify administrator password"""

        password = self.password_entry.get()

        if password == self.admin_password:
            self.authenticated = True
            self.load_config()
        else:
            messagebox.showerror(
                "Access Denied",
                "Incorrect password!\n\nAccess restricted to administrators only."
            )
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

    def load_config(self):
        """Load database configuration"""

        config_file = Path("unvoid_config.ini")

        if not config_file.exists():
            messagebox.showerror(
                "Configuration Error",
                f"Configuration file not found: {config_file}\n\n"
                "Please create unvoid_config.ini with database settings."
            )
            self.root.quit()
            return

        try:
            self.config = configparser.ConfigParser()
            self.config.read(config_file)

            # Test database connection
            self.test_connection()

        except Exception as e:
            messagebox.showerror(
                "Configuration Error",
                f"Failed to load configuration:\n\n{str(e)}"
            )
            self.root.quit()

    def test_connection(self):
        """Test database connection"""

        try:
            conn = mysql_connector.connect(
                host=self.config['database']['host'],
                user=self.config['database']['user'],
                password=self.config['database']['password'],
                database=self.config['database']['database'],
                port=int(self.config['database'].get('port', 3306))
            )

            if conn.open:
                conn.close()
                # Connection successful, show main screen
                self.show_main_screen()

        except Error as e:
            messagebox.showerror(
                "Database Connection Error",
                f"Cannot connect to database:\n\n{str(e)}\n\n"
                "Please check your configuration file."
            )
            self.root.quit()

    def show_main_screen(self):
        """Display main application screen"""

        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Header
        header_frame = tk.Frame(self.root, bg="#2196F3", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="Patient Unvoid Tool",
            font=("Arial", 18, "bold"),
            bg="#2196F3",
            fg="white"
        ).pack(pady=(15, 0))

        tk.Label(
            header_frame,
            text="Catholic Caritas Foundation of Nigeria",
            font=("Arial", 10),
            bg="#2196F3",
            fg="white"
        ).pack()

        # Main content
        content_frame = tk.Frame(self.root, padx=30, pady=20)
        content_frame.pack(fill="both", expand=True)

        # Search section
        search_frame = tk.LabelFrame(
            content_frame,
            text="Step 1: Enter Patient Identifier",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        search_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            search_frame,
            text="ART Identifier (e.g., IMO01104166):",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(0, 5))

        entry_frame = tk.Frame(search_frame)
        entry_frame.pack(fill="x")

        self.identifier_entry = tk.Entry(
            entry_frame,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief="solid"
        )
        self.identifier_entry.pack(side="left", padx=(0, 10))
        self.identifier_entry.focus()

        tk.Button(
            entry_frame,
            text="SEARCH PATIENT",
            command=self.search_patient,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(side="left")

        # Bind Enter key
        self.identifier_entry.bind("<Return>", lambda e: self.search_patient())

        # Patient details section
        self.details_frame = tk.LabelFrame(
            content_frame,
            text="Step 2: Verify Patient Details",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        self.details_frame.pack(fill="x", pady=(0, 20))

        self.details_text = tk.Text(
            self.details_frame,
            height=6,
            font=("Courier", 10),
            bg="#f5f5f5",
            relief="solid",
            bd=1
        )
        self.details_text.pack(fill="x")
        self.details_text.config(state="disabled")

        # Action section
        action_frame = tk.LabelFrame(
            content_frame,
            text="Step 3: Unvoid Patient Records",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        action_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            action_frame,
            text="⚠ WARNING: This action will unvoid ALL records for this patient.",
            font=("Arial", 9),
            fg="#d32f2f"
        ).pack(pady=(0, 10))

        self.unvoid_button = tk.Button(
            action_frame,
            text="UNVOID PATIENT RECORDS",
            command=self.confirm_unvoid,
            bg="#cccccc",  # Gray when disabled
            fg="#666666",  # Dark gray text when disabled
            font=("Arial", 12, "bold"),
            padx=30,
            pady=12,
            cursor="hand2",
            state="disabled",
            disabledforeground="#666666"  # Keep text visible when disabled
        )
        self.unvoid_button.pack()

        # Log section
        log_frame = tk.LabelFrame(
            content_frame,
            text="Activity Log",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        log_frame.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Courier", 9),
            bg="#1e1e1e",
            fg="#00ff00",
            insertbackground="white"
        )
        self.log_text.pack(fill="both", expand=True)

        # Initial log
        self.log("System ready. Administrator authenticated.")
        self.log(f"Database: {self.config['database']['database']} @ {self.config['database']['host']}")
        self.log("-" * 70)

    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def get_connection(self):
        """Get database connection"""
        try:
            if self.connection and self.connection.open:
                return self.connection

            self.connection = mysql_connector.connect(
                host=self.config['database']['host'],
                user=self.config['database']['user'],
                password=self.config['database']['password'],
                database=self.config['database']['database'],
                port=int(self.config['database'].get('port', 3306))
            )
            return self.connection

        except Error as e:
            messagebox.showerror("Database Error", f"Connection failed:\n\n{str(e)}")
            return None

    def search_patient(self):
        """Search for patient by identifier"""

        identifier = self.identifier_entry.get().strip()

        if not identifier:
            messagebox.showwarning("Input Required", "Please enter an ART identifier.")
            return

        self.log(f"Searching for patient: {identifier}")

        conn = self.get_connection()
        if not conn:
            return

        cursor = None
        try:
            cursor = conn.cursor(mysql_connector.cursors.DictCursor)

            # Find patient by identifier (voided records only)
            query = """
                SELECT 
                    pi.patient_id,
                    pi.identifier,
                    CONCAT(pn.given_name, ' ', pn.family_name) AS patient_name,
                    p.gender,
                    p.birthdate,
                    pi.voided,
                    pi.date_voided,
                    pi.void_reason
                FROM patient_identifier pi
                JOIN person p ON pi.patient_id = p.person_id
                LEFT JOIN person_name pn ON p.person_id = pn.person_id AND pn.voided = 0
                WHERE pi.identifier = %s AND pi.voided = 1
                LIMIT 1
            """

            cursor.execute(query, (identifier,))
            result = cursor.fetchone()
            cursor.fetchall()  # Consume any remaining results

            if not result:
                # Close current cursor and create new one for second query
                cursor.close()
                cursor = conn.cursor(mysql_connector.cursors.DictCursor)

                # Check if exists but not voided
                cursor.execute(
                    "SELECT patient_id FROM patient_identifier WHERE identifier = %s AND voided = 0",
                    (identifier,)
                )
                exists = cursor.fetchone()
                cursor.fetchall()  # Consume any remaining results

                if exists:
                    self.log(f"ERROR: Patient {identifier} is NOT voided. No action needed.")
                    messagebox.showinfo(
                        "Patient Not Voided",
                        f"Patient {identifier} is already active (not voided).\n\n"
                        "No unvoid action is required."
                    )
                else:
                    self.log(f"ERROR: Patient {identifier} not found in database.")
                    messagebox.showerror(
                        "Patient Not Found",
                        f"No patient found with identifier: {identifier}\n\n"
                        "Please check the identifier and try again."
                    )

                self.current_patient = None
                self.unvoid_button.config(state="disabled", bg="#cccccc")
                return

            # Store patient data
            self.current_patient = result

            # Display patient details
            self.display_patient_details(result)

            # Enable unvoid button with proper color
            self.unvoid_button.config(state="normal", bg="#f44336")

            self.log(f"SUCCESS: Found patient - {result['patient_name']} (ID: {result['patient_id']})")

        except Error as e:
            self.log(f"ERROR: Database query failed - {str(e)}")
            messagebox.showerror("Database Error", f"Query failed:\n\n{str(e)}")

        finally:
            if cursor:
                cursor.close()

    def display_patient_details(self, patient):
        """Display patient information for verification"""

        self.details_text.config(state="normal")
        self.details_text.delete(1.0, tk.END)

        details = f"""
Identifier:    {patient['identifier']}
Patient ID:    {patient['patient_id']}
Name:          {patient['patient_name']}
Gender:        {patient['gender']}
Birthdate:     {patient['birthdate']}
Status:        VOIDED
Voided Date:   {patient['date_voided']}
Void Reason:   {patient['void_reason'] or 'Not specified'}
"""

        self.details_text.insert(1.0, details.strip())
        self.details_text.config(state="disabled")

    def confirm_unvoid(self):
        """Confirm before unvoiding"""

        if not self.current_patient:
            return

        patient = self.current_patient

        response = messagebox.askyesno(
            "Confirm Unvoid Action",
            f"Are you sure you want to UNVOID this patient?\n\n"
            f"Identifier: {patient['identifier']}\n"
            f"Name: {patient['patient_name']}\n"
            f"Patient ID: {patient['patient_id']}\n\n"
            f"This will restore ALL voided records for this patient.\n\n"
            f"Do you want to proceed?",
            icon="warning"
        )

        if response:
            # Double confirmation
            response2 = messagebox.askyesno(
                "FINAL CONFIRMATION",
                f"LAST CHANCE!\n\n"
                f"This action will unvoid all records for:\n"
                f"{patient['patient_name']} ({patient['identifier']})\n\n"
                f"Are you ABSOLUTELY SURE?",
                icon="warning"
            )

            if response2:
                self.unvoid_patient()

    def unvoid_patient(self):
        """Execute unvoid operations"""

        if not self.current_patient:
            return

        patient = self.current_patient
        patient_id = patient['patient_id']
        identifier = patient['identifier']
        admin_name = self.config['settings'].get('admin_name', 'Administrator')

        self.log("-" * 70)
        self.log(f"STARTING UNVOID OPERATION")
        self.log(f"Patient: {patient['patient_name']} ({identifier})")
        self.log(f"Patient ID: {patient_id}")
        self.log("-" * 70)

        conn = self.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()

            # Ensure audit table exists
            self.create_audit_table(cursor)

            # Tables to unvoid
            tables = [
                'patient',
                'patient_identifier',
                'patient_program',
                'person',
                'person_name',
                'person_address',
                'person_attribute',
                'visit',
                'encounter',
                'obs'
            ]

            total_updated = 0

            # Unvoid each table
            for table in tables:
                self.log(f"Unvoiding {table}...")

                # Determine ID column
                id_col = 'patient_id' if table in ['patient', 'patient_identifier', 'patient_program', 'visit',
                                                   'encounter'] else 'person_id'

                query = f"""
                    UPDATE {table}
                    SET voided = 0, 
                        voided_by = NULL, 
                        date_voided = NULL, 
                        void_reason = NULL
                    WHERE {id_col} = %s AND voided = 1
                """

                cursor.execute(query, (patient_id,))
                rows = cursor.rowcount
                total_updated += rows

                if rows > 0:
                    self.log(f"  [OK] {rows} record(s) unvoided in {table}")
                else:
                    self.log(f"  [INFO] No voided records in {table}")

            # Log to audit table
            audit_query = """
                INSERT INTO nmrs_unvoid_audit
                (identifier, patient_id, patient_name, executed_by, action_status, remarks)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            cursor.execute(audit_query, (
                identifier,
                patient_id,
                patient['patient_name'],
                admin_name,
                'SUCCESS',
                f'Patient and related records unvoided. Total: {total_updated} records'
            ))

            # Commit transaction
            conn.commit()

            self.log("-" * 70)
            self.log(f"SUCCESS: Unvoided {total_updated} total records")
            self.log(f"Audit entry created in nmrs_unvoid_audit")
            self.log("-" * 70)

            # Show success message
            messagebox.showinfo(
                "Unvoid Complete",
                f"✅ Patient records successfully unvoided!\n\n"
                f"Patient: {patient['patient_name']}\n"
                f"Identifier: {identifier}\n"
                f"Total Records Unvoided: {total_updated}\n\n"
                f"Audit entry has been logged."
            )

            # Reset form
            self.clear_form()

        except Error as e:
            conn.rollback()
            self.log(f"ERROR: Unvoid operation failed - {str(e)}")
            messagebox.showerror(
                "Unvoid Failed",
                f"Operation failed:\n\n{str(e)}\n\n"
                "No changes have been made to the database."
            )

        finally:
            cursor.close()

    def create_audit_table(self, cursor):
        """Ensure audit table exists"""

        create_table_sql = """
            CREATE TABLE IF NOT EXISTS nmrs_unvoid_audit (
                audit_id        INT AUTO_INCREMENT PRIMARY KEY,
                action_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                identifier      VARCHAR(50) NOT NULL,
                patient_id      INT NOT NULL,
                patient_name    VARCHAR(255),
                executed_by     VARCHAR(100),
                action_status   VARCHAR(20) NOT NULL,
                remarks         TEXT,

                INDEX idx_audit_patient_id (patient_id),
                INDEX idx_audit_identifier (identifier),
                INDEX idx_audit_action_time (action_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        """

        cursor.execute(create_table_sql)

    def clear_form(self):
        """Clear form for next patient"""
        self.identifier_entry.delete(0, tk.END)
        self.current_patient = None
        self.unvoid_button.config(state="disabled", bg="#cccccc", fg="#666666")

        self.details_text.config(state="normal")
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state="disabled")

        self.identifier_entry.focus()


def main():
    """Main entry point"""
    root = tk.Tk()

    # Configure font
    try:
        from tkinter import font
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)
    except:
        pass

    app = UnvoidPatientApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()