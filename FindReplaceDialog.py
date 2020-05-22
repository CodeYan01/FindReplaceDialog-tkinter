from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import showinfo

class Test_GUI(Frame):
    def __init__(self, master=None, *args, **kw):
        super().__init__(master, *args, **kw)
        self.master = master
        self.columnconfigure(0, weight=1)

        self.text = Text(self, font=("Consolas", 11), borderwidth=2, relief=GROOVE)
        self.text.config(inactiveselectbackground=self.text.cget("selectbackground")) # it defaults to none, becomes a problem when not in focus
        self.text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.editButton = Button(self, text="Find and Replace", command=self.openFindReplaceDialog)
        self.editButton.grid(row=1, column=0, pady=5)

        self.bind_all("<Control-f>", self.openFindReplaceDialog)

    def openFindReplaceDialog(self, e=None):
        if getattr(self, "findReplace", None): # Check if `self.findReplace()` exists
            self.findReplace.deiconify()
        else:
            self.findReplace = FindReplaceDialog(self, self.text, True)

class FindReplaceDialog(Toplevel):
    def __init__(self, master, textWidget, withdrawInsteadOfDestroy=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.transient(master)
        self.resizable(False, False)

        frame = FindReplaceFrame(self, textWidget)
        frame.pack(fill="both", padx=10, pady=10)

        x = master.winfo_rootx() + (master.winfo_width()/2) - (self.winfo_reqwidth()/2)
        y = master.winfo_rooty() + (master.winfo_height()/2) - (self.winfo_reqheight()/2)
        self.geometry(f'+{int(x)}+{int(y)}')

        if withdrawInsteadOfDestroy: # Set this to True if you want to reuse the window.
            self.protocol("WM_DELETE_WINDOW", self.withdraw)
            # use `self.deiconify()` to show the dialog again
        

class FindReplaceFrame(Frame): # You can use the frame directly instead of creating a Toplevel window
    def __init__(self, master, textWidget, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.textWidget = textWidget
        self.findStartPos = 1.0

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, pad=8)
        self.rowconfigure(1, pad=8)

        Label(self, text="Find: ").grid(row=0, column=0, sticky="nw")
        self.findEntry = Entry(self)
        self.findEntry.grid(row=0, column=1, sticky="new")
        self.findEntry.focus()

        Label(self, text="Replace: ").grid(row=1, column=0, sticky="nw")
        self.replaceEntry = Entry(self)
        self.replaceEntry.grid(row=1, column=1, sticky="new")

        buttonFrame = Frame(self)
        buttonFrame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.findNextButton = Button(buttonFrame, text="Find Next", command=self.findNext)
        self.findNextButton.grid(row=0, column=0, padx=(0, 5))
        self.replaceButton = Button(buttonFrame, text="Replace", command=self.replace)
        self.replaceButton.grid(row=0, column=1, padx=(0, 5))
        self.replaceAllButton = Button(buttonFrame, text="Replace All", command=self.replaceAll)
        self.replaceAllButton.grid(row=0, column=2)

        optionsFrame = Frame(self)
        optionsFrame.grid(row=3, column=0, sticky="nsew")
        self.matchCaseVar = BooleanVar(self, True)
        self.matchCaseCheckbutton = Checkbutton(optionsFrame, text="Match Case", variable=self.matchCaseVar)
        self.matchCaseCheckbutton.grid(row=0, column=0, sticky="nw")
        

    def findNext(self):
        """
            Finds the given search term and selects the text if found.
        """
        key = self.findEntry.get()
        pos = self.textWidget.search(key, INSERT, nocase=not self.matchCaseVar.get())
        if pos:
            endIndex = f'{pos}+{len(key)}c'
            if self.textWidget.tag_ranges(SEL): 
                self.textWidget.tag_remove(SEL, SEL_FIRST, SEL_LAST) # Allow only one selection
            self.textWidget.tag_add(SEL, pos, endIndex)
            self.textWidget.mark_set(INSERT, endIndex)
            self.textWidget.see(endIndex)

    def replace(self):
        """
            If there is a selection, checks if it matches key. If it does, this replaces the given key with the replacement string. Otherwise, call self.findNext()
        """
        key = self.findEntry.get()
        repl = self.replaceEntry.get()
        flags = 0

        selRange = self.textWidget.tag_ranges(SEL)
        if selRange:
            selection = self.textWidget.get(selRange[0], selRange[1])
            if not self.matchCaseVar.get():
                key = key.lower()
                selection = selection.lower()
            if key == selection:
                self.textWidget.delete(selRange[0], selRange[1])
                self.textWidget.insert(selRange[0], repl)
        self.findNext()

    def replaceAll(self):
        """
            Replaces all occurences of `key` with `repl`.
        """
        start = "1.0"
        key = self.findEntry.get()
        repl = self.replaceEntry.get()
        count = 0
        
        while True:
            pos = self.textWidget.search(key, start, "end")
            if pos:
                self.textWidget.delete(pos, f"{pos}+{len(key)}c")
                self.textWidget.insert(pos, repl)
                start = f"{pos}+{len(repl)}c"
                count += 1
            else:
                showinfo("", f"Replaced {count} occurences.")
                break
            

if __name__ == "__main__":
    root = Tk()
    frame = Test_GUI(root)
    frame.pack(fill="both", expand=True)
    root.mainloop()