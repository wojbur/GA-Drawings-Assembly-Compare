"""A tool used to search content of steel construction General Arrangement PDF drawings to find if all steel asseblies are listed"""

from PyPDF2 import PdfReader
from pathlib import Path
import re
import tkinter as tk
import tkinter.filedialog as fd

root = tk.Tk()
root.withdraw()
ga_drawings = fd.askopenfilenames(parent=root, title='select GA drawings', filetypes=[('PDF', '.pdf')])

assy_on_ga = set()
pat = re.compile(r'^\d+[A-Z]{1,3}\d+$')

for drawing in ga_drawings:
    reader = PdfReader(drawing)
    page = reader.pages[0]
    page_text = page.extract_text()
    print(f'searching {drawing}')
    page_lst = page_text.splitlines()
    page_assembly_lst = {i for i in page_lst if pat.match(i)}
    assy_on_ga.update(page_assembly_lst)


assy_dwgs = fd.askopenfilenames(parent=root, title='select assembly drawings drawings', filetypes=[('PDF', '.pdf')])
assy_nums = {Path(file).stem for file in assy_dwgs}

print(assy_on_ga)
print(assy_nums)

print(assy_nums.issubset(assy_on_ga))



