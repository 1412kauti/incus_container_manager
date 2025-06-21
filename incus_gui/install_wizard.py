"""InstallWizard module for Incus installation GUI wizard.

This module provides a PySide6 QDialog-based wizard to allow users to select Incus version,
channel, network, and storage settings, and initiate the installation process.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QLineEdit, QCheckBox 
)
from PySide6.QtCore import Qt

class InstallWizard(QDialog):
    """Incus installation wizard dialog.

    This dialog allows users to select Incus version, channel, network, and storage settings,
    and initiates the installation process.

    Args:
        available_versions (list): List of available Incus versions or images.
        parent (QWidget, optional): Parent widget for the dialog. Defaults to None.
    """

    def __init__(self, available_versions, parent=None):
        """Initialize the InstallWizard dialog.

        Args:
            available_versions (list): List of available Incus versions or images.
            parent (QWidget, optional): Parent widget for the dialog. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Incus Installation Wizard")
        self.setMinimumWidth(400)
        self.available_versions = available_versions
        self.preseed_settings = {}
        self.process = None

        layout = QVBoxLayout(self)

        # Channel selection (for Ubuntu/Debian)
        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["daily", "stable", "lts"])
        layout.addWidget(QLabel("Select Channel:"))
        layout.addWidget(self.channel_combo)  

        # For Ubuntu 24.04+, add a checkbox to use native LTS package
        self.use_native_check = QCheckBox("Use official Ubuntu package (for LTS channel)")
        self.use_native_check.setChecked(True)
        layout.addWidget(self.use_native_check)

        # Version selection (for other distros or if needed)
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

        # Install button
        self.install_btn = QPushButton("Install Incus")
        self.install_btn.clicked.connect(self.start_install)
        layout.addWidget(self.install_btn)

    def get_preseed_settings(self):
        """Get the current preseed settings from the GUI inputs.

        Returns:
            dict: A dictionary containing the selected channel, use_native flag, version, network, and storage.
        """
        self.preseed_settings = {
            "channel": self.channel_combo.currentText(),
            "use_native": self.use_native_check.isChecked(),
            "version": self.version_combo.currentText(),
            "network": self.network_line.text(),
            "storage": self.storage_line.text(),
        }
        return self.preseed_settings

    def start_install(self):
        """Start the Incus installation process based on user input.

        Validates input fields, initiates installation, and handles reboot prompts.
        """
        settings = self.get_preseed_settings()
        if not settings["network"] or not settings["storage"]:
            QMessageBox.warning(self, "Input Error", "Please enter network and storage settings.")
            return

        QMessageBox.information(self, "Installation", "Incus will now be installed. Please wait...")

        from incus_operations import install_incus
        try:
            reboot_required = install_incus(settings)
            if reboot_required:
                reply = QMessageBox.question(
                    self,
                    "Reboot Required",
                    "A reboot is required to apply group changes. Would you like to reboot now?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    import subprocess
                    subprocess.run(["sudo", "reboot"])
                else:
                    QMessageBox.information(
                        self,
                        "Reboot Required",
                        "Please reboot your machine to apply group changes before using Incus."
                    )
            else:
                QMessageBox.information(
                    self,
                    "Installation Complete",
                    "Incus has been installed. You can now use the GUI."
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to install Incus: {e}")
