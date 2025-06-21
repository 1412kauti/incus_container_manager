import unittest
from unittest.mock import patch, MagicMock, call
from incus_gui.incus_operations import list_containers, launch_container, delete_container,toggle_container,list_profiles

class TestIncusOperations(unittest.TestCase):
    @patch('incus_gui.incus_operations.subprocess.run')
    def test_launch_container_success(self, mock_run):
        mock_run.return_value.returncode = 0
        launch_container('test', 'ubuntu/24.04', 'profile')
        self.assertEqual(mock_run.call_count, 2)

    @patch('incus_gui.incus_operations.requests_unixsocket.Session')
    def test_list_containers_success(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"metadata": ["/1.0/instances/container1"]}
        mock_session.return_value.get.return_value = mock_resp
        containers = list_containers()
        self.assertEqual(len(containers), 1)

    @patch('incus_gui.incus_operations.subprocess.run')
    def test_delete_container_success(self, mock_run):
        mock_run.return_value.returncode = 0
        delete_container('test')
        mock_run.assert_called_with(['incus', 'delete', 'test'], capture_output=True, text=True)

    @patch('incus_gui.incus_operations.subprocess.run')
    def test_toggle_container_running(self, mock_run):
        toggle_container('test', 'running')
        mock_run.assert_called_once()

    @patch('incus_gui.incus_operations.subprocess.run')
    def test_list_profiles(self, mock_run):
        mock_run.return_value.stdout = "Name\nprofile1\nprofile2"
        profiles = list_profiles()
        self.assertEqual(profiles, ['profile1', 'profile2'])
