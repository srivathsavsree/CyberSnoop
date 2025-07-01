# CyberSnoop Installer Setup Script
# Creates a professional Windows installer for CyberSnoop

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_installer():
    """Create a Windows installer for CyberSnoop"""
    
    print("🚀 Creating CyberSnoop Installer...")
    
    # Create installer directory
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    
    # Create setup script
    setup_script = '''
import os
import sys
import shutil
import subprocess
from pathlib import Path
import winreg
import win32com.client

def install_cybersnoop():
    """Install CyberSnoop to Program Files and create desktop shortcut"""
    
    print("🛡️ Installing CyberSnoop...")
    
    # Installation directory
    program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
    install_dir = Path(program_files) / "CyberSnoop"
    
    try:
        # Create installation directory
        install_dir.mkdir(exist_ok=True)
        print(f"✅ Created installation directory: {install_dir}")
        
        # Copy application files
        current_dir = Path(__file__).parent
        
        # Copy main application files
        files_to_copy = [
            "desktop_app",
            "requirements.txt",
            "setup.py",
            "README.md",
            "LICENSE.md"
        ]
        
        for item in files_to_copy:
            src = current_dir / item
            dst = install_dir / item
            
            if src.exists():
                if src.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"✅ Copied: {item}")
        
        # Install Python dependencies
        print("📦 Installing Python dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            str(install_dir / "requirements.txt")
        ], check=True)
        
        # Create launcher script
        launcher_script = f'''@echo off
cd /d "{install_dir}"
python desktop_app\\enhanced_cybersnoop_desktop.py
pause
'''
        
        launcher_path = install_dir / "CyberSnoop.bat"
        with open(launcher_path, 'w') as f:
            f.write(launcher_script)
        
        # Create desktop shortcut
        create_desktop_shortcut(install_dir)
        
        # Add to Windows registry (for uninstall)
        add_to_registry(install_dir)
        
        print("✅ CyberSnoop installed successfully!")
        print(f"📍 Installation location: {install_dir}")
        print("🖥️ Desktop shortcut created")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def create_desktop_shortcut(install_dir):
    """Create desktop shortcut for CyberSnoop"""
    
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "CyberSnoop.lnk"
    
    # Create Windows shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(install_dir / "CyberSnoop.bat")
    shortcut.WorkingDirectory = str(install_dir)
    shortcut.Description = "CyberSnoop - Network Security Monitor"
    shortcut.save()
    
    print(f"✅ Desktop shortcut created: {shortcut_path}")

def add_to_registry(install_dir):
    """Add CyberSnoop to Windows registry for proper uninstall"""
    
    try:
        # Add to Programs and Features
        key_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\CyberSnoop"
        
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "CyberSnoop")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "CyberSnoop Team")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_dir))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{install_dir}\\uninstall.bat"')
        
        print("✅ Added to Windows registry")
        
    except Exception as e:
        print(f"⚠️ Registry update failed: {e}")

if __name__ == "__main__":
    print("🛡️ CyberSnoop Installer")
    print("=" * 50)
    
    if install_cybersnoop():
        print("\\n🎉 Installation completed successfully!")
        print("Look for the CyberSnoop shortcut on your desktop.")
        input("Press Enter to exit...")
    else:
        print("\\n❌ Installation failed!")
        input("Press Enter to exit...")
'''
    
    # Write setup script
    with open(installer_dir / "install.py", 'w') as f:
        f.write(setup_script)
    
    print("✅ Installer script created")
    
    # Create batch file for easy execution
    batch_script = '''@echo off
echo 🛡️ CyberSnoop Installer
echo =====================
echo.
echo Installing CyberSnoop...
python install.py
'''
    
    with open(installer_dir / "install.bat", 'w') as f:
        f.write(batch_script)
    
    print("✅ Batch installer created")
    
    # Create requirements for installer
    installer_requirements = '''pywin32>=227
'''
    
    with open(installer_dir / "installer_requirements.txt", 'w') as f:
        f.write(installer_requirements)
    
    print("✅ Installer requirements created")
    
    print("\n🎯 Next steps:")
    print("1. Run: pip install -r installer/installer_requirements.txt")
    print("2. Test: python installer/install.py")
    print("3. Create executable: Use PyInstaller or similar")

if __name__ == "__main__":
    create_installer()
