# Patient Unvoid Tool - User Guide

## Overview

The **Patient Unvoid Tool** is a secure administrative application for restoring voided patient records in the OpenMRS database at Catholic Caritas Foundation of Nigeria (CCFN).

### Security Features
- 🔒 Password-protected (Administrator only)
- 🔑 Password: `pibtib`
- ⚠️ Double confirmation before unvoiding
- 📝 Complete audit trail

---

## Prerequisites

### System Requirements
- Python 3.6 or higher
- MySQL database (OpenMRS)
- Required Python package:
  ```bash
  pip install mysql-connector-python
  ```

### Database Access
- Read/Write access to OpenMRS database
- Permissions to UPDATE tables
- Permissions to CREATE TABLE (for audit log)

---

## Quick Start

### 1. Install Dependency
```bash
pip install mysql-connector-python
```

### 2. Configure Database
Edit `unvoid_config.ini`:
```ini
[database]
host = localhost
port = 3306
user = openmrs_user
password = your_password_here
database = openmrs

[settings]
admin_name = Alhassan Danjuma
```

### 3. Run Application
```bash
python patient_unvoid_tool.py
```

### 4. Login
- Password: `pibtib`

### 5. Enter Identifier
- Example: `IMO01104166`
- Click "SEARCH PATIENT"

### 6. Verify & Unvoid
- Check patient details
- Click "UNVOID PATIENT RECORDS"
- Confirm twice
- Done!

---

## Detailed Workflow

### Step 1: Administrator Login

**What you see:**
```
┌───────────────────────────────────┐
│ 🔒 ADMINISTRATOR ACCESS REQUIRED  │
│                                   │
│ Catholic Caritas Foundation       │
│ of Nigeria                        │
│                                   │
│ Administrator Password:           │
│ [**********]                      │
│                                   │
│      [    LOGIN    ]              │
└───────────────────────────────────┘
```

**Actions:**
1. Type password: `pibtib`
2. Press Enter or click LOGIN
3. System connects to database
4. Main screen loads

---

### Step 2: Search Patient

**What you see:**
```
┌─ Step 1: Enter Patient Identifier ─┐
│                                     │
│ ART Identifier (e.g., IMO01104166): │
│ [IMO01104166_____] [SEARCH PATIENT] │
└─────────────────────────────────────┘
```

**Actions:**
1. Type ART identifier
2. Press Enter or click SEARCH PATIENT
3. Wait for search results

**Possible Outcomes:**

✅ **Patient Found (Voided)**
- Shows patient details
- Enables unvoid button
- Log: "SUCCESS: Found patient - John Doe (ID: 12345)"

ℹ️ **Patient Not Voided**
- Alert: "Patient is already active"
- No action needed
- Log: "ERROR: Patient IMO01104166 is NOT voided"

❌ **Patient Not Found**
- Alert: "No patient found with identifier"
- Check identifier spelling
- Log: "ERROR: Patient IMO01104166 not found"

---

### Step 3: Verify Patient Details

**What you see:**
```
┌─ Step 2: Verify Patient Details ───┐
│                                     │
│ Identifier:    IMO01104166          │
│ Patient ID:    12345                │
│ Name:          John Doe             │
│ Gender:        M                    │
│ Birthdate:     1985-01-15           │
│ Status:        VOIDED               │
│ Voided Date:   2025-12-01 10:30:00  │
│ Void Reason:   Duplicate record     │
└─────────────────────────────────────┘
```

**CRITICAL:** Verify this is the correct patient!

Check:
- Name matches expected
- ID is correct
- Reason for voiding makes sense

---

### Step 4: Unvoid Patient

**What you see:**
```
┌─ Step 3: Unvoid Patient Records ───┐
│                                     │
│ ⚠ WARNING: This action will unvoid  │
│   ALL records for this patient.     │
│                                     │
│  [🔓 UNVOID PATIENT RECORDS]        │
└─────────────────────────────────────┘
```

**Actions:**

1. Click "UNVOID PATIENT RECORDS"

