import pywifi
from pywifi import const
import time
import platform
import logging
import subprocess # Added for subprocess calls on macOS

class WifiManager:
    """Handles Wi-Fi scanning, connection, and disconnection."""

    def __init__(self, logger):
        """
        Initializes the WifiManager.
        Args:
            logger: The logging object for logging messages.
        """
        self.logger = logger
        self.os_platform = platform.system()
        # pywifi is only used for Linux/Windows
        if self.os_platform == "Linux" or self.os_platform == "Windows":
            self.wifi = pywifi.PyWiFi()
            try:
                # Ensure an interface is found before proceeding
                self.iface = self.wifi.interfaces()[0]  # Get the first wireless interface
                self.logger.info(f"WifiManager initialized for {self.os_platform} on interface {self.iface.name()}")
            except IndexError:
                self.logger.error("No wireless interface found by pywifi. Check Wi-Fi adapter.")
                self.iface = None # Indicate no interface found
            except Exception as e:
                self.logger.error(f"Error initializing pywifi: {e}")
                self.iface = None
        else: # macOS
            self.wifi = None # pywifi not used on macOS
            self.iface = None # No pywifi interface for macOS
            self.logger.info(f"WifiManager initialized for {self.os_platform}.")

    def find_and_connect(self, ssid_prefixes):
        """
        Scans for networks and connects to the first one matching the given prefixes.
        Args:
            ssid_prefixes (list): A list of SSID prefixes to search for.
        Returns:
            bool: True if connection is successful, False otherwise.
        """
        if self.os_platform == "Linux" or self.os_platform == "Windows":
            if not self.iface:
                self.logger.error("No Wi-Fi interface available for pywifi. Cannot connect.")
                return False
            return self._connect_pywifi(ssid_prefixes)
        elif self.os_platform == "Darwin":
            return self._connect_macos(ssid_prefixes)
        else:
            self.logger.error(f"Unsupported OS for Wi-Fi control: {self.os_platform}")
            return False

    def _connect_pywifi(self, ssid_prefixes):
        """Handles connection using pywifi for Linux and Windows."""
        self.logger.info("Scanning for Wi-Fi networks using pywifi...")
        try:
            self.iface.scan()
            time.sleep(5)  # Wait for scan to complete

            scan_results = self.iface.scan_results()
            target_network_ssid = None

            for network in scan_results:
                for prefix in ssid_prefixes:
                    if network.ssid.startswith(prefix):
                        self.logger.info(f"Found target camera network: {network.ssid}")
                        target_network_ssid = network.ssid
                        break
                if target_network_ssid:
                    break
            
            if not target_network_ssid:
                self.logger.warning("No camera Wi-Fi network found using pywifi.")
                return False

            # Create a new profile for the connection
            profile = pywifi.Profile()
            profile.ssid = target_network_ssid
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm.append(const.AKM_TYPE_NONE)
            profile.cipher = const.CIPHER_TYPE_NONE

            self.iface.remove_all_network_profiles()
            temp_profile = self.iface.add_network_profile(profile)

            self.logger.info(f"Connecting to {target_network_ssid} using pywifi...")
            self.iface.connect(temp_profile)

            # Wait for connection
            for _ in range(10): # 10 seconds timeout
                if self.iface.status() == const.IFACE_CONNECTED:
                    self.logger.info("Successfully connected to Wi-Fi using pywifi.")
                    return True
                time.sleep(1)
            
            self.logger.error(f"Failed to connect to Wi-Fi network {target_network_ssid} using pywifi after 10 seconds.")
            return False
        except Exception as e:
            self.logger.error(f"Error during pywifi connection: {e}")
            return False

    def _connect_macos(self, ssid_prefixes):
        """Handles connection for macOS using subprocess and networksetup."""
        self.logger.info("Scanning for Wi-Fi networks on macOS...")
        try:
            # Use /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s
            # to scan for networks.
            airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            scan_command = [airport_path, "-s"]
            scan_output = subprocess.check_output(scan_command, text=True, stderr=subprocess.PIPE).strip()
            
            target_ssid = None
            # Parse output, skipping header line
            for line in scan_output.splitlines()[1:]:
                # Example line: "Insta360_X3_001  -80  -- WPA2(PSK/AES/AES)  -no-          -no-  802.11n"
                # SSID can have spaces, so we find the first non-whitespace part as SSID
                parts = line.strip().split("  ") # Double space is a common delimiter
                if parts and parts[0].strip():
                    ssid = parts[0].strip()
                    for prefix in ssid_prefixes:
                        if ssid.startswith(prefix):
                            self.logger.info(f"Found target camera network: {ssid} on macOS.")
                            target_ssid = ssid
                            break
                if target_ssid:
                    break
            
            if not target_ssid:
                self.logger.warning("No camera Wi-Fi network found on macOS.")
                return False

            # Get the current Wi-Fi interface name
            # This is typically 'en0' or 'en1', but can be dynamic.
            interface_command = ["networksetup", "-listallhardwareports"]
            interface_output = subprocess.check_output(interface_command, text=True, stderr=subprocess.PIPE).strip()
            wifi_interface = None
            for block in interface_output.split("\n\n"):
                if "Wi-Fi" in block and "Device:" in block:
                    for line in block.splitlines():
                        if "Device:" in line:
                            wifi_interface = line.split(":")[1].strip()
                            break
                if wifi_interface:
                    break

            if not wifi_interface:
                self.logger.error("Could not determine Wi-Fi interface on macOS.")
                return False

            self.logger.info(f"Connecting to {target_ssid} using interface {wifi_interface} on macOS...")
            # Command to connect to an open network. No password needed for camera hotspot.
            connect_command = ["networksetup", "-setairportnetwork", wifi_interface, target_ssid]
            subprocess.check_call(connect_command, stderr=subprocess.PIPE)
            
            # Verify connection by checking current SSID
            for _ in range(15): # Give it more time, up to 15 seconds
                time.sleep(1)
                current_ssid_command = [airport_path, "-I"]
                current_ssid_output = subprocess.check_output(current_ssid_command, text=True, stderr=subprocess.PIPE).strip()
                if f"SSID: {target_ssid}" in current_ssid_output:
                    self.logger.info("Successfully connected to Wi-Fi on macOS.")
                    return True
            
            self.logger.error(f"Failed to connect to Wi-Fi network {target_ssid} on macOS after 15 seconds.")
            return False

        except subprocess.CalledProcessError as e:
            self.logger.error(f"macOS Wi-Fi command failed (Exit Code: {e.returncode}): {e.stderr.strip()}")
            return False
        except FileNotFoundError:
            self.logger.error("`airport` or `networksetup` command not found. Ensure Xcode Command Line Tools are installed.")
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during macOS Wi-Fi connection: {e}")
            return False

    def disconnect(self):
        """Disconnects from the current Wi-Fi network."""
        if self.os_platform == "Linux" or self.os_platform == "Windows":
            if self.iface:
                self.logger.info("Disconnecting from Wi-Fi using pywifi...")
                try:
                    self.iface.disconnect()
                    self.logger.info("Wi-Fi disconnected.")
                except Exception as e:
                    self.logger.error(f"Error during pywifi disconnection: {e}")
            else:
                self.logger.warning("No pywifi interface to disconnect from.")
        elif self.os_platform == "Darwin":
            self.logger.info("Disconnecting from Wi-Fi on macOS...")
            try:
                # Find current Wi-Fi interface
                interface_command = ["networksetup", "-listallhardwareports"]
                interface_output = subprocess.check_output(interface_command, text=True, stderr=subprocess.PIPE).strip()
                wifi_interface = None
                for block in interface_output.split("\n\n"):
                    if "Wi-Fi" in block and "Device:" in block:
                        for line in block.splitlines():
                            if "Device:" in line:
                                wifi_interface = line.split(":")[1].strip()
                                break
                    if wifi_interface:
                        break
                
                if wifi_interface:
                    # Deactivate Wi-Fi. This essentially disconnects from any network.
                    self.logger.info(f"Turning off Wi-Fi on interface {wifi_interface} on macOS.")
                    subprocess.check_call(["networksetup", "-setairportpower", wifi_interface, "off"], stderr=subprocess.PIPE)
                    self.logger.info("Wi-Fi turned off on macOS.")
                    # Optionally, turn it back on to reconnect to previous network
                    # subprocess.check_call(["networksetup", "-setairportpower", wifi_interface, "on"])
                    # self.logger.info("Wi-Fi turned back on on macOS.")
                else:
                    self.logger.error("Could not determine Wi-Fi interface on macOS for disconnection.")
                
            except subprocess.CalledProcessError as e:
                self.logger.error(f"macOS Wi-Fi disconnection command failed (Exit Code: {e.returncode}): {e.stderr.strip()}")
            except FileNotFoundError:
                self.logger.error("`networksetup` command not found on macOS for disconnection.")
            except Exception as e:
                self.logger.error(f"An unexpected error occurred during macOS Wi-Fi disconnection: {e}")
        else:
            self.logger.warning(f"Disconnect not implemented for OS: {self.os_platform}")
