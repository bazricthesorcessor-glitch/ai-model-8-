#!/usr/bin/env python3
"""
OS Connection Quality Check - Hyprland Integration Diagnostics
"""

import subprocess
import json
import time
from typing import Tuple, Dict, Any

class OSConnectionDiagnostics:
    """Check OS connection quality and capabilities"""
    
    @staticmethod
    def check_hyprland() -> Dict[str, Any]:
        """Check Hyprland connectivity"""
        results = {
            "hyprland_available": False,
            "hyprctl_available": False,
            "hyprland_version": None,
            "active_window": None,
            "workspaces": 0,
            "errors": []
        }
        
        # Check if hyprctl exists
        try:
            result = subprocess.run(['which', 'hyprctl'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                results["hyprctl_available"] = True
        except Exception as e:
            results["errors"].append(f"which hyprctl: {str(e)}")
        
        # Check Hyprland environment variable
        import os
        if os.getenv('HYPRLAND_INSTANCE_SIGNATURE'):
            results["hyprland_available"] = True
        else:
            results["errors"].append("HYPRLAND_INSTANCE_SIGNATURE not set - not running in Hyprland")
        
        # Get version
        try:
            result = subprocess.run(['hyprctl', 'version'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                results["hyprland_version"] = result.stdout.split('\n')[0]
        except Exception as e:
            results["errors"].append(f"hyprctl version: {str(e)}")
        
        # Get active window
        try:
            result = subprocess.run(['hyprctl', 'activewindow'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                results["active_window"] = result.stdout.split('\n')[0]
        except Exception as e:
            results["errors"].append(f"hyprctl activewindow: {str(e)}")
        
        # Get workspace count
        try:
            result = subprocess.run(['hyprctl', 'workspaces'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                results["workspaces"] = len([l for l in result.stdout.split('\n') if l.strip() and 'workspace ID' in l])
        except Exception as e:
            results["errors"].append(f"hyprctl workspaces: {str(e)}")
        
        return results
    
    @staticmethod
    def check_input_devices() -> Dict[str, Any]:
        """Check input device access"""
        results = {
            "keyboard_available": False,
            "mouse_available": False,
            "touchpad_available": False,
            "libinput_available": False,
            "errors": []
        }
        
        # Check libinput
        try:
            result = subprocess.run(['libinput', 'list-devices'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                results["libinput_available"] = True
                devices = result.stdout.count("Device:")
                results["input_devices"] = devices
                
                if "keyboard" in result.stdout.lower():
                    results["keyboard_available"] = True
                if "mouse" in result.stdout.lower():
                    results["mouse_available"] = True
                if "touchpad" in result.stdout.lower():
                    results["touchpad_available"] = True
        except Exception as e:
            results["errors"].append(f"libinput: {str(e)}")
        
        return results
    
    @staticmethod
    def check_system_info() -> Dict[str, Any]:
        """Check system information"""
        results = {
            "wm": "unknown",
            "display_server": "unknown",
            "resolution": None,
            "errors": []
        }
        
        import os
        
        # Check display server
        if os.getenv('WAYLAND_DISPLAY'):
            results["display_server"] = "Wayland"
        elif os.getenv('DISPLAY'):
            results["display_server"] = "X11"
        
        # Check window manager
        if os.getenv('HYPRLAND_INSTANCE_SIGNATURE'):
            results["wm"] = "Hyprland"
        
        # Get resolution
        try:
            result = subprocess.run(['hyprctl', 'monitors'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'resolution' in line.lower():
                        results["resolution"] = line.strip()
                        break
        except Exception as e:
            results["errors"].append(f"hyprctl monitors: {str(e)}")
        
        return results
    
    @staticmethod
    def check_gesture_support() -> Dict[str, Any]:
        """Check gesture support"""
        results = {
            "libgestures_available": False,
            "touchpad_gestures": False,
            "gesture_daemon_available": False,
            "errors": []
        }
        
        # Check for gesture libraries
        try:
            result = subprocess.run(['which', 'libinput'], capture_output=True, text=True, timeout=2)
            results["libgestures_available"] = result.returncode == 0
        except:
            pass
        
        try:
            result = subprocess.run(['which', 'gesture-manager'], capture_output=True, text=True, timeout=2)
            results["gesture_daemon_available"] = result.returncode == 0
        except:
            pass
        
        return results
    
    @staticmethod
    def run_full_check() -> Dict[str, Any]:
        """Run full OS connection check"""
        print("=" * 70)
        print("OS CONNECTION QUALITY CHECK - Hyprland Integration Diagnostics")
        print("=" * 70)
        
        checks = {
            "Hyprland": OSConnectionDiagnostics.check_hyprland(),
            "Input Devices": OSConnectionDiagnostics.check_input_devices(),
            "System Info": OSConnectionDiagnostics.check_system_info(),
            "Gesture Support": OSConnectionDiagnostics.check_gesture_support(),
        }
        
        # Print results
        for category, results in checks.items():
            print(f"\n📊 {category}:")
            print("-" * 70)
            for key, value in results.items():
                if key == "errors":
                    if value:
                        print(f"  ⚠️  {key}:")
                        for error in value:
                            print(f"     - {error}")
                else:
                    status = "✅" if (isinstance(value, bool) and value) else ("✅" if value else "❌")
                    print(f"  {status} {key}: {value}")
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY:")
        print("=" * 70)
        
        hyprland_ok = checks["Hyprland"]["hyprland_available"] and checks["Hyprland"]["hyprctl_available"]
        input_ok = checks["Input Devices"]["keyboard_available"] and checks["Input Devices"]["mouse_available"]
        
        print(f"  Hyprland Integration: {'✅ READY' if hyprland_ok else '❌ NOT READY'}")
        print(f"  Input Devices: {'✅ READY' if input_ok else '❌ NOT READY'}")
        print(f"  Display Server: {checks['System Info']['display_server']}")
        print(f"  Window Manager: {checks['System Info']['wm']}")
        
        overall_status = "✅ READY FOR OS INTEGRATION" if hyprland_ok else "⚠️  LIMITED FUNCTIONALITY"
        print(f"\n  Overall Status: {overall_status}")
        print("=" * 70)
        
        return checks

if __name__ == "__main__":
    OSConnectionDiagnostics.run_full_check()
