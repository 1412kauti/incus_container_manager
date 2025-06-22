"""LaunchContainerDialog module for launching new Incus containers.

This module provides a PySide6 QDialog-based dialog to allow users to specify container
name, image, and profile for launching new Incus containers.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
)

class LaunchContainerDialog(QDialog):
    """Dialog for launching new Incus containers.

    Args:
        images (list): List of available container images.
        profiles (list): List of available profiles (excluding 'default').
        parent (QWidget, optional): Parent widget for the dialog. Defaults to None.
    """

    def __init__(self, images, profiles, parent=None):
        """Initialize the LaunchContainerDialog.

        Args:
            images (list): List of available container images.
            profiles (list): List of available profiles (excluding 'default').
            parent (QWidget, optional): Parent widget for the dialog. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Launch New Container")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Container name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Container Name:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Image selection
        image_layout = QHBoxLayout()
        image_label = QLabel("Image:")
        self.image_combo = QComboBox()
        self.image_combo.addItems(images)
        image_layout.addWidget(image_label)
        image_layout.addWidget(self.image_combo)
        layout.addLayout(image_layout)

        # Profile selection
        profile_layout = QHBoxLayout()
        profile_label = QLabel("Profile:")
        self.profile_combo = QComboBox()
        self.profile_combo.addItem("None")
        self.profile_combo.addItems(profiles)
        profile_layout.addWidget(profile_label)
        profile_layout.addWidget(self.profile_combo)
        layout.addLayout(profile_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.launch_btn = QPushButton("Launch")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addStretch()
        btn_layout.addWidget(self.launch_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.launch_btn.clicked.connect(self.on_launch)
        self.cancel_btn.clicked.connect(self.reject)

    def on_launch(self):
        """Handle the launch button click.

        Validates the container name input and sets the selected image and profile.
        Accepts the dialog if input is valid, otherwise shows a warning.
        """
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a container name.")
            return
        self.container_name = name
        self.selected_image = self.image_combo.currentText()
        profile = self.profile_combo.currentText()
        self.selected_profile = None if profile == "None" else profile
        self.accept()
