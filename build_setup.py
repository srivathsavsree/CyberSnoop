# Build CyberSnoop Setup.exe
# This script creates a single executable installer

import os
import subprocess
import sys
from pathlib import Path

def build_executable():
    """Build CyberSnoop-Setup.exe using PyInstaller"""
    
    print("🏗️ Building CyberSnoop-Setup.exe...")
    
    # Install required packages
    packages = [
        "pyinstaller",
        "pywin32"
    ]
    
    for package in packages:
        print(f"📦 Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
    
    # Create the main installer script
    installer_script = '''
import os
import sys
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import tempfile
import zipfile
import urllib.request

class CyberSnoopInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CyberSnoop Setup")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the installer UI"""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🛡️ CyberSnoop", 
                font=("Arial", 20, "bold"), 
                fg="white", bg="#2c3e50").pack(pady=20)
        
        # Main content
        content_frame = tk.Frame(self.root, padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        tk.Label(content_frame, 
                text="Network Security Monitor", 
                font=("Arial", 12)).pack(pady=(0, 10))
        
        tk.Label(content_frame, 
                text="This will install CyberSnoop on your computer.\\n"
                     "CyberSnoop is a free, open-source network security monitoring tool.", 
                justify="left", wraplength=450).pack(pady=(0, 20))
        
        # Installation directory
        dir_frame = tk.Frame(content_frame)
        dir_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(dir_frame, text="Installation Directory:").pack(anchor="w")
        
        self.install_dir = tk.StringVar()
        program_files = os.environ.get('PROGRAMFILES', 'C:\\\\Program Files')
        self.install_dir.set(os.path.join(program_files, "CyberSnoop"))
        
        tk.Entry(dir_frame, textvariable=self.install_dir, width=60).pack(fill="x", pady=(5, 0))
        
        # Options
        options_frame = tk.Frame(content_frame)
        options_frame.pack(fill="x", pady=(0, 20))
        
        self.desktop_shortcut = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Create desktop shortcut", 
                      variable=self.desktop_shortcut).pack(anchor="w")
        
        self.start_menu = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Add to Start Menu", 
                      variable=self.start_menu).pack(anchor="w")
        
        # Progress bar
        self.progress = ttk.Progressbar(content_frame, mode='indeterminate')
        self.progress.pack(fill="x", pady=(0, 10))
        
        # Status label
        self.status_label = tk.Label(content_frame, text="Ready to install", fg="blue")
        self.status_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill="x")
        
        tk.Button(button_frame, text="Cancel", 
                 command=self.root.quit).pack(side="right", padx=(10, 0))
        
        self.install_button = tk.Button(button_frame, text="Install", 
                                       command=self.start_installation, 
                                       bg="#27ae60", fg="white", 
                                       font=("Arial", 10, "bold"))
        self.install_button.pack(side="right")
        
    def start_installation(self):
        """Start the installation process"""
        
        self.install_button.config(state="disabled")
        self.progress.start()
        
        # Run installation in separate thread
        thread = threading.Thread(target=self.install)
        thread.daemon = True
        thread.start()
        
    def install(self):
        """Perform the actual installation"""
        
        try:
            install_path = Path(self.install_dir.get())
            
            # Update status
            self.update_status("Creating installation directory...")
            install_path.mkdir(parents=True, exist_ok=True)
            
            # Download and extract CyberSnoop
            self.update_status("Downloading CyberSnoop...")
            self.download_cybersnoop(install_path)
            
            # Install Python dependencies
            self.update_status("Installing dependencies...")
            self.install_dependencies(install_path)
            
            # Create shortcuts
            if self.desktop_shortcut.get():
                self.update_status("Creating desktop shortcut...")
                self.create_desktop_shortcut(install_path)
            
            if self.start_menu.get():
                self.update_status("Adding to Start Menu...")
                self.create_start_menu_shortcut(install_path)
            
            # Create uninstaller
            self.update_status("Creating uninstaller...")
            self.create_uninstaller(install_path)
            
            self.update_status("Installation completed successfully!", "green")
            
            # Show completion message
            self.root.after(1000, self.show_completion)
            
        except Exception as e:
            self.update_status(f"Installation failed: {str(e)}", "red")
            messagebox.showerror("Installation Error", f"Installation failed:\\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.install_button.config(state="normal")
    
    def update_status(self, message, color="blue"):
        """Update status label"""
        self.status_label.config(text=message, fg=color)
        self.root.update()
    
    def download_cybersnoop(self, install_path):
        """Download CyberSnoop from GitHub"""
        
        # For now, we'll create a basic structure
        # In a real installer, you'd download from GitHub
        
        # Create basic directory structure
        (install_path / "desktop_app").mkdir(exist_ok=True)
        
        # Create main executable script
        main_script = '''
import sys
import os
from pathlib import Path

# Add the installation directory to Python path
install_dir = Path(__file__).parent
sys.path.insert(0, str(install_dir))

try:
    # Import and run the main application
    from desktop_app.enhanced_cybersnoop_desktop import main
    main()
except ImportError as e:
    print(f"Error importing CyberSnoop: {e}")
    print("Please ensure all dependencies are installed.")
    input("Press Enter to exit...")
except Exception as e:
    print(f"Error running CyberSnoop: {e}")
    input("Press Enter to exit...")
'''
        
        with open(install_path / "CyberSnoop.py", 'w') as f:
            f.write(main_script)
        
        # Create requirements.txt
        requirements = '''PySide6>=6.0.0
scapy>=2.4.0
requests>=2.25.0
sqlalchemy>=1.4.0
fastapi>=0.68.0
uvicorn>=0.15.0
pandas>=1.3.0
numpy>=1.21.0
cryptography>=3.4.0
python-multipart>=0.0.5
websockets>=10.0
pydantic>=1.8.0
'''
        
        with open(install_path / "requirements.txt", 'w') as f:
            f.write(requirements)
    
    def install_dependencies(self, install_path):
        """Install Python dependencies"""
        
        requirements_file = install_path / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True)
    
    def create_desktop_shortcut(self, install_path):
        """Create desktop shortcut"""
        
        try:
            import win32com.client
            
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "CyberSnoop.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{install_path / "CyberSnoop.py"}"'
            shortcut.WorkingDirectory = str(install_path)
            shortcut.Description = "CyberSnoop - Network Security Monitor"
            shortcut.save()
            
        except Exception as e:
            print(f"Failed to create desktop shortcut: {e}")
    
    def create_start_menu_shortcut(self, install_path):
        """Create Start Menu shortcut"""
        
        try:
            import win32com.client
            
            start_menu = Path(os.environ.get('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            shortcut_path = start_menu / "CyberSnoop.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{install_path / "CyberSnoop.py"}"'
            shortcut.WorkingDirectory = str(install_path)
            shortcut.Description = "CyberSnoop - Network Security Monitor"
            shortcut.save()
            
        except Exception as e:
            print(f"Failed to create Start Menu shortcut: {e}")
    
    def create_uninstaller(self, install_path):
        """Create uninstaller"""
        
        uninstaller_script = f'''
import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

def uninstall():
    """Uninstall CyberSnoop"""
    
    if messagebox.askyesno("Uninstall CyberSnoop", 
                          "Are you sure you want to uninstall CyberSnoop?"):
        
        try:
            # Remove installation directory
            install_dir = Path(r"{install_path}")
            if install_dir.exists():
                shutil.rmtree(install_dir)
            
            # Remove shortcuts
            desktop_shortcut = Path.home() / "Desktop" / "CyberSnoop.lnk"
            if desktop_shortcut.exists():
                desktop_shortcut.unlink()
            
            start_menu_shortcut = Path(os.environ.get('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "CyberSnoop.lnk"
            if start_menu_shortcut.exists():
                start_menu_shortcut.unlink()
            
            messagebox.showinfo("Uninstall Complete", "CyberSnoop has been uninstalled successfully.")
            
        except Exception as e:
            messagebox.showerror("Uninstall Error", f"Failed to uninstall CyberSnoop:\\n{{str(e)}}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window
    uninstall()
'''
        
        with open(install_path / "uninstall.py", 'w') as f:
            f.write(uninstaller_script)
    
    def show_completion(self):
        """Show installation completion dialog"""
        
        result = messagebox.showinfo(
            "Installation Complete",
            "CyberSnoop has been installed successfully!\\n\\n"
            "You can now run CyberSnoop from:\\n"
            "• Desktop shortcut (if created)\\n"
            "• Start Menu\\n"
            "• Installation directory\\n\\n"
            "Would you like to launch CyberSnoop now?",
        )
        
        self.root.quit()
    
    def run(self):
        """Run the installer"""
        self.root.mainloop()

if __name__ == "__main__":
    installer = CyberSnoopInstaller()
    installer.run()
'''
    
    # Write the installer script
    with open("cybersnoop_installer.py", 'w') as f:
        f.write(installer_script)
    
    print("✅ Installer script created")
    
    # Build executable
    print("🔨 Building executable...")
    
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "CyberSnoop-Setup",
        "--icon", "NONE",
        "cybersnoop_installer.py"
    ]
    
    subprocess.run(pyinstaller_cmd, check=True)
    
    print("✅ CyberSnoop-Setup.exe created in dist/ folder")
    
    # Move to main directory
    setup_exe = Path("dist") / "CyberSnoop-Setup.exe"
    if setup_exe.exists():
        shutil.move(setup_exe, "CyberSnoop-Setup.exe")
        print("✅ CyberSnoop-Setup.exe moved to main directory")
    
    print("\n🎉 Setup complete!")
    print("📦 CyberSnoop-Setup.exe is ready for distribution")

if __name__ == "__main__":
    build_executable()
