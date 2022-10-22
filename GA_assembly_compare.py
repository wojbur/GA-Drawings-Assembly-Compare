"""A tool used to search content of PFD files of steel construction General Arrangement drawings to find if all steel asseblies
have corresponding assembly marks. The tool reads all text from GA drawings, searches for assembly marks and compares the results
with list of given assembly drawings"""


from PyPDF2 import PdfReader
from pathlib import Path
import re
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.scrolledtext as st


# Set display window
window = tk.Tk()
window.title('GA - Assembly compare')
window.iconbitmap('compare.ico')
window.resizable(0, 0)

# Define application class
class GaAssemblyCompare:
    def __init__(self, main):
        self.main = main

        # Define list of files to compare
        self.ga_dwgs = []
        self.assy_dwgs = []

        # Define main frames grid
        self.frame1 = tk.Frame(self.main, width=100, borderwidth=5)
        self.frame2 = tk.Frame(self.main, width=100, borderwidth=5)
        self.frame3 = tk.Frame(self.main, width=100, borderwidth=5)
        self.frame4 = tk.Frame(self.main, width=100, borderwidth=5)
        self.frame1.grid(row=0, column=0, padx=2)
        self.frame2.grid(row=0, column=1, padx=2)
        self.frame3.grid(row=0, column=2, padx=2)
        self.frame4.grid(row=0, column=3, padx=2)

        # Define assembly and ga drawings listboxes
        self.assy_lstbox = tk.Listbox(self.frame1, width=30, height=30, selectmode=tk.SINGLE)
        self.assy_lstbox.grid(row=1, column=1)
        self.assy_scrollbar = tk.Scrollbar(self.frame1, orient=tk.VERTICAL, command=self.assy_lstbox.yview)
        self.assy_scrollbar.grid(row=1, column=0, sticky=tk.NS)
        self.assy_lstbox.config(yscrollcommand=self.assy_scrollbar)

        self.ga_lstbox = tk.Listbox(self.frame2, width=30, height=30, selectmode=tk.SINGLE)
        self.ga_lstbox.grid(row=1, column=1)
        self.ga_scrollbar = tk.Scrollbar(self.frame2, orient=tk.VERTICAL, command=self.ga_lstbox.yview)
        self.ga_scrollbar.grid(row=1, column=0, sticky=tk.NS)
        self.ga_lstbox.config(yscrollcommand=self.ga_scrollbar)

        # Define buttons
        self.button_add_assy = tk.Button(self.frame1, text='Select assembly drawings', command=self.select_assy_dwgs)
        self.button_add_assy.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

        self.button_add_ga = tk.Button(self.frame2, text='Select GA drawings', command=self.select_ga_dwgs)
        self.button_add_ga.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

        self.button_compare = tk.Button(self.frame3, text='Compare marks \u279d', command=self.compare_drawings, width=21)
        self.button_compare.grid(row=0, column=0, columnspan=2)

        # Define output text widget
        self.output_txt = st.ScrolledText(self.frame4, width=25, height=30)
        self.output_txt.grid(row=1, column=0, sticky=tk.NS)
        self.output_txt.insert(tk.INSERT, "Assembly marks printed in white/invisible color will be treated as visible!")
        self.output_txt.config(background='gray92', state='disabled', wrap='word')

        # Define drop down menu to select assembly mark numbering pattern
        self.pattern = None

        self.dropdown_label = tk.Label(self.frame3, text='Fabricator:')
        self.dropdown_label.grid(row=1, column=0, sticky=tk.W)

        self.fab_options = ['','ALM', 'BSC', 'TSC', 'CSS', 'other']
        self.fab = tk.StringVar()
        self.fab.set(self.fab_options[0])

        self.dropdown = tk.OptionMenu(self.frame3, self.fab, *self.fab_options, command=self.pattern_changed)
        self.dropdown.grid(row=1, column=1, sticky=tk.E)

        self.pattern_label = tk.Label(self.frame3)
        self.pattern_label.grid(row=2, column=0, columnspan=2, sticky=tk.EW)
    
    # Define button functions

    def pattern_changed(self, *args):
        """Change assembly numbering regex pattern to be used to find assembly marks on GA drawings"""
        if self.fab.get() == '':
            self.pattern_label['text'] = ''
            self.pattern = None
        elif self.fab.get() == 'ALM':
            self.pattern_label['text'] = 'num pattern: 1B234'
            self.pattern = re.compile(r'^\d+[A-Z]{1,3}\d+$')
        elif self.fab.get() == 'TSC':
            self.pattern_label['text'] = 'num pattern: 1234B'
            self.pattern = re.compile(r'^\d{3,5}[A-Z]{1,3}$')
        elif self.fab.get() == 'BSC':
            self.pattern_label['text'] = 'num pattern: [G]1234'
            self.pattern = re.compile(r'^G*\d{3,}$')
        elif self.fab.get() == 'CSS':
            self.pattern_label['text'] = 'num pattern: 123B'
            self.pattern = re.compile(r'^\d+[A-Z]{1,3}$')
        elif self.fab.get() == 'other':
            self.pattern_label['text'] = 'might find false positives'
            self.pattern = re.compile(r'^.+$')

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
        """Compare content of all selected GA drawings with list of selected assembly drawings"""

        # Clear output text window
        self.output_txt.config(state='normal')
        self.output_txt.delete('1.0', tk.END)

        # Display warnings
        if not self.assy_dwgs:
            self.output_txt.insert(tk.INSERT, 'Select assembly drawings!')
            self.output_txt.config(state='disabled')
            return
        if not self.ga_dwgs:
            self.output_txt.insert(tk.INSERT, 'Select GA drawings!')
            self.output_txt.config(state='disabled')
            return
        if not self.pattern:
            self.output_txt.insert(tk.INSERT, 'Select Fabricator!')
            self.output_txt.config(state='disabled')
            return

        # Find all assembly marks matching given regex
        assy_on_ga = set()
        for dwg in self.ga_dwgs:
            reader = PdfReader(dwg[0])
            page = reader.pages[0]
            self.output_txt.insert(tk.INSERT, f'Searching {dwg[1]}...\n')
            page_text = page.extract_text()
            page_lst = page_text.splitlines()
            page_assy_lst = {i for i in page_lst if self.pattern.match(i)}
            assy_on_ga.update(page_assy_lst)
            self.main.update()

        # Set of all assembly numbers from given assembly drawings
        assy = {i[1] for i in self.assy_dwgs}

        # Display result messages
        if assy.issubset(assy_on_ga):
            self.output_txt.delete('1.0', tk.END)
            self.output_txt.insert(tk.INSERT, "OK. All assemblies are shown on GA drawings.") 
        else:
            assy_not_shown = sorted(list(assy - assy_on_ga))
            self.output_txt.delete('1.0', tk.END)
            self.output_txt.insert(tk.INSERT, "Missing assembly marks on GA drawings:")
            for i in assy_not_shown:
                self.output_txt.insert(tk.INSERT, f'\n{i}')
        self.output_txt.config(state='disabled')

# Create app object
app = GaAssemblyCompare(window)
window.mainloop()
