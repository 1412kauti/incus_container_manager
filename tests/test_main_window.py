import pytest
from PySide6.QtCore import Qt
from incus_gui.main_window import IncusGui
from incus_gui.incus_operations import list_containers

@pytest.fixture
def app(qtbot):
    """Create and return the main window"""
    window = IncusGui()
    qtbot.addWidget(window)
    return window

def test_initial_state(app):
    """Test initial UI state"""
    assert app.windowTitle() == "Incus Container Manager (Qt 6)"
    assert app.container_list.count() == 0  # Starts empty

@patch('main_window.list_containers')
def test_refresh_containers(mock_list, app, qtbot):
    """Test container list refresh"""
    mock_list.return_value = [{"name": "test", "status": "running"}]
    qtbot.mouseClick(app.refresh_btn, Qt.LeftButton)
    assert app.container_list.count() == 1

@patch('main_window.launch_container')
def test_launch_container_dialog(mock_launch, app, qtbot):
    """Test container launch workflow"""
    # Open launch dialog
    qtbot.mouseClick(app.launch_btn, Qt.LeftButton)
    # Should have dialog open here (in real test would interact with dialog)
    mock_launch.assert_called_once()
