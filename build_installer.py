"""
CyberSnoop Setup Builder
Creates a Windows installer executable
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def create_simple_installer():
    """Create a simple installer for CyberSnoop"""
    
    print("🏗️ Creating CyberSnoop Installer...")
    
    # Simple installer script
    installer_code = '''
import os
import sys
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
import threading

class CyberSnoopInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CyberSnoop Setup v1.0")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=100)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🛡️ CyberSnoop Installer", 
                font=("Arial", 24, "bold"), 
                fg="white", bg="#2c3e50").pack(pady=30)
        
        # Main content
        main_frame = tk.Frame(self.root, padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, 
                text="Network Security Monitor - Free & Open Source", 
                font=("Arial", 14)).pack(pady=(0, 20))
        
        tk.Label(main_frame, 
                text="This installer will download and install CyberSnoop on your computer.\\n"
                     "CyberSnoop provides enterprise-grade network security monitoring.", 
                justify="center", 
                wraplength=500).pack(pady=(0, 30))
        
        # Installation options
        options_frame = tk.LabelFrame(main_frame, text="Installation Options", padx=10, pady=10)
        options_frame.pack(fill="x", pady=(0, 20))
        
        self.desktop_shortcut = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Create Desktop Shortcut", 
                      variable=self.desktop_shortcut).pack(anchor="w")
        
        # Install button
        tk.Button(main_frame, text="Install CyberSnoop", 
                 command=self.install,
                 bg="#27ae60", fg="white", 
                 font=("Arial", 14, "bold"),
                 pady=10).pack(pady=20)
        
        tk.Button(main_frame, text="Cancel", 
                 command=self.root.quit).pack()
        
        # Status
        self.status_var = tk.StringVar(value="Ready to install")
        tk.Label(main_frame, textvariable=self.status_var, 
                fg="blue").pack(pady=(20, 0))
    
    def install(self):
        """Install CyberSnoop"""
        threading.Thread(target=self._install_process, daemon=True).start()
    
    def _install_process(self):
        try:
            # Get Program Files directory
            program_files = os.environ.get('PROGRAMFILES', 'C:\\\\Program Files')
            install_dir = Path(program_files) / "CyberSnoop"
            
            self.status_var.set("Creating installation directory...")
            install_dir.mkdir(exist_ok=True)
            
            self.status_var.set("Downloading CyberSnoop from GitHub...")
            
            # Download from GitHub
            import urllib.request
            import zipfile
            import tempfile
            
            github_url = "https://github.com/srivathsavsree/CyberSnoop/archive/refs/heads/main.zip"
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
                urllib.request.urlretrieve(github_url, tmp_file.name)
                
                self.status_var.set("Extracting files...")
                
                with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                    zip_ref.extractall(install_dir)
                
                # Move files from extracted folder to install_dir
                extracted_folder = install_dir / "CyberSnoop-main"
                if extracted_folder.exists():
                    for item in extracted_folder.iterdir():
                        shutil.move(str(item), str(install_dir / item.name))
                    extracted_folder.rmdir()
            
            self.status_var.set("Installing Python dependencies...")
            
            # Install requirements
            requirements_file = install_dir / "requirements.txt"
            if requirements_file.exists():
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True, capture_output=True)
            
            # Create launcher
            self.status_var.set("Creating launcher...")
            self.create_launcher(install_dir)
            
            # Create desktop shortcut
            if self.desktop_shortcut.get():
                self.status_var.set("Creating desktop shortcut...")
                self.create_shortcut(install_dir)
            
            self.status_var.set("Installation completed successfully!")
            
            messagebox.showinfo("Success", 
                              f"CyberSnoop installed successfully!\\n\\n"
                              f"Installation location: {install_dir}\\n\\n"
                              f"Desktop shortcut created: {'Yes' if self.desktop_shortcut.get() else 'No'}\\n\\n"
                              f"You can now run CyberSnoop from your desktop!")
            
        except Exception as e:
            self.status_var.set(f"Installation failed: {str(e)}")
            messagebox.showerror("Installation Error", f"Installation failed:\\n\\n{str(e)}")
    
    def create_launcher(self, install_dir):
        """Create CyberSnoop launcher"""
        launcher_content = f\"\"\"@echo off
title CyberSnoop - Network Security Monitor
cd /d "{install_dir}"
echo Starting CyberSnoop...
python desktop_app\\\\enhanced_cybersnoop_desktop.py
if errorlevel 1 (
    echo.
    echo Error: Failed to start CyberSnoop
    echo Please ensure Python and all dependencies are installed.
    pause
)
\"\"\"
        
        launcher_path = install_dir / "CyberSnoop.bat"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
    
    def create_shortcut(self, install_dir):
        """Create desktop shortcut"""
        try:
            import win32com.client
            
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "CyberSnoop.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(install_dir / "CyberSnoop.bat")
            shortcut.WorkingDirectory = str(install_dir)
            shortcut.Description = "CyberSnoop - Network Security Monitor"
            shortcut.IconLocation = str(install_dir / "CyberSnoop.bat")
            shortcut.save()
            
        except ImportError:
            # Fallback: create a simple batch file on desktop
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "CyberSnoop.bat"
            
            shortcut_content = f\"\"\"@echo off
cd /d "{install_dir}"
start "" "{install_dir}\\\\CyberSnoop.bat"
\"\"\"
            
            with open(shortcut_path, 'w') as f:
                f.write(shortcut_content)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    installer = CyberSnoopInstaller()
    installer.run()
'''
    
    # Write installer script
    with open("cybersnoop_setup.py", 'w', encoding='utf-8') as f:
        f.write(installer_code)
    
    print("✅ Installer script created: cybersnoop_setup.py")
    return True

def build_exe():
    """Build the installer as an executable"""
    
    print("📦 Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    print("🔨 Building CyberSnoop-Setup.exe...")
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=CyberSnoop-Setup",
        "cybersnoop_setup.py"
    ]
    
    subprocess.run(cmd, check=True)
    
    # Move executable to main directory
    exe_path = Path("dist") / "CyberSnoop-Setup.exe"
    if exe_path.exists():
        shutil.move(str(exe_path), "CyberSnoop-Setup.exe")
        print("✅ CyberSnoop-Setup.exe created successfully!")
        
        # Clean up
        shutil.rmtree("build", ignore_errors=True)
        shutil.rmtree("dist", ignore_errors=True)
        Path("CyberSnoop-Setup.spec").unlink(missing_ok=True)
        
        return True
    
    return False

def main():
    """Main function"""
    
    print("🛡️ CyberSnoop Setup Builder")
    print("=" * 50)
    
    try:
        # Create installer script
        if create_simple_installer():
            print("✅ Installer script ready")
            
            # Build executable
            if build_exe():
                print("\\n🎉 SUCCESS!")
                print("📦 CyberSnoop-Setup.exe is ready for distribution")
                print("\\n📋 What the installer does:")
                print("  • Downloads CyberSnoop from GitHub")
                print("  • Installs to Program Files")
                print("  • Installs Python dependencies")  
                print("  • Creates desktop shortcut")
                print("  • Creates launcher script")
                print("\\n🎯 Users can now:")
                print("  • Download CyberSnoop-Setup.exe")
                print("  • Run it to install CyberSnoop")
                print("  • Use the desktop shortcut to launch")
                
            else:
                print("❌ Failed to build executable")
        else:
            print("❌ Failed to create installer script")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
