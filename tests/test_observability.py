import unittest
import os
import json
import logging
import csv
from datetime import datetime
import shutil
from execution.logger import setup_logger, PipelineLogger, get_run_id, RUN_ID

class TestObservability(unittest.TestCase):
    
    def setUp(self):
        self.test_log_dir = ".tmp/test_runs"
        self.test_journal = "test_trade_journal.csv"
        # Clean up before test
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        if os.path.exists(self.test_journal):
            os.remove(self.test_journal)
            
        self.logger = setup_logger("test_bot", self.test_log_dir)

    def tearDown(self):
        # Shut down logging to release file locks
        logging.shutdown()
        # Clean up after test
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        if os.path.exists(self.test_journal):
            os.remove(self.test_journal)

    def test_json_logs_contain_run_id(self):
        self.logger.info("Test message")
        
        # Find the log file
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(self.test_log_dir, date_str, "log.jsonl")
        
        self.assertTrue(os.path.exists(log_file))
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 0)
            log_entry = json.loads(lines[0])
            
            self.assertIn("run_id", log_entry)
            self.assertEqual(log_entry["run_id"], RUN_ID)
            self.assertEqual(log_entry["message"], "Test message")

    def test_pipeline_logger_lifecycle(self):
        with PipelineLogger(self.test_journal, self.logger) as pl:
            pl.update(symbol="EURUSD", price=1.2345)
            self.logger.info("Inside pipeline")
            
        # Check journal
        self.assertTrue(os.path.exists(self.test_journal))
        with open(self.test_journal, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertIn("run_id", rows[0])
            self.assertEqual(rows[0]["run_id"], RUN_ID)
            self.assertEqual(rows[0]["symbol"], "EURUSD")

        # Check logs for start/end events
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(self.test_log_dir, date_str, "log.jsonl")
        with open(log_file, 'r') as f:
            logs = [json.loads(line) for line in f]
            
            event_types = [l.get("event_type") for l in logs if "event_type" in l]
            self.assertIn("RUN_START", event_types)
            self.assertIn("RUN_END", event_types)

    def test_pipeline_logger_failure(self):
        try:
            with PipelineLogger(self.test_journal, self.logger) as pl:
                pl.update(symbol="GBPUSD")
                raise ValueError("Simulated failure")
        except ValueError:
            pass
        
        # Check journal for error
        with open(self.test_journal, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["decision"], "ERROR")
            self.assertEqual(rows[0]["reason"], "Simulated failure")

        # Check failure log
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(self.test_log_dir, date_str, "log.jsonl")
        with open(log_file, 'r') as f:
            logs = [json.loads(line) for line in f]
            
            failure_logs = [l for l in logs if l.get("event_type") == "FAILURE"]
            self.assertTrue(len(failure_logs) > 0)
            self.assertEqual(failure_logs[0]["failure_summary"], "Simulated failure")
            self.assertEqual(failure_logs[0]["next_steps"], "Review stack trace and input data")

if __name__ == '__main__':
    unittest.main()
