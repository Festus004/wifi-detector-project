
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import re

class WifiDetector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WiFi Detector")
        self.root.configure(bg="#87CEEB")  # Light blue background

        # Scan button
        self.scan_button = tk.Button(
            self.root,
            text="Scan for WiFi Networks",
            command=self.scan_wifi,
            bg="#4CAF50",
            fg="#fff"
        )
        self.scan_button.pack(pady=10)

        # Output area
        self.output = tk.Text(self.root, height=15, width=60, bg="#f0f0f0")
        self.output.pack(pady=5)

        # Network name entry
        self.network_name_label = tk.Label(
            self.root,
            text="Enter the network name:",
            bg="#87CEEB"
        )
        self.network_name_label.pack()
        self.network_name_entry = tk.Entry(self.root)
        self.network_name_entry.pack()

        # Password entry
        self.password_label = tk.Label(
            self.root,
            text="Enter the password (if required):",
            bg="#87CEEB"
        )
        self.password_label.pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        # Connect button
        self.connect_button = tk.Button(
            self.root,
            text="Connect",
            command=self.connect_wifi,
            bg="#4CAF50",
            fg="#fff"
        )
        self.connect_button.pack(pady=10)

        # Status label
        self.status_label = tk.Label(self.root, text="", bg="#87CEEB")
        self.status_label.pack()

    def scan_wifi(self):
        try:
            output = subprocess.check_output(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'], shell=True).decode('utf-8', errors='ignore')
            lines = output.split('\n')
            networks = []
            ssid = None
            signal = None
            auth = None
            for line in lines:
                line = line.strip()
                if line.startswith('SSID'):
                    ssid_match = re.match(r'SSID\s+\d+\s+:\s+(.*)', line)
                    if ssid_match:
                        ssid = ssid_match.group(1)
                elif line.startswith('Signal'):
                    signal_match = re.match(r'Signal\s+:\s+(\d+)%', line)
                    if signal_match:
                        signal = signal_match.group(1)
                elif line.startswith('Authentication'):
                    auth_match = re.match(r'Authentication\s+:\s+(.*)', line)
                    if auth_match:
                        auth = auth_match.group(1)
                if ssid and signal and auth:
                    security = 'Open' if auth.lower() == 'open' else 'Secured'
                    networks.append((ssid, signal, security))
                    ssid = None
                    signal = None
                    auth = None
            if networks:
                output_text = "Nearby WiFi Networks:\n"
                for i, (ssid, signal, security) in enumerate(networks):
                    output_text += f"{i+1}. {ssid} - Signal Strength: {signal}% - {security}\n"
            else:
                output_text = "No WiFi networks found."
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, output_text)
        except Exception as e:
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"Failed to scan for WiFi networks: {str(e)}")

    def connect_wifi(self):
        ssid = self.network_name_entry.get().strip()
        password = self.password_entry.get().strip()

        if not ssid:
            messagebox.showwarning("Input Error", "Please enter a network name.")
            return

        confirm = messagebox.askyesno("Confirm Connection", f"Do you want to connect to '{ssid}'?")
        if not confirm:
            self.status_label.config(text="Connection cancelled.", fg="blue")
            return

        try:
            if password:
                # Create a temporary WiFi profile XML file
                profile = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
                with open("temp_profile.xml", "w") as f:
                    f.write(profile)
                subprocess.run(f'netsh wlan add profile filename="temp_profile.xml"', shell=True, check=True)

            # Attempt to connect
            subprocess.run(f'netsh wlan connect name="{ssid}"', shell=True, check=True)
            self.status_label.config(text=f"Connected to '{ssid}'", fg="green")
        except subprocess.CalledProcessError:
            self.status_label.config(text=f"Failed to connect to '{ssid}'", fg="red")
        finally:
            if os.path.exists("temp_profile.xml"):
                os.remove("temp_profile.xml")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    WifiDetector().run()
