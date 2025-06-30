"""
Privilege Detection and UAC Handling for CyberSnoop
Handles Windows UAC elevation and privilege detection for network packet capture.
"""

import sys
import os
import logging
import ctypes
import subprocess
from typing import Optional, Tuple
from pathlib import Path

def is_admin() -> bool:
    """Check if the current process is running with administrator privileges"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except:
        return False

def is_elevated() -> bool:
    """Check if the current process is elevated (UAC)"""
    try:
        # Try to access a system directory that requires elevation
        test_path = Path("C:\\Windows\\System32\\drivers\\etc\\hosts")
        return os.access(str(test_path), os.W_OK)
    except:
        return False

def get_privilege_level() -> str:
    """Get current privilege level description"""
    if is_admin():
        return "Administrator"
    elif is_elevated():
        return "Elevated User"
    else:
        return "Standard User"

def check_network_capture_privileges() -> Tuple[bool, str]:
    """
    Check if current privileges are sufficient for network packet capture
    Returns: (has_privileges, reason)
    """
    # Check if running as administrator
    if is_admin():
        return True, "Administrator privileges available"
    
    # Check if we can access network interfaces
    try:
        import socket
        # Try to create a raw socket (requires admin on Windows)
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        s.close()
        return True, "Raw socket access available"
    except (OSError, socket.error):
        pass
    
    # Check if we have packet capture capabilities
    try:
        # Try to import Scapy and check if we can capture
        from scapy.all import sniff
        # Quick test - this will fail if no privileges
        sniff(count=1, timeout=1)  # This might fail, but we'll catch it
        return True, "Packet capture libraries available"
    except Exception as e:
        return False, f"Insufficient privileges for packet capture: {str(e)}"

def request_elevation(reason: str = "Network packet capture requires administrator privileges") -> bool:
    """
    Request UAC elevation for the current application
    Returns True if elevation was granted, False otherwise
    """
    try:
        if is_admin():
            return True
            
        # Show a message about why elevation is needed
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        result = messagebox.askyesno(
            "Administrator Privileges Required",
            f"{reason}\n\n"
            "CyberSnoop needs administrator privileges to monitor network traffic.\n\n"
            "Would you like to restart the application as administrator?",
            icon="warning"
        )
        
        root.destroy()
        
        if result:
            # Restart the application with elevation
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    sys.executable,
                    " ".join(sys.argv),
                    None,
                    1
                )
                return True
            except Exception as e:
                logging.error(f"Failed to restart with elevation: {e}")
                return False
        else:
            return False
            
    except Exception as e:
        logging.error(f"Failed to request elevation: {e}")
        return False

def check_npcap_installation() -> Tuple[bool, str]:
    """
    Check if Npcap (WinPcap replacement) is installed
    Returns: (is_installed, version_or_message)
    """
    try:
        # Check common Npcap installation paths
        npcap_paths = [
            "C:\\Windows\\System32\\Npcap",
            "C:\\Windows\\SysWOW64\\Npcap",
            "C:\\Program Files\\Npcap",
            "C:\\Program Files (x86)\\Npcap"
        ]
        
        for path in npcap_paths:
            npcap_dir = Path(path)
            if npcap_dir.exists():
                # Look for key Npcap files
                if (npcap_dir / "wpcap.dll").exists():
                    return True, f"Npcap found at {path}"
        
        # Check registry for Npcap installation
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Npcap")
            version = winreg.QueryValueEx(key, "Version")[0]
            winreg.CloseKey(key)
            return True, f"Npcap version {version}"
        except:
            pass
            
        return False, "Npcap not found - required for packet capture"
        
    except Exception as e:
        return False, f"Error checking Npcap installation: {e}"

def get_system_info() -> dict:
    """Get system information relevant to network monitoring"""
    info = {
        "platform": sys.platform,
        "python_version": sys.version,
        "is_admin": is_admin(),
        "is_elevated": is_elevated(),
        "privilege_level": get_privilege_level(),
        "architecture": "64-bit" if sys.maxsize > 2**32 else "32-bit"
    }
    
    # Check packet capture capabilities
    has_capture, capture_reason = check_network_capture_privileges()
    info["can_capture_packets"] = has_capture
    info["capture_status"] = capture_reason
    
    # Check Npcap installation
    has_npcap, npcap_info = check_npcap_installation()
    info["has_npcap"] = has_npcap
    info["npcap_status"] = npcap_info
    
    return info

def setup_packet_capture_environment() -> Tuple[bool, str]:
    """
    Set up the environment for packet capture
    Returns: (success, message)
    """
    try:
        # Check current privileges
        has_privileges, priv_reason = check_network_capture_privileges()
        
        if not has_privileges:
            logging.warning(f"Insufficient privileges: {priv_reason}")
            
            # Try to request elevation
            if request_elevation("Network monitoring requires administrator privileges"):
                return True, "Elevation granted - please restart the application"
            else:
                return False, "Administrator privileges required for packet capture"
        
        # Check Npcap installation
        has_npcap, npcap_info = check_npcap_installation()
        
        if not has_npcap:
            logging.warning(f"Npcap not available: {npcap_info}")
            return False, "Npcap installation required for packet capture"
        
        logging.info("Packet capture environment ready")
        return True, "Ready for packet capture"
        
    except Exception as e:
        error_msg = f"Failed to setup packet capture environment: {e}"
        logging.error(error_msg)
        return False, error_msg

def log_system_info():
    """Log system information for debugging"""
    info = get_system_info()
    
    logging.info("=== System Information ===")
    for key, value in info.items():
        logging.info(f"{key}: {value}")
    logging.info("=" * 30)

if __name__ == "__main__":
    # Test the privilege detection system
    print("CyberSnoop Privilege Detection Test")
    print("=" * 40)
    
    info = get_system_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 40)
    
    # Test packet capture setup
    success, message = setup_packet_capture_environment()
    print(f"Packet capture setup: {success}")
    print(f"Message: {message}")
