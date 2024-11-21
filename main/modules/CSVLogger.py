import csv
import time
import threading

class CSVLogger(threading.Thread):
    def __init__(self, filename, outputs, interval=0.1):
        super().__init__()
        self.filename = filename
        self.outputs = outputs
        self.interval = interval
        self.file = open(self.filename, mode='w', newline='')
        self.writer = csv.writer(self.file)
        self.running = threading.Event()
        self.running.set()
        self.lock = threading.Lock()

        # Optionally, write headers if needed
        #self.write_headers()

    def write_headers(self):
        headers = ['timestamp'] + [f'output_{i}' for i in range(len(self.outputs))]
        self.writer.writerow(headers)

    def run(self):
        try:
            while self.running.is_set():
                data_row = [time.time()]

                for capture_q in self.outputs:                    
                    if not capture_q.empty():
                        data = capture_q.get()
                        data_row.append(data)
                    else:
                        data_row.append(None)

                # Check if all fields have values (no `None` or empty fields)
                if all(value is not None for value in data_row[1:]):  # Skip timestamp in the check
                    with self.lock:
                        self.writer.writerow(data_row)
                    print(data_row)

                time.sleep(self.interval)
        except Exception as e:
            print(f"Logging encountered an error: {e}")
        finally:
            self.stop()

    def stop(self):
        self.running.clear()
        with self.lock:
            self.file.close()
        print(f"Logging stopped. File '{self.filename}' closed.")
