import Tkinter as tk
import ttk
import ScrolledText


class OptionsDialog(tk.Toplevel):
    def __init__(self, config, console, parent, action):
        """
        Init
        :param config: dict
        :param console: logger
        :param parent: Tk object
        :return:
        """
        tk.Toplevel.__init__(self, parent)
        #self.transient(parent) # so that this dialog doesn't show up as a new icon in the window manager
        #
        self.config = config
        self.console = console
        self.parent = parent
        self.action = action
        #
        self.resizable(0,0)
        self.title("Settings")
        #
        self.win = tk.Frame(self)
        self.initial_focus = self.body(self.win)
        self.win.pack()
        #
        self.gui()
        #
        self.grab_set() # prevent focus on the parent
        if not self.initial_focus:
            # bring into focus immediately
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        #
        self.initial_focus.focus_set()
        self.load_config()
        self.wait_window(self)

    def gui(self):
        """
        Main gui constructor
        :return: None
        """
        #self.bind("<Return>", self.on_ok) # interfere with email body
        self.bind("<Escape>", self.on_cancel)
        #self.win.pack()

        self.panel_navigation = self.create_panel_navigation(self.win)
        self.panel_navigation.grid(row=0, column=0, rowspan=2, sticky="NS")
        # http://stackoverflow.com/questions/25940217/python-getting-started-with-tk-widget-not-resizing-on-grid
        self.panel_navigation.rowconfigure(0, weight=1)
        self.panel_navigation.columnconfigure(0, weight=1)

        self.frame_ar = self.create_frame_ar(self.win)
        #self.frame_ar.grid(row=0, column=1,sticky="NW", padx=5, pady=5)

        self.frame_email = self.create_frame_email(self.win)
        self.frame_email.grid(row=0, column=1,sticky="NW", padx=5, pady=5)

    def load_config(self):
        """
        Load the configurations into the Tk objects
        :return: None
        """
        self.entry_server_host.insert(tk.INSERT, self.config.dict_config["email"]["relay_server_host"])
        self.entry_server_port.insert(tk.INSERT, self.config.dict_config["email"]["relay_server_port"])
        self.entry_from.insert(tk.INSERT, self.config.dict_config["email"]["email_from"])
        self.text_recipients.insert(tk.INSERT, self.config.dict_config["email"]["recipients"])
        #
        self.entry_enabled_subject.insert(tk.INSERT, self.config.dict_config["email"]["ar_enabled_subject"])
        self.text_enabled_body.insert(tk.INSERT, self.config.dict_config["email"]["ar_enabled_body"])
        #
        self.entry_disabled_subject.insert(tk.INSERT, self.config.dict_config["email"]["ar_disabled_subject"])
        self.text_disabled_body.insert(tk.INSERT, self.config.dict_config["email"]["ar_disabled_body"])
        #
        self.text_ips.insert(tk.INSERT, self.config.dict_config["access_restriction"]["ips"])
        self.entry_url.insert(tk.INSERT, self.config.dict_config["access_restriction"]["ar_url"])

    def create_panel_navigation(self, frame_parent):
        """
        Create the configuration left panel
        :param frame_parent: tk.Frame
        :return: ttk.Frame
        """
        panel = ttk.Frame(frame_parent)

        tree = ttk.Treeview(panel, selectmode="browse") # "browse" mode limits to one selection only
        tree.heading("#0", text="Category")
        tree.column("#0", width=130)
        #tree.bind("<ButtonRelease-1>", self.on_category_select)  # left-button release
        tree.bind("<<TreeviewSelect>>", self.on_category_select)
        #
        tree.insert('', tk.END, text="Email")
        tree.insert('', tk.END, text="Access Restriction")
        tree.selection_set(tree.get_children()[0]) # select the first item on init
        tree.grid(sticky="NS")

        # http://stackoverflow.com/questions/25940217/python-getting-started-with-tk-widget-not-resizing-on-grid
        # or you can just do this: tree.pack(fill=tk.BOTH, expand=1)
        tree.rowconfigure(0, weight=1)
        tree.columnconfigure(0, weight=1)
        return panel

    def create_frame_ar(self, frame_parent):
        """
        Create Access Restriction configuration window
        :param frame_parent:
        :return:
        """
        frame = ttk.LabelFrame(frame_parent, text="Access Restriction Settings")
        # master width control
        ttk.Label(frame, width=70).grid()
        #
        label_ips = ttk.Label(frame, text="Exempted Hosts/IPs (newline delimited)")
        label_ips.grid(row=0, column=0, sticky="NW")
        #
        self.text_ips =ScrolledText.ScrolledText(frame, height=5, width=1)
        self.text_ips.grid(row=1, column=0, sticky='WE')
        #
        label_url = ttk.Label(frame, text="Access Restricted URL")
        label_url.grid(row=2, column=0, sticky="WE")
        #
        self.entry_url = ttk.Entry(frame)
        self.entry_url.grid(row=3, column=0, sticky="WE")

        frame_control = self.create_frame_control()
        frame_control.grid(row=1, column=1, sticky="SE")
        return frame

    def create_frame_email(self, frame_parent):
        """
        Create Email configuration window
        :param frame_parent:
        :return:
        """
        frame = ttk.LabelFrame(frame_parent, text="Email Settings")
        # master width control

        label_server_host = ttk.Label(frame, text="Relay Server Host:")
        label_server_host.grid(row=0, column=0, sticky="W")
        #
        self.entry_server_host = ttk.Entry(frame)
        self.entry_server_host.grid(row=0, column=1, sticky="WE")

        label_server_port = ttk.Label(frame, text="Relay Server Port:")
        label_server_port.grid(row=1, column=0, sticky="W")
        #
        self.entry_server_port = ttk.Entry(frame)
        self.entry_server_port.grid(row=1, column=1, sticky="WE")

        label_from = ttk.Label(frame, text="Email From:")
        label_from.grid(row=2, column=0, sticky="W")
        #
        self.entry_from = ttk.Entry(frame)
        self.entry_from.grid(row=2, column=1, sticky="WE")

        label_recipients = ttk.Label(frame, text="Email Recipients (newline delimited):")
        label_recipients.grid(row=3, column=0, columnspan=2, sticky="NW")
        #
        self.text_recipients = ScrolledText.ScrolledText(frame, wrap=tk.WORD, height=5, width=1)
        self.text_recipients.grid(row=4, column=0, columnspan=2, sticky='WE')

        frame_ar_state = ttk.LabelFrame(frame, text="Access Restriction State")
        frame_ar_state.grid(row=5, column=0, columnspan=2, sticky="W")

        ar_modes = [
            # text, mode, column
            ("Enabled", True, 0),
            ("Disabled", False, 1)
            ]

        self.ar_status = tk.StringVar()
        self.ar_status.set(True)

        for (text, mode, column) in ar_modes:
            _rb = ttk.Radiobutton(frame_ar_state, text=text, variable=self.ar_status,
                                  value=mode, command=self.on_ar_status)
            _rb.grid(row=0, column=column,)
        #
        label_subject = ttk.Label(frame, text="Email Subject:")
        label_subject.grid(row=6, column=0, sticky="W")

        self.entry_disabled_subject = ttk.Entry(frame)
        #self.entry_disabled_subject.grid(row=6, column=1, sticky="WE")

        label_body = ttk.Label(frame, text="Email Body:")
        label_body.grid(row=7, column=0, columnspan=2, sticky="NW")       #

        self.text_disabled_body = ScrolledText.ScrolledText(frame, wrap=tk.WORD, height=5, width=1)
        #self.text_disabled_body.grid(row=8, column=0, columnspan=2, sticky='WE')

        #########

        self.entry_enabled_subject = ttk.Entry(frame)
        self.entry_enabled_subject.grid(row=6, column=1, sticky="WE")

        self.text_enabled_body = ScrolledText.ScrolledText(frame, wrap=tk.WORD, height=5, width=1)
        self.text_enabled_body.grid(row=8, column=0, columnspan=2, sticky='WE')

        ######

        _width_control_1 = ttk.Label(frame, width=17)
        _width_control_1.grid(row=0, column=0)
        _width_control_1.lower() # hide it
        _width_control_2 = ttk.Label(frame, width=90)
        _width_control_2.grid(row=0, column=1)
        _width_control_2.lower() # hide it
        #
        frame_control = self.create_frame_control()
        frame_control.grid(row=1, column=1, sticky="SE")
        return frame

    def create_frame_control(self):
        frame = ttk.Frame(self.win)
        ttk.Button(frame, text="OK", command=self.on_ok).grid(row=0, column=0, padx=5, pady=10)
        ttk.Button(frame, text="Cancel", command=self.on_cancel).grid(row=0, column=1, padx=5, pady=10)
        return frame

    def on_category_select(self, event):
        widget = event.widget
        str_item = widget.item(widget.selection()[0], "text")
        self.console.debug('Selected: "{}"'.format(str_item))
        if str_item == "Email":
            self.frame_ar.grid_forget()
            self.frame_email.grid(row=0, column=1, sticky="NW", padx=5, pady=5)
            #self.panel_navigation.grid_configure(sticky="NS")
        elif str_item == "Access Restriction":
            self.frame_email.grid_forget()
            self.frame_ar.grid(row=0, column=1, sticky="NW", padx=5, pady=5)

    def body(self, master):
        """
        TK related... not sure what this is for... :/
        :param master:
        :return: None
        """
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        pass

    def on_save(self):
        """
        Action for saving the configuration, not the file (not called directly but from the OK button)
        :param event:
        :return: None
        """
        #new_config = ConfigParser.RawConfigParser()
        cur_config = self.config.dict_config
        #
        # update the dict_config
        cur_config["access_restriction"]["ips"] = self.text_ips.get(1.0, tk.END).strip()
        cur_config["access_restriction"]["ar_url"] = self.entry_url.get().strip()
        #
        cur_config["email"]["relay_server_host"] = self.entry_server_host.get().strip()
        cur_config["email"]["relay_server_port"] = self.entry_server_port.get().strip()
        cur_config["email"]["email_from"] = self.entry_from.get().strip()
        cur_config["email"]["recipients"] = self.text_recipients.get(1.0, tk.END).strip()
        cur_config["email"]["ar_enabled_subject"] = self.entry_enabled_subject.get().strip()
        cur_config["email"]["ar_enabled_body"] = self.text_enabled_body.get(1.0, tk.END).strip()
        cur_config["email"]["ar_disabled_subject"] = self.entry_disabled_subject.get()
        cur_config["email"]["ar_disabled_body"] = self.text_disabled_body.get(1.0, tk.END).strip()

        #self.action.save_config()
        # # sync dict_config to the gui
        # for section in self.config.dict_config:
        #     new_config.add_section(section)
        #     for item in self.config.dict_config[section]:
        #         new_config.set(section, item, self.config.dict_config[section][item])
        # #
        # # saving to a file
        # with open(self.config.file_path, 'w') as newconfigfile:
        #     new_config.write(newconfigfile)
        #
        # # mbox.showinfo("Information",
        # #               "Current configuration has been successfully saved to '%s'" % os.path.basename(self.configfile))
        # self.console.debug("Configuration has been saved to '%s'" % self.config.file_path)

    def on_ok(self, event=None):
        """
        Action for the OK button
        :param event:
        :return: None
        """
        self.on_save()
        # if not self.validate():
        #     self.initial_focus.focus_set() # put focus back
        #     return
        # self.withdraw()
        # self.update_idletasks()
        self.on_cancel()

    def on_cancel(self, event=None):
        """
        Action for the Cancel button
        :param event:
        :return: None
        """
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def on_ar_status(self):
        """
        Switching between AR mode
        :return: None
        """
        if self.ar_status.get() == "1":
            self.console.debug("AR Enabled radio button selected")
            #
            self.entry_disabled_subject.grid_forget()
            self.text_disabled_body.grid_forget()
            #
            self.entry_enabled_subject.grid(row=6, column=1, sticky="WE")
            self.text_enabled_body.grid(row=8, column=0, columnspan=2, sticky='WE')
        else: # "0"
            self.console.debug("AR Disabled radio button selected")
            #
            self.entry_enabled_subject.grid_forget()
            self.text_enabled_body.grid_forget()
            #
            self.entry_disabled_subject.grid(row=6, column=1, sticky="WE")
            self.text_disabled_body.grid(row=8, column=0, columnspan=2, sticky='WE')

    def validate(self):
        """
        TK related..not sure what it is :/
        :return:
        """
        return 1 # override

