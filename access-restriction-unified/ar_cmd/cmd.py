from ar_action.action import Action
from ar_model import ordered_set

class Cmd:
    def __init__(self, config, console):
        self.config = config
        self.console = console
        self.ordered_set_selected = ordered_set.OrderedSet()
        self.action = Action(config=self.config)
        self.__load()

    def __load(self):
        saved_list = self.config.dict_config["data"]["saved_list"].strip()
        list_from_config = []
        if saved_list:
            list_from_config = saved_list.split("\n")
        #
        self.ordered_set_selected = ordered_set.OrderedSet(list_from_config)

    def do(self, action):
        if not len(self.ordered_set_selected):
            self.console.debug("Saved list is empty. Nothing to do.")
            return

        if action == "enable":
            self.action.change_state(action="disable",
                                     websites=self.ordered_set_selected)
            output = self.action.change_state(action="enable",
                                              websites=self.ordered_set_selected)
        elif action == "disable":
            output = self.action.change_state(action="disable",
                                     websites=self.ordered_set_selected)
        else:
            raise Exception("Unrecognized action: '%s'" % action )

        if self.config.dict_config["email"]["email_notification"]:
            self.console.debug("Sending email notification")
            err = self.action.send_email(ar_state="ar_%sd" % action,
                                         websites=self.ordered_set_selected)
            if err:
                self.console.error("Failed to send out email notification due to: \n{}".format(err))

        print output

        logfile = self.action.write_log(output)
        print "[INFO] Output has been saved to log file: %s" % logfile

