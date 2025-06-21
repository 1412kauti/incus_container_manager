"""Main window module for the Incus Container Manager GUI.

This module provides the main application window for managing Incus containers,
including listing, starting, stopping, restarting, and deleting containers,
as well as launching new containers and handling user interactions.
"""

from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QListWidget, QListWidgetItem,  # <-- Fix to: QMainWindow
    QPushButton, QLabel, QHBoxLayout, QApplication, QDialog, QMessageBox
)
from PySide6.QtCore import QTimer
from launch_dialog import LaunchContainerDialog
from incus_operations import list_containers, toggle_container, restart_container, launch_container, list_profiles, delete_container

class IncusGui(QMainWindow):
    """Main window for the Incus Container Manager GUI.

    Provides a user interface for managing Incus containers, including listing,
    starting, stopping, restarting, and deleting containers, as well as launching
    new containers and managing profiles.

    Attributes:
        toggling_container (str|None): Name of the container currently being toggled.
        restarting_container (str|None): Name of the container currently being restarted.
        container_list (QListWidget): List widget displaying containers.
        refresh_btn (QPushButton): Button to refresh the container list.
        launch_btn (QPushButton): Button to launch a new container.  # <-- Fix to: QPushButton
        timer (QTimer): Timer for auto-refreshing the container list.
    """

    def __init__(self):
        """Initialize the main window and set up the UI."""
        super().__init__()
        self.setWindowTitle("Incus Container Manager (Qt 6)")
        self.setGeometry(100, 100, 600, 400)
        self.toggling_container = None
        self.restarting_container = None

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # Top layout for buttons
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)
        top_layout.addStretch()

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_containers)
        top_layout.addWidget(self.refresh_btn)

        # Launch new container button
        self.launch_btn = QPushButton("Launch New Container")
        self.launch_btn.clicked.connect(self.show_launch_dialog)
        top_layout.addWidget(self.launch_btn)

        # Container list
        self.container_list = QListWidget()
        main_layout.addWidget(self.container_list)

        # Auto-refresh timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_containers)
        self.timer.start(5000)  # Refresh every 5 seconds

        self.refresh_containers()

    def refresh_containers(self):
        """Refresh the list of containers displayed in the GUI.

        Fetches the current list of containers and updates the UI. Displays errors
        if the fetch fails.
        """
        self.container_list.clear()
        try:
            for container in list_containers():
                self.add_container_item(container["name"], container["status"])
        except Exception as ex:
            print(f"Exception in refresh_containers: {ex}")
            self.container_list.addItem(f"Exception: {str(ex)}")

    def add_container_item(self, container_name, status):  # <-- Fix to: add_container_item
        """Add a container item widget to the list.

        Creates a custom widget for each container, including name, status indicator,
        and action buttons (start/stop, restart, delete).

        Args:
            container_name (str): Name of the container.
            status (str): Current status of the container.
        """
        item = QListWidgetItem()
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)

        label = QLabel(container_name)
        item_layout.addWidget(label)

        status_box = QWidget()
        status_box.setFixedSize(24, 24)
        if self.toggling_container == container_name or self.restarting_container == container_name:
            status_box.setStyleSheet("background: yellow; border: 1px solid #666; border-radius: 3px;")
        elif status.lower() == "running":
            status_box.setStyleSheet("background: green; border: 1px solid #666; border-radius: 3px;")
        elif status.lower() == "stopped":
            status_box.setStyleSheet("background: red; border: 1px solid #666; border-radius: 3px;")
        else:
            status_box.setStyleSheet("background: gray; border: 1px solid #666; border-radius: 3px;")
        item_layout.addWidget(status_box)

        toggle_btn = QPushButton()
        if status.lower() == "running":
            toggle_btn.setText("Stop")
        else:
            toggle_btn.setText("Start")
        toggle_btn.setEnabled(self.toggling_container != container_name and self.restarting_container != container_name)
        toggle_btn.clicked.connect(
            lambda checked, name=container_name, current_status=status:
                self.toggle_container(name, current_status)
        )
        item_layout.addWidget(toggle_btn)

        restart_btn = QPushButton("Restart")
        restart_btn.setEnabled(self.toggling_container != container_name and self.restarting_container != container_name)
        restart_btn.clicked.connect(
            lambda checked, name=container_name:
                self.restart_container(name)
        )
        item_layout.addWidget(restart_btn)

        # Add delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setEnabled(self.toggling_container != container_name and self.restarting_container != container_name)
        delete_btn.clicked.connect(
            lambda checked, name=container_name, current_status=status:
                self.confirm_delete_container(name, current_status)
        )
        item_layout.addWidget(delete_btn)

        self.container_list.addItem(item)
        item.setSizeHint(item_widget.sizeHint())
        self.container_list.setItemWidget(item, item_widget)

    def toggle_container(self, container_name, current_status):
        """Toggle the state of a container (start/stop).

        Args:
            container_name (str): Name of the container to toggle.
            current_status (str): Current status of the container.
        """
        try:
            self.toggling_container = container_name
            self.refresh_containers()
            QApplication.processEvents()

            toggle_container(container_name, current_status)
        except Exception as e:
            print(f"Exception during toggle of {container_name}: {e}")
        finally:
            self.toggling_container = None
            self.refresh_containers()

    def restart_container(self, container_name):
        """Restart a container (stop, then start).

        Args:
            container_name (str): Name of the container to restart.
        """
        try:
            self.restarting_container = container_name
            self.refresh_containers()
            QApplication.processEvents()

            restart_container(container_name)
        except Exception as e:
            print(f"Exception during restart of {container_name}: {e}")
        finally:
            self.restarting_container = None
            self.refresh_containers()

    def show_launch_dialog(self):
        """Show the dialog for launching a new container.

        Opens a dialog for the user to specify container name, image, and profile,
        and initiates the launch process.
        """
        # Example lists (replace with actual data from your system)
        images = ["images:ubuntu/24.04", "images:ubuntu/22.04", "images:alpine/edge"]
        profiles = list_profiles()  # Excludes 'default'

        dialog = LaunchContainerDialog(images, profiles, self)
        if dialog.exec() == QDialog.Accepted:
            try:
                launch_container(
                    dialog.container_name,
                    dialog.selected_image,
                    dialog.selected_profile
                )
                self.refresh_containers()
            except Exception as e:
                print(f"Failed to launch container: {e}")
                QMessageBox.warning(self, "Error", f"Failed to launch container: {e}")

    def delete_container(self, container_name):
        """Delete a container.

        Args:
            container_name (str): Name of the container to delete.
        """
        from incus_operations import delete_container
        delete_container(container_name)
        self.refresh_containers()

    def confirm_delete_container(self, container_name, current_status):
        """Confirm and handle container deletion, with optional stop if running.

        Args:
            container_name (str): Name of the container to delete.
            current_status (str): Current status of the container.
        """
        # If container is running, ask if user wants to stop it first
        if current_status.lower() == "running":
            reply = QMessageBox.question(
                self,
                "Container Running",
                f"Container '{container_name}' is currently running. Do you want to stop it before deleting?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return  # User canceled
            elif reply == QMessageBox.Yes:
                try:
                    toggle_container(container_name, "running")  # Stop the container
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to stop container: {e}")
                    return
            # If No, proceed to delete (may fail if container is still running)

        # Ask for confirmation to delete
        reply = QMessageBox.question(
            self,
            "Delete Container",
            f"Are you sure you want to delete container '{container_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                delete_container(container_name)
                self.refresh_containers()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete container: {e}")
