# Patient Unvoid Tool - Build Guide

## Overview

This guide shows how to create standalone executables for:
- 🪟 **Windows** (.exe file)
- 🐧 **Ubuntu** (Linux binary)

No Python installation needed on target machines!

---

## Prerequisites

### For Building (Development Machine)

**Both Platforms:**
- Python 3.6 or higher
- pip (Python package manager)

**Required Python Packages:**
```bash
pip install pyinstaller mysql-connector-python
```

---

## 📦 Quick Build (Automated)

### Windows
```cmd
build_windows.bat
```

### Ubuntu
```bash
chmod +x build_ubuntu.sh
./build_ubuntu.sh
```

**Done!** Package ready in `PatientUnvoidTool_Windows/` or `PatientUnvoidTool_Ubuntu/`

---

## 🔧 Manual Build Instructions

### Windows Build

#### Step 1: Install Dependencies
```cmd
pip install pyinstaller mysql-connector-python
```

#### Step 2: Build Executable
```cmd
pyinstaller --onefile --windowed --name="PatientUnvoidTool" patient_unvoid_tool.py
```

#### Step 3: Package Files
```cmd
mkdir PatientUnvoidTool_Windows
copy dist\PatientUnvoidTool.exe PatientUnvoidTool_Windows\
copy unvoid_config.ini PatientUnvoidTool_Windows\
copy PATIENT_UNVOID_GUIDE.md PatientUnvoidTool_Windows\README.md
```

#### Output Location
```
PatientUnvoidTool_Windows/
├── PatientUnvoidTool.exe       ← Run this!
├── unvoid_config.ini           ← Edit database settings
└── README.md                   ← User guide
```

---

### Ubuntu Build

#### Step 1: Install Dependencies
```bash
pip3 install pyinstaller mysql-connector-python
```

#### Step 2: Build Executable
```bash
pyinstaller --onefile --windowed --name="PatientUnvoidTool" patient_unvoid_tool.py
```

#### Step 3: Make Executable
```bash
chmod +x dist/PatientUnvoidTool
```

#### Step 4: Package Files
```bash
mkdir PatientUnvoidTool_Ubuntu
cp dist/PatientUnvoidTool PatientUnvoidTool_Ubuntu/
cp unvoid_config.ini PatientUnvoidTool_Ubuntu/
cp PATIENT_UNVOID_GUIDE.md PatientUnvoidTool_Ubuntu/README.md
```

#### Output Location
```
PatientUnvoidTool_Ubuntu/
├── PatientUnvoidTool           ← Run this!
├── unvoid_config.ini           ← Edit database settings
└── README.md                   ← User guide
```

---

## 📋 Distribution Checklist

Before distributing to end users:

### 1. Configure Database
Edit `unvoid_config.ini`:
```ini
[database]
host = localhost
port = 3306
user = openmrs_user
password = YOUR_PASSWORD_HERE  ← Change this!
database = openmrs

[settings]
admin_name = Administrator Name ← Change this!
```

### 2. Test Executable
- ✅ Run on clean machine (without Python)
- ✅ Test login with password: `pibtib`
- ✅ Test database connection
- ✅ Test patient search
- ✅ Test unvoid operation

### 3. Package for Distribution
Create a ZIP file:
- Windows: `PatientUnvoidTool_Windows.zip`
- Ubuntu: `PatientUnvoidTool_Ubuntu.zip`

### 4. Documentation
Include in package:
- ✅ Executable
- ✅ Config file template
- ✅ User guide (README.md)
- ✅ Version number

---

## 🚀 Deployment Instructions

### Windows Deployment

**Option 1: Simple Copy**
1. Copy `PatientUnvoidTool_Windows` folder to target machine
2. Edit `unvoid_config.ini` with database credentials
3. Double-click `PatientUnvoidTool.exe`

**Option 2: Install to Program Files**
1. Copy to `C:\Program Files\CCFN\PatientUnvoidTool\`
2. Create desktop shortcut to `.exe`
3. Edit config file
4. Run from shortcut

---

### Ubuntu Deployment

**Option 1: User Directory**
```bash
# Copy to user's home
cp -r PatientUnvoidTool_Ubuntu ~/PatientUnvoidTool

# Edit config
nano ~/PatientUnvoidTool/unvoid_config.ini

# Run
cd ~/PatientUnvoidTool
./PatientUnvoidTool
```

**Option 2: System-Wide Installation**
```bash
# Install to /opt
sudo cp -r PatientUnvoidTool_Ubuntu /opt/patient-unvoid-tool
sudo chmod +x /opt/patient-unvoid-tool/PatientUnvoidTool

