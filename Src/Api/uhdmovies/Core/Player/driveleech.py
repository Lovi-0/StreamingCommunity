# 30.06.24

import time
import logging


# External library
from bs4 import BeautifulSoup
from seleniumbase import Driver


# Internal utilities
from Src.Util._jsonConfig import config_manager


# Config
USE_HEADLESS = config_manager.get_bool("BROWSER", "headless")


class DownloadAutomation:
    def __init__(self, download_link):
        self.download_link = download_link
        self.driver = Driver(uc=True, uc_cdp_events=True, headless=USE_HEADLESS)
        self.mp4_link = None

    def run(self):
        """
        Executes the entire automation process.
        """
        try:
            self.driver.get(self.download_link)
            self._inject_css()
            self._observe_title_change()
            self._bypass_page_1()
            self._bypass_page_2_verify_button()
            self._bypass_page_2_two_steps_btn()
            self._wait_for_document_complete()
            self._wait_for_bypass_completion()
            self._extract_download_link()

        except Exception as e:
            logging.error(f"Error occurred during automation: {str(e)}")

        finally:
            self.quit()

    def _inject_css(self):
        """
        Injects CSS to make all elements on the page invisible.
        """
        try:
            css_script = """
                const voidCSS = `* {opacity: 0;z-index: -999999;}`;
                function addStyle(css) {
                    let head = document.querySelector('head'),
                        style = document.createElement('style');
                    style.innerHTML = css;
                    head.appendChild(style);
                }
            """
            
            self.driver.execute_script(css_script)
            logging.info("CSS injected.")
            time.sleep(0.4)

        except Exception as e:
            logging.error(f"Error injecting CSS: {str(e)}")

    def _observe_title_change(self):
        """
        Observes changes in the document title and applies CSS injection.
        """
        try:
            observer_script = """
                let headObserver = new MutationObserver(function() {
                    if (document.title) {
                        addStyle(voidCSS.replace(';', ' !important;'));
                        headObserver.disconnect();
                    }
                });
            headObserver.observe(document.documentElement, {childList: true, subtree: true});
            """

            self.driver.execute_script(observer_script)
            logging.info("Title observer set.")
            time.sleep(0.4)

        except Exception as e:
            logging.error(f"Error setting title observer: {str(e)}")

    def _bypass_page_1(self):
        """
        Executes action to bypass Page 1.
        """
        try:
            action1_script = """
                function action1() {
                    try {
                        document.querySelector('#landing').submit();
                        document.title = "Bypass Action (1/3)";
                    } catch {}
                }
                action1();
            """

            self.driver.execute_script(action1_script)
            logging.info("Page 1 bypassed.")
            time.sleep(0.4)

        except Exception as e:
            logging.error(f"Error bypassing Page 1: {str(e)}")

    def _bypass_page_2_verify_button(self):
        """
        Executes action to bypass Page 2 by clicking on verify_button.
        """
        try:
            action2_script = """
                function action2() {
                    try {
                        document.querySelector('#verify_button').click();
                        document.title = "Bypass Action (2/3)";
                    } catch {}
                }
                action2();
            """

            self.driver.execute_script(action2_script)
            logging.info("Page 2 bypassed.")
            time.sleep(0.4)

        except Exception as e:
            logging.error(f"Error bypassing Page 2: {str(e)}")

    def _bypass_page_2_two_steps_btn(self):
        """
        Executes action to bypass Page 2 by waiting for and clicking two_steps_btn.
        """
        try:
            action3_script = """
                function action3() {
                    try {
                        let observer = new MutationObserver(function() {
                            if (document.querySelector('#two_steps_btn').href !== "") {
                                observer.disconnect();
                                document.title = "Bypass Action (3/3)";
                                window.location = document.querySelector('#two_steps_btn').href;
                            }
                        });
                        observer.observe(document.querySelector('#two_steps_btn'), {attributes: true});
                    } catch {}
                }
                action3();
            """

            self.driver.execute_script(action3_script)
            logging.info("Page 2 bypassed with observation and redirect.")
            time.sleep(0.4)

        except Exception as e:
            logging.error(f"Error bypassing Page 2 with observation: {str(e)}")

    def _wait_for_document_complete(self):
        """
        Waits for the document to be completely loaded to execute actions.
        """
        try:
            onreadystatechange_script = """
                document.onreadystatechange = function () {
                    if (document.readyState === 'complete') {
                        action1();
                        action2();
                        action3();
                    }
                }
            """

            self.driver.execute_script(onreadystatechange_script)
            logging.info("onreadystatechange set.")
            time.sleep(0.4)

        except Exception as e:
            logging.error(f"Error setting onreadystatechange: {str(e)}")

    def _wait_for_bypass_completion(self):
        """
        Waits for the bypass process to complete.
        """
        try:
            while True:
                if ".mkv" in self.driver.title or ".mp4" in self.driver.title:
                    logging.info("Bypass completed.")
                    break

                time.sleep(0.5)

        except Exception as e:
            logging.error(f"Error waiting for bypass completion: {str(e)}")

    def _extract_download_link(self):
        """
        Extracts the final download link after bypassing and loads the download page.
        """
        try:
            final_html = self.driver.page_source
            soup = BeautifulSoup(final_html, 'html.parser')
            video_link = soup.find("a", class_="btn").get('href')

            logging.info("Loading download page.")
            self.driver.get(video_link)
            logging.info(f"Download page link: {video_link}")

        except Exception as e:
            logging.error(f"Error extracting download link: {str(e)}")

    def capture_url(self, req):
        """
        Function to capture url in background
        """
        try:
            url = req['params']['documentURL']

            # Filter for mp4 video download
            if "googleusercontent" in str(url):
                self.mp4_link = url

        except:
            pass

    def quit(self):
        """
        Quits the WebDriver instance.
        """
        try:
            logging.info("Removing ad headers.")
            css_script = """
                const voidCSS = ``;
                function addStyle(css) {
                    let head = document.querySelector('head'),
                        style = document.createElement('style');
                    style.innerHTML = css;
                    head.appendChild(style);
                }
            """

            self.driver.execute_script(css_script)
            self.driver.add_cdp_listener("*", lambda data: self.capture_url(data))
            time.sleep(0.3)

            logging.info("Clicking button.")
            self.driver.execute_script("document.getElementById('ins').click();")

            while True:
                time.sleep(0.3)
                if self.mp4_link is not None:
                    break

            logging.info(f"MP4 Link: {self.mp4_link}")
            logging.info("Quitting...")
            self.driver.quit()

        except Exception as e:
            logging.error(f"Error during quitting: {str(e)}")
