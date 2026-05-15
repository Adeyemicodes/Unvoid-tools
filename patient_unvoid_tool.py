#!/usr/bin/env python3
"""
Patient Unvoid Tool v2.0 - CCFN OpenMRS
========================================
CRITICAL SAFETY UPGRADE: Timestamp-Based Unvoiding

NEW in v2.0:
- Only unvoids records from specific bulk void operation (±120 seconds)
- Requires void_reason = 'Bulk void via ART/DATIM mapping'
- Blocks unvoid if wrong/missing void_reason
- Shows timestamp and time range to user
- Enhanced audit trail with timestamp info

Features:
- Password-protected (Administrator only)
- Patient lookup by ART Identifier
- Timestamp-based selective unvoiding (SAFE!)
- Double confirmation with time range display
- Comprehensive audit trail
- Real-time feedback

Author: Adeyemi
Date: February 2026
Python: 3.6+
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import pymysql as mysql_connector
from pymysql.err import Error
import configparser
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
import traceback


class UnvoidPatientApp:
    """Patient Unvoid Application with Security"""

    def __init__(self, root):
        self.root = root
        self.root.title("Patient Unvoid Tool v6.1.4 - CCFN")
        self.root.geometry("960x880")
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
            text="ADMINISTRATOR ACCESS REQUIRED",
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
            text="WARNING: This tool unvoids patient records.\nUse with extreme caution.",
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
        """Display main application screen with tabbed interface."""

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

        # Tabbed notebook
        notebook_frame = tk.Frame(self.root, padx=30, pady=10)
        notebook_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill="both", expand=True)

        unvoid_tab = tk.Frame(self.notebook)
        self.notebook.add(unvoid_tab, text="  Unvoid Patient  ")
        self._build_unvoid_tab(unvoid_tab)

        inh_tab = tk.Frame(self.notebook)
        self.notebook.add(inh_tab, text="  Clear INH Dates  ")
        self._build_inh_tab(inh_tab)

        move_tab = tk.Frame(self.notebook)
        self.notebook.add(move_tab, text="  Move Encounter Date  ")
        self._build_move_encounter_tab(move_tab)

        biom_tab = tk.Frame(self.notebook)
        self.notebook.add(biom_tab, text="  Biometric Swap  ")
        self._build_biometric_swap_tab(biom_tab)

        # Shared activity log (root level, beneath the notebook)
        log_frame = tk.LabelFrame(
            self.root,
            text="Activity Log",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        log_frame.pack(fill="both", expand=False, padx=30, pady=(0, 15))

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
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

    def _build_unvoid_tab(self, parent):
        """Build the original Unvoid Patient UI inside the given tab frame."""

        content_frame = tk.Frame(parent, padx=20, pady=15)
        content_frame.pack(fill="both", expand=True)

        # Search section
        search_frame = tk.LabelFrame(
            content_frame,
            text="Step 1: Enter Patient Identifier",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        search_frame.pack(fill="x", pady=(0, 15))

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

        self.identifier_entry.bind("<Return>", lambda e: self.search_patient())

        # Patient details section
        self.details_frame = tk.LabelFrame(
            content_frame,
            text="Step 2: Verify Patient Details",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        self.details_frame.pack(fill="x", pady=(0, 15))

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
        action_frame.pack(fill="x")

        tk.Label(
            action_frame,
            text="WARNING: This action will unvoid ALL records for this patient.",
            font=("Arial", 9),
            fg="#d32f2f"
        ).pack(pady=(0, 10))

        self.unvoid_button = tk.Button(
            action_frame,
            text="UNVOID PATIENT RECORDS",
            command=self.confirm_unvoid,
            bg="#cccccc",
            fg="#666666",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=12,
            cursor="hand2",
            state="disabled",
            disabledforeground="#666666"
        )
        self.unvoid_button.pack()

    def _build_inh_tab(self, parent):
        """Build the Clear INH Dates UI inside the given tab frame."""

        content_frame = tk.Frame(parent, padx=20, pady=15)
        content_frame.pack(fill="both", expand=True)

        # Step 1: Identifier lookup
        search_frame = tk.LabelFrame(
            content_frame,
            text="Step 1: Enter Patient Identifier",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=12
        )
        search_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            search_frame,
            text="ART Identifier (e.g., IMO03210207):",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(0, 5))

        entry_frame = tk.Frame(search_frame)
        entry_frame.pack(fill="x")

        self.inh_identifier_entry = tk.Entry(
            entry_frame,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief="solid"
        )
        self.inh_identifier_entry.pack(side="left", padx=(0, 10))

        tk.Button(
            entry_frame,
            text="LOOKUP INH DATES",
            command=self.lookup_inh_dates,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(side="left")

        self.inh_identifier_entry.bind("<Return>", lambda e: self.lookup_inh_dates())

        # Step 2: Patient summary
        summary_frame = tk.LabelFrame(
            content_frame,
            text="Step 2: Patient Summary",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        summary_frame.pack(fill="x", pady=(0, 12))

        self.inh_summary_label = tk.Label(
            summary_frame,
            text="(no patient loaded)",
            font=("Courier", 10),
            fg="#666",
            anchor="w",
            justify="left"
        )
        self.inh_summary_label.pack(fill="x", anchor="w")

        # Step 3: Obs rows with checkboxes
        results_frame = tk.LabelFrame(
            content_frame,
            text="Step 3: Select INH Date Records to Clear (set value_datetime to NULL)",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=8
        )
        results_frame.pack(fill="both", expand=True, pady=(0, 12))

        header_row = tk.Frame(results_frame, bg="#eeeeee")
        header_row.pack(fill="x")
        for text, width in [
            ("Clear?", 7),
            ("Obs ID", 10),
            ("Concept", 14),
            ("Current Date", 14),
            ("Encounter Date", 16),
            ("Encounter ID", 12),
        ]:
            tk.Label(
                header_row, text=text, font=("Arial", 9, "bold"),
                width=width, anchor="w", bg="#eeeeee"
            ).pack(side="left")

        rows_container = tk.Frame(results_frame)
        rows_container.pack(fill="both", expand=True)

        rows_canvas = tk.Canvas(rows_container, height=140, highlightthickness=0)
        rows_scroll = ttk.Scrollbar(rows_container, orient="vertical", command=rows_canvas.yview)
        self.inh_rows_frame = tk.Frame(rows_canvas)
        self.inh_rows_frame.bind(
            "<Configure>",
            lambda e: rows_canvas.configure(scrollregion=rows_canvas.bbox("all"))
        )
        rows_canvas.create_window((0, 0), window=self.inh_rows_frame, anchor="nw")
        rows_canvas.configure(yscrollcommand=rows_scroll.set)
        rows_canvas.pack(side="left", fill="both", expand=True)
        rows_scroll.pack(side="right", fill="y")

        # Step 4: Apply
        action_frame = tk.LabelFrame(
            content_frame,
            text="Step 4: Apply Changes",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        action_frame.pack(fill="x")

        tk.Label(
            action_frame,
            text="Only the rows you tick will be cleared. Voided obs are not shown.",
            font=("Arial", 9),
            fg="#555"
        ).pack(pady=(0, 8))

        self.inh_clear_button = tk.Button(
            action_frame,
            text="CLEAR SELECTED DATES",
            command=self.confirm_clear_inh_dates,
            bg="#cccccc",
            fg="#666666",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            cursor="hand2",
            state="disabled",
            disabledforeground="#666666"
        )
        self.inh_clear_button.pack()

        # State
        self.inh_obs_rows = []
        self.inh_patient = None

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
            # CRITICAL: Get void_reason and date_voided from patient table for safety check
            # NOTE: person_name may be voided too, so we don't filter by voided = 0
            query = """
                SELECT 
                    pi.patient_id,
                    pi.identifier,
                    CONCAT(pn.given_name, ' ', IFNULL(pn.family_name, '')) AS patient_name,
                    p.gender,
                    p.birthdate,
                    pi.voided AS identifier_voided,
                    pi.date_voided AS identifier_date_voided,
                    pat.voided AS patient_voided,
                    pat.date_voided AS patient_date_voided,
                    pat.void_reason AS patient_void_reason
                FROM patient_identifier pi
                JOIN person p ON pi.patient_id = p.person_id
                JOIN patient pat ON pi.patient_id = pat.patient_id
                LEFT JOIN person_name pn ON p.person_id = pn.person_id
                WHERE pi.identifier = %s AND pi.voided = 1
                ORDER BY pn.preferred DESC, pn.date_created DESC
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
                self.unvoid_button.config(state="disabled", bg="#cccccc", fg="#666666")
                return

            # CRITICAL SAFETY CHECK: Verify void_reason
            void_reason = result.get('patient_void_reason', '')
            required_reason = 'Bulk void via ART/DATIM mapping'

            if void_reason != required_reason:
                self.log(f"ERROR: Invalid void reason: '{void_reason}'")
                self.log(f"       Required: '{required_reason}'")
                self.log(f"       Operation BLOCKED for safety")
                messagebox.showerror(
                    "Cannot Unvoid - Wrong Void Reason",
                    f"SAFETY BLOCK: This tool can ONLY unvoid patients with:\n\n"
                    f"Void Reason: '{required_reason}'\n\n"
                    f"This patient has:\n"
                    f"Void Reason: '{void_reason or 'NULL'}'\n\n"
                    f"Operation BLOCKED for safety.\n\n"
                    f"If you need to unvoid this patient, please contact\n"
                    f"your database administrator."
                )
                self.current_patient = None
                self.unvoid_button.config(state="disabled", bg="#cccccc", fg="#666666")
                return

            # Verify we have a date_voided timestamp
            if not result.get('patient_date_voided'):
                self.log(f"ERROR: No date_voided timestamp found")
                self.log(f"       Operation BLOCKED for safety")
                messagebox.showerror(
                    "Cannot Unvoid - Missing Timestamp",
                    "Patient record does not have a date_voided timestamp.\n\n"
                    "Operation BLOCKED for safety.\n\n"
                    "Contact your database administrator."
                )
                self.current_patient = None
                self.unvoid_button.config(state="disabled", bg="#cccccc", fg="#666666")
                return

            # Calculate time range (±120 seconds)
            void_timestamp = result['patient_date_voided']
            time_start = void_timestamp - timedelta(seconds=120)
            time_end = void_timestamp + timedelta(seconds=120)

            # Store calculated values
            result['time_start'] = time_start
            result['time_end'] = time_end

            # Store patient data
            self.current_patient = result

            # Display patient details
            self.display_patient_details(result)

            # Enable unvoid button with proper color
            self.unvoid_button.config(state="normal", bg="#f44336", fg="white")

            self.log(f"SUCCESS: Found patient - {result['patient_name']} (ID: {result['patient_id']})")
            self.log(f"         Void reason: '{void_reason}' - VALID")
            self.log(f"         Void timestamp: {void_timestamp}")
            self.log(f"         Time range: {time_start} to {time_end} (±120 sec)")

        except Error as e:
            self.log(f"ERROR: Database query failed - {str(e)}")
            messagebox.showerror("Database Error", f"Query failed:\n\n{str(e)}")

        finally:
            if cursor:
                cursor.close()

    def display_patient_details(self, patient):
        """Display patient information with timestamp and time range"""

        self.details_text.config(state="normal")
        self.details_text.delete(1.0, tk.END)

        void_timestamp = patient['patient_date_voided']
        time_start = patient['time_start']
        time_end = patient['time_end']

        details = f"""
Identifier:    {patient['identifier']}
Patient ID:    {patient['patient_id']}
Name:          {patient['patient_name']}
Gender:        {patient['gender']}
Birthdate:     {patient['birthdate']}

VOID INFORMATION:
Status:        VOIDED
Void Reason:   {patient['patient_void_reason']}
Void Time:     {void_timestamp}

TIMESTAMP-BASED UNVOID RANGE:
From:          {time_start}  (-2 min)
To:            {time_end}  (+2 min)
Window:        4 minutes total

SAFETY NOTE:
Only records voided within this 4-minute time window 
will be unvoided. Records voided at other times will 
remain voided for safety.
"""

        self.details_text.insert(1.0, details.strip())
        self.details_text.config(state="disabled")

    def confirm_unvoid(self):
        """Confirm before unvoiding with timestamp details"""

        if not self.current_patient:
            return

        patient = self.current_patient
        void_timestamp = patient['patient_date_voided']
        time_start = patient['time_start']
        time_end = patient['time_end']

        response = messagebox.askyesno(
            "Confirm Unvoid Action",
            f"Are you sure you want to UNVOID this patient?\n\n"
            f"Patient: {patient['patient_name']} ({patient['identifier']})\n"
            f"Patient ID: {patient['patient_id']}\n\n"
            f"Bulk Void Timestamp: {void_timestamp}\n\n"
            f"Time Range to Unvoid:\n"
            f"  From: {time_start}  (-2 minutes)\n"
            f"  To:   {time_end}  (+2 minutes)\n\n"
            f"IMPORTANT: This will ONLY unvoid records voided within\n"
            f"this 4-minute window. Records voided at other times will\n"
            f"remain voided for safety.\n\n"
            f"Do you want to proceed?",
            icon="warning"
        )

        if response:
            self.unvoid_patient()

    def unvoid_patient(self):
        """Execute smart unvoid operations (SAFE - Three-Tier Strategy)

        CRITICAL SAFETY DESIGN:
        - Patient table: Check void_reason + timestamp (SAFETY GATE)

        THREE-TIER STRATEGY:
        1. Tables with reliable timestamps (7 tables):
           - Use timestamp-based unvoid (±120 seconds)
           - patient_identifier, patient_program, person, visit, encounter, obs

        2. Sensitive identity tables (3 tables):
           - Unvoid MOST RECENT voided record ONLY
           - Prevents duplicates, respects old legitimate voids
           - person_name, person_address, person_attribute

        3. Patient table:
           - void_reason + timestamp check

        RATIONALE FOR "MOST RECENT ONLY":
        - These tables should have ONE active record (name, address, attributes)
        - Bulk void voided the most recent record
        - Old voided records were legitimately voided and should stay voided
        - Unvoiding all would create duplicate active records
        """

        if not self.current_patient:
            return

        patient = self.current_patient
        patient_id = patient['patient_id']
        identifier = patient['identifier']
        admin_name = self.config['settings'].get('admin_name', 'Administrator')

        # Get timestamp range
        void_timestamp = patient['patient_date_voided']
        time_start = patient['time_start']
        time_end = patient['time_end']

        self.log("-" * 70)
        self.log(f"STARTING SMART UNVOID OPERATION")
        self.log(f"Patient: {patient['patient_name']} ({identifier})")
        self.log(f"Patient ID: {patient_id}")
        self.log(f"Void Timestamp: {void_timestamp}")
        self.log(f"Time Range: {time_start} to {time_end} (±120 seconds)")
        self.log(f"")
        self.log(f"STRATEGY:")
        self.log(f"  - 7 tables: Timestamp-based (±120 sec)")
        self.log(f"  - 3 sensitive tables: Most recent only (prevents duplicates)")
        self.log(f"    (person_name, person_address, person_attribute)")
        self.log("-" * 70)

        conn = self.get_connection()
        if not conn:
            return

        try:
            # CRITICAL: Use DictCursor for dictionary-based result access
            cursor = conn.cursor(mysql_connector.cursors.DictCursor)

            # Ensure audit table exists
            self.create_audit_table(cursor)

            total_updated = 0

            # IMPORTANT: Only the patient table has void_reason set during bulk void.
            # Other tables only have date_voided timestamp.
            # Strategy:
            #   - Patient table: Check BOTH void_reason AND timestamp
            #   - All other tables: Check timestamp ONLY

            # 1. Unvoid patient table (with void_reason check for safety)
            self.log(f"Unvoiding patient...")
            query = """
                UPDATE patient
                SET voided = 0, 
                    voided_by = NULL, 
                    date_voided = NULL, 
                    void_reason = NULL
                WHERE patient_id = %s 
                  AND voided = 1
                  AND void_reason = 'Bulk void via ART/DATIM mapping'
                  AND date_voided BETWEEN %s AND %s
            """
            cursor.execute(query, (patient_id, time_start, time_end))
            rows = cursor.rowcount
            total_updated += rows
            if rows > 0:
                self.log(f"  [OK] {rows} record(s) unvoided in patient")
            else:
                self.log(f"  [WARNING] No records matched in patient table")

            # 2. Unvoid patient_identifier (timestamp-based ONLY - no void_reason!)
            self.log(f"Unvoiding patient_identifier...")
            query = """
                UPDATE patient_identifier
                SET voided = 0, 
                    voided_by = NULL, 
                    date_voided = NULL, 
                    void_reason = NULL
                WHERE patient_id = %s 
                  AND voided = 1
                  AND date_voided BETWEEN %s AND %s
            """
            cursor.execute(query, (patient_id, time_start, time_end))
            rows = cursor.rowcount
            total_updated += rows
            if rows > 0:
                self.log(f"  [OK] {rows} record(s) unvoided in patient_identifier")

            # 3. Unvoid patient_program (timestamp-based ONLY - no void_reason!)
            self.log(f"Unvoiding patient_program...")
            query = """
                UPDATE patient_program
                SET voided = 0, 
                    voided_by = NULL, 
                    date_voided = NULL, 
                    void_reason = NULL
                WHERE patient_id = %s 
                  AND voided = 1
                  AND date_voided BETWEEN %s AND %s
            """
            cursor.execute(query, (patient_id, time_start, time_end))
            rows = cursor.rowcount
            total_updated += rows
            if rows > 0:
                self.log(f"  [OK] {rows} record(s) unvoided in patient_program")

            # 4. Unvoid person (timestamp-based ONLY - no void_reason!)
            self.log(f"Unvoiding person...")
            query = """
                UPDATE person
                SET voided = 0, 
                    voided_by = NULL, 
                    date_voided = NULL, 
                    void_reason = NULL
                WHERE person_id = %s 
                  AND voided = 1
                  AND date_voided BETWEEN %s AND %s
            """
            cursor.execute(query, (patient_id, time_start, time_end))
            rows = cursor.rowcount
            total_updated += rows
            if rows > 0:
                self.log(f"  [OK] {rows} record(s) unvoided in person")

            # 5. Unvoid person_name (MOST RECENT ONLY - sensitive identity data!)
            # CRITICAL: Only unvoid the most recent voided record to prevent duplicates
            # Rationale: Patient should have ONE active name, not multiple
            # Old legitimately voided names should remain voided
            self.log(f"Unvoiding person_name (most recent only)...")

            # Step 1: Find most recent voided record
            query = """
                SELECT person_name_id 
                FROM person_name
                WHERE person_id = %s AND voided = 1
                ORDER BY COALESCE(date_voided, date_created) DESC
                LIMIT 1
            """
            cursor.execute(query, (patient_id,))
            result = cursor.fetchone()

            if result:
                # Step 2: Unvoid only that one record
                name_id = result['person_name_id']
                query = """
                    UPDATE person_name
                    SET voided = 0, 
                        voided_by = NULL, 
                        date_voided = NULL, 
                        void_reason = NULL
                    WHERE person_name_id = %s
                """
                cursor.execute(query, (name_id,))
                rows = cursor.rowcount
                total_updated += rows
                if rows > 0:
                    self.log(f"  [OK] Unvoided most recent person_name record (ID: {name_id})")
            else:
                self.log(f"  [INFO] No voided person_name records found")

            # 6. Unvoid person_address (MOST RECENT ONLY - sensitive identity data!)
            # CRITICAL: Only unvoid the most recent voided record to prevent duplicates
            # Rationale: Patient should have ONE active address, not multiple
            # Old legitimately voided addresses should remain voided
            # NOTE: Bulk void script doesn't set date_voided for this table
            self.log(f"Unvoiding person_address (most recent only)...")

            # Step 1: Find most recent voided record
            query = """
                SELECT person_address_id 
                FROM person_address
                WHERE person_id = %s AND voided = 1
                ORDER BY COALESCE(date_voided, date_created) DESC
                LIMIT 1
            """
            cursor.execute(query, (patient_id,))
            result = cursor.fetchone()

            if result:
                # Step 2: Unvoid only that one record
                address_id = result['person_address_id']
                query = """
                    UPDATE person_address
                    SET voided = 0, 
                        voided_by = NULL, 
                        date_voided = NULL, 
                        void_reason = NULL
                    WHERE person_address_id = %s
                """
                cursor.execute(query, (address_id,))
                rows = cursor.rowcount
                total_updated += rows
                if rows > 0:
                    self.log(f"  [OK] Unvoided most recent person_address record (ID: {address_id})")
            else:
                self.log(f"  [INFO] No voided person_address records found")

            # 7. Unvoid person_attribute (MOST RECENT ONLY - sensitive identity data!)
            # CRITICAL: Only unvoid the most recent voided record to prevent duplicates
            # Rationale: Patient should have ONE set of active attributes, not multiple
            # Old legitimately voided attributes should remain voided
            # NOTE: Bulk void script doesn't set date_voided for this table
            self.log(f"Unvoiding person_attribute (most recent only)...")

            # Step 1: Find most recent voided record
            query = """
                SELECT person_attribute_id 
                FROM person_attribute
                WHERE person_id = %s AND voided = 1
                ORDER BY COALESCE(date_voided, date_created) DESC
                LIMIT 1
            """
            cursor.execute(query, (patient_id,))
            result = cursor.fetchone()

            if result:
                # Step 2: Unvoid only that one record
                attribute_id = result['person_attribute_id']
                query = """
                    UPDATE person_attribute
                    SET voided = 0, 
                        voided_by = NULL, 
                        date_voided = NULL, 
                        void_reason = NULL
                    WHERE person_attribute_id = %s
                """
                cursor.execute(query, (attribute_id,))
                rows = cursor.rowcount
                total_updated += rows
                if rows > 0:
                    self.log(f"  [OK] Unvoided most recent person_attribute record (ID: {attribute_id})")
            else:
                self.log(f"  [INFO] No voided person_attribute records found")

            # 8. Unvoid visit (timestamp-based ONLY - no void_reason!)
            self.log(f"Unvoiding visit...")
            query = """
                UPDATE visit
                SET voided = 0, 
                    voided_by = NULL, 
                    date_voided = NULL, 
                    void_reason = NULL
                WHERE patient_id = %s 
                  AND voided = 1
                  AND date_voided BETWEEN %s AND %s
            """
            cursor.execute(query, (patient_id, time_start, time_end))
            rows = cursor.rowcount
            total_updated += rows
            if rows > 0:
                self.log(f"  [OK] {rows} record(s) unvoided in visit")

            # 9. Unvoid encounter (timestamp-based ONLY - no void_reason!)
            self.log(f"Unvoiding encounter...")
            query = """
                UPDATE encounter
                SET voided = 0, 
                    voided_by = NULL, 
                    date_voided = NULL, 
                    void_reason = NULL
                WHERE patient_id = %s 
                  AND voided = 1
                  AND date_voided BETWEEN %s AND %s
            """
            cursor.execute(query, (patient_id, time_start, time_end))
            rows = cursor.rowcount
            total_updated += rows
            if rows > 0:
                self.log(f"  [OK] {rows} record(s) unvoided in encounter")

            # 10. Unvoid obs (timestamp-based ONLY - no void_reason!)
            self.log(f"Unvoiding obs...")
            query = """
                UPDATE obs
                SET voided = 0, 
                    voided_by = NULL, 
                    date_voided = NULL, 
                    void_reason = NULL
                WHERE person_id = %s 
                  AND voided = 1
                  AND date_voided BETWEEN %s AND %s
            """
            cursor.execute(query, (patient_id, time_start, time_end))
            rows = cursor.rowcount
            total_updated += rows
            if rows > 0:
                self.log(f"  [OK] {rows} record(s) unvoided in obs")

            # Log to audit table with timestamp info
            audit_query = """
                INSERT INTO nmrs_unvoid_audit
                (identifier, patient_id, patient_name, executed_by, action_status, remarks)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            remarks = (
                f'Timestamp-based unvoid: {void_timestamp} (±120sec). '
                f'Range: {time_start} to {time_end}. '
                f'Total: {total_updated} records. '
                f'void_reason: Bulk void via ART/DATIM mapping. '
                f'SMART STRATEGY: person_name, person_address, person_attribute unvoided '
                f'using MOST RECENT ONLY (prevents duplicates, respects old legitimate voids)'
            )

            cursor.execute(audit_query, (
                identifier,
                patient_id,
                patient['patient_name'],
                admin_name,
                'SUCCESS',
                remarks
            ))

            # Commit transaction
            conn.commit()

            self.log("-" * 70)
            self.log(f"SUCCESS: Unvoided {total_updated} total records")
            self.log(f"         within timestamp range (±120 seconds)")
            self.log(f"         Records outside this range remain voided (SAFE)")
            self.log("-" * 70)
            self.log(f"Audit entry created in nmrs_unvoid_audit")
            self.log("-" * 70)

            # Show success message
            messagebox.showinfo(
                "Unvoid Complete",
                f"SUCCESS: Patient records successfully unvoided!\n\n"
                f"Patient: {patient['patient_name']}\n"
                f"Identifier: {identifier}\n"
                f"Total Records Unvoided: {total_updated}\n\n"
                f"SMART STRATEGY APPLIED:\n"
                f"• 7 tables: Timestamp-based (±120 seconds)\n"
                f"• 3 sensitive tables: Most recent only\n"
                f"  (person_name, person_address, person_attribute)\n\n"
                f"Timestamp Range: {time_start} to {time_end}\n\n"
                f"SAFETY: This prevents duplicate records and\n"
                f"respects old legitimate voids.\n\n"
                f"Audit entry has been logged."
            )

            # Reset form
            self.clear_form()

        except Error as e:
            conn.rollback()
            error_msg = f"ERROR: Unvoid operation failed - {str(e)}"
            self.log(error_msg)
            self.log(f"ERROR DETAILS: {traceback.format_exc()}")
            messagebox.showerror(
                "Unvoid Failed",
                f"Operation failed:\n\n{str(e)}\n\n"
                "No changes have been made to the database.\n\n"
                "Check the log for details."
            )

        except Exception as e:
            conn.rollback()
            error_msg = f"UNEXPECTED ERROR: {str(e)}"
            self.log(error_msg)
            self.log(f"TRACEBACK: {traceback.format_exc()}")
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\n"
                "No changes have been made to the database.\n\n"
                "Check the log for details."
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

    # ------------------------------------------------------------------
    # INH Date Clear feature
    # ------------------------------------------------------------------
    # Looks up obs rows for INH Start Date (concept_id 164852) and
    # Stop Date (concept_id 166096) on form_id=56 encounters for the
    # given ART identifier (identifier_type=4) and lets the admin
    # selectively NULL their value_datetime. Each cleared row is
    # recorded in nmrs_inh_date_clear_audit.

    INH_FORM_ID = 56
    INH_IDENTIFIER_TYPE = 4
    INH_CONCEPT_LABELS = {164852: "Start Date", 166096: "Stop Date"}

    def lookup_inh_dates(self):
        """Fetch active INH Start/Stop date obs for the entered identifier."""

        identifier = self.inh_identifier_entry.get().strip()

        # Reset UI state first so a failed lookup doesn't leave stale rows
        for child in self.inh_rows_frame.winfo_children():
            child.destroy()
        self.inh_obs_rows = []
        self.inh_patient = None
        self.inh_clear_button.config(state="disabled", bg="#cccccc", fg="#666666")
        self.inh_summary_label.config(text="(no patient loaded)", fg="#666")

        if not identifier:
            messagebox.showwarning("Input Required", "Please enter an ART identifier.")
            return

        self.log(f"[INH] Looking up INH dates for: {identifier}")

        conn = self.get_connection()
        if not conn:
            return

        cursor = None
        try:
            cursor = conn.cursor(mysql_connector.cursors.DictCursor)

            query = """
                SELECT
                    o.obs_id,
                    o.concept_id,
                    o.value_datetime,
                    o.encounter_id,
                    e.encounter_datetime,
                    e.patient_id,
                    CONCAT(pn.given_name, ' ', IFNULL(pn.family_name, '')) AS patient_name
                FROM obs o
                JOIN encounter e ON o.encounter_id = e.encounter_id
                JOIN patient_identifier pid ON e.patient_id = pid.patient_id
                LEFT JOIN person_name pn
                    ON e.patient_id = pn.person_id AND pn.voided = 0
                WHERE pid.identifier = %s
                  AND pid.identifier_type = %s
                  AND pid.voided = 0
                  AND e.form_id = %s
                  AND e.voided = 0
                  AND o.concept_id IN (164852, 166096)
                  AND o.voided = 0
                ORDER BY e.encounter_datetime DESC, o.concept_id
            """
            cursor.execute(query, (identifier, self.INH_IDENTIFIER_TYPE, self.INH_FORM_ID))
            rows = cursor.fetchall()

            if not rows:
                self.log(f"[INH] No matching INH date observations for {identifier}")
                messagebox.showinfo(
                    "No INH Dates Found",
                    f"No active INH Start/Stop date observations were found for "
                    f"identifier {identifier} on form_id={self.INH_FORM_ID} encounters.\n\n"
                    f"Nothing to clear."
                )
                return

            first = rows[0]
            self.inh_patient = {
                "identifier": identifier,
                "patient_id": first["patient_id"],
                "patient_name": (first["patient_name"] or "(unknown)").strip(),
            }
            self.inh_summary_label.config(
                text=(
                    f"Identifier:        {identifier}\n"
                    f"Patient ID:        {first['patient_id']}\n"
                    f"Name:              {self.inh_patient['patient_name']}\n"
                    f"Matching obs rows: {len(rows)}"
                ),
                fg="#222"
            )

            for row in rows:
                var = tk.BooleanVar(value=False)
                row_frame = tk.Frame(self.inh_rows_frame)
                row_frame.pack(fill="x", pady=1)

                tk.Checkbutton(
                    row_frame,
                    variable=var,
                    command=self._update_inh_clear_button_state,
                    width=5
                ).pack(side="left")

                value_dt = row["value_datetime"]
                value_str = value_dt.strftime("%Y-%m-%d") if value_dt else "(NULL)"
                enc_dt = row["encounter_datetime"]
                enc_str = enc_dt.strftime("%Y-%m-%d %H:%M") if enc_dt else "(unknown)"
                concept_name = self.INH_CONCEPT_LABELS.get(
                    row["concept_id"], str(row["concept_id"])
                )

                for text, width in [
                    (str(row["obs_id"]), 10),
                    (concept_name, 14),
                    (value_str, 14),
                    (enc_str, 16),
                    (str(row["encounter_id"]), 12),
                ]:
                    tk.Label(
                        row_frame, text=text, font=("Courier", 9),
                        width=width, anchor="w"
                    ).pack(side="left")

                self.inh_obs_rows.append({
                    "var": var,
                    "obs_id": row["obs_id"],
                    "concept_id": row["concept_id"],
                    "concept_name": concept_name,
                    "current_value": value_dt,
                    "encounter_id": row["encounter_id"],
                    "encounter_datetime": enc_dt,
                })

            self.log(f"[INH] Loaded {len(rows)} INH date row(s) for {identifier}")

        except Error as e:
            self.log(f"[INH] ERROR: {str(e)}")
            messagebox.showerror("Database Error", f"Lookup failed:\n\n{str(e)}")
        finally:
            if cursor:
                cursor.close()

    def _update_inh_clear_button_state(self):
        """Enable Clear button only when at least one box is ticked."""
        any_checked = any(row["var"].get() for row in self.inh_obs_rows)
        if any_checked:
            self.inh_clear_button.config(state="normal", bg="#f44336", fg="white")
        else:
            self.inh_clear_button.config(state="disabled", bg="#cccccc", fg="#666666")

    def confirm_clear_inh_dates(self):
        """Confirm before clearing selected INH date obs rows."""

        if not self.inh_patient:
            return

        selected = [r for r in self.inh_obs_rows if r["var"].get()]
        if not selected:
            return

        lines = [
            "  obs_id={oid}  {cn:<11}  current={cv}".format(
                oid=r["obs_id"],
                cn=r["concept_name"],
                cv=r["current_value"].strftime("%Y-%m-%d") if r["current_value"] else "(NULL)"
            )
            for r in selected
        ]

        msg = (
            f"You are about to set value_datetime = NULL on the following obs row(s):\n\n"
            f"Patient:    {self.inh_patient['patient_name']} ({self.inh_patient['identifier']})\n"
            f"Patient ID: {self.inh_patient['patient_id']}\n\n"
            + "\n".join(lines)
            + f"\n\nTotal rows: {len(selected)}\n\nProceed?"
        )

        if not messagebox.askyesno("Confirm Clear INH Dates", msg, icon="warning"):
            return

        self.execute_clear_inh_dates(selected)

    def execute_clear_inh_dates(self, selected):
        """Execute the UPDATE for each selected obs row, atomically."""

        if not self.inh_patient or not selected:
            return

        admin_name = self.config["settings"].get("admin_name", "Administrator")

        self.log("-" * 70)
        self.log(
            f"[INH] Clearing {len(selected)} INH date row(s) for "
            f"{self.inh_patient['identifier']} "
            f"(patient_id={self.inh_patient['patient_id']})"
        )

        conn = self.get_connection()
        if not conn:
            return

        cursor = None
        try:
            cursor = conn.cursor(mysql_connector.cursors.DictCursor)
            self.create_inh_audit_table(cursor)

            updated = 0
            for r in selected:
                cursor.execute(
                    "UPDATE obs SET value_datetime = NULL "
                    "WHERE obs_id = %s AND voided = 0",
                    (r["obs_id"],)
                )
                row_count = cursor.rowcount
                updated += row_count

                cursor.execute(
                    """
                    INSERT INTO nmrs_inh_date_clear_audit
                        (identifier, patient_id, patient_name, obs_id, concept_id,
                         concept_name, encounter_id, encounter_datetime,
                         previous_value_datetime, executed_by, action_status, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        self.inh_patient["identifier"],
                        self.inh_patient["patient_id"],
                        self.inh_patient["patient_name"],
                        r["obs_id"],
                        r["concept_id"],
                        r["concept_name"],
                        r["encounter_id"],
                        r["encounter_datetime"],
                        r["current_value"],
                        admin_name,
                        "SUCCESS" if row_count == 1 else "NO_CHANGE",
                        "value_datetime set to NULL via INH Date Clear feature.",
                    ),
                )

                status_icon = "[OK]" if row_count == 1 else "[SKIP]"
                self.log(
                    f"  {status_icon} obs_id={r['obs_id']} ({r['concept_name']}) "
                    f"prev={r['current_value']} -> NULL  (rows={row_count})"
                )

            conn.commit()
            self.log(
                f"[INH] Done. {updated} of {len(selected)} row(s) updated. "
                f"Audit recorded in nmrs_inh_date_clear_audit."
            )
            self.log("-" * 70)

            messagebox.showinfo(
                "INH Dates Cleared",
                f"Updated {updated} of {len(selected)} obs row(s).\n\n"
                f"Patient: {self.inh_patient['patient_name']} "
                f"({self.inh_patient['identifier']})\n\n"
                f"Audit entries written to nmrs_inh_date_clear_audit."
            )

            # Refresh the lookup so the updated state shows immediately
            self.lookup_inh_dates()

        except Error as e:
            conn.rollback()
            self.log(f"[INH] ERROR: rollback - {str(e)}")
            messagebox.showerror(
                "Update Failed",
                f"Operation failed:\n\n{str(e)}\n\n"
                f"No changes have been made (rolled back)."
            )
        except Exception as e:
            conn.rollback()
            self.log(f"[INH] UNEXPECTED ERROR: {str(e)}")
            self.log(traceback.format_exc())
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\n"
                f"No changes have been made (rolled back)."
            )
        finally:
            if cursor:
                cursor.close()

    def create_inh_audit_table(self, cursor):
        """Ensure the INH date clear audit table exists."""

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nmrs_inh_date_clear_audit (
                audit_id                INT AUTO_INCREMENT PRIMARY KEY,
                action_time             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                identifier              VARCHAR(50) NOT NULL,
                patient_id              INT,
                patient_name            VARCHAR(255),
                obs_id                  INT NOT NULL,
                concept_id              INT NOT NULL,
                concept_name            VARCHAR(50),
                encounter_id            INT,
                encounter_datetime      DATETIME,
                previous_value_datetime DATETIME,
                executed_by             VARCHAR(100),
                action_status           VARCHAR(20),
                remarks                 TEXT,
                INDEX idx_inh_audit_obs (obs_id),
                INDEX idx_inh_audit_identifier (identifier),
                INDEX idx_inh_audit_action_time (action_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            """
        )

    # ------------------------------------------------------------------
    # Move Encounter Date feature
    # ------------------------------------------------------------------
    # Shifts encounter_datetime for selected encounter(s) of a client
    # (identifier_type=4, not voided) from a stated current date to a
    # new date. The same delta is applied to every non-voided obs row
    # on those encounters: obs_datetime always, and value_datetime when
    # concept_id = 5096 (RETURN VISIT DATE) or concept_id = 164989
    # (ORDER DATE). If the shift would push the encounter outside its
    # visit window, the user is asked (via a per-row checkbox in the
    # preview) whether to shift the visit too.

    MOVE_IDENTIFIER_TYPE = 4
    MOVE_RETURN_VISIT_CONCEPT = 5096
    MOVE_ORDER_DATE_CONCEPT = 164989

    def _build_move_encounter_tab(self, parent):
        """Build the Move Encounter Date UI inside the given tab frame."""

        content_frame = tk.Frame(parent, padx=20, pady=15)
        content_frame.pack(fill="both", expand=True)

        # Step 1: Inputs
        input_frame = tk.LabelFrame(
            content_frame,
            text="Step 1: Encounter Lookup",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        input_frame.pack(fill="x", pady=(0, 12))

        # Identifiers
        tk.Label(
            input_frame,
            text="ART Identifier(s) — single, or comma-separated for batch:",
            font=("Arial", 10)
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))

        self.move_identifier_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bd=2, relief="solid")
        self.move_identifier_entry.grid(row=1, column=0, columnspan=4, sticky="we", pady=(0, 8))

        tk.Label(input_frame, text="Form ID:", font=("Arial", 10)).grid(row=2, column=0, sticky="e", padx=(0, 4))
        self.move_form_entry = tk.Entry(input_frame, font=("Arial", 11), width=8, bd=2, relief="solid")
        self.move_form_entry.grid(row=2, column=1, sticky="w", padx=(0, 12))

        tk.Label(input_frame, text="Current Date (YYYY-MM-DD):", font=("Arial", 10)).grid(row=2, column=2, sticky="e", padx=(0, 4))
        self.move_current_entry = tk.Entry(input_frame, font=("Arial", 11), width=14, bd=2, relief="solid")
        self.move_current_entry.grid(row=2, column=3, sticky="w")

        tk.Label(input_frame, text="New Date (YYYY-MM-DD):", font=("Arial", 10)).grid(row=3, column=2, sticky="e", padx=(0, 4), pady=(6, 0))
        self.move_new_entry = tk.Entry(input_frame, font=("Arial", 11), width=14, bd=2, relief="solid")
        self.move_new_entry.grid(row=3, column=3, sticky="w", pady=(6, 0))

        tk.Button(
            input_frame,
            text="PREVIEW MATCHES",
            command=self.lookup_move_encounters,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=6,
            cursor="hand2"
        ).grid(row=2, column=4, rowspan=2, padx=(20, 0))

        # Step 2: Preview grid
        preview_frame = tk.LabelFrame(
            content_frame,
            text="Step 2: Encounters Found — tick those to shift",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=8
        )
        preview_frame.pack(fill="both", expand=True, pady=(0, 12))

        header_row = tk.Frame(preview_frame, bg="#eeeeee")
        header_row.pack(fill="x")
        for text, width in [
            ("Shift?", 7),
            ("Enc ID", 8),
            ("Identifier", 14),
            ("Patient", 22),
            ("Form", 6),
            ("Current", 17),
            ("New", 17),
            ("Obs", 5),
            ("RV", 4),
            ("OrdDt", 6),
            ("Visit", 7),
            ("Shift Visit?", 12),
        ]:
            tk.Label(
                header_row, text=text, font=("Arial", 9, "bold"),
                width=width, anchor="w", bg="#eeeeee"
            ).pack(side="left")

        rows_container = tk.Frame(preview_frame)
        rows_container.pack(fill="both", expand=True)

        rows_canvas = tk.Canvas(rows_container, height=180, highlightthickness=0)
        rows_scroll = ttk.Scrollbar(rows_container, orient="vertical", command=rows_canvas.yview)
        self.move_rows_frame = tk.Frame(rows_canvas)
        self.move_rows_frame.bind(
            "<Configure>",
            lambda e: rows_canvas.configure(scrollregion=rows_canvas.bbox("all"))
        )
        rows_canvas.create_window((0, 0), window=self.move_rows_frame, anchor="nw")
        rows_canvas.configure(yscrollcommand=rows_scroll.set)
        rows_canvas.pack(side="left", fill="both", expand=True)
        rows_scroll.pack(side="right", fill="y")

        # Step 3: Apply
        action_frame = tk.LabelFrame(
            content_frame,
            text="Step 3: Apply Shift",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8
        )
        action_frame.pack(fill="x")

        tk.Label(
            action_frame,
            text="Voided encounters/obs are excluded. RV = RETURN VISIT DATE (concept 5096). "
                 "OrdDt = ORDER DATE (concept 164989). "
                 "Tick 'Shift Visit?' to also shift the encounter's visit window by the same delta.",
            font=("Arial", 9),
            fg="#555",
            wraplength=860,
            justify="left"
        ).pack(anchor="w", pady=(0, 6))

        self.move_apply_button = tk.Button(
            action_frame,
            text="APPLY SHIFT",
            command=self.confirm_move_encounters,
            bg="#cccccc",
            fg="#666666",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            cursor="hand2",
            state="disabled",
            disabledforeground="#666666"
        )
        self.move_apply_button.pack()

        # State
        self.move_rows = []

    # Characters often pasted in alongside an identifier — strip these in addition
    # to standard whitespace so the IN-clause match isn't sabotaged by invisibles.
    _MOVE_ID_INVISIBLES = " ​‌‍⁠﻿"

    def _parse_move_identifiers(self, raw):
        """Split on any common separator (comma, newline, tab, semicolon, pipe),
        strip whitespace and zero-width / BOM characters, drop empties.
        """
        # Normalise separators to commas first.
        normalised = raw
        for sep in ("\r\n", "\r", "\n", "\t", ";", "|"):
            normalised = normalised.replace(sep, ",")
        cleaned = []
        for token in normalised.split(","):
            t = token.strip().strip(self._MOVE_ID_INVISIBLES).strip()
            if t:
                cleaned.append(t)
        return cleaned

    def _parse_date(self, s, field_label):
        """Parse YYYY-MM-DD; return date or None (and warn)."""
        try:
            return datetime.strptime(s.strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                f"{field_label} must be in YYYY-MM-DD format (got: '{s}')."
            )
            return None

    def lookup_move_encounters(self):
        """Find non-voided encounters matching the identifier/form/current_date inputs."""

        # Reset UI first
        for child in self.move_rows_frame.winfo_children():
            child.destroy()
        self.move_rows = []
        self.move_apply_button.config(state="disabled", bg="#cccccc", fg="#666666")

        raw_ids = self.move_identifier_entry.get().strip()
        form_raw = self.move_form_entry.get().strip()
        current_raw = self.move_current_entry.get().strip()
        new_raw = self.move_new_entry.get().strip()

        if not raw_ids or not form_raw or not current_raw or not new_raw:
            messagebox.showwarning(
                "Input Required",
                "Please supply identifier(s), form ID, current date, and new date."
            )
            return

        try:
            form_id = int(form_raw)
        except ValueError:
            messagebox.showwarning("Invalid Form ID", f"Form ID must be an integer (got: '{form_raw}').")
            return

        current_date = self._parse_date(current_raw, "Current Date")
        new_date = self._parse_date(new_raw, "New Date")
        if not current_date or not new_date:
            return

        if current_date == new_date:
            messagebox.showinfo("No Change", "Current date and new date are the same — nothing to shift.")
            return

        identifiers = self._parse_move_identifiers(raw_ids)
        if not identifiers:
            messagebox.showwarning("Input Required", "Please supply at least one identifier.")
            return

        # Log with repr so hidden characters (zero-width, NBSP, BOM) are visible if any slipped through.
        self.log(
            f"[MOVE] Lookup: ids={[repr(i) for i in identifiers]} "
            f"form={form_id} current={current_date} new={new_date}"
        )

        conn = self.get_connection()
        if not conn:
            return

        cursor = None
        try:
            cursor = conn.cursor(mysql_connector.cursors.DictCursor)

            placeholders = ",".join(["%s"] * len(identifiers))
            query = f"""
                SELECT
                    e.encounter_id,
                    e.encounter_datetime,
                    e.form_id,
                    e.visit_id,
                    e.patient_id,
                    pi.identifier,
                    CONCAT(pn.given_name, ' ', IFNULL(pn.family_name, '')) AS patient_name,
                    v.date_started   AS visit_started,
                    v.date_stopped   AS visit_stopped
                FROM encounter e
                JOIN patient_identifier pi
                    ON pi.patient_id = e.patient_id
                   AND pi.identifier_type = %s
                   AND pi.voided = 0
                LEFT JOIN person_name pn
                    ON pn.person_id = e.patient_id AND pn.voided = 0
                LEFT JOIN visit v
                    ON v.visit_id = e.visit_id AND v.voided = 0
                WHERE pi.identifier IN ({placeholders})
                  AND e.form_id = %s
                  AND DATE(e.encounter_datetime) = %s
                  AND e.voided = 0
                ORDER BY pi.identifier, e.encounter_datetime
            """
            params = [self.MOVE_IDENTIFIER_TYPE] + list(identifiers) + [form_id, current_date]
            cursor.execute(query, params)
            encounters = cursor.fetchall()

            if not encounters:
                diag = self._diagnose_move_lookup(cursor, identifiers, form_id, current_date)
                self.log(f"[MOVE] No matching non-voided encounters found.")
                for line in diag:
                    self.log(f"[MOVE] DIAG: {line}")
                messagebox.showinfo(
                    "No Matches",
                    "No non-voided encounters matched the supplied identifier(s), form ID, "
                    "and current date.\n\nDiagnostics:\n  - " + "\n  - ".join(diag)
                )
                return

            for enc in encounters:
                # Count obs and return-visit obs to be shifted (informational only)
                cursor.execute(
                    "SELECT COUNT(*) AS c FROM obs WHERE encounter_id = %s AND voided = 0",
                    (enc["encounter_id"],)
                )
                obs_count = cursor.fetchone()["c"]

                cursor.execute(
                    "SELECT COUNT(*) AS c FROM obs WHERE encounter_id = %s AND voided = 0 "
                    "AND concept_id = %s AND value_datetime IS NOT NULL",
                    (enc["encounter_id"], self.MOVE_RETURN_VISIT_CONCEPT)
                )
                rv_count = cursor.fetchone()["c"]

                cursor.execute(
                    "SELECT COUNT(*) AS c FROM obs WHERE encounter_id = %s AND voided = 0 "
                    "AND concept_id = %s AND value_datetime IS NOT NULL",
                    (enc["encounter_id"], self.MOVE_ORDER_DATE_CONCEPT)
                )
                order_count = cursor.fetchone()["c"]

                old_dt = enc["encounter_datetime"]
                # Preserve time-of-day on the new datetime
                new_dt = datetime.combine(new_date, old_dt.time()) if old_dt else None

                # Determine if visit window would be invalidated
                visit_id = enc["visit_id"]
                needs_visit_shift = False
                if visit_id and new_dt:
                    vs = enc["visit_started"]
                    ve = enc["visit_stopped"]
                    if (vs is not None and new_dt < vs) or (ve is not None and new_dt > ve):
                        needs_visit_shift = True

                self._add_move_row(
                    enc=enc,
                    old_dt=old_dt,
                    new_dt=new_dt,
                    obs_count=obs_count,
                    rv_count=rv_count,
                    order_count=order_count,
                    visit_id=visit_id,
                    needs_visit_shift=needs_visit_shift
                )

            self.log(f"[MOVE] Loaded {len(encounters)} encounter row(s) for preview.")

        except Error as e:
            self.log(f"[MOVE] ERROR: {str(e)}")
            messagebox.showerror("Database Error", f"Lookup failed:\n\n{str(e)}")
        finally:
            if cursor:
                cursor.close()

    def _diagnose_move_lookup(self, cursor, identifiers, form_id, current_date):
        """When the strict lookup finds nothing, pinpoint which filter dropped the row.

        Returns a list of operator-readable lines. Runs a few targeted queries
        against patient_identifier and encounter, ignoring voided/type filters
        progressively until something matches; reports what it found.
        """

        lines = []
        placeholders = ",".join(["%s"] * len(identifiers))

        # 1) Identifier existence (any type, any voided)
        cursor.execute(
            f"""
            SELECT identifier, identifier_type, voided, patient_id
            FROM patient_identifier
            WHERE identifier IN ({placeholders})
            """,
            list(identifiers),
        )
        pi_rows = cursor.fetchall()

        seen_ids = {r["identifier"] for r in pi_rows}
        missing = [i for i in identifiers if i not in seen_ids]
        for m in missing:
            # Show repr + byte length so hidden chars (zero-width, NBSP, BOM, embedded spaces) are visible.
            lines.append(
                f"identifier {m!r} (len={len(m)}, bytes={len(m.encode('utf-8'))}) "
                f"not found in patient_identifier — likely a hidden character or wrong DB"
            )

        for ident in identifiers:
            ident_rows = [r for r in pi_rows if r["identifier"] == ident]
            if not ident_rows:
                continue

            unvoided_t4 = [r for r in ident_rows if r["voided"] == 0 and r["identifier_type"] == self.MOVE_IDENTIFIER_TYPE]
            if not unvoided_t4:
                voided_t4 = [r for r in ident_rows if r["voided"] == 1 and r["identifier_type"] == self.MOVE_IDENTIFIER_TYPE]
                other_types = sorted({r["identifier_type"] for r in ident_rows if r["voided"] == 0})
                if voided_t4 and not other_types:
                    lines.append(f"identifier '{ident}' exists as type {self.MOVE_IDENTIFIER_TYPE} but is voided")
                elif other_types:
                    lines.append(
                        f"identifier '{ident}' exists, but with identifier_type(s) {other_types}, "
                        f"not the expected {self.MOVE_IDENTIFIER_TYPE}"
                    )
                else:
                    lines.append(f"identifier '{ident}' exists but no unvoided type-{self.MOVE_IDENTIFIER_TYPE} row")
                continue

            # We have at least one valid pi row for this identifier; check encounters.
            patient_ids = sorted({r["patient_id"] for r in unvoided_t4})
            pid_placeholders = ",".join(["%s"] * len(patient_ids))

            # Any encounter at all for these patient(s) on that date?
            cursor.execute(
                f"""
                SELECT encounter_id, form_id, voided, encounter_datetime
                FROM encounter
                WHERE patient_id IN ({pid_placeholders})
                  AND DATE(encounter_datetime) = %s
                """,
                patient_ids + [current_date],
            )
            day_rows = cursor.fetchall()

            if not day_rows:
                # Find the closest encounter date for this patient (form match preferred)
                cursor.execute(
                    f"""
                    SELECT DATE(encounter_datetime) AS d, form_id, voided
                    FROM encounter
                    WHERE patient_id IN ({pid_placeholders})
                      AND form_id = %s
                      AND voided = 0
                    ORDER BY ABS(DATEDIFF(encounter_datetime, %s)) ASC
                    LIMIT 3
                    """,
                    patient_ids + [form_id, current_date],
                )
                near = cursor.fetchall()
                if near:
                    near_str = ", ".join(str(r["d"]) for r in near)
                    lines.append(
                        f"'{ident}' has no encounter on {current_date}; "
                        f"nearest form-{form_id} encounter date(s): {near_str}"
                    )
                else:
                    lines.append(
                        f"'{ident}' has no encounter on {current_date}, and no form-{form_id} encounters at all"
                    )
                continue

            same_form = [r for r in day_rows if r["form_id"] == form_id]
            if not same_form:
                forms_on_day = sorted({r["form_id"] for r in day_rows})
                lines.append(
                    f"'{ident}' has encounter(s) on {current_date} but for form(s) {forms_on_day}, "
                    f"not form {form_id}"
                )
                continue

            unvoided_same_form = [r for r in same_form if r["voided"] == 0]
            if not unvoided_same_form:
                lines.append(
                    f"'{ident}' has form-{form_id} encounter(s) on {current_date} but ALL are voided "
                    f"(encounter_id(s): {[r['encounter_id'] for r in same_form]})"
                )
                continue

            # Shouldn't reach here — the strict query would have matched.
            lines.append(
                f"'{ident}' appears to match (encounter_id(s): {[r['encounter_id'] for r in unvoided_same_form]}); "
                f"strict join still returned nothing — please report this case"
            )

        if not lines:
            lines.append("no diagnostic findings — please share the input you used")
        return lines

    def _add_move_row(self, enc, old_dt, new_dt, obs_count, rv_count, order_count, visit_id, needs_visit_shift):
        """Render one encounter row in the preview grid."""

        var = tk.BooleanVar(value=False)
        visit_var = tk.BooleanVar(value=needs_visit_shift)

        row_frame = tk.Frame(self.move_rows_frame)
        row_frame.pack(fill="x", pady=1)

        tk.Checkbutton(
            row_frame, variable=var,
            command=self._update_move_apply_button_state, width=5
        ).pack(side="left")

        old_str = old_dt.strftime("%Y-%m-%d %H:%M") if old_dt else "(unknown)"
        new_str = new_dt.strftime("%Y-%m-%d %H:%M") if new_dt else "(unknown)"
        patient_str = (enc.get("patient_name") or "").strip()[:21]

        for text, width in [
            (str(enc["encounter_id"]), 8),
            (str(enc["identifier"]), 14),
            (patient_str, 22),
            (str(enc["form_id"]), 6),
            (old_str, 17),
            (new_str, 17),
            (str(obs_count), 5),
            (str(rv_count), 4),
            (str(order_count), 6),
            (str(visit_id) if visit_id else "-", 7),
        ]:
            tk.Label(row_frame, text=text, font=("Courier", 9), width=width, anchor="w").pack(side="left")

        visit_cb = tk.Checkbutton(row_frame, variable=visit_var, width=10)
        if not visit_id:
            visit_cb.config(state="disabled")
        # Highlight when needed
        if needs_visit_shift:
            visit_cb.config(fg="#d32f2f")
        visit_cb.pack(side="left")

        self.move_rows.append({
            "var": var,
            "visit_var": visit_var,
            "needs_visit_shift": needs_visit_shift,
            "encounter_id": enc["encounter_id"],
            "old_dt": old_dt,
            "new_dt": new_dt,
            "form_id": enc["form_id"],
            "identifier": enc["identifier"],
            "patient_id": enc["patient_id"],
            "patient_name": (enc.get("patient_name") or "").strip(),
            "visit_id": visit_id,
            "visit_started": enc["visit_started"],
            "visit_stopped": enc["visit_stopped"],
            "obs_count": obs_count,
            "rv_count": rv_count,
            "order_count": order_count,
        })

    def _update_move_apply_button_state(self):
        any_checked = any(r["var"].get() for r in self.move_rows)
        if any_checked:
            self.move_apply_button.config(state="normal", bg="#f44336", fg="white")
        else:
            self.move_apply_button.config(state="disabled", bg="#cccccc", fg="#666666")

    def confirm_move_encounters(self):
        """Single confirmation summarising what will be shifted."""

        selected = [r for r in self.move_rows if r["var"].get()]
        if not selected:
            return

        lines = []
        visit_shift_lines = []
        for r in selected:
            delta = r["new_dt"] - r["old_dt"]
            lines.append(
                f"  enc={r['encounter_id']:>7}  {r['identifier']:<12}  "
                f"{r['old_dt'].strftime('%Y-%m-%d %H:%M')} -> "
                f"{r['new_dt'].strftime('%Y-%m-%d %H:%M')}  "
                f"(obs={r['obs_count']}, rv={r['rv_count']}, ord={r['order_count']})"
            )
            if r["visit_id"] and r["visit_var"].get():
                visit_shift_lines.append(
                    f"  visit={r['visit_id']} (enc {r['encounter_id']})  shift by {delta}"
                )

        msg = (
            f"You are about to shift {len(selected)} encounter(s):\n\n"
            + "\n".join(lines)
            + ("\n\nVisit window shifts:\n" + "\n".join(visit_shift_lines) if visit_shift_lines else "")
            + "\n\nFor each encounter:\n"
            + "  - encounter.encounter_datetime is set to the new datetime\n"
            + "  - obs.obs_datetime is shifted by the same delta (voided=0)\n"
            + "  - obs.value_datetime for concept 5096 (RETURN VISIT DATE) is shifted by the same delta\n"
            + "  - obs.value_datetime for concept 164989 (ORDER DATE) is shifted by the same delta\n"
            + ("  - visit.date_started/date_stopped is shifted where ticked\n" if visit_shift_lines else "")
            + "\nProceed?"
        )

        if not messagebox.askyesno("Confirm Move Encounter", msg, icon="warning"):
            return

        self.execute_move_encounters(selected)

    def execute_move_encounters(self, selected):
        """Execute the encounter shift atomically (one transaction)."""

        admin_name = self.config["settings"].get("admin_name", "Administrator")

        self.log("-" * 70)
        self.log(f"[MOVE] Shifting {len(selected)} encounter(s)")

        conn = self.get_connection()
        if not conn:
            return

        cursor = None
        try:
            cursor = conn.cursor(mysql_connector.cursors.DictCursor)
            self.create_move_encounter_audit_table(cursor)

            total_obs = 0
            total_rv = 0
            total_order = 0
            total_visits = 0

            for r in selected:
                delta = r["new_dt"] - r["old_dt"]
                delta_seconds = int(delta.total_seconds())

                cursor.execute(
                    "UPDATE encounter SET encounter_datetime = %s, date_changed = NOW() "
                    "WHERE encounter_id = %s AND voided = 0",
                    (r["new_dt"], r["encounter_id"])
                )
                enc_rows = cursor.rowcount

                cursor.execute(
                    "UPDATE obs "
                    "SET obs_datetime = DATE_ADD(obs_datetime, INTERVAL %s SECOND) "
                    "WHERE encounter_id = %s AND voided = 0",
                    (delta_seconds, r["encounter_id"])
                )
                obs_rows = cursor.rowcount
                total_obs += obs_rows

                cursor.execute(
                    "UPDATE obs "
                    "SET value_datetime = DATE_ADD(value_datetime, INTERVAL %s SECOND) "
                    "WHERE encounter_id = %s AND voided = 0 "
                    "AND concept_id = %s AND value_datetime IS NOT NULL",
                    (delta_seconds, r["encounter_id"], self.MOVE_RETURN_VISIT_CONCEPT)
                )
                rv_rows = cursor.rowcount
                total_rv += rv_rows

                cursor.execute(
                    "UPDATE obs "
                    "SET value_datetime = DATE_ADD(value_datetime, INTERVAL %s SECOND) "
                    "WHERE encounter_id = %s AND voided = 0 "
                    "AND concept_id = %s AND value_datetime IS NOT NULL",
                    (delta_seconds, r["encounter_id"], self.MOVE_ORDER_DATE_CONCEPT)
                )
                order_rows = cursor.rowcount
                total_order += order_rows

                visit_shifted = 0
                if r["visit_id"] and r["visit_var"].get():
                    cursor.execute(
                        "UPDATE visit "
                        "SET date_started = DATE_ADD(date_started, INTERVAL %s SECOND), "
                        "    date_stopped = CASE WHEN date_stopped IS NULL THEN NULL "
                        "                        ELSE DATE_ADD(date_stopped, INTERVAL %s SECOND) END "
                        "WHERE visit_id = %s AND voided = 0",
                        (delta_seconds, delta_seconds, r["visit_id"])
                    )
                    visit_shifted = cursor.rowcount
                    total_visits += visit_shifted

                cursor.execute(
                    """
                    INSERT INTO nmrs_move_encounter_audit
                        (identifier, patient_id, patient_name, encounter_id, form_id,
                         old_encounter_datetime, new_encounter_datetime, delta_seconds,
                         obs_rows_shifted, return_visit_rows_shifted, order_date_rows_shifted,
                         visit_id, visit_shifted, executed_by, action_status, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        r["identifier"], r["patient_id"], r["patient_name"],
                        r["encounter_id"], r["form_id"],
                        r["old_dt"], r["new_dt"], delta_seconds,
                        obs_rows, rv_rows, order_rows,
                        r["visit_id"], 1 if visit_shifted else 0,
                        admin_name,
                        "SUCCESS" if enc_rows == 1 else "NO_CHANGE",
                        f"Shift via Move Encounter feature. delta={delta}.",
                    )
                )

                self.log(
                    f"  [OK] enc={r['encounter_id']}  obs={obs_rows}  rv={rv_rows}  "
                    f"ord={order_rows}  visit_shifted={visit_shifted}"
                )

            conn.commit()
            self.log(
                f"[MOVE] Done. {len(selected)} encounter(s); "
                f"{total_obs} obs, {total_rv} return-visit obs, {total_order} order-date obs, "
                f"{total_visits} visit window(s) shifted."
            )
            self.log("-" * 70)

            messagebox.showinfo(
                "Encounter Shift Complete",
                f"Shifted {len(selected)} encounter(s).\n\n"
                f"obs rows shifted: {total_obs}\n"
                f"RETURN VISIT DATE rows shifted: {total_rv}\n"
                f"ORDER DATE rows shifted: {total_order}\n"
                f"Visit windows shifted: {total_visits}\n\n"
                f"Audit entries written to nmrs_move_encounter_audit."
            )

            # Clear the preview rows — the just-shifted encounters no longer match
            # the old "current date" filter, and auto-searching would surface a
            # misleading "no matches" dialog right after a successful shift.
            # Pre-fill the current-date entry with the new date so a manual PREVIEW
            # would now find the moved encounter without further typing.
            for child in self.move_rows_frame.winfo_children():
                child.destroy()
            self.move_rows = []
            self.move_apply_button.config(state="disabled", bg="#cccccc", fg="#666666")
            self.move_current_entry.delete(0, "end")
            self.move_current_entry.insert(0, self.move_new_entry.get().strip())

        except Error as e:
            conn.rollback()
            self.log(f"[MOVE] ERROR: rollback - {str(e)}")
            messagebox.showerror(
                "Move Failed",
                f"Operation failed:\n\n{str(e)}\n\nNo changes have been made (rolled back)."
            )
        except Exception as e:
            conn.rollback()
            self.log(f"[MOVE] UNEXPECTED ERROR: {str(e)}")
            self.log(traceback.format_exc())
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\nNo changes have been made (rolled back)."
            )
        finally:
            if cursor:
                cursor.close()

    def create_move_encounter_audit_table(self, cursor):
        """Ensure the Move Encounter audit table exists."""

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nmrs_move_encounter_audit (
                audit_id                  INT AUTO_INCREMENT PRIMARY KEY,
                action_time               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                identifier                VARCHAR(50) NOT NULL,
                patient_id                INT,
                patient_name              VARCHAR(255),
                encounter_id              INT NOT NULL,
                form_id                   INT,
                old_encounter_datetime    DATETIME,
                new_encounter_datetime    DATETIME,
                delta_seconds             BIGINT,
                obs_rows_shifted          INT,
                return_visit_rows_shifted INT,
                order_date_rows_shifted   INT,
                visit_id                  INT,
                visit_shifted             TINYINT(1),
                executed_by               VARCHAR(100),
                action_status             VARCHAR(20),
                remarks                   TEXT,
                INDEX idx_mve_encounter (encounter_id),
                INDEX idx_mve_identifier (identifier),
                INDEX idx_mve_action_time (action_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            """
        )

        # Add order_date_rows_shifted to pre-existing audit tables (no-op if already present).
        cursor.execute(
            """
            SELECT COUNT(*) AS c
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'nmrs_move_encounter_audit'
              AND COLUMN_NAME = 'order_date_rows_shifted'
            """
        )
        if cursor.fetchone()["c"] == 0:
            cursor.execute(
                "ALTER TABLE nmrs_move_encounter_audit "
                "ADD COLUMN order_date_rows_shifted INT AFTER return_visit_rows_shifted"
            )

    # ------------------------------------------------------------------
    # Biometric Swap feature
    # ------------------------------------------------------------------
    # Restores correct biometric prints when Client A's print was
    # captured under Client B's id on a mobile NMRS and synced. The
    # admin loads a pre-sync .sql extract of biometricverificationinfo
    # into a session-scoped staging table, then supplies identifiers
    # for A and B. The tool:
    #   1. backs up the current (post-sync) biometric row for B
    #      — which is actually A's print
    #   2. writes that backup onto A's row (insert if A has no row)
    #   3. restores B's row from the pre-sync staging table
    # All inside one transaction with before/after hash checks.

    BIOMETRIC_TABLE = "biometricverificationinfo"
    BIOMETRIC_STAGING_TABLE = "biometric_presync_staging"
    BIOMETRIC_CORRUPT_BACKUP_TABLE = "biometric_corrupt_backup"
    BIOMETRIC_COLUMNS = [
        "patient_Id", "template", "imageWidth", "imageHeight", "imageDPI",
        "imageQuality", "fingerPosition", "serialNumber", "model",
        "manufacturer", "creator", "date_created", "new_template",
        "encoded_template", "hashed", "recapture_count",
    ]

    def _build_biometric_swap_tab(self, parent):
        """Build the Biometric Swap UI inside the given tab frame."""

        content_frame = tk.Frame(parent, padx=20, pady=15)
        content_frame.pack(fill="both", expand=True)

        # Step 1: Load pre-sync extract
        load_frame = tk.LabelFrame(
            content_frame,
            text="Step 1: Load Pre-Sync Biometric Extract (.sql)",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        load_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            load_frame,
            text=(
                f"Loads INSERT statements for {self.BIOMETRIC_TABLE} into "
                f"session-scoped {self.BIOMETRIC_STAGING_TABLE}. Existing staging rows are cleared first."
            ),
            font=("Arial", 9),
            fg="#555",
            wraplength=860,
            justify="left"
        ).pack(anchor="w", pady=(0, 6))

        load_row = tk.Frame(load_frame)
        load_row.pack(fill="x")

        tk.Button(
            load_row,
            text="LOAD PRE-SYNC .SQL",
            command=self.load_biometric_presync,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=6,
            cursor="hand2"
        ).pack(side="left")

        self.biom_load_label = tk.Label(
            load_row,
            text="(no file loaded)",
            font=("Courier", 9),
            fg="#666",
            anchor="w"
        )
        self.biom_load_label.pack(side="left", padx=(12, 0))

        # Step 2: Identifiers
        id_frame = tk.LabelFrame(
            content_frame,
            text="Step 2: Identifiers",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        id_frame.pack(fill="x", pady=(0, 12))

        tk.Label(id_frame, text="Client A (whose print was captured):", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=(0, 6))
        self.biom_a_entry = tk.Entry(id_frame, font=("Arial", 11), width=22, bd=2, relief="solid")
        self.biom_a_entry.grid(row=0, column=1, sticky="w")

        tk.Label(id_frame, text="Client B (whose ID was wrongly used):", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=(0, 6), pady=(6, 0))
        self.biom_b_entry = tk.Entry(id_frame, font=("Arial", 11), width=22, bd=2, relief="solid")
        self.biom_b_entry.grid(row=1, column=1, sticky="w", pady=(6, 0))

        tk.Button(
            id_frame,
            text="LOOKUP",
            command=self.lookup_biometric_swap,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=6,
            cursor="hand2"
        ).grid(row=0, column=2, rowspan=2, padx=(20, 0))

        # Step 3: Preview
        preview_frame = tk.LabelFrame(
            content_frame,
            text="Step 3: Swap Preview",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        preview_frame.pack(fill="both", expand=True, pady=(0, 12))

        self.biom_preview_text = tk.Text(
            preview_frame,
            height=12,
            font=("Courier", 9),
            bg="#f5f5f5",
            relief="solid",
            bd=1
        )
        self.biom_preview_text.pack(fill="both", expand=True)
        self.biom_preview_text.config(state="disabled")

        # Step 4: Apply
        action_frame = tk.LabelFrame(
            content_frame,
            text="Step 4: Apply Swap",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8
        )
        action_frame.pack(fill="x")

        tk.Label(
            action_frame,
            text=(
                "Backs up B's current (post-sync, corrupt) row, writes it to A, "
                "then restores B from the pre-sync staging table. Hash checks run before commit."
            ),
            font=("Arial", 9),
            fg="#555",
            wraplength=860,
            justify="left"
        ).pack(anchor="w", pady=(0, 6))

        self.biom_apply_button = tk.Button(
            action_frame,
            text="APPLY SWAP",
            command=self.confirm_biometric_swap,
            bg="#cccccc",
            fg="#666666",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            cursor="hand2",
            state="disabled",
            disabledforeground="#666666"
        )
        self.biom_apply_button.pack()

        # State
        self.biom_staging_loaded = False
        self.biom_lookup = None  # populated on successful lookup

    def load_biometric_presync(self):
        """Load the user-supplied .sql extract into session-scoped staging table."""

        path = filedialog.askopenfilename(
            title="Select pre-sync biometric extract",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            messagebox.showerror("File Error", f"Could not read file:\n\n{str(e)}")
            return

        conn = self.get_connection()
        if not conn:
            return

        cursor = None
        try:
            cursor = conn.cursor()

            # (Re)create staging table mirroring biometricverificationinfo
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {self.BIOMETRIC_STAGING_TABLE} "
                f"LIKE {self.BIOMETRIC_TABLE}"
            )
            cursor.execute(f"TRUNCATE TABLE {self.BIOMETRIC_STAGING_TABLE}")

            # Parse INSERT statements targeting biometricverificationinfo (any backtick style)
            pattern = re.compile(
                r"INSERT\s+(?:IGNORE\s+)?INTO\s+`?" + re.escape(self.BIOMETRIC_TABLE) + r"`?[^;]*;",
                re.IGNORECASE | re.DOTALL,
            )
            statements = pattern.findall(content)

            if not statements:
                messagebox.showwarning(
                    "No INSERTs Found",
                    f"No INSERT statements targeting {self.BIOMETRIC_TABLE} were found in the file."
                )
                return

            loaded = 0
            for stmt in statements:
                redirected = re.sub(
                    r"`?" + re.escape(self.BIOMETRIC_TABLE) + r"`?",
                    f"`{self.BIOMETRIC_STAGING_TABLE}`",
                    stmt,
                    count=1,
                    flags=re.IGNORECASE,
                )
                cursor.execute(redirected)
                loaded += cursor.rowcount

            conn.commit()

            self.biom_staging_loaded = True
            self.biom_load_label.config(
                text=f"{Path(path).name} — {loaded} row(s) into {self.BIOMETRIC_STAGING_TABLE}",
                fg="#222"
            )
            self.log(
                f"[BIOM] Loaded {loaded} row(s) from {path} into {self.BIOMETRIC_STAGING_TABLE}"
            )

        except Error as e:
            conn.rollback()
            self.log(f"[BIOM] ERROR loading extract: {str(e)}")
            messagebox.showerror("Database Error", f"Failed to load extract:\n\n{str(e)}")
        except Exception as e:
            conn.rollback()
            self.log(f"[BIOM] UNEXPECTED ERROR: {str(e)}")
            self.log(traceback.format_exc())
            messagebox.showerror("Unexpected Error", f"Failed to load extract:\n\n{str(e)}")
        finally:
            if cursor:
                cursor.close()

    def _resolve_active_patient(self, cursor, identifier):
        """Return (patient_id, patient_name) for an active identifier_type=4 row, or None."""
        cursor.execute(
            """
            SELECT pi.patient_id,
                   CONCAT(pn.given_name, ' ', IFNULL(pn.family_name, '')) AS patient_name
            FROM patient_identifier pi
            LEFT JOIN person_name pn ON pn.person_id = pi.patient_id AND pn.voided = 0
            WHERE pi.identifier = %s
              AND pi.identifier_type = %s
              AND pi.voided = 0
            LIMIT 1
            """,
            (identifier, self.MOVE_IDENTIFIER_TYPE),
        )
        row = cursor.fetchone()
        return row

    def _row_hash(self, row):
        """Hash the biometric template columns of a fetched row (dict or None)."""
        if not row:
            return None
        h = hashlib.sha256()
        for col in ("template", "new_template", "encoded_template", "hashed"):
            v = row.get(col)
            if v is None:
                h.update(b"\x00NULL\x00")
            elif isinstance(v, (bytes, bytearray)):
                h.update(b"\x00B\x00"); h.update(bytes(v))
            else:
                h.update(b"\x00S\x00"); h.update(str(v).encode("utf-8"))
        return h.hexdigest()

    def lookup_biometric_swap(self):
        """Resolve A and B; show side-by-side preview of current vs staging biometric state."""

        self.biom_apply_button.config(state="disabled", bg="#cccccc", fg="#666666")
        self.biom_lookup = None
        self._set_biom_preview("")

        if not self.biom_staging_loaded:
            messagebox.showwarning(
                "Load Extract First",
                "Load the pre-sync .sql extract (Step 1) before looking up clients."
            )
            return

        a_id = self.biom_a_entry.get().strip()
        b_id = self.biom_b_entry.get().strip()
        if not a_id or not b_id:
            messagebox.showwarning("Input Required", "Please supply both Client A and Client B identifiers.")
            return
        if a_id == b_id:
            messagebox.showwarning("Same Identifier", "Client A and Client B identifiers must differ.")
            return

        conn = self.get_connection()
        if not conn:
            return

        cursor = None
        try:
            cursor = conn.cursor(mysql_connector.cursors.DictCursor)

            a = self._resolve_active_patient(cursor, a_id)
            b = self._resolve_active_patient(cursor, b_id)
            if not a:
                messagebox.showerror("Not Found", f"No active patient with identifier {a_id} (type=4).")
                return
            if not b:
                messagebox.showerror("Not Found", f"No active patient with identifier {b_id} (type=4).")
                return

            cursor.execute(
                f"SELECT * FROM {self.BIOMETRIC_TABLE} WHERE patient_Id = %s",
                (a["patient_id"],)
            )
            a_current = cursor.fetchone()

            cursor.execute(
                f"SELECT * FROM {self.BIOMETRIC_TABLE} WHERE patient_Id = %s",
                (b["patient_id"],)
            )
            b_current = cursor.fetchone()

            cursor.execute(
                f"SELECT * FROM {self.BIOMETRIC_STAGING_TABLE} WHERE patient_Id = %s",
                (b["patient_id"],)
            )
            b_staging = cursor.fetchone()

            cursor.execute(
                f"SELECT * FROM {self.BIOMETRIC_STAGING_TABLE} WHERE patient_Id = %s",
                (a["patient_id"],)
            )
            a_staging = cursor.fetchone()

            if not b_current:
                messagebox.showerror(
                    "Missing Live Row",
                    f"No biometric row for Client B (patient_id={b['patient_id']}) in {self.BIOMETRIC_TABLE}. "
                    f"Nothing to back up."
                )
                return
            if not b_staging:
                messagebox.showerror(
                    "Missing Staging Row",
                    f"No biometric row for Client B (patient_id={b['patient_id']}) in "
                    f"{self.BIOMETRIC_STAGING_TABLE}. The pre-sync extract must contain B's original print."
                )
                return

            self.biom_lookup = {
                "a_identifier": a_id,
                "a_patient_id": a["patient_id"],
                "a_patient_name": (a.get("patient_name") or "").strip(),
                "a_current": a_current,
                "a_current_hash": self._row_hash(a_current),
                "a_staging": a_staging,
                "b_identifier": b_id,
                "b_patient_id": b["patient_id"],
                "b_patient_name": (b.get("patient_name") or "").strip(),
                "b_current": b_current,
                "b_current_hash": self._row_hash(b_current),
                "b_staging": b_staging,
                "b_staging_hash": self._row_hash(b_staging),
            }

            preview = (
                f"Client A: {a_id}  (patient_id={a['patient_id']}, {self.biom_lookup['a_patient_name']})\n"
                f"  Current row in {self.BIOMETRIC_TABLE}: "
                f"{'YES — will be overwritten' if a_current else 'NO — will be inserted'}\n"
                f"  Current hash: {self.biom_lookup['a_current_hash']}\n"
                f"  Staging row : {'present' if a_staging else 'absent'}\n"
                f"\n"
                f"Client B: {b_id}  (patient_id={b['patient_id']}, {self.biom_lookup['b_patient_name']})\n"
                f"  Current row in {self.BIOMETRIC_TABLE}: present "
                f"(believed to be A's print)\n"
                f"  Current hash: {self.biom_lookup['b_current_hash']}\n"
                f"  Pre-sync staging hash (B original): {self.biom_lookup['b_staging_hash']}\n"
                f"\n"
                f"Planned swap:\n"
                f"  1. Copy B's current row -> {self.BIOMETRIC_CORRUPT_BACKUP_TABLE} (rescue of A's print)\n"
                f"  2. Write that copy to Client A's row (patient_id={a['patient_id']})\n"
                f"  3. Restore Client B's row from staging (patient_id={b['patient_id']})\n"
            )
            self._set_biom_preview(preview)

            self.biom_apply_button.config(state="normal", bg="#f44336", fg="white")
            self.log(
                f"[BIOM] Lookup OK. A={a_id}/{a['patient_id']}  B={b_id}/{b['patient_id']}"
            )

        except Error as e:
            self.log(f"[BIOM] ERROR: {str(e)}")
            messagebox.showerror("Database Error", f"Lookup failed:\n\n{str(e)}")
        finally:
            if cursor:
                cursor.close()

    def _set_biom_preview(self, text):
        self.biom_preview_text.config(state="normal")
        self.biom_preview_text.delete(1.0, tk.END)
        self.biom_preview_text.insert(tk.END, text)
        self.biom_preview_text.config(state="disabled")

    def confirm_biometric_swap(self):
        """Single confirmation before executing the swap."""

        if not self.biom_lookup:
            return

        lk = self.biom_lookup
        msg = (
            f"Apply biometric swap?\n\n"
            f"  A: {lk['a_identifier']} (patient_id={lk['a_patient_id']}, {lk['a_patient_name']})\n"
            f"  B: {lk['b_identifier']} (patient_id={lk['b_patient_id']}, {lk['b_patient_name']})\n\n"
            f"This will:\n"
            f"  1. Back up B's current biometric row to {self.BIOMETRIC_CORRUPT_BACKUP_TABLE}\n"
            f"  2. Assign that backup row to A (overwrites A's existing row if any)\n"
            f"  3. Restore B's row from the pre-sync staging extract\n\n"
            f"Hash checks run before commit. Reminder: rebuild any external fingerprint "
            f"matching index/cache after success.\n\nProceed?"
        )
        if not messagebox.askyesno("Confirm Biometric Swap", msg, icon="warning"):
            return

        self.execute_biometric_swap()

    def execute_biometric_swap(self):
        """Execute the swap atomically, with before/after hash checks."""

        lk = self.biom_lookup
        admin_name = self.config["settings"].get("admin_name", "Administrator")

        conn = self.get_connection()
        if not conn:
            return

        cursor = None
        try:
            cursor = conn.cursor(mysql_connector.cursors.DictCursor)
            self.create_biometric_swap_audit_table(cursor)
            self.create_biometric_corrupt_backup_table(cursor)

            self.log("-" * 70)
            self.log(
                f"[BIOM] Swap start. A={lk['a_identifier']}/{lk['a_patient_id']}  "
                f"B={lk['b_identifier']}/{lk['b_patient_id']}"
            )

            # 1. Rescue copy: snapshot B's current row into corrupt-backup table
            cursor.execute(
                f"INSERT INTO {self.BIOMETRIC_CORRUPT_BACKUP_TABLE} "
                f"(action_time, source_patient_id, executed_by, "
                f"  patient_Id, template, imageWidth, imageHeight, imageDPI, imageQuality, "
                f"  fingerPosition, serialNumber, model, manufacturer, creator, date_created, "
                f"  new_template, encoded_template, hashed, recapture_count) "
                f"SELECT NOW(), %s, %s, "
                f"  patient_Id, template, imageWidth, imageHeight, imageDPI, imageQuality, "
                f"  fingerPosition, serialNumber, model, manufacturer, creator, date_created, "
                f"  new_template, encoded_template, hashed, recapture_count "
                f"FROM {self.BIOMETRIC_TABLE} WHERE patient_Id = %s",
                (lk["b_patient_id"], admin_name, lk["b_patient_id"])
            )
            backup_id = cursor.lastrowid
            self.log(f"  [OK] B's current row backed up (backup_id={backup_id})")

            # Hold A-print payload in memory (read it once for the writes below)
            payload = lk["b_current"]
            a_rescue_hash = self._row_hash(payload)

            # 2. Write A-print payload to A's row (UPDATE if exists, else INSERT)
            assign_cols = [c for c in self.BIOMETRIC_COLUMNS if c not in ("patient_Id",)]
            if lk["a_current"]:
                set_clause = ", ".join(f"`{c}` = %s" for c in assign_cols)
                cursor.execute(
                    f"UPDATE {self.BIOMETRIC_TABLE} SET {set_clause} WHERE patient_Id = %s",
                    [payload[c] for c in assign_cols] + [lk["a_patient_id"]]
                )
                self.log(f"  [OK] A's existing biometric row updated with rescued print")
            else:
                col_list = ", ".join(f"`{c}`" for c in self.BIOMETRIC_COLUMNS)
                placeholders = ", ".join(["%s"] * len(self.BIOMETRIC_COLUMNS))
                values = []
                for c in self.BIOMETRIC_COLUMNS:
                    values.append(lk["a_patient_id"] if c == "patient_Id" else payload[c])
                cursor.execute(
                    f"INSERT INTO {self.BIOMETRIC_TABLE} ({col_list}) VALUES ({placeholders})",
                    values
                )
                self.log(f"  [OK] New biometric row inserted for A with rescued print")

            # 3. Restore B's row from staging
            staging = lk["b_staging"]
            set_clause = ", ".join(f"`{c}` = %s" for c in assign_cols)
            cursor.execute(
                f"UPDATE {self.BIOMETRIC_TABLE} SET {set_clause} WHERE patient_Id = %s",
                [staging[c] for c in assign_cols] + [lk["b_patient_id"]]
            )
            self.log(f"  [OK] B's row restored from pre-sync staging")

            # Hash verification
            cursor.execute(
                f"SELECT * FROM {self.BIOMETRIC_TABLE} WHERE patient_Id = %s",
                (lk["a_patient_id"],)
            )
            a_after = cursor.fetchone()
            cursor.execute(
                f"SELECT * FROM {self.BIOMETRIC_TABLE} WHERE patient_Id = %s",
                (lk["b_patient_id"],)
            )
            b_after = cursor.fetchone()

            a_after_hash = self._row_hash(a_after)
            b_after_hash = self._row_hash(b_after)
            expected_b_hash = lk["b_staging_hash"]

            if a_after_hash != a_rescue_hash or b_after_hash != expected_b_hash:
                raise RuntimeError(
                    f"Post-write hash mismatch — rolling back. "
                    f"A expected {a_rescue_hash} got {a_after_hash}; "
                    f"B expected {expected_b_hash} got {b_after_hash}."
                )

            cursor.execute(
                """
                INSERT INTO nmrs_biometric_swap_audit
                    (a_identifier, a_patient_id, a_patient_name,
                     b_identifier, b_patient_id, b_patient_name,
                     b_corrupt_backup_id,
                     a_hash_before, a_hash_after,
                     b_hash_before, b_hash_after,
                     executed_by, action_status, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    lk["a_identifier"], lk["a_patient_id"], lk["a_patient_name"],
                    lk["b_identifier"], lk["b_patient_id"], lk["b_patient_name"],
                    backup_id,
                    lk["a_current_hash"], a_after_hash,
                    lk["b_current_hash"], b_after_hash,
                    admin_name,
                    "SUCCESS",
                    "Biometric swap via Biometric Swap feature. "
                    "Rebuild any external fingerprint matching index/cache.",
                )
            )

            conn.commit()
            self.log(f"[BIOM] Swap committed. Hash checks passed.")
            self.log("-" * 70)

            messagebox.showinfo(
                "Biometric Swap Complete",
                f"Swap committed successfully.\n\n"
                f"A: {lk['a_identifier']}  hash={a_after_hash[:16]}...\n"
                f"B: {lk['b_identifier']}  hash={b_after_hash[:16]}...\n\n"
                f"Backup row: {self.BIOMETRIC_CORRUPT_BACKUP_TABLE} id={backup_id}\n"
                f"Audit row : nmrs_biometric_swap_audit\n\n"
                f"REMINDER: if NMRS keeps a separate fingerprint matching index/cache, "
                f"trigger a rebuild for both patients."
            )

        except (Error, RuntimeError) as e:
            conn.rollback()
            self.log(f"[BIOM] ERROR: rollback - {str(e)}")
            messagebox.showerror(
                "Swap Failed",
                f"Operation failed:\n\n{str(e)}\n\nNo changes have been made (rolled back)."
            )
        except Exception as e:
            conn.rollback()
            self.log(f"[BIOM] UNEXPECTED ERROR: {str(e)}")
            self.log(traceback.format_exc())
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\nNo changes have been made (rolled back)."
            )
        finally:
            if cursor:
                cursor.close()

    def create_biometric_corrupt_backup_table(self, cursor):
        """Ensure the corrupt-row backup table exists (persistent rescue copies)."""

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.BIOMETRIC_CORRUPT_BACKUP_TABLE} (
                backup_id          INT AUTO_INCREMENT PRIMARY KEY,
                action_time        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                source_patient_id  INT NOT NULL,
                executed_by        VARCHAR(100),
                patient_Id         INT NOT NULL,
                template           TEXT,
                imageWidth         INT,
                imageHeight        INT,
                imageDPI           INT,
                imageQuality       INT,
                fingerPosition     VARCHAR(50),
                serialNumber       VARCHAR(255),
                model              VARCHAR(255),
                manufacturer       VARCHAR(255),
                creator            INT,
                date_created       DATETIME,
                new_template       LONGBLOB,
                encoded_template   TEXT,
                hashed             TEXT,
                recapture_count    INT,
                INDEX idx_bcb_source (source_patient_id),
                INDEX idx_bcb_time (action_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            """
        )

    def create_biometric_swap_audit_table(self, cursor):
        """Ensure the biometric swap audit table exists."""

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nmrs_biometric_swap_audit (
                audit_id            INT AUTO_INCREMENT PRIMARY KEY,
                action_time         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                a_identifier        VARCHAR(50) NOT NULL,
                a_patient_id        INT,
                a_patient_name      VARCHAR(255),
                b_identifier        VARCHAR(50) NOT NULL,
                b_patient_id        INT,
                b_patient_name      VARCHAR(255),
                b_corrupt_backup_id INT,
                a_hash_before       VARCHAR(64),
                a_hash_after        VARCHAR(64),
                b_hash_before       VARCHAR(64),
                b_hash_after        VARCHAR(64),
                executed_by         VARCHAR(100),
                action_status       VARCHAR(20),
                remarks             TEXT,
                INDEX idx_bsa_a_identifier (a_identifier),
                INDEX idx_bsa_b_identifier (b_identifier),
                INDEX idx_bsa_action_time (action_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            """
        )


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