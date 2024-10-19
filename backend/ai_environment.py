from nbformat.v4 import new_notebook, new_code_cell
from nbclient import NotebookClient
import base64
import nbformat

# Step 1: Create a new notebook
nb = new_notebook()

# Step 2: Add code cells to the notebook
nb.cells.append(new_code_cell("%pip install -q pandas numpy matplotlib"))
nb.cells.append(new_code_cell("import pandas as pd"))
nb.cells.append(new_code_cell("import numpy as np"))
nb.cells.append(new_code_cell("import matplotlib.pyplot as plt"))
nb.cells.append(new_code_cell("plt.plot([1, 2, 3, 4], [10, 20, 25, 30])\nplt.savefig('plot.png')\nplt.show()"))
nb.cells.append(new_code_cell("print('Hello, world!')"))
nb.cells.append(new_code_cell("x = 42\nprint(f'The answer is {x}')"))

# Step 3: Create a client to execute the notebook
client = NotebookClient(nb)

# Step 4: Execute the notebook
try:
    client.execute()
except Exception as e:
    print(f"Error executing notebook: {str(e)}")

# Step 5: Save the output to a file
with open("notebook_output.txt", "w") as output_file:
    for cell_index, cell in enumerate(nb.cells):
        if cell.cell_type == 'code':
            for output in cell.outputs:
                try:
                    if 'text' in output:
                        output_file.write(f"Cell {cell_index} output:\n{output['text']}\n")
                    elif 'data' in output:
                        if 'text/plain' in output['data']:
                            output_file.write(f"Cell {cell_index} output:\n{output['data']['text/plain']}\n")
                        if 'image/png' in output['data']:
                            # Decode the base64 image data and save it to a file
                            image_data = base64.b64decode(output['data']['image/png'])
                            image_filename = f'plot_output_cell_{cell_index}.png'
                            with open(image_filename, 'wb') as image_file:
                                image_file.write(image_data)
                            output_file.write(f"Cell {cell_index} image saved as {image_filename}\n")
                except Exception as e:
                    # Log the error with cell index
                    output_file.write(f"Error processing cell {cell_index} output: {str(e)}\n")