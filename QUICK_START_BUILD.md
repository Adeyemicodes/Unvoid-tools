# Patient Unvoid Tool - Quick Start

## 🚀 Build in 3 Steps

### Windows

```cmd
# 1. Install dependencies
pip install pyinstaller mysql-connector-python

# 2. Run build script
build_windows.bat

# 3. Done! Find your package in:
PatientUnvoidTool_Windows\PatientUnvoidTool.exe
```

---

### Ubuntu

```bash
# 1. Install dependencies
pip3 install pyinstaller mysql-connector-python

# 2. Run build script
chmod +x build_ubuntu.sh
./build_ubuntu.sh

# 3. Done! Find your package in:
PatientUnvoidTool_Ubuntu/PatientUnvoidTool
```

---

## 📦 What You Get

After building, you'll have a complete package:

```
PatientUnvoidTool_[Platform]/
├── PatientUnvoidTool[.exe]  ← Standalone executable (no Python needed!)
├── unvoid_config.ini        ← Database configuration
└── README.md                ← User guide
```

---

## ⚙️ Before First Use

1. **Edit Config File**
   ```ini
   [database]
   host = localhost
   user = openmrs_user
   password = YOUR_PASSWORD  ← Change this!
   database = openmrs
   
   [settings]
   admin_name = Your Name    ← Change this!
   ```

2. **Test on Your Machine**
   - Run the executable
   - Login with password: `pibtib`
   - Test database connection
   - Try searching for a patient

3. **Distribute to Users**
   - ZIP the entire folder
   - Send to administrators
   - They just double-click to run!

---

## 🎯 Target Machines (No Python Needed!)

Your built executable will run on:
- ✅ Windows 10/11 (any edition)
- ✅ Ubuntu 20.04/22.04/24.04 LTS
- ✅ Any machine with same architecture (x64)

**No Python installation required on target machines!**

---

## 📏 Size

- Windows: ~25 MB
- Ubuntu: ~20 MB

This is normal! Includes entire Python runtime + MySQL connector.

---

## 🔧 Common Issues

**Windows: "vcruntime140.dll missing"**
- Install: [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

**Ubuntu: "Permission denied"**
```bash
chmod +x PatientUnvoidTool
```

**Both: "Config file not found"**
- Make sure `unvoid_config.ini` is in same folder as executable

---

## 📚 Full Documentation

For detailed build options, troubleshooting, and deployment:
- See `BUILD_GUIDE.md`
- See `PATIENT_UNVOID_GUIDE.md`

---

## ✅ Quick Test

After building:

```
1. Run executable
2. Login: pibtib
3. Search: IMO00701507 (or any voided patient)
4. Verify patient details show
5. Click UNVOID (test on demo/test patient only!)
```

---

**That's it! Build once, distribute everywhere!** 🎉
