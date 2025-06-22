"""InstallWizard module for Incus installation GUI wizard.

This module provides a PySide6 QDialog-based wizard to allow users to select Incus version,
channel, network, and storage settings, and initiate the installation process.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QLineEdit, QCheckBox, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt,QThread, Signal
import subprocess
import os
from pathlib import Path

class InstallThread(QThread):
    finished = Signal(bool)
    progress = Signal(int, str)

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

    def run(self):
        try:
            # Step 1: Add Zabbly key and repo (if needed)
            self.progress.emit(1, "Adding Zabbly key and repo...")
            # ... (your existing code for Zabbly setup)

            # Step 2: Update package list and install Incus
            self.progress.emit(2, "Updating package list...")
            subprocess.run(["sudo", "apt", "update"], check=True)
            self.progress.emit(3, "Installing Incus...")
            subprocess.run(["sudo", "apt", "install", "-y", "incus"], check=True)

            # Step 3: Add user to incus-admin group
            self.progress.emit(4, "Adding user to incus-admin group...")
            user = os.getenv("USER")
            subprocess.run(["sudo", "adduser", user, "incus-admin"], check=True)

            # Step 4: Create storage pool (if not exists)
            self.progress.emit(5, "Creating storage pool...")
            try:
                subprocess.run(["sudo","incus", "storage", "create", "default", "dir"], check=True)
                #subprocess.run(["sudo","incus", "storage", "list"], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                # If storage list fails, assume no pool exists
                subprocess.run(["sudo","incus", "storage", "create", "default", "dir"], check=True)

            # Step 5: Create network bridge (if not exists)
            self.progress.emit(6, "Creating network bridge...")
            try:
                subprocess.run(["sudo","incus", "network", "show", "incusbr0"], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                # If network show fails, assume bridge does not exist
                subprocess.run(["sudo","incus", "network", "create", "incusbr0", "--type=bridge"], check=True)

            # Step 6: Update default profile
            self.progress.emit(7, "Updating default profile...")
            #subprocess.run(["sudo","incus", "profile", "device", "remove", "default", "root"], check=True)
            #subprocess.run(["sudo","incus", "profile", "device", "add", "default", "root", "disk", "pool=default", "path=/"], check=True)
            #subprocess.run(["sudo","incus", "profile", "device", "remove", "default", "eth0"], check=True)
            #subprocess.run(["sudo","incus", "profile", "device", "add", "default", "eth0", "nic", "network=incusbr0"], check=True)

            self.progress.emit(8, "Installation complete. Please reboot.")
            self.finished.emit(True)
        except subprocess.CalledProcessError as e:
            self.progress.emit(8, f"Error: Command failed: {e}")
            self.finished.emit(False)
        except Exception as e:
            self.progress.emit(8, f"Error: {e}")
            self.finished.emit(False)


class InstallWizard(QDialog):
    """Incus installation wizard dialog.

    Args:
        available_versions (list): List of available Incus versions or images.
        parent (QWidget, optional): Parent widget for the dialog. Defaults to None.
    """

    def __init__(self, available_versions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Incus Installation Wizard")
        self.setMinimumWidth(400)
        self.available_versions = available_versions
        self.preseed_settings = {}

        layout = QVBoxLayout(self)

        # Channel selection
        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["daily", "stable", "lts"])
        layout.addWidget(QLabel("Select Channel:"))
        layout.addWidget(self.channel_combo)

        # Use native package checkbox
        self.use_native_check = QCheckBox("Use official Ubuntu package (for LTS channel)")
        self.use_native_check.setChecked(True)
        layout.addWidget(self.use_native_check)

        # Version selection
        self.version_combo = QComboBox()
        self.version_combo.addItems(available_versions)
        layout.addWidget(QLabel("Select Incus Version:"))
        layout.addWidget(self.version_combo)

        # Network config
        self.network_line = QLineEdit()
        self.network_line.setPlaceholderText("Network bridge (e.g., lxdbr0)")
        layout.addWidget(QLabel("Network Bridge:"))
        layout.addWidget(self.network_line)

        # Storage config
        self.storage_line = QLineEdit()
        self.storage_line.setPlaceholderText("Storage pool (e.g., default)")
        layout.addWidget(QLabel("Storage Pool:"))
        layout.addWidget(self.storage_line)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 8)
        layout.addWidget(self.progress)

        # Log area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        # Install button
        self.install_btn = QPushButton("Install Incus")
        self.install_btn.clicked.connect(self.start_install)
        layout.addWidget(self.install_btn)


    def get_preseed_settings(self):
        """Get the current preseed settings from the GUI inputs.

        Returns:
            dict: A dictionary containing the selected channel, use_native flag, version, network, and storage.
        """
        network = self.network_line.text().strip() or "lxdbr0"
        storage = self.storage_line.text().strip() or "default"
        self.preseed_settings = {
            "channel": self.channel_combo.currentText(),
            "use_native": self.use_native_check.isChecked(),
            "version": self.version_combo.currentText(),
            "network": network,
            "storage": storage,
        }
        return self.preseed_settings

    def get_available_incus_versions():
        try:
            # Try apt (Debian/Ubuntu)
            result = subprocess.run(['apt-cache', 'madison', 'incus'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if lines and lines[0]:
                return [line.split('|')[1].strip() for line in lines if line]
            # Try snap
            result = subprocess.run(['snap', 'find', 'incus'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # First line is header
                return [line.split()[0] for line in lines[1:] if line]
        except Exception:
            pass
        return ["incus"]  # Fallback

    def start_install(self):
        settings = self.get_preseed_settings()
        # Use defaults if not set
        if not settings["network"]:
            settings["network"] = "incusbr0"
        if not settings["storage"]:
            settings["storage"] = "default"
        # Start the thread
        self.thread = InstallThread(settings)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.install_finished)
        self.thread.start()

    def update_progress(self, step, message):
        self.progress.setValue(step)
        self.log.append(message)

    def install_finished(self, success):
        if success:
            QMessageBox.information(self, "Installation", "Installation complete. Please reboot your system.")
        else:
            QMessageBox.critical(self, "Error", "Installation failed. Check the log for details.")
        self.accept()
