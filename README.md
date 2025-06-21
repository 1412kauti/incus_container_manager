# incus_container_manager
> A simple (for now) PyQT6 based GUI to manage your incus containers (not planning on VMs for now)

A modern GUI for managing Incus containers, with a user-friendly interface and robust installer.

## Features

- **List, start, stop, restart, and delete containers**
- **Launch new containers with custom profiles**
- **Install Incus automatically if not present**
- **Supports Ubuntu, Debian, Fedora, Arch, Rocky, and Gentoo**
- **Clean, modular code structure**

## Installation

### Clone the repository
```
git clone https://github.com/1412kauti/incus_container_manager.git
cd incus_container_manager
```
### (Optional) Virtual environmennt:
```
conda create -n incus_manager python=3.13 -y
conda activate incus_manager
```
### Install Dependencies
```
pip install -r requirements.txt
```
### Run
```
cd incus_gui
python3 main.py
```

## Usage

- **Refresh the list of containers**
- **Start, stop, restart, or delete containers**
- **Launch new containers with custom profiles**
- **Install Incus if not present**

## Documentation

All modules, classes, and methods are documented with **Google-style docstrings**.  
This makes the codebase easy to understand and maintain, and allows automated tools to generate API documentation.

### How to Write Docstrings

- **Use triple double quotes (`"""`) for docstrings.**
- **Place docstrings as the first statement in modules, classes, functions, and methods.**
- **For Google-style docstrings:**
  - **Summary:** A one-line description.
  - **Blank line:** Separate the summary from the detailed description.
  - **Detailed description:** Explain usage, parameters, return values, and exceptions as needed.
  - **Example:**  
    ```
    """Returns the sum of two numbers.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: Sum of a and b.
    """
    ```
- **Keep docstrings concise but informative.**
- **Update docstrings whenever code changes.**

### How to Read Docstrings

- **From the command line:**
```
python3 -c "help(incus_gui.main_window.IncusGui)"
```
- **In your favorite IDE:** Most modern IDEs show docstrings as tooltips or in documentation panels.
- **In the code:** Docstrings are visible at the top of each module, class, and function.
#### Further Reading

- **[PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)**
- **[Google Python Style Guide – Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)**
- **[Real Python: Documenting Python Code](https://realpython.com/documenting-python-code/)**


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT. See [LICENSE](LICENSE).
