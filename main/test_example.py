from modules.rssi_collector import RSSICollector
from modules.rssi_collector import RSSICollector
from modules.pipeline import Pipeline
from modules.test_filter import TESTFilter

pipeline = Pipeline()

rssi_collector = RSSICollector()
rssi_collector.start()

test_filter = TESTFilter()

pipeline.add_module(rssi_collector)
pipeline.add_module(test_filter)

output = pipeline.get_output()

while True:
    data = output.get()
    if data is not None:
        print(data)
