from notebook import Notebook
import json

class NotebookWrapper:
    def __init__(self, notebook: Notebook):
        self.notebook = notebook
    
    def create_cell(self, args):
        args = json.loads(args)
        output = self.notebook.create_cell(args['cell_name'], args['cell_content'])
        return output
    
    def edit_cell(self, args):
        args = json.loads(args)
        output = self.notebook.edit_cell(args['cell_index'], args['new_content'])
        return output

    def get_cell_content(self, args):
        args = json.loads(args)
        output = self.notebook.get_cell_content(args['cell_index'])
        return str({'name': output[0], 'content': output[1]})

    def delete_cell(self, args):
        args = json.loads(args)
        output = self.notebook.delete_cell(args['cell_index'])
        return output
    
    def insert_cell(self, args):
        args = json.loads(args)
        output = self.notebook.insert_cell(args['cell_index'], args['cell_name'], args['cell_content'])
        return output
    
    def execute_all_cells(self, args):
        output = self.notebook.execute_all_cells()
        return str(output)
    
    def install_package(self, args):
        args = json.loads(args)
        output = self.notebook.install_package(args['package_name'])
        return output
    
    def save(self, save_path):
        return self.notebook.save(save_path)
    