# Create desktop entry
sudo nano /usr/share/applications/patient-unvoid-tool.desktop
```

Desktop entry contents:
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Patient Unvoid Tool
Comment=CCFN Patient Unvoid Tool
Exec=/opt/patient-unvoid-tool/PatientUnvoidTool
Icon=utilities-terminal
Terminal=false
Categories=Utility;Medical;
```

**Option 3: Create Symbolic Link**
```bash
# Link to /usr/local/bin
sudo ln -s /opt/patient-unvoid-tool/PatientUnvoidTool /usr/local/bin/patient-unvoid

# Run from anywhere
patient-unvoid
```

---

## 🐛 Troubleshooting Builds

### Windows Issues

**Issue: "PyInstaller not found"**
```cmd
pip install pyinstaller
```

**Issue: "vcruntime140.dll missing"**
Download and install: [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

**Issue: Antivirus blocks executable**
- Add exception in antivirus
- Or use `--debug` flag in PyInstaller

**Issue: Executable size too large**
Normal! Expected size: 20-30 MB (includes Python runtime)

---

### Ubuntu Issues

**Issue: "Permission denied"**
```bash
chmod +x PatientUnvoidTool
```

**Issue: "libpython3.x.so not found"**
```bash
# Install Python development files
sudo apt-get install python3-dev
```

**Issue: GUI doesn't start**
```bash
# Install tkinter
sudo apt-get install python3-tk
```

**Issue: "cannot execute binary"**
Build on same architecture (x86_64 → x86_64, ARM → ARM)

---

## 📊 Build Size Comparison

| Platform | Size | Contents |
|----------|------|----------|
| Windows | ~25 MB | .exe + Python runtime + MySQL connector |
| Ubuntu | ~20 MB | Binary + Python runtime + MySQL connector |

**Note:** Size is normal for PyInstaller packages (includes entire Python environment)

---

## 🔄 Version Management

### Version Numbering
Format: `v[major].[minor].[patch]`
- Example: v1.1.0

### Update Checklist
When creating new version:
1. Update version in script header
2. Update changelog
3. Rebuild executables
4. Test on both platforms
5. Update user guide
6. Create release notes

### Changelog Template
```
Version 1.1 (2026-02-10)
- Fixed: Database cursor error
- Improved: Button UI (gray when disabled)
- Added: Better error messages
```

---

## 🧪 Testing Matrix

Before release, test on:

| Platform | Version | Python | Status |
|----------|---------|--------|--------|
| Windows 10 | 22H2 | 3.8+ | ✅ |
| Windows 11 | 23H2 | 3.8+ | ✅ |
| Ubuntu 20.04 | LTS | 3.8+ | ✅ |
| Ubuntu 22.04 | LTS | 3.10+ | ✅ |
| Ubuntu 24.04 | LTS | 3.12+ | ✅ |

---

## 📦 Alternative Build Methods

### Using PyInstaller Spec File

Create `patient_unvoid_tool.spec`:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['patient_unvoid_tool.py'],
    pathex=[],
    binaries=[],
    datas=[('unvoid_config.ini', '.')],
    hiddenimports=['mysql.connector'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PatientUnvoidTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

Build with:
```bash
pyinstaller patient_unvoid_tool.spec
```

---

## 🔐 Security Considerations

### Executable Signing

**Windows:**
```cmd
signtool sign /f certificate.pfx /p password /t http://timestamp.server.com PatientUnvoidTool.exe
```

**Ubuntu:**
Not typically required, but can use `codesign` on macOS or similar tools.

### Config File Security
- ⚠️ Config file contains database password
- Store in secure location
- Use file permissions:
  - Windows: Restrict to Administrators group
  - Ubuntu: `chmod 600 unvoid_config.ini`

---

## 📚 Additional Resources

### PyInstaller Documentation
- Official docs: https://pyinstaller.org/
- Options reference: https://pyinstaller.org/en/stable/usage.html

### MySQL Connector
- Documentation: https://dev.mysql.com/doc/connector-python/

### Distribution
- Windows installer: Use NSIS or Inno Setup
- Ubuntu package: Create .deb with `dpkg`

---

## ✅ Final Checklist

Before distributing:

- [ ] Tested on Windows 10/11
- [ ] Tested on Ubuntu 20.04/22.04/24.04
- [ ] Database connection works
- [ ] Password protection works (pibtib)
- [ ] Patient search works
- [ ] Unvoid operation works
- [ ] Audit trail created
- [ ] Error handling tested
- [ ] User guide included
- [ ] Config template included
- [ ] Version number documented
- [ ] Release notes created

---

## 🆘 Support

For build issues:
1. Check error messages carefully
2. Review troubleshooting section
3. Verify all dependencies installed
4. Try building on clean system

---

**Build Status:** Production Ready  
**Platforms:** Windows 10/11, Ubuntu 20.04/22.04/24.04  
**Python:** 3.6+  
**Last Updated:** February 10, 2026
