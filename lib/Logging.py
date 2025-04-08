import os
import datetime


def log(message, print_console=False):
    """
    Log the message to the console and a log file.
    :param message: string message to log
    :param print_console: boolean flag to print the message to console
    """
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    with open(os.path.join('logs', f'log_{current_date}.log'), 'a') as log_file:
        log_file.write(f'{datetime.datetime.now()} - {message}\n')

    if print_console:
        print(message)


class Logging:
    """
    Logging class to handle logging messages to a file and console.
    """

    def __init__(self):
        """
        Initialize the Logging class.
        """
        if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
            os.makedirs('logs', exist_ok=True)
