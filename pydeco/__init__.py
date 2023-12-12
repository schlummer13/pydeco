import time
import logging
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import sys, traceback


class EmailEventTrigger:
    def __init__(self, host, username, password, recipients):
        self.host = host
        self.username = username
        self.password = password
        self.recipients = recipients

    def send_email(self, subject, body):
        message = MIMEMultipart()
        message["From"] = self.username
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP(self.host)
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(self.username, self.recipients, message.as_string())
        server.quit()

    def event(self, subject, body):
        def decorator(func):
            def wrapper(*args, **kwargs):
                event_thread = threading.Thread(
                    target=self.send_email,
                    args=(
                        subject,
                        body,
                    ),
                )
                event_thread.start()
                result = func(*args, **kwargs)
                event_thread.join()
                return result

            return wrapper

        return decorator


class ProgrammAnalyzer:
    def __init__(self) -> None:
        self.programm = []
        self.funcs = {}

    def analyze(self, file: str = None):
        def decorator(func):
            log = logging.getLogger(func.__name__)
            log.setLevel(logging.INFO)
            if file:
                # Konfiguriere das Logging in eine Datei
                file_handler = logging.FileHandler(file)
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(
                    logging.Formatter("%(asctime)s - %(message)s")
                )
                log.addHandler(file_handler)
            else:
                # Konfiguriere das Logging auf der Konsole
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(
                    logging.Formatter("%(asctime)s - %(message)s")
                )
                log.addHandler(console_handler)

            def wrapper(*args, **kwargs):
                # start the timer
                exception = "N/A"
                start_time = time.time()
                result = None
                line_number = 0
                if func.__name__ not in self.funcs.keys():
                    self.funcs[func.__name__] = 1
                else:
                    self.funcs[func.__name__] += 1
                try:
                    # call the decorated function
                    result = func(*args, **kwargs)
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    exception = exc_value
                    line_number = int(traceback.extract_tb(exc_traceback)[-1][1])
                finally:
                    # remeasure the time
                    end_time = time.time()
                    # compute the elapsed time and print it
                    execution_time = end_time - start_time
                    self.programm.append(
                        {
                            "Func": func.__name__,
                            "Time": round(execution_time, 6),
                            "Exception": exception,
                            "Line": line_number,
                            "Views": self.funcs.get(func.__name__),
                        }
                    )
                    log.info(
                        f"Func: {func.__name__} - {execution_time:.6f} - {exception} - {line_number}"
                    )
                return result

            return wrapper

        return decorator

    def get_report(self, save: str = None) -> pd.DataFrame:
        df = pd.DataFrame(self.programm)
        if save:
            df.to_csv(save)
        return df


def retry(max_attempts: int, delay: int = 1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Attempt {attempts} failed: {e}")
                    time.sleep(delay)
            print(f"Function failed after {max_attempts} attempts")

        return wrapper

    return decorator
