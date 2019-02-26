import Tkinter as tk
import ttk
import os

import re
import options
from pprint import pformat
from win32com.shell import shell
import tkMessageBox as mbox
import tkFileDialog # open file dialog

from ar_action.action import Action
import ar_log.log as ar_log
import ar_config.config as ar_config
from ar_model import ordered_set

class Mainframe(tk.Frame):
    def __init__(self, config, console, win):
        """
        Constructor for the main frame
        :param config: dict
        :param console: logger
        :param win: Tk object
        :return:
        """
        tk.Frame.__init__(self, win)
        self.config = config
        self.action = Action(config=self.config)
        self.console = console
        self.win = win
        self.ordered_set_selected = ordered_set.OrderedSet()
        self.dict_websites = dict()
        self.list_websites = []
        self.saved_list_func = True # disable/enable the saved-list function
        #
        self.create_menu()
        self.create_gui()
        self.win.protocol("WM_DELETE_WINDOW", self.on_quit) # "x" button runs self.on_quit
        #
        # warning if (not an admin) and (local admin override not checked) and (list of websites not empty)
        if not shell.IsUserAnAdmin() and \
                not self.config.dict_config["internal"]["local_admin_override"] and \
                self.dict_websites:
            mbox.showwarning("Warning - Unprivileged Access", "Access Restriction functionalities have been disabled. "
                                         "To enable, please restart this application with local admin privileges.")
        # if not shell.IsUserAnAdmin():
        #     #self.boolean_ar_func = True
        #     mbox.showwarning("Warning", "Unable to retrieve the IIS websites. Please ensure that you run this "
        #                                 "application with local admin privileges.")
        #     self.win.destroy()
        #
        self.on_reload(notify=False) # get the list of websites
        self.load_saved_list()

    def check_empty_websites(self):
        if not self.dict_websites:
            mbox.showwarning("Warning", "Unable to retrieve the IIS websites. Please ensure that you run this "
                                        "application with local admin privileges.")
            self.saved_list_func = False

    def load_saved_list(self):
        """
        Load the saved list from the configuration file
        :return:
        """
        saved_list = self.config.dict_config["data"]["saved_list"].strip()
        list_from_config = []
        if saved_list:
            list_from_config = saved_list.split("\n")
        #
        self.ordered_set_selected = ordered_set.OrderedSet(list_from_config)
        #
        self.sync_lists()

    def create_gui(self):
        self.var_currentconfig = tk.StringVar()
        #self.var_currentconfig.set(self.config.file_path)

        label_currentconfig = ttk.Label(self.win, relief=tk.SUNKEN,
                                        textvariable=self.var_currentconfig)
        label_currentconfig.grid(padx=5, pady=5)

        self.labelframe_tools = self.create_frame_tools()
        self.labelframe_tools.grid()
        #
        self.labelframe_detected = self.create_labelframe_detected()
        self.labelframe_detected.grid()
        #
        self.labelframe_addremove = self.create_frame_addremoveclear()
        self.labelframe_addremove.grid()
        #
        self.labelframe_selected = self.create_labelframe_selected()
        self.labelframe_selected.grid()
        #
        self.labelframe_enabledisable = self.create_frame_enabledisable()
        self.labelframe_enabledisable.grid()

    def on_about(self):
        version = "1.3"
        try:
            version = open("VERSION", "r").readlines()[0]
        except IOError:
            pass
        mbox.showinfo("Version", "Access Restriction %s" % version)

    def on_quit(self):
        #self.sync_config()
        self.win.destroy()

    def sync_config(self):
        """
        Sync configurations
        :return:
        """
        cur_config = self.config.dict_config
        #
        # email notification
        new_value = False
        if self.email_notification.get():
            new_value = True
        cur_config["email"]["email_notification"] = new_value
        #
        # selected list
        if self.saved_list_func:
            cur_config["data"]["saved_list"] = "\n".join(self.ordered_set_selected)
            self.action.save_config()
        self.sync_lists()

    def on_reload(self, notify=True):
        """
        Retrieve the websites and populate the parents list while clearing the other lists
        :return:
        """
        # clear children list
        self.populate_listbox(self.listbox_children, [], clear=True)
        #
        # get a fresh list of websites
        self.list_websites, self.dict_websites = self.action.get_websites() #self.get_websites()
        #
        # clear current selection on the parents list
        self.listbox_parents.select_clear(0,tk.END)
        # force listbox sync
        self.sync_lists()
        #
        parent_frame = self.listbox_children.master
        text = parent_frame.cget("text")
        text = re.sub(r'\d+', str(0), text)
        parent_frame.configure(text=text)
        # clear selected
        #self.on_clear()
        #
        if notify and self.dict_websites:
            mbox.showinfo("Information", "Successfully retrieved a new list of websites.")
        self.check_empty_websites()

    def on_options(self):
        # refresh the configuration
        #self.config = ar_config.read_config(ar_config.configfile_fullpath)
        options.OptionsDialog(self.config, self.console, self.win, self.action)

    def create_menu(self):
        """
        Create the main application's menu
        :return: None
        """
        menu = tk.Menu(self.win)
        self.win.config(menu=menu)
        #
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Config", command=self.on_config_save)
        file_menu.add_command(label="Save Config As...", command=self.on_config_save_as)
        file_menu.add_command(label="Load Config", command=self.on_config_load)
        file_menu.add_command(label="Exit", command=self.on_quit)
        #
        option_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Tools", menu=option_menu)
        option_menu.add_command(label="Reload", command=self.on_reload)
        option_menu.add_command(label="Options", command=self.on_options)
        #
        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.on_about)

    def create_frame_tools(self):
        frame = ttk.Frame(self.win)
        button_reload = ttk.Button(frame, text="Reload", command=self.on_reload)
        button_settings = ttk.Button(frame, text="Options", command=self.on_options)
        button_saveconfig = ttk.Button(frame, text="Save Config", command=self.on_config_save)
        button_saveconfigas = ttk.Button(frame, text="Save Config As...", command=self.on_config_save_as)
        button_loadconfig = ttk.Button(frame, text="Load Config", command=self.on_config_load)
        #
        button_reload.grid(row=0, column=0, padx=5, pady=5)
        button_settings.grid(row=0, column=1, padx=5, pady=5)
        button_saveconfig.grid(row=0, column=2, padx=5, pady=5)
        button_saveconfigas.grid(row=0, column=3, padx=5, pady=5)
        button_loadconfig.grid(row=0, column=4, padx=5, pady=5)
        #
        return frame

    def on_config_load(self):
        """
        Load an external configuration file
        :return: None
        """
        file_types = [('Configuration files', '*.ini'), ('All files', '*')]
        file_selected = tkFileDialog.Open(self, filetypes=file_types).show()

        if file_selected:
            #self.sync_config()
            self.console.debug("Loading configuration file: '{}'".format(file_selected))
            self.config = ar_config.Config(file_path=file_selected,
                                           console=self.console)
            self.action.config = self.config
            self.load_saved_list()

    def on_config_save(self):
        """
        Load an external configuration file
        :return: None
        """
        self.sync_config()
        mbox.showinfo("Information", "Configurations have been saved to: '{}'".format(self.config.file_path))

    def on_config_save_as(self):
        """
        Load an external configuration file
        :return: None
        """
        file_types = [('Configuration files', '*.ini'), ('All files', '*')]
        file_selected = tkFileDialog.SaveAs(self, filetypes=file_types).show()


        if file_selected:
            self.console.debug("Saving configuration file: '{}'".format(file_selected))
            self.config.file_path = file_selected
            self.console.debug("self.config.file_path = '{}'".format(self.config.file_path))
            self.sync_config()
            mbox.showinfo("Information", "Configurations have been saved to: '{}'".format(self.config.file_path))
            #mbox.showinfo("Information", "Configurations have been saved to: '{}'".format(file_selected))


    def create_frame_addremoveclear(self):
        frame = ttk.Frame(self.win)
        self.button_add = ttk.Button(frame, text="Add", command=self.on_add)
        self.button_remove = ttk.Button(frame, text="Remove", command=self.on_remove)
        self.button_clear = ttk.Button(frame, text="Clear", command=self.on_clear)
        #
        self.button_add.grid(row=0, column=0, padx=5, pady=5)
        self.button_remove.grid(row=0, column=1, padx=5, pady=5)
        self.button_clear.grid(row=0, column=2, padx=5, pady=5)
        #
        # initially disable both the add and remove buttons
        self.button_add.configure(state="disabled")
        self.button_remove.configure(state="disabled")
        self.button_clear.configure(state="disabled")
        return frame

    def sync_lists(self):
        '''
        Use the data from self.dict_websites and self.ordered_set_selected to
        re-populate listbox_parents and listbox_selected
        :return: None
        '''
        self.console.debug("Synchronizing lists")# + str(self.listbox_parents.curselection()))
        #
        # if a parent item is selected, save it
        current_selection = -1
        if len(self.listbox_parents.curselection()): # a parent website is selected
            current_selection = self.listbox_parents.curselection()[0] # set to 0 since only 1 can be selected
        #
        # re-populate the parents listbox
        self.populate_listbox(self.listbox_parents, self.dict_websites.keys(), clear=True)
        # restore the saved parent selection
        if current_selection != -1:
            self.listbox_parents.select_set(current_selection)
        #
        # compare ordered_set_selected and the new list of websites and remove any invalids
        self.ordered_set_selected = ordered_set.OrderedSet(self.ordered_set_selected) & \
                                    ordered_set.OrderedSet(self.list_websites)
        # re-populate the selected listbox
        self.populate_listbox(self.listbox_selected, self.ordered_set_selected , clear=True)
        #
        # update the number that has been selected
        self.update_number(self.listbox_selected)
        #
        # update the states of the buttons
        if len(self.ordered_set_selected):
            # there are items in the selected list
            self.button_clear.configure(state="enable")
            self.button_enable.configure(state="enabled")
            self.button_disable.configure(state="enabled")
        else:
            self.button_clear.configure(state="disable")
            self.button_enable.configure(state="disabled")
            self.button_disable.configure(state="disabled")

        # update email_notification checkbox
        if self.config.dict_config["email"]["email_notification"]:
            self.email_notification.set(1)
        else:
            self.email_notification.set(0)

        # update current configuration file path
        self.var_currentconfig.set(self.config.file_path)

    def on_enable(self):
        #ips = self.config.dict_config["access_restriction"]["ips"].split("\n")
        #
        # let's disable AR first
        output = self.action.change_state(action="disable",
                                    websites=self.ordered_set_selected)
        # let's clear it for now to prevent confusion..sigh...
        output = ""
        output += self.action.change_state(action="enable",
                                    websites=self.ordered_set_selected)

        if self.email_notification.get():
            err = self.action.send_email(ar_state="ar_enabled", websites=self.ordered_set_selected)
            if err:
                mbox.showerror("Email Notification", "Failed to send out email notification due to: \n{}".format(err))

        logfile = self.action.write_log(output)
        mbox.showinfo("Information",
                      "Access Restriction has been enabled.\n"
                      "Details can be found in the log file:\n%s" % logfile)

        notepad = self.config.dict_config["internal"]["notepad"]
        self.action.execute(notepad, [logfile], invisible=False, block=False)

    def on_disable(self):
        ips = self.config.dict_config["access_restriction"]["ips"].split("\n")
        output = self.action.change_state(action="disable",
                                    websites=self.ordered_set_selected)

        if self.email_notification.get():
            err = self.action.send_email(ar_state="ar_disabled", websites=self.ordered_set_selected)
            if err:
                mbox.showerror("Email Notification", "Failed to send out email notification due to: {}".format(err))

        logfile = self.action.write_log(output)
        mbox.showinfo("Information",
                      "Access Restriction has been disabled.\n"
                      "Details can be found in the log file '%s'." % logfile)
        notepad = self.config.dict_config["internal"]["notepad"]
        self.action.execute(notepad, [logfile], invisible=False, block=False)

    def on_add(self):
        # e.g. MTOWEB-SAE intra.dev.apps.rus.mto.gov.on.ca_8001_44301
        str_parent_add = self.listbox_parents.get(self.listbox_parents.curselection()[0])
        # e.g. ['/auditws','/cns'...]
        list_children_add = [self.listbox_children.get(i) for i in self.listbox_children.curselection()]
        #
        for entry in list_children_add:
            self.ordered_set_selected.add("{parent}{child}".format(parent=str_parent_add, child=entry))
        #
        self.console.debug("Parent: {}".format(str_parent_add))
        self.console.debug("Adding:\n{}".format(pformat(list_children_add)))
        #
        self.button_add.configure(state="disabled")
        self.sync_lists()

    def on_remove(self):
        list_selected_remove = [self.listbox_selected.get(i) for i in self.listbox_selected.curselection()]
        #
        self.console.debug("Removing:\n{}".format(pformat(list_selected_remove)))
        self.ordered_set_selected = self.ordered_set_selected - list_selected_remove
        #
        # disable the remove button
        self.button_remove.configure(state="disabled")
        self.sync_lists()

    def on_clear(self):
        self.console.debug("Clearing the selected listbox.")
        self.ordered_set_selected.clear()
        #
        self.sync_lists()
        #
        # reset button state
        self.button_remove.configure(state="disabled")
        self.button_enable.configure(state="disabled")
        self.button_disable.configure(state="disabled")

    def on_select_parents(self, event):
        """
        Define action for listbox_parents
        :param event: Tkinter event
        :return: None
        """
        listbox = event.widget
        if not len(listbox.curselection()):
            return
        index = listbox.curselection()[0]
        value = listbox.get(index)
        self.console.debug('Selected website: {}'.format(value))
        #
        # let's populate the children listbox
        self.populate_listbox(self.listbox_children, self.dict_websites[value], clear=True)
        self.listbox_children.select_set(0)
        self.update_number(self.listbox_children)
        #
        self.button_add.configure(state="enable")

    def on_select_children(self, event):
        """
        Define action for the children listbox
        :param event: Tkinter event
        :return: None
        """
        self.update_number(event.widget)
        # at least one item is selected
        if len(event.widget.curselection()): # at least one item is selected
            self.button_add.configure(state="enabled")
        else:
            self.button_add.configure(state="disabled")

    def on_select_selected(self, event):
        """
        Define action for the selected listbox
        :param event: Tkinter event
        :return: None
        """
        # enable/disable the remove button based on the number of children is selected
        self.update_number(event.widget)
        #
        # at least one item is selected
        if len(event.widget.curselection()): # at least one item is selected
            self.button_remove.configure(state="enabled")
        else:
            self.button_remove.configure(state="disabled")

    def create_frame_enabledisable(self):
        frame = ttk.LabelFrame(self.win, text="Action")
        #
        self.email_notification = tk.IntVar()
        self.checkbox_email = ttk.Checkbutton(frame, text="Send Email Notification",
                                              variable=self.email_notification)
        self.checkbox_email.grid(row=0, column=0, columnspan=2)
        #self.checkbox_email.configure(state="checked")
        #
        self.button_enable = ttk.Button(frame, text="Enable Access Restriction", command=self.on_enable)
        self.button_disable = ttk.Button(frame, text="Disable Access Restriction", command=self.on_disable)
        #
        self.button_enable.grid(row=1, column=0, padx=10, pady=10)
        self.button_disable.grid(row=1, column=1, padx=10, pady=10)
        #
        # initially disable both the add and remove buttons
        self.button_enable.configure(state="disabled")
        self.button_disable.configure(state="disabled")
        #
        return frame


    def create_labelframe_detected(self):
        # create the "Detected Websites" label frame
        labelframe = ttk.Frame(self.win)#, text="Websites", labelanchor=tk.N)

        _height = 14

        # create the "Websites" ("Parents") label frame
        self.labelframe_detected_parents = ttk.LabelFrame(labelframe, text="Website")
        self.labelframe_detected_parents.grid(column=0, row=0)

        # create the "Children" label frame
        self.labelframe_detected_children = ttk.LabelFrame(labelframe, text="Children (0/0)")
        self.labelframe_detected_children.grid(column=1, row=0)

        # create the parents listbox
        self.listbox_parents = self.create_scrollable_listbox(self.labelframe_detected_parents,
                                                              width=80, height=_height, row=0, column=0,
                                                              padx=5, pady=5)
        self.listbox_parents.bind("<<ListboxSelect>>", self.on_select_parents)
        #self.populate_listbox(self.listbox_parents, self.dict_websites.keys())

        # create the children listbox
        self.listbox_children = self.create_scrollable_listbox(self.labelframe_detected_children,
                                                               width=40, height=_height, row=0, column=2,
                                                               padx=5, pady=5)
        self.listbox_children.bind("<<ListboxSelect>>", self.on_select_children)
        self.listbox_children.bind('<Control-a>', self.on_select_all)
        self.listbox_children.configure(selectmode=tk.EXTENDED) # allows multiple selection
        #
        return labelframe

    def create_labelframe_selected(self):
        # create the "Selected Websites" label frame
        labelframe = ttk.LabelFrame(self.win, text="Selected Websites (0/0)")
        #
        # create the children listboxes
        self.listbox_selected = self.create_scrollable_listbox(labelframe,
                                                               width=0, height=10,
                                                               row=0, column=0,
                                                               padx=5, pady=5)
        #
        # fix so that the listbox expands if there's available space within the labelframe
        labelframe.grid_configure(sticky="WE")
        labelframe.grid_columnconfigure(0, weight=1)
        self.listbox_selected.grid_configure(sticky="WE")
        self.listbox_selected.grid_columnconfigure(0, weight=1)

        self.listbox_selected.bind("<<ListboxSelect>>", self.on_select_selected)
        self.listbox_selected.bind('<Control-a>', self.on_select_all)
        self.listbox_selected.configure(selectmode=tk.EXTENDED) # allows multiple selection
        return labelframe

    def on_select_all(self, event):
        """
        Gets invoked when Ctrl-a is pressed
        :param event: Tk event
        :return:
        """
        listbox = event.widget
        listbox.select_set(0, tk.END)
        self.update_number(listbox)

    def populate_listbox(self, listbox, list_data, clear=False):
        """
        Populate a listbox based
        :param listbox: Tk
        :param list_data: list
        :param clear:
        :return:
        """
        # clear the listbox if marked
        if clear:
            listbox.delete(0, tk.END)
        #
        self.console.debug('Populating listbox (clear={}) with:\n{}'.
                           format(clear, pformat(list_data)))
        for entry in sorted(list_data):
            listbox.insert(tk.END, entry)

    def update_number(self, listbox):
        """
        Update the number of selected items: e.g. "Selected Websites (123)" or "Children (1/10)"
        :return: None
        """
        parent_frame = listbox.master
        text = parent_frame.cget("text") # grab "Selected Websites (0)" or "Children (1/0)"
        total = len(listbox.get(0, tk.END))
        #
        selected = len(listbox.curselection())
        text = re.sub(r'\d+/\d+', "{}/{}".format(selected, total), text)
        parent_frame.configure(text=text)

    def create_scrollable_listbox(self, frame, width, height, row, column,
                                  # so that entry does not get unselected when focus on another listbox
                                  exportselection=0,
                                  padx=0, pady=0):
        """
        Create a listbox with horizontal and vertical scrollbars
        :param frame: the parent frame where the widget will be created
        :param row: x position
        :param column: y position
        :param selectmode: default to tk.BROWSE or can be tk.EXTENDED...etc
        :return: listbox widget with
        """
        listbox = tk.Listbox(frame, width=width, height=height,
                             exportselection=exportselection)

        xscrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        xscrollbar.config(command=listbox.xview)
        xscrollbar.grid(row=row+1, column=column, sticky="WE")

        yscrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        yscrollbar.config(command=listbox.yview)
        yscrollbar.grid(row=row, column=column+1, sticky="NS")

        listbox.config(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
        listbox.grid(row=row, column=column,
                     padx=padx, pady=pady)
        return listbox

def main(config):
    """
    Create main graphical layout
    :param config: OrderedDict
    """
    console = ar_log.get_logger("console")
    console.debug("Initializing graphical layout...")

    win = tk.Tk()
    win.title("Access Restriction")
    win.resizable(0, 0)

    app = Mainframe(config, console, win)
    win.mainloop()