2. **First Confirmation:**
   ```
   Are you sure you want to UNVOID this patient?
   
   Identifier: IMO01104166
   Name: John Doe
   Patient ID: 12345
   
   This will restore ALL voided records.
   
   Do you want to proceed?
   [No] [Yes]
   ```
   Click **Yes** to continue

3. **Second Confirmation:**
   ```
   LAST CHANCE!
   
   This action will unvoid all records for:
   John Doe (IMO01104166)
   
   Are you ABSOLUTELY SURE?
   [No] [Yes]
   ```
   Click **Yes** to execute

4. **Processing:**
   Activity Log shows progress:
   ```
   [14:30:20] STARTING UNVOID OPERATION
   [14:30:20] Patient: John Doe (IMO01104166)
   [14:30:21] Unvoiding patient...
   [14:30:21]   [OK] 1 record(s) unvoided in patient
   [14:30:21] Unvoiding patient_identifier...
   [14:30:21]   [OK] 2 record(s) unvoided in patient_identifier
   ...
   [14:30:25] SUCCESS: Unvoided 158 total records
   [14:30:25] Audit entry created
   ```

5. **Success Message:**
   ```
   ✅ Patient records successfully unvoided!
   
   Patient: John Doe
   Identifier: IMO01104166
   Total Records Unvoided: 158
   
   Audit entry has been logged.
   [OK]
   ```

6. **Form Clears Automatically**
   - Ready for next patient
   - Enter new identifier

---

## Tables Unvoided

| # | Table | ID Column | What It Contains |
|---|-------|-----------|------------------|
| 1 | patient | patient_id | Patient core record |
| 2 | patient_identifier | patient_id | ART identifiers |
| 3 | patient_program | patient_id | Program enrollment |
| 4 | person | person_id | Demographics |
| 5 | person_name | person_id | Names |
| 6 | person_address | person_id | Addresses |
| 7 | person_attribute | person_id | Custom attributes |
| 8 | visit | patient_id | Visit records |
| 9 | encounter | patient_id | Clinical encounters |
| 10 | obs | person_id | Observations/results |

**All tables are unvoided in a single transaction.**

---

## Audit Trail

Every operation is logged in `nmrs_unvoid_audit`:

```sql
mysql> SELECT * FROM nmrs_unvoid_audit ORDER BY action_time DESC LIMIT 5;
```

**Audit Record Contains:**
- `audit_id` - Unique ID
- `action_time` - When unvoided
- `identifier` - ART identifier
- `patient_id` - Patient ID
- `patient_name` - Patient name
- `executed_by` - Who did it
- `action_status` - SUCCESS/FAILED
- `remarks` - Details

**Query Examples:**
```sql
-- View all unvoid operations today
SELECT * FROM nmrs_unvoid_audit
WHERE DATE(action_time) = CURDATE();

-- Find who unvoided specific patient
SELECT executed_by, action_time, remarks
FROM nmrs_unvoid_audit
WHERE identifier = 'IMO01104166';

-- Count unvoid operations by administrator
SELECT executed_by, COUNT(*) as operations
FROM nmrs_unvoid_audit
GROUP BY executed_by;
```

---

## Error Messages

### "Incorrect password!"
**Cause:** Wrong password entered  
**Solution:** Use correct password: `pibtib`

### "Configuration file not found"
**Cause:** Missing `unvoid_config.ini`  
**Solution:** Create config file in same directory

### "Cannot connect to database"
**Cause:** Database connection failed  
**Solutions:**
- Check credentials in config file
- Verify database server is running
- Test connection manually

### "No patient found with identifier"
**Cause:** Identifier doesn't exist or typo  
**Solution:** Verify identifier and try again

### "Patient is already active"
**Cause:** Patient is not voided  
**Solution:** No action needed

### "Access denied for user"
**Cause:** Insufficient database permissions  
**Solution:** Grant UPDATE privilege to user

---

## Safety Features

### 1. Password Protection
- Only authorized administrators can access
- Password: `pibtib`
- Failed attempts logged

### 2. Double Confirmation
- Two separate confirmation dialogs
- Easy to cancel at any point
- Clear warnings shown

### 3. Voided-Only Search
- Only finds voided patients
- Cannot accidentally unvoid active patients
- Prevents errors

### 4. Transaction Safety
- All changes in single transaction
- Rollback on any error
- Database stays consistent

### 5. Audit Trail
- Cannot be disabled
- Permanent record
- Who, what, when logged

### 6. Real-time Feedback
- Activity Log shows every step
- Immediate error reporting
- Progress tracking

---

## Best Practices

### ✅ Before Unvoiding
1. Verify you have correct identifier
2. Understand why patient was voided
3. Get approval if required
4. Backup database (recommended)
5. Have reversal plan ready

### ✅ During Operation
1. Read patient details carefully
2. Verify name and ID match
3. Read all confirmation dialogs
4. Watch Activity Log
5. Don't close app during processing

### ✅ After Unvoiding
1. Verify success message
2. Check audit log entry
3. Verify patient in OpenMRS
4. Document in facility records
5. Inform relevant staff

---

## Troubleshooting

### Application Won't Start

**Error:** `ModuleNotFoundError: No module named 'mysql'`

**Solution:**
```bash
pip install mysql-connector-python
```

---

### Can't Connect to Database

**Check List:**
1. Database server running?
2. Credentials correct in config?
3. Network connection OK?
4. Firewall blocking connection?

**Test Manually:**
```bash
mysql -h localhost -u openmrs_user -p openmrs
```

---

### Search Returns No Results

**Possible Causes:**
- Patient not voided (already active)
- Wrong identifier
- Patient doesn't exist

**Solutions:**
1. Check identifier spelling
2. Verify in OpenMRS interface
3. Query database directly:
   ```sql
   SELECT * FROM patient_identifier
   WHERE identifier = 'IMO01104166';
   ```

---

## FAQ

**Q: Can I unvoid multiple patients at once?**  
A: No. Tool processes one patient at a time for safety.

**Q: What if I unvoid the wrong patient?**  
A: You'll need to void them again in OpenMRS. Always verify before confirming!

**Q: Can I change the password?**  
A: Yes, edit line 31 in the script: `self.admin_password = "your_new_password"`

**Q: Is there a dry run mode?**  
A: No. As requested, dry run was skipped. Always verify details before confirming.

**Q: Can I unvoid specific tables only?**  
A: No. Tool unvoids all tables for data integrity.

**Q: What if operation fails mid-way?**  
A: Transaction rolls back automatically. No changes saved.

**Q: Can I see audit log in the app?**  
A: No. Use MySQL to query `nmrs_unvoid_audit` table.

**Q: Does tool work on Windows and Linux?**  
A: Yes! Works on both Windows and Ubuntu.

---

## Security Checklist

Before using this tool:

- [ ] Database credentials secured in config file
- [ ] Config file not in version control
- [ ] Password changed from default (recommended)
- [ ] Only authorized administrators know password
- [ ] Database user has appropriate permissions
- [ ] Audit log reviewed regularly
- [ ] Computer locked when unattended
- [ ] Facility SOP followed

---

## Command Reference

```bash
# Install dependencies
pip install mysql-connector-python

# Run application
python patient_unvoid_tool.py

# Test database connection
mysql -h localhost -u openmrs_user -p openmrs

# View audit log
mysql -u openmrs_user -p openmrs -e "SELECT * FROM nmrs_unvoid_audit;"

# Check patient status
mysql -u openmrs_user -p openmrs -e "
SELECT pi.identifier, p.voided
FROM patient_identifier pi
JOIN patient p ON pi.patient_id = p.patient_id
WHERE pi.identifier = 'IMO01104166';
"
```

---

## Support

### Technical Issues
- Review error messages in Activity Log
- Check troubleshooting section
- Verify database connection
- Test manually in MySQL

### Policy Questions
- Contact CCFN Data Management Team
- Review facility SOPs
- Get proper approvals

---

**Catholic Caritas Foundation of Nigeria**  
**Data Management Team**  
**January 2026**

**Tool Version:** 1.0  
**Author:** Adeyemi  
**Password:** pibtib (Administrator only)
