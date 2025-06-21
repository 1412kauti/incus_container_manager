"""Incus operations module.

This module provides functions for interacting with Incus containers and profiles,
including launching, listing, toggling, restarting, and deleting containers,
as well as listing profiles and managing installations.
"""

import requests_unixsocket
import time
import subprocess
import shutil
import platform
import os
from PySide6.QtWidgets import QMessageBox 

SOCKET_PATH = "/var/lib/incus/unix.socket"
BASE_URL = f"http+unix://%2Fvar%2Flib%2Fincus%2Funix.socket/1.0"


def list_containers():
    """List all containers and their statuses.

    Queries the Incus API to retrieve a list of all containers and their current status.

    Returns:
        list[dict]: A list of dictionaries, each containing 'name' and 'status' of a container.

    Raises:
        Exception: If the API request fails.
    """
    api_url = f"{BASE_URL}/instances"
    session = requests_unixsocket.Session()
    resp = session.get(api_url)
    if resp.status_code == 200:
        data = resp.json()
        containers = []
        for instance_path in data.get("metadata", []):
            container_name = instance_path.split('/')[-1]
            state_url = f"{BASE_URL}/instances/{container_name}/state"
            state_resp = session.get(state_url)
            status = "unknown"
            if state_resp.status_code == 200:
                state_data = state_resp.json()
                status = state_data.get("metadata", {}).get("status", "unknown")
            containers.append({"name": container_name, "status": status})
        return containers
    else:
        raise Exception(f"Failed to fetch containers: {resp.status_code} - {resp.text}")


def toggle_container(container_name, current_status): 
    """Start or stop a container based on its current status.

    Args:
        container_name (str): Name of the container to toggle.
        current_status (str): Current status of the container (e.g., 'running', 'stopped').

    Raises:
        Exception: If the API request fails.
    """
    api_url = f"{BASE_URL}/instances/{container_name}/state"
    session = requests_unixsocket.Session()
    if current_status.lower() == "running":
        resp = session.put(api_url, json={"action": "stop"})
    else:
        resp = session.put(api_url, json={"action": "start"})
    if resp.status_code not in (200, 202):
        raise Exception(f"Failed to toggle container {container_name}: {resp.status_code}")


def restart_container(container_name):
    """Restart a container (stop, then start).

    Args:
        container_name (str): Name of the container to restart.

    Raises:
        Exception: If the API request fails or the container cannot be started.
    """
    api_url = f"{BASE_URL}/instances/{container_name}/state"
    session = requests_unixsocket.Session()
    # Try to stop the container (ignore if already stopped)
    try:
        resp = session.put(api_url, json={"action": "stop"})
        print(f"Stop attempt: {resp.status_code} - {resp.text}")
        if resp.status_code not in (200, 202):
            print(f"Warning: Could not stop container {container_name}: {resp.status_code}")
    except Exception as e:
        print(f"Warning: Exception stopping container {container_name}: {e}")
    # Small delay to allow state to settle (optional)
    time.sleep(1)
    # Try to start the container (ignore if already running)
    try:
        resp = session.put(api_url, json={"action": "start"})
        print(f"Start attempt: {resp.status_code} - {resp.text}")
        if resp.status_code not in (200, 202):
            raise Exception(f"Failed to start container {container_name}: {resp.status_code}")
    except Exception as e:
        print(f"Exception starting container {container_name}: {e}")
        raise


