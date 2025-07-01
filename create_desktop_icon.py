import os
import sys
from pathlib import Path
import shutil

def create_desktop_icon():
    """Create a desktop shortcut for CyberSnoop"""
    
    # Get desktop path
    desktop = Path.home() / "Desktop"
    
    # CyberSnoop installation path
    cybersnoop_path = Path(__file__).parent.parent
    app_path = cybersnoop_path / "desktop_app" / "enhanced_cybersnoop_desktop.py"
    
    # Icon content for Windows (.bat file)
    bat_content = f"""@echo off
cd /d "{cybersnoop_path / 'desktop_app'}"
python enhanced_cybersnoop_desktop.py
pause
"""
    
    # Create .bat file on desktop
    desktop_bat = desktop / "CyberSnoop.bat"
    
    try:
        with open(desktop_bat, 'w') as f:
            f.write(bat_content)
        
        print(f"✅ Desktop shortcut created: {desktop_bat}")
        
        # Also create a PowerShell script version
        ps1_content = f"""Set-Location "{cybersnoop_path / 'desktop_app'}"
python enhanced_cybersnoop_desktop.py
Read-Host "Press Enter to continue..."
"""
        
        desktop_ps1 = desktop / "CyberSnoop.ps1"
        with open(desktop_ps1, 'w') as f:
            f.write(ps1_content)
            
        print(f"✅ PowerShell shortcut created: {desktop_ps1}")
        
        # Create a simple launcher script
        launcher_content = f"""#!/usr/bin/env python3
import subprocess
import os

os.chdir(r"{cybersnoop_path / 'desktop_app'}")
subprocess.run([r"{sys.executable}", "enhanced_cybersnoop_desktop.py"])
"""
        
        desktop_launcher = desktop / "CyberSnoop_Launcher.py"
        with open(desktop_launcher, 'w') as f:
            f.write(launcher_content)
            
        print(f"✅ Python launcher created: {desktop_launcher}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create desktop shortcut: {e}")
        return False

if __name__ == "__main__":
    create_desktop_icon()
