import subprocess
import os
from cwd import cwd

def create_venv():
    with cwd("tmp/test"):
        subprocess.check_call(["python3", "-m", "venv", ".venv"])
        subprocess.check_call([os.path.join(".venv", "bin", "python"),"-m", "pip", "install", "ipykernel"])
        # subprocess.check_call(["venv/bin/python", "-m", "ipykernel", "install", "--user", "--name=test_kernel"])
        subprocess.check_call([os.path.join(".venv", "bin", "python"), "-m", "ipykernel", "install", "--prefix", ".", "--name", "venv", "--display-name", "venv"]) 

def create_kernel_in_custom_directory(venv_path, kernel_name, custom_kernel_dir):
    """
    Programmatically create and register a Jupyter kernel in a custom directory.
    
    :param venv_path: Path to the virtual environment (e.g., /path/to/venv).
    :param kernel_name: Name for the Jupyter kernel to register (e.g., "my_venv_kernel").
    :param custom_kernel_dir: Directory where the kernel should be installed (e.g., /opt/my_kernels).
    """
    # Ensure ipykernel is installed in the virtual environment
    subprocess.check_call([os.path.join(venv_path, "bin", "python"), "-m", "pip", "install", "ipykernel"])

    # Install the kernel in the custom directory
    subprocess.check_call([
        os.path.join(venv_path, "bin", "python"),
        "-m", "ipykernel", "install",
        "--prefix", custom_kernel_dir,
        "--name", kernel_name
    ])

    print(f"Kernel '{kernel_name}' registered in {custom_kernel_dir}/share/jupyter/kernels/{kernel_name}")

    # Optionally set the JUPYTER_PATH if you want Jupyter to find kernels in custom directory
    jupyter_path = os.path.join(custom_kernel_dir, "share", "jupyter")
    os.environ['JUPYTER_PATH'] = jupyter_path
    print(f"Set JUPYTER_PATH to {jupyter_path}")


def run_notebook_with_kernel(notebook_path, kernel_name):
    """
    Programmatically execute a Jupyter notebook using nbclient with the specified kernel.
    
    :param notebook_path: Path to the Jupyter notebook (.ipynb).
    :param kernel_name: Name of the Jupyter kernel to use (e.g., "my_venv_kernel").
    """
    from nbclient import NotebookClient
    from nbformat import read, write

    # Load the notebook
    with open(notebook_path) as f:
        notebook = read(f, as_version=4)

    # Update the notebook to use the newly registered kernel
    notebook['metadata']['kernelspec'] = {
        "name": kernel_name,
        "display_name": f"Python ({kernel_name})"
    }

    # Set up the notebook client with the desired kernel
    client = NotebookClient(notebook, timeout=600, kernel_name=kernel_name)

    # Execute the notebook
    client.execute()

    # Save the executed notebook
    executed_notebook_path = notebook_path.replace(".ipynb", "_executed.ipynb")
    with open(executed_notebook_path, 'w') as f:
        write(notebook, f)

    print(f"Notebook executed and saved to {executed_notebook_path}")


if __name__ == "__main__":
    create_venv()
