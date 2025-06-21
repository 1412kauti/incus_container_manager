import pytest
from PySide6.QtCore import Qt
from incus_gui.install_wizard import InstallWizard

@pytest.fixture
def wizard(qtbot):
    """Create and return the installation wizard"""
    wiz = InstallWizard(["ubuntu/24.04"], ["gui"])
    qtbot.addWidget(wiz)
    return wiz

def test_wizard_initial_state(wizard):
    """Test initial wizard state"""
    assert wizard.windowTitle() == "Launch New Container/Instance"
    assert wizard.channel_combo.currentText() == "daily"
    assert wizard.image_combo.currentText() == "ubuntu/24.04"

def test_valid_launch(wizard, qtbot):
    """Test valid launch submission"""
    # Set required fields
    wizard.name_edit.setText("test-container")
    wizard.network_line.setText("lxdbr0")
    wizard.storage_line.setText("default")
    
    # Capture accepted signal
    with qtbot.waitSignal(wizard.accepted, timeout=1000):
        qtbot.mouseClick(wizard.launch_btn, Qt.LeftButton)
    
    assert wizard.container_name == "test-container"
    assert wizard.selected_image == "ubuntu/24.04"
