"""
Selenium Test Suite - Task Manager Application
DevOps CSC418 - Terminal Exam

Run: pip install selenium webdriver-manager
     python selenium/test_taskmanager.py

Set APP_URL env var if not running locally:
     APP_URL=http://<your-aks-ip> python selenium/test_taskmanager.py
"""

import os
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

APP_URL = os.environ.get("APP_URL", "http://localhost:8081")


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    return webdriver.Chrome(options=options)


class TestTaskManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.driver.get(APP_URL)
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    # ─────────────────────────────────────────────
    # Test 1: Homepage loads correctly
    # ─────────────────────────────────────────────
    def test_01_homepage_loads(self):
        """Verify the homepage title and key UI elements are present."""
        driver = self.driver

        self.assertIn("Task Manager", driver.title,
                      "Page title should contain 'Task Manager'")

        heading = driver.find_element(By.TAG_NAME, "h1")
        self.assertIn("Task Manager", heading.text,
                      "H1 heading should contain 'Task Manager'")

        task_input = driver.find_element(By.ID, "taskTitle")
        self.assertTrue(task_input.is_displayed(),
                        "Task title input should be visible")

        submit_btn = driver.find_element(By.CSS_SELECTOR, ".btn-add")
        self.assertTrue(submit_btn.is_displayed(),
                        "Add Task button should be visible")

        print("✅ Test 1 PASSED: Homepage loads correctly")

    # ─────────────────────────────────────────────
    # Test 2: Create a new task (form behaviour)
    # ─────────────────────────────────────────────
    def test_02_create_task(self):
        """Validate that submitting the form adds a new task to the list."""
        driver = self.driver
        wait   = self.wait

        title_input = driver.find_element(By.ID, "taskTitle")
        desc_input  = driver.find_element(By.ID, "taskDescription")
        submit_btn  = driver.find_element(By.CSS_SELECTOR, ".btn-add")

        test_title = f"Selenium Test Task {int(time.time())}"
        test_desc  = "Created by automated Selenium test"

        title_input.clear()
        title_input.send_keys(test_title)
        desc_input.clear()
        desc_input.send_keys(test_desc)
        submit_btn.click()

        # Wait for the task to appear in the list
        time.sleep(2)

        task_list = driver.find_element(By.ID, "tasksList")
        self.assertIn(test_title, task_list.text,
                      f"Newly created task '{test_title}' should appear in the list")

        self.assertEqual(title_input.get_attribute("value"), "",
                         "Title input should be cleared after submission")

        print(f"✅ Test 2 PASSED: Task '{test_title}' created and visible")

    # ─────────────────────────────────────────────
    # Test 3: Backend API response check via frontend
    # ─────────────────────────────────────────────
    def test_03_api_response_reflected_in_ui(self):
        """
        Verify frontend-to-backend communication:
        tasks loaded on page load should be shown in the task list
        (not the 'Loading...' or error state).
        """
        driver = self.driver

        driver.refresh()
        time.sleep(3)

        task_list = driver.find_element(By.ID, "tasksList")

        self.assertNotIn("Error loading tasks", task_list.text,
                         "Task list should NOT show an error — backend must be reachable")

        self.assertNotIn("Loading tasks...", task_list.text,
                         "Task list should have finished loading")

        print("✅ Test 3 PASSED: Frontend successfully fetched data from backend API")

    # ─────────────────────────────────────────────
    # Test 4: Navigation / button behaviour
    # ─────────────────────────────────────────────
    def test_04_complete_and_delete_task(self):
        """Verify Complete and Delete buttons work correctly."""
        driver = self.driver
        wait   = self.wait

        # Create a fresh task to operate on
        title_input = driver.find_element(By.ID, "taskTitle")
        title_input.clear()
        title_input.send_keys("Button Test Task")
        driver.find_element(By.CSS_SELECTOR, ".btn-add").click()
        time.sleep(2)

        # Click the Complete button on the first task
        complete_btns = driver.find_elements(By.CSS_SELECTOR, ".btn-complete")
        self.assertGreater(len(complete_btns), 0, "At least one Complete button should exist")
        complete_btns[0].click()
        time.sleep(1)

        # After completing, the task item should have class 'completed'
        completed_items = driver.find_elements(By.CSS_SELECTOR, ".task-item.completed")
        self.assertGreater(len(completed_items), 0,
                           "At least one task should be marked as completed")

        # Click Delete on the first available delete button
        delete_btns = driver.find_elements(By.CSS_SELECTOR, ".btn-delete")
        initial_count = len(driver.find_elements(By.CSS_SELECTOR, ".task-item"))
        delete_btns[0].click()

        # Handle the confirm dialog
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except Exception:
            pass

        time.sleep(2)

        final_count = len(driver.find_elements(By.CSS_SELECTOR, ".task-item"))
        self.assertLess(final_count, initial_count,
                        "Task count should decrease after deletion")

        print("✅ Test 4 PASSED: Complete and Delete buttons work correctly")


if __name__ == "__main__":
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None          # keep definition order
    suite  = loader.loadTestsFromTestCase(TestTaskManager)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n🎉 All Selenium tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} failure(s), {len(result.errors)} error(s)")
        exit(1)
