import unittest
from unittest.mock import patch, MagicMock, call
from incus_gui import incus_operations

class TestIncusOperations(unittest.TestCase):
    @patch('incus_operations.subprocess.run')
    def test_list_containers_success(self, mock_run):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"metadata": ["/1.0/instances/container1"]}
        with patch('incus_operations.requests_unixsocket.Session') as mock_session:
            mock_session.return_value.get.return_value = mock_resp
            containers = incus_operations.list_containers()
            self.assertEqual(len(containers), 1)
            self.assertEqual(containers[0]['name'], 'container1')

    @patch('incus_operations.subprocess.run')
    def test_launch_container_success(self, mock_run):
        mock_run.return_value.returncode = 0
        incus_operations.launch_container('test', 'ubuntu/24.04')
        self.assertEqual(mock_run.call_count, 2)

    @patch('incus_operations.subprocess.run')
    def test_delete_container_success(self, mock_run):
        mock_run.return_value.returncode = 0
        incus_operations.delete_container('test')
        mock_run.assert_called_with(['incus', 'delete', 'test'], capture_output=True, text=True)

    @patch('incus_operations.subprocess.run')
    def test_toggle_container_running(self, mock_run):
        incus_operations.toggle_container('test', 'running')
        mock_run.assert_called_once()

    @patch('incus_operations.subprocess.run')
    def test_list_profiles(self, mock_run):
        mock_run.return_value.stdout = "Name\nprofile1\nprofile2"
        profiles = incus_operations.list_profiles()
        self.assertEqual(profiles, ['profile1', 'profile2'])
