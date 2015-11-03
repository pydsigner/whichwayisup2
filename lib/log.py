"""A logging module - error messages using the error_message function
will only be displayed on screen if the verbose setting is on, and written
to the log variable by default. The log doesn't need to be initialized
to be used, but you must call the write_log function in util.py on exit if you
want the log to be saved."""

from .variables import variables


def error_message(string):
    """Add a message specified as an error to the message log."""
    log_message("Error: " + string)


def log_message(string):
    """Add a message to the message log, which can be written on disk later."""

    #Multiple messages of the same type aren't added to the log:
    if variables.vdict.has_key("last_log_message"):
      if string == variables["last_log_message"]:
        return
    
    if variables['verbose']:
        print(string)
    
    variables["last_log_message"] = string
    
    if 'log' in variables:
        variables["log"] = string + "\n" + variables["log"]
    else:
        variables["log"] = string