def launch_container(name, image, profile=None):
    """Launch a new Incus container.

    Args:
        name (str): Name of the container to launch.
        image (str): Image to use for the container.
        profile (str, optional): Profile to apply to the container. Defaults to None.

    Raises:
        Exception: If the container launch or profile addition fails.
    """
    cmd_launch = ["incus", "launch", image, name]
    result = subprocess.run(cmd_launch, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to launch container: {result.stderr or result.stdout}")

    if profile:
        cmd_profile_add = ["incus", "profile", "add", name, profile]
        result = subprocess.run(cmd_profile_add, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to add profile: {result.stderr or result.stdout}")  # <-- Fix: raise


def list_profiles():
    """List all available profiles excluding 'default'.

    Returns:
        list: List of profile names (excluding 'default').

    Raises:
        Exception: If the profile listing command fails.
    """
    result = subprocess.run(["incus", "profile", "list", "--format", "csv"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to list profiles: {result.stderr or result.stdout}")

    profiles = []
    for line in result.stdout.strip().splitlines()[1:]:  # Skip header
        if line:
            profile_name = line.split(',')[0].strip()
            if profile_name != "default":
                profiles.append(profile_name)
    return profiles


def delete_container(name):
    """Delete an Incus container.

    Args:
        name (str): Name of the container to delete.

    Raises:
        Exception: If the deletion command fails.
    """
    cmd = ["incus", "delete", name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to delete container: {result.stderr or result.stdout}")


def is_incus_installed():
    """Check if Incus is installed on the system.

    Returns:
        bool: True if Incus is installed, False otherwise.
    """
    return shutil.which('incus') is not None


def get_available_incus_versions():
    """Get available Incus versions for the current system.

    Checks both apt and snap package managers for available versions.

    Returns:
        list: List of available Incus versions.
    """
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
    return []


def generate_preseed_file(settings, filename="incus-preseed.yaml"):
    """Generate a preseed configuration file for Incus initialization.

    Args:
        settings (dict): Dictionary containing 'network' and 'storage' keys.
        filename (str, optional): Output filename. Defaults to "incus-preseed.yaml".

    Returns:
        str: The path to the generated preseed file.
    """
    with open(filename, "w") as f:
        f.write(
            f"config:\n"
            f"  core.https_address: 0.0.0.0\n"
            f"  core.trust_password: ''\n"
            f"storage_pools:\n"
            f"- name: {settings['storage']}\n"
            f"  driver: dir\n"
            f"networks:\n"
            f"- name: {settings['network']}\n"
            f"  type: bridge\n"
            f"  config:\n"
            f"    ipv4.address: auto\n"
            f"    ipv6.address: auto\n"
        )
    return filename


def get_distro_info():
    """Detect the current Linux distribution, version, and codename.

    Reads /etc/os-release to determine the distribution, version, and codename.

    Returns:
        tuple: (distro, version, codename), where distro is the distribution ID,
               version is the version number, and codename is the release codename.
    """
    distro = platform.system().lower()
    version = None
    codename = None
    if distro == "linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line.strip().split("=")[1].strip('"')
                    elif line.startswith("VERSION_ID="):
                        version = line.strip().split("=")[1].strip('"')
                    elif line.startswith("VERSION_CODENAME="):
                        codename = line.strip().split("=")[1].strip('"')
        except Exception:
            pass
    return distro, version, codename


def install_incus(settings):
    """Install Incus on the current system based on user settings.

    Supports multiple distributions and installation methods (native, Zabbly, etc.).

    Args:
        settings (dict): Dictionary containing 'channel', 'network', 'storage',
                        and optionally 'use_native'.

    Returns:
        bool: True if a reboot is required after installation, False otherwise.

    Raises:
        Exception: If installation fails.
    """
    distro, version, codename = get_distro_info()
    channel = settings.get("channel", "stable")
    network = settings.get("network")
    storage = settings.get("storage")

    reboot_required = False

    try:
        # --- Ubuntu 24.04+ ---
        if distro == "ubuntu" and version and float(version) >= 24.04:
            if channel == "lts" and settings.get("use_native", True):
                # Use official Ubuntu package
                subprocess.run(["sudo", "apt", "install", "-y", "incus"], check=True)
            else:
                # Use Zabbly repository for daily/stable/lts (if user wants)
                repo_url = f"https://pkgs.zabbly.com/incus/{channel}"
                os.makedirs("/etc/apt/keyrings", exist_ok=True)
                subprocess.run(["wget", "-qO", "-", "https://pkgs.zabbly.com/key.asc"], check=True, stdout=open("/etc/apt/keyrings/zabbly.asc", "wb"))
                sources_file = f"/etc/apt/sources.list.d/zabbly-incus-{channel}.sources"
                with open(sources_file, "w") as f:
                    f.write(
                        f"Enabled: yes\nTypes: deb\nURIs: {repo_url}\nSuites: {codename}\nComponents: main\nArchitectures: {subprocess.check_output(['dpkg', '--print-architecture']).decode().strip()}\nSigned-By: /etc/apt/keyrings/zabbly.asc\n"
                    )
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", "incus"], check=True)
            reboot_required = True

        # --- Ubuntu < 24.04 / Debian ---
        elif (distro == "ubuntu" and version and float(version) < 24.04) or (distro == "debian"):
            # Use Zabbly repository
            repo_url = f"https://pkgs.zabbly.com/incus/{channel}"
            os.makedirs("/etc/apt/keyrings", exist_ok=True)
            subprocess.run(["wget", "-qO", "-", "https://pkgs.zabbly.com/key.asc"], check=True, stdout=open("/etc/apt/keyrings/zabbly.asc", "wb"))
            sources_file = f"/etc/apt/sources.list.d/zabbly-incus-{channel}.sources"
            with open(sources_file, "w") as f:
                f.write(
                    f"Enabled: yes\nTypes: deb\nURIs: {repo_url}\nSuites: {codename if codename else version}\nComponents: main\nArchitectures: {subprocess.check_output(['dpkg', '--print-architecture']).decode().strip()}\nSigned-By: /etc/apt/keyrings/zabbly.asc\n"
                )
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "incus"], check=True)
            reboot_required = True

        # --- Other distros (Fedora, Arch, Rocky, Gentoo) ---
        elif distro == "fedora":
            subprocess.run(["sudo", "dnf", "install", "-y", "incus"], check=True)
        elif distro == "arch":
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "incus"], check=True)
        elif distro == "rocky":
            subprocess.run(["sudo", "dnf", "install", "-y", "incus"], check=True)
        elif distro == "gentoo":
            subprocess.run(["sudo", "emerge", "-av", "app-containers/incus"], check=True)
        else:
            raise Exception("Unsupported distribution")

        # Add user to incus-admin group
        user = os.getenv("USER")
        if user:
            subprocess.run(["sudo", "usermod", "-aG", "incus-admin", user], check=True)
            reboot_required = True

        return reboot_required

    except Exception as e:
        print(f"Installation failed: {e}")
        raise
