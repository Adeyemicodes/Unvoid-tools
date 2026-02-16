#!/bin/bash
# ============================================================================
# Patient Unvoid Tool - Ubuntu Build Script
# ============================================================================
# This script builds a standalone Ubuntu executable
# ============================================================================

echo ""
echo "============================================================================"
echo "Patient Unvoid Tool - Ubuntu Build"
echo "============================================================================"
echo ""

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "[ERROR] PyInstaller not found!"
    echo ""
    echo "Installing PyInstaller..."
    pip3 install --user pyinstaller
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install PyInstaller"
        exit 1
    fi
fi

# Check if pymysql is installed
if ! python3 -c "import pymysql" 2>/dev/null; then
    echo "[ERROR] pymysql not found!"
    echo ""
    echo "Installing pymysql..."
    pip3 install --user pymysql
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install pymysql"
        exit 1
    fi
fi

echo ""
echo "[1/5] Cleaning previous build..."
rm -rf build dist patient_unvoid_tool.spec

echo "[2/5] Building executable..."
python3 -m PyInstaller --onefile \
    --windowed \
    --name="PatientUnvoidTool" \
    --add-data="unvoid_config.ini:." \
    patient_unvoid_tool.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Build failed!"
    exit 1
fi

echo "[3/5] Copying config file..."
cp unvoid_config.ini dist/

echo "[4/5] Making executable..."
chmod +x dist/PatientUnvoidTool

echo "[5/5] Creating package folder..."
mkdir -p PatientUnvoidTool_Ubuntu
cp dist/PatientUnvoidTool PatientUnvoidTool_Ubuntu/
cp unvoid_config.ini PatientUnvoidTool_Ubuntu/
cp PATIENT_UNVOID_GUIDE.md PatientUnvoidTool_Ubuntu/README.md

# Create desktop launcher
cat > PatientUnvoidTool_Ubuntu/PatientUnvoidTool.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Patient Unvoid Tool
Comment=CCFN Patient Unvoid Tool
Exec=/path/to/PatientUnvoidTool
Icon=utilities-terminal
Terminal=false
Categories=Utility;
EOF

echo ""
echo "============================================================================"
echo "BUILD COMPLETE!"
echo "============================================================================"
echo ""
echo "Executable location: PatientUnvoidTool_Ubuntu/PatientUnvoidTool"
echo "Config file:          PatientUnvoidTool_Ubuntu/unvoid_config.ini"
echo "User guide:           PatientUnvoidTool_Ubuntu/README.md"
echo "Desktop launcher:     PatientUnvoidTool_Ubuntu/PatientUnvoidTool.desktop"
echo ""
echo "IMPORTANT: Edit unvoid_config.ini with your database credentials before running!"
echo ""
echo "To run: cd PatientUnvoidTool_Ubuntu && ./PatientUnvoidTool"
echo ""
echo "============================================================================"