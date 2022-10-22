"""A tool used to search content of steel construction General Arrangement PDF drawings to find if all steel asseblies are listed"""

from PyPDF2 import PdfReader
from pathlib import Path
import re
import tkinter as tk
import tkinter.filedialog as fd


# Define display window
window = tk.Tk()
window.title('GA - Assembly compare')


# Define application class
class GAAssemblyCompare:
    def __init__(self, main):

        # Define list of files to compare
        self.ga_dwgs = []
        self.assy_dwgs = []

        # Define assembly numbering pattern
        self.pattern = re.compile(r'^\d+[A-Z]{1,3}\d+$')

        # Define main frames grid
        self.frame1 = tk.Frame(main, width=100, borderwidth=5)
        self.frame2 = tk.Frame(main, width=100, borderwidth=5)
        self.frame3 = tk.Frame(main, width=100, borderwidth=5)
        self.frame1.grid(row=0, column=0)
        self.frame2.grid(row=0, column=1)
        self.frame3.grid(row=0, column=2)

        # Define assembly and ga drawings listboxes
        self.assy_lstbox = tk.Listbox(self.frame1, width=30, height=30, selectmode=tk.EXTENDED)
        self.assy_lstbox.grid(row=1, column=1)
        self.assy_scrollbar = tk.Scrollbar(self.frame1, orient=tk.VERTICAL, command=self.assy_lstbox.yview)
        self.assy_scrollbar.grid(row=1, column=0, sticky=tk.NS)
        self.assy_lstbox.config(yscrollcommand=self.assy_scrollbar)

        self.ga_lstbox = tk.Listbox(self.frame2, width=30, height=30, selectmode=tk.EXTENDED)
        self.ga_lstbox.grid(row=1, column=1)
        self.ga_scrollbar = tk.Scrollbar(self.frame2, orient=tk.VERTICAL, command=self.ga_lstbox.yview)
        self.ga_scrollbar.grid(row=1, column=0, sticky=tk.NS)
        self.ga_lstbox.config(yscrollcommand=self.ga_scrollbar)

        # Define test buttons
        self.button_test1 = tk.Button(self.frame3, text='print_assy_dwgs', command=self.print_assy_dwgs)
        self.button_test1.grid(row=0, column=0)
    
        self.button_test2 = tk.Button(self.frame3, text='print_ga_dwgs', command=self.print_ga_dwgs)
        self.button_test2.grid(row=1, column=0)

        self.button_test2 = tk.Button(self.frame3, text='compare dwgs', command=self.compare_drawings)
        self.button_test2.grid(row=2, column=0)

        # Define buttons
        self.button_add_assy = tk.Button(self.frame1, text='Select assembly drawings', command=self.select_assy_dwgs)
        self.button_add_assy.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

        self.button_add_ga = tk.Button(self.frame2, text='Select GA drawings', command=self.select_ga_dwgs)
        self.button_add_ga.grid(row=0, column=0, columnspan=2, sticky=tk.EW)
    
    # Test functions
    def print_assy_dwgs(self):
        for dwg in self.assy_dwgs:
            print(dwg)

    def print_ga_dwgs(self):
        for dwg in self.ga_dwgs:
            print(dwg)
    

    # Define button functions

    def select_assy_dwgs(self):
        """Empty assembly drawings list and listbox and populate with new selected files"""
        self.assy_dwgs.clear()
        self.assy_lstbox.delete(0, tk.END)

        selected_files = self.select_files('Select assembly drawings')
        for filepath in selected_files:
            self.assy_dwgs.append((filepath, Path(filepath).stem))
        self.populate_listbox(self.assy_lstbox, self.assy_dwgs)

    def select_ga_dwgs(self):
        """Empty GA drawings list and listbox and populate with new selected files"""
        self.ga_dwgs.clear()
        self.ga_lstbox.delete(0, tk.END)

        selected_files = self.select_files('Select GA drawings')
        for filepath in selected_files:
            self.ga_dwgs.append((filepath, Path(filepath).stem))
        self.populate_listbox(self.ga_lstbox, self.ga_dwgs)
    
    def select_files(self, msg):
        """Open a dialog window and select PDF files"""
        root = tk.Tk()
        root.withdraw()
        selected_files = fd.askopenfilenames(parent=root, title=msg, filetypes=[('PDF', '.pdf')])
        root.destroy()
        return selected_files

    def populate_listbox(self, lstbox, files):
        """Populate tkinter listbox with filenames from list"""
        lstbox.delete(0, tk.END)
        for file in files:
            lstbox.insert(tk.END, file[1])
    
    def compare_drawings(self):
        assy_on_ga = set()
        for dwg in self.ga_dwgs:
            reader = PdfReader(dwg[0])
            page = reader.pages[0]
            print(f'Searching {dwg[1]}')
            page_text = page.extract_text()
            page_lst = page_text.splitlines()
            page_assy_lst = {i for i in page_lst if self.pattern.match(i)}
            assy_on_ga.update(page_assy_lst)
        print(assy_on_ga)

        assy = {i[1] for i in self.assy_dwgs}
        print(assy)

        print(assy.issubset(assy_on_ga))


# Create app object
app = GAAssemblyCompare(window)
window.mainloop()
