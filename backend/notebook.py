import nbformat
from nbformat.v4 import new_notebook, new_code_cell
from nbclient import NotebookClient
from cwd import cwd
import base64
import sys
import subprocess
import base_log

log = base_log.BASE_LOG.getChild(__name__)
"""
A class to represent a notebook.
Cell 0 is reserved for package installations.
"""
class Notebook:
    def __init__(self, agent_id):
        self.notebook = new_notebook()
        self.client = NotebookClient(self.notebook)
        self.names = {}
        self.agent_id = agent_id
        self.create_cell("pip package install", "")

    def create_cell(self, cell_name, cell_content):
        """Create a new cell and add it to the python notebook. The cell is added at the end of the notebook. cell_name should be a short, descriptive name for the cell.

        Args:
            cell_name (string): The name of the cell. Use this to reference the cell in the future.
            cell_content (string): The contents of the cell, in LF format.
        """
        cell_content = self.unescape_string(cell_content)
        cell = new_code_cell(cell_content)
        self.notebook.cells.append(cell)
        self.names[len(self.notebook.cells) - 2] = cell_name
        log.debug(f"{self.agent_id}:Cell created: {len(self.notebook.cells) - 2} {cell_name}\n{cell_content}")
        return f"Cell created at index {len(self.notebook.cells) - 2}."

    def insert_cell(self, cell_index, cell_name, cell_content):
        """Insert a new cell at the specified index. cell_name should be a short, descriptive name for the cell.

        Args:
            cell_index (integer): The index to insert the cell at.
            cell_name (string): The name of the cell. Use this to reference the cell in the future.
            cell_content (string): The contents of the cell, in LF format.
        """
        cell_index = cell_index + 1
        if cell_index < 0:
            log.warning(f"{self.agent_id}:Invalid cell index.")
            return "Invalid cell index."
        if cell_index > len(self.notebook.cells):
            log.warning(f"{self.agent_id}:Cell index out of range.")
            return "Cell index out of range."
        
        cell_content = self.unescape_string(cell_content)
        cell = new_code_cell(cell_content)
        self.notebook.cells.insert(cell_index, cell)
        self.names[cell_index - 1] = cell_name
        log.debug(f"{self.agent_id}:Cell inserted: {cell_index - 1} {cell_name}\n{cell_content}")
        return f"Cell inserted at index {cell_index - 1}."
    
    def delete_cell(self, cell_index):
        """Delete a cell at the specified index.

        Args:
            cell_index (integer): The index of the cell to delete.
        """
        cell_index = cell_index + 1
        if cell_index < 0:
            return "Invalid cell index."
        if cell_index >= len(self.notebook.cells):
            return "Cell index out of range."
        
        name = self.names[cell_index - 1]
        del self.notebook.cells[cell_index]
        del self.names[cell_index - 1]
        log.debug(f"{self.agent_id}:Cell deleted: {cell_index - 1} {name}")
        return f"Cell {cell_index-1} deleted successfully."

    def get_cell_content(self, cell_index):
        """Get the content of a cell.

        Args:
            cell_index (integer): The index of the cell.

        Returns:
            str: The content of the cell.
        """
        cell_index = cell_index + 1
        if cell_index < 0 or cell_index >= len(self.notebook.cells):
            log.warning(f"{self.agent_id}:Cell index out of range.")
            return "Cell index out of range."
        
        log.debug(f"{self.agent_id}:Getting content of cell: {cell_index - 1} {self.names[cell_index - 1]}")
        return self.names[cell_index - 1], self.notebook.cells[cell_index].source
    
    def edit_cell(self, cell_index, new_content):
        """Replace the contents of a cell with new content.

        Args:
            cell_index (integer): The index of the cell to edit.
            new_content (string): The new content to replace the cell with, in LF format.
        """
        cell_index = cell_index + 1
        if cell_index < 0 or cell_index >= len(self.notebook.cells):
            return "Cell index out of range."
        
        new_content = self.unescape_string(new_content)
        self.notebook.cells[cell_index].source = new_content
        log.debug(f"{self.agent_id}:Cell edited: {cell_index - 1} {self.names[cell_index - 1]}\n{new_content}")
        return f"Cell {cell_index-1} edited successfully."
    
    def execute_all_cells(self):
        """Execute the notebook. Return the output of each cell.

        Returns:
            list: The output of each cell.
        """
        np_outputs = []
        try:
            self.client.execute()
        except Exception as e:
            log.info(f"{self.agent_id}:Error executing notebook: {e}")
            # np_outputs.append({"error": f"An error occurred while executing the notebook. Files may not have been saved. {e}"})
            pass


        # TODO: support multiple output images
        for cell_index, cell in enumerate(self.notebook.cells[1:]):
            if cell.cell_type == 'code':
                outputs = []
                for output in cell.outputs:
                    if 'ename' in output:
                        outputs.append("Error - " + output['ename'] + (":" + output['evalue'] if 'evalue' in output else "") + (":" + str(output['traceback']) if 'traceback' in output else ""))
                    if 'text' in output:
                        outputs.append(output['text'])
                    if 'data' in output:
                        if 'text/plain' in output['data']:
                            outputs.append(output['data']['text/plain'])
                        if 'image/png' in output['data']:
                            image_data = base64.b64decode(output['data']['image/png'])
                            with open(f'cell_{cell_index}.png', 'wb') as image_file:
                                image_file.write(image_data)
                            outputs.append(f'image/png saved as cell_{cell_index}.png')
                np_outputs.append({f"{cell_index} - {self.names[cell_index]}":outputs})
        log.debug(f"{self.agent_id}:Executed all cells. Outputs -> \n{np_outputs}")
        return np_outputs

    def install_package(self, package_name):
        """Install the specified package using pip.

        Args:
            package_name (string): The name of the package to install.
        """
        # TODO: error catching here
        content = self.get_cell_content(-1)[1]
        if not content:
            content = f"%pip -q install {package_name}"
        else:
            content += f"\n%pip -q install {package_name}"
        self.edit_cell(-1, content)
        output = self.execute_all_cells()
        log.debug(f"{self.agent_id}:Package installed: {package_name}")
        return "Package installed successfully."
    
    def save(self, save_path):
        with open(save_path, 'w', encoding='utf-8') as f:
            nbformat.write(self.notebook, f)

    def unescape_string(self, string):
        return bytes(string, "utf-8").decode("unicode_escape")