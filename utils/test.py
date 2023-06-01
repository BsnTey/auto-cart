import undetected_chromedriver as uc


class CustomChromeTest(uc.Chrome):
    def __del__(self):
        try:
            self.quit()
        except OSError:
            pass
