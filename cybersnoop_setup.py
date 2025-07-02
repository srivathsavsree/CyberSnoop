import os
import sys
import shutil
import subprocess
import glob
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import threading
import ctypes
from ctypes import wintypes

def get_user_desktop_path():
    """Get the current user's desktop path even when running as administrator"""
    SHGFP_TYPE_CURRENT = 0
    CSIDL_DESKTOPDIRECTORY = 0x10
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOPDIRECTORY, None, SHGFP_TYPE_CURRENT, buf)
    return Path(buf.value)

class CyberSnoopInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CyberSnoop Setup v1.0")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.installing = False
        self.setup_ui()
        
    def setup_ui(self):
        header = tk.Frame(self.root, bg="#2c3e50", height=100)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🛡️ CyberSnoop Installer", 
                font=("Arial", 24, "bold"), 
                fg="white", bg="#2c3e50").pack(pady=30)
        
        main_frame = tk.Frame(self.root, padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, 
                text="Network Security Monitor - Free & Open Source", 
                font=("Arial", 14)).pack(pady=(0, 20))
        
        tk.Label(main_frame, 
                text="This installer will install CyberSnoop on your computer.\n"
                     "CyberSnoop provides enterprise-grade network security monitoring.\n\n"
                     "System Requirements:\n"
                     "• Minimum: Intel i5 (4th gen) or AMD Ryzen 5, 8GB RAM\n"
                     "• Recommended: Intel i7 (8th gen+) or AMD Ryzen 7, 16GB RAM", 
                justify="center", 
                wraplength=500).pack(pady=(0, 30))
        
        options_frame = tk.LabelFrame(main_frame, text="Installation Options", padx=10, pady=10)
        options_frame.pack(fill="x", pady=(0, 20))
        
        self.desktop_shortcut = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Create Desktop Shortcut", 
                      variable=self.desktop_shortcut).pack(anchor="w")
        
        self.install_btn = tk.Button(main_frame, text="Install CyberSnoop", 
                 command=self.install,
                 bg="#27ae60", fg="white", 
                 font=("Arial", 14, "bold"),
                 pady=10)
        self.install_btn.pack(pady=20)
        
        tk.Button(main_frame, text="Cancel", 
                 command=self.root.quit).pack()
        
        self.status_var = tk.StringVar(value="Ready to install")
        tk.Label(main_frame, textvariable=self.status_var, 
                fg="blue").pack(pady=(20, 0))
    
    def install(self):
        if self.installing:
            return
        self.installing = True
        self.install_btn.config(state="disabled", text="Installing...", bg="#95a5a6")
        threading.Thread(target=self._install_process, daemon=True).start()
    
    def _install_process(self):
        try:
            program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
            install_dir = Path(program_files) / "CyberSnoop"
            self.status_var.set("Creating installation directory...")
            install_dir.mkdir(exist_ok=True)
            
            self.status_var.set("Installing CyberSnoop files...")
            
            # When running as PyInstaller exe, files are bundled in sys._MEIPASS
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller bundle
                current_dir = Path(sys._MEIPASS)
            else:
                # Running as script
                current_dir = Path(__file__).parent

            files_to_copy = [
                "desktop_app",
                "requirements.txt", 
                "README.md",
                "LICENSE.md"
            ]
            self.status_var.set("Copying application files...")
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

            self.status_var.set("Installing Python dependencies...")
            requirements_file = install_dir / "requirements.txt"
            if requirements_file.exists():
                python_exe = shutil.which("python") or shutil.which("python3")
                if not python_exe:
                    for path in [
                        r"C:\Python3*\python.exe",
                        r"C:\Program Files\Python3*\python.exe",
                        r"C:\Users\*\AppData\Local\Programs\Python\Python3*\python.exe"
                    ]:
                        matches = glob.glob(path)
                        if matches:
                            python_exe = matches[-1]
                            break
                if python_exe:
                    subprocess.run([
                        python_exe, "-m", "pip", "install", "-r", str(requirements_file)
                    ], check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    raise Exception("Python executable not found. Please ensure Python is installed.")

            self.status_var.set("Creating launcher...")
            self.create_launcher(install_dir)

            # Create icon file first
            self.status_var.set("Creating application icon...")
            self.create_icon_file(install_dir)

            shortcut_created = False
            if self.desktop_shortcut.get():
                self.status_var.set("Creating desktop shortcut...")
                shortcut_created = self.create_shortcut(install_dir)
                
                # If shortcut creation failed, throw an error to stop installation
                if not shortcut_created:
                    raise Exception("Failed to create desktop shortcut. Please ensure you have administrator privileges.")

            self.status_var.set("Installation completed successfully!")
            messagebox.showinfo("Success", 
                f"CyberSnoop installed successfully!\n\n"
                f"Location: {install_dir}\n"
                f"Desktop shortcut: {'Created successfully ✓' if shortcut_created else 'Not created (manual creation may be needed)'}\n\n"
                f"You can now launch CyberSnoop from {'your desktop or' if shortcut_created else ''} the installation directory!")

        except Exception as e:
            self.status_var.set(f"Installation failed: {str(e)}")
            messagebox.showerror("Installation Error", f"Installation failed:\n\n{str(e)}")

        finally:
            self.installing = False
            self.install_btn.config(state="normal", text="Install CyberSnoop", bg="#27ae60")

    def create_launcher(self, install_dir):
        launcher = f"""@echo off
title CyberSnoop - Network Security Monitor
cd /d "{install_dir}"
echo Starting CyberSnoop...
python desktop_app\\enhanced_cybersnoop_desktop.py
if errorlevel 1 (
    echo.
    echo Error: Failed to start CyberSnoop
    echo Please ensure Python and all dependencies are installed.
    pause
)
"""
        with open(install_dir / "CyberSnoop.bat", 'w') as f:
            f.write(launcher)

    def create_icon_file(self, install_dir):
        """Create a simple icon file for the application"""
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple shield icon
            icon_size = 32
            img = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a shield shape
            shield_color = (44, 62, 80)  # Dark blue-gray
            points = [
                (icon_size//2, 2),
                (icon_size-2, icon_size//4),
                (icon_size-2, icon_size*3//4),
                (icon_size//2, icon_size-2),
                (2, icon_size*3//4),
                (2, icon_size//4)
            ]
            draw.polygon(points, fill=shield_color)
            
            # Add a white checkmark or "S" 
            draw.text((icon_size//2-4, icon_size//2-6), "S", fill=(255, 255, 255))
            
            # Save as ICO file
            icon_path = install_dir / "cybersnoop.ico"
            img.save(icon_path, format='ICO')
            return icon_path
            
        except ImportError:
            # Fallback: Copy from a Windows system icon or create a simple text-based one
            icon_path = install_dir / "cybersnoop.ico"
            # Use a default Windows executable icon by copying from system32
            try:
                import shutil
                system_icon = r"C:\Windows\System32\shell32.dll"
                if os.path.exists(system_icon):
                    # We'll use the batch file itself as icon source
                    return None
            except:
                pass
            return None

    def create_shortcut(self, install_dir):
        """Create desktop shortcut using VBS, PowerShell, or win32com fallback."""
        desktop = get_user_desktop_path()  # Use correct user desktop even when running as admin
        icon_path = install_dir / "cybersnoop.ico"
        shortcut_path = desktop / "CyberSnoop.lnk"
        target_path = str(install_dir / "CyberSnoop.bat")

        # Method 1: VBS script (most reliable)
        try:
            vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target_path}"
oLink.WorkingDirectory = "{install_dir}"
oLink.Description = "CyberSnoop - Network Security Monitor"
oLink.WindowStyle = 1
'''
            if icon_path.exists():
                vbs_script += f'oLink.IconLocation = "{icon_path}"\n'
            vbs_script += 'oLink.Save\n'
            
            vbs_file = install_dir / "create_shortcut.vbs"
            with open(vbs_file, 'w') as f:
                f.write(vbs_script)
                
            result = subprocess.run([
                "cscript", "//NoLogo", str(vbs_file)
            ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Clean up VBS file
            if vbs_file.exists():
                vbs_file.unlink()
                
            if result.returncode == 0 and shortcut_path.exists():
                return True
        except Exception as e:
            print(f"VBS shortcut creation failed: {e}")

        # Method 2: PowerShell fallback
        try:
            ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.WorkingDirectory = "{install_dir}"
$Shortcut.Description = "CyberSnoop - Network Security Monitor"
$Shortcut.WindowStyle = 1
'''
            if icon_path.exists():
                ps_script += f'$Shortcut.IconLocation = "{icon_path}"\n'
            ps_script += '$Shortcut.Save()\n'
            
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script
            ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0 and shortcut_path.exists():
                return True
        except Exception as e:
            print(f"PowerShell shortcut creation failed: {e}")

        # Method 3: win32com fallback
        try:
            import win32com.client
            import pythoncom
            pythoncom.CoInitialize()
            
            if shortcut_path.exists():
                shortcut_path.unlink()
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = target_path
            shortcut.WorkingDirectory = str(install_dir)
            shortcut.Description = "CyberSnoop - Network Security Monitor"
            shortcut.WindowStyle = 1
            
            if icon_path.exists():
                shortcut.IconLocation = str(icon_path)
            
            shortcut.save()
            
            if shortcut_path.exists():
                return True
        except Exception as e:
            print(f"win32com shortcut creation failed: {e}")

        # If all methods fail
        return False
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    installer = CyberSnoopInstaller()
    installer.run()
