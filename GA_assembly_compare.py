"""A tool used to search content of PFD files with steel construction General Arrangement drawings to find if all steel asseblies
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
# window.iconbitmap('compare.ico')
window.resizable(0, 0)

# Define application class
class GaAssemblyCompare:
    def __init__(self, main):
        self.main = main

        # Define list of files to compare
        self.ga_dwgs = []
        self.assy_dwgs = []
        self.log_txt = ""

        # Define main frames grid
        self.frame1 = tk.Frame(self.main, width=100, borderwidth=5)
        self.frame2 = tk.Frame(self.main, width=100, borderwidth=5)
        self.frame3 = tk.Frame(self.main, width=100, borderwidth=5)
        self.frame4 = tk.Frame(self.main, width=100, borderwidth=5)
        self.frame1.grid(row=0, column=0, padx=2)
        self.frame2.grid(row=0, column=1, padx=2)
        self.frame3.grid(row=0, column=2, padx=2, sticky=tk.N)
        self.frame4.grid(row=0, column=3, padx=2)

        # Define assembly and ga drawings listboxes
        self.assy_lstbox = tk.Listbox(self.frame1, width=25, height=30, selectmode=tk.SINGLE)
        self.assy_lstbox.grid(row=1, column=1)
        self.assy_scrollbar = tk.Scrollbar(self.frame1, orient=tk.VERTICAL, command=self.assy_lstbox.yview)
        self.assy_scrollbar.grid(row=1, column=0, sticky=tk.NS)
        self.assy_lstbox.config(yscrollcommand=self.assy_scrollbar)

        self.ga_lstbox = tk.Listbox(self.frame2, width=25, height=30, selectmode=tk.SINGLE)
        self.ga_lstbox.grid(row=1, column=1)
        self.ga_scrollbar = tk.Scrollbar(self.frame2, orient=tk.VERTICAL, command=self.ga_lstbox.yview)
        self.ga_scrollbar.grid(row=1, column=0, sticky=tk.NS)
        self.ga_lstbox.config(yscrollcommand=self.ga_scrollbar)

        # Define buttons
        self.button_add_assy = tk.Button(self.frame1, text='Select assembly drawings', command=self.select_assy_dwgs)
        self.button_add_assy.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

        self.button_add_ga = tk.Button(self.frame2, text='Select GA drawings', command=self.select_ga_dwgs)
        self.button_add_ga.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

        self.button_auto_fill = tk.Button(self.frame3, text='Auto-fill drawings', command=self.auto_select)
        self.button_auto_fill.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=(0,200))

        self.button_compare = tk.Button(self.frame3, text='Compare marks \u279d', command=self.compare_drawings, width=21)
        self.button_compare.grid(row=1, column=0, columnspan=2)

        self.button_save = tk.Button(self.frame3, text='Save log file', command=self.save_log, width=21)
        self.button_save.grid(row=2, column=0, columnspan=2)


        # Define output text widget
        self.output_txt = st.ScrolledText(self.frame4, width=40, height=30)
        self.output_txt.grid(row=1, column=0, sticky=tk.NS)
        self.output_txt.config(background='gray92', wrap='word')
        self.display_message("Select assembly and GA drawings or Auto-fill and select \"Drawings\" folder")
        self.display_message("\n\nAssembly marks printed in white/invisible color will be treated as visible!", clear_box=False)

        # Define drop down menu to select assembly mark numbering pattern
        self.assy_pattern = None

        self.dropdown_label = tk.Label(self.frame3, text='Fabricator:')
        self.dropdown_label.grid(row=3, column=0, sticky=tk.W)

        self.fab_options = ['','ALM', 'BSC', 'TSC', 'CSS', 'other']
        self.fab = tk.StringVar()
        self.fab.set(self.fab_options[0])

        self.dropdown = tk.OptionMenu(self.frame3, self.fab, *self.fab_options, command=self.pattern_changed)
        self.dropdown.grid(row=3, column=1, sticky=tk.E)
    
    # Define button functions
    def display_message(self, message, clear_box=True):
        """Displays given message in textbox"""
        self.output_txt.config(state='normal')
        if clear_box:
            self.output_txt.delete('1.0', tk.END)
        else:
            self.output_txt.insert(tk.INSERT, "\n")
        self.output_txt.insert(tk.INSERT, message)
        self.output_txt.config(state='disabled')


    def pattern_changed(self, *args):
        """Change assembly numbering regex pattern to be used to find assembly marks on GA drawings"""
        if self.fab.get() == '':
            self.assy_pattern = None
        elif self.fab.get() == 'ALM':
            self.display_message('Numbering pattern:\n1B234\nE-3.2.1')
            self.assy_pattern = re.compile(r'(\d+[A-Z]{1,3}\d+)')
            self.ga_pattern = re.compile(r'^E-\d{1,3}\.\d{1,3}\.\d{1,3}$')
        elif self.fab.get() == 'TSC':
            self.display_message('Numbering pattern:\n1234B\nE4321')
            self.assy_pattern = re.compile(r'(\d{1,6}[A-Z]{1,3})')
            self.ga_pattern = re.compile(r'^[A-M]{1,2}\d{1,6}$')
        elif self.fab.get() == 'BSC':
            self.display_message('Numbering pattern:\n[G]1234\nE4321')
            self.assy_pattern = re.compile(r'(G*\d{3,})')
            self.ga_pattern = re.compile(r'^(?!G)[A-Z]{1,2}\d{1,6}$')
        elif self.fab.get() == 'CSS':
            self.display_message('Numbering pattern:\n123B\nE-321')
            self.assy_pattern = re.compile(r'(\d+[A-Z]{1,3})')
            self.ga_pattern = re.compile(r'^[A-Z]{1,2}-\d{1,4}$')
        elif self.fab.get() == 'other':
            self.display_message('Log file will not contain all assembly marks on GA drawings list')
            self.assy_pattern = re.compile(r'(.+)')

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
    
    def auto_select(self):
        """Open a dialog window and select folder containing all drawings. Auto fill assembly drawings and GA drawings lists."""
        if not self.fab.get():
            self.display_message("Select fabricator first.")
            return
        elif self.fab.get() == 'other':
            self.display_message('Auto-fill can not be performed with "other" fabricator selected.')
            return
        else:
            root = tk.Tk()
            root.withdraw()
            dwgs_dir = fd.askdirectory(parent=root, title='Select drawings folder')
            root.destroy()
            # List all files in selected directory
            files_in_dir = list(Path(dwgs_dir).iterdir())
            # Find assembly drawings and GA drawings paths
            assy_paths = sorted([Path(file) for file in files_in_dir if self.assy_pattern.match(Path(file).stem)])
            ga_paths = sorted([Path(file) for file in files_in_dir if self.ga_pattern.match(Path(file).stem)])
            # Empty drawing lists
            self.assy_dwgs.clear()
            self.assy_lstbox.delete(0, tk.END)
            self.ga_dwgs.clear()
            self.ga_lstbox.delete(0, tk.END)
            # Fill drawing lists
            for filepath in assy_paths:
                self.assy_dwgs.append((filepath, Path(filepath).stem))
            self.populate_listbox(self.assy_lstbox, self.assy_dwgs)

            for filepath in ga_paths:
                self.ga_dwgs.append((filepath, Path(filepath).stem))
            self.populate_listbox(self.ga_lstbox, self.ga_dwgs)

            # Display number of drawings found
            self.display_message(f'Assembly drawings found:\t{len(assy_paths)}')
            self.display_message(f'GA drawings found:\t{len(ga_paths)}', clear_box=False)


    def populate_listbox(self, lstbox, files):
        """Populate tkinter listbox with filenames from list"""
        lstbox.delete(0, tk.END)
        for file in files:
            lstbox.insert(tk.END, file[1])
    
    def save_log(self):
        """Save log file with list of missing assembly marks"""
        if self.log_txt:
            save_dir = Path(self.assy_dwgs[0][0]).parents[0]
            file_dir = Path(save_dir, 'log.txt')
            with open(file_dir, 'w') as f:
                f.write(self.log_txt)
            self.display_message(f'\nLog file saved:\n{file_dir}', clear_box=False)
        else:
            self.display_message('Nothing to save.\nRun "Compare marks" first.')

    def compare_drawings(self):
        """Compare content of all selected GA drawings with list of selected assembly drawings"""
        # Clear output text window
        self.output_txt.config(state='normal')
        self.output_txt.delete('1.0', tk.END)

        # Clear out log string
        self.log_txt = ""
        log_string = ""

        # Display warnings
        if not self.assy_dwgs:
            self.display_message('Select assembly drawings!')
            return
        if not self.ga_dwgs:
            self.display_message('Select GA drawings!')
            return
        if not self.assy_pattern:
            self.display_message('Select Fabricator!')
            return

        # Find all assembly marks matching given regex
        assy_on_ga = set()
        for dwg in self.ga_dwgs:
            self.output_txt.insert(tk.INSERT, f'Searching {dwg[1]}...\n')
            reader = PdfReader(dwg[0])
            page = reader.pages[0]
            page_text = page.extract_text()
            page_assy_lst = set(re.findall(self.assy_pattern, page_text))
            assy_on_ga.update(page_assy_lst)

            # Create log file containilg list of all assembly marks on GA drawings
            if self.fab.get() != 'other':
                log_string += f'\t{dwg[1]}:\n'
                for i in sorted(list(page_assy_lst)):
                    log_string += f'{i}\n'

            self.main.update()
            
        # Set of all assembly numbers from given assembly drawings
        assy = {i[1] for i in self.assy_dwgs}

        # Display result messages
        if assy.issubset(assy_on_ga):
            self.log_txt += "OK. All assemblies are shown on GA drawings."
            self.display_message("OK. All assemblies are shown on GA drawings.")
        else:
            assy_not_shown = sorted(list(assy - assy_on_ga))
            self.output_txt.delete('1.0', tk.END)
            self.output_txt.insert(tk.INSERT, "Missing assembly marks on GA drawings:")
            self.log_txt += "\tMissing assembly marks on GA drawings:\n"
            for i in assy_not_shown:
                self.output_txt.insert(tk.INSERT, f'\n{i}')
                self.log_txt += f'{i}\n'
        self.output_txt.config(state='disabled')

        # Add list of assembly marks on GA drawings to log file
        if self.fab.get() != 'other':
            self.log_txt += "\nAssembly marks shown on GA drawings:\n"
            self.log_txt += log_string

# Create app object
app = GaAssemblyCompare(window)
window.mainloop()
