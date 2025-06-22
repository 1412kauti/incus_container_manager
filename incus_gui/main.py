"""Main entry point for the Incus GUI Manager.

This script initializes the Qt application, checks if Incus is installed,
and launches the installation wizard if needed. After installation (or if Incus
is already present), it starts the main GUI window.
"""

import sys
from incus_gui.incus_operations import is_incus_installed, get_available_incus_versions, generate_preseed_file, install_incus
from incus_gui.install_wizard import InstallWizard
from incus_gui.main_window import IncusGui
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog  # <-- Fix: QMessageBox

app = QApplication(sys.argv)

if not is_incus_installed():
    versions = get_available_incus_versions()
    # Always launch the wizard, even if no versions are found
    wizard = InstallWizard(versions or ["images:ubuntu/24.04"])  # Fallback to a default image
    if wizard.exec() == QDialog.Accepted:
        # Proceed with installation
        settings = wizard.get_preseed_settings()
        preseed_file = generate_preseed_file(wizard.get_preseed_settings())
        settings["preseed_file"] = preseed_file 
        if not install_incus(settings):
            QMessageBox.critical(None, "Error", "Failed to install Incus. Check logs.")
            sys.exit(1)
    else:
        sys.exit(0)

gui = IncusGui()
gui.show()
sys.exit(app.exec())
