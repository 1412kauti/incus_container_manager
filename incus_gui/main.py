"""Main entry point for the Incus GUI Manager.

This script initializes the Qt application, checks if Incus is installed,
and launches the installation wizard if needed. After installation (or if Incus
is already present), it starts the main GUI window.
"""

import sys
from incus_gui.incus_operations import is_incus_installed, get_available_incus_versions, generate_preseed_file, install_incus
from incus_gui.install_wizard import InstallWizard
from incus_gui.main_window import IncusGui
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog

app = QApplication(sys.argv)

if not is_incus_installed():
    # If Incus is not installed, check for available versions
    versions = get_available_incus_versions()
    if not versions:
        QMessageBox.critical(None, "Error", "No Incus package found for your distro.")
        sys.exit(1)
    # Launch the installation wizard
    wizard = InstallWizard(versions)
    if wizard.exec() == QDialog.Accepted:
        # Generate preseed file and install Incus
        preseed_file = generate_preseed_file(wizard.get_preseed_settings())
        if not install_incus(wizard.get_preseed_settings()["version"], preseed_file):
            QMessageBox.critical(None, "Error", "Failed to install Incus. Check logs.")
            sys.exit(1)
    else:
        # User canceled the installation
        sys.exit(0)

# Start the main GUI window
gui = IncusGui()
gui.show()
sys.exit(app.exec())
