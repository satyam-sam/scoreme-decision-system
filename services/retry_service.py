import time

class RetryService:

    def retry(self, func, retries=3, delay=1):
        """
        Retry logic with exponential backoff
        Attempt 1 → wait 1 sec
        Attempt 2 → wait 2 sec
        Attempt 3 → wait 4 sec
        """
        last_error = None

        for attempt in range(1, retries + 1):
            try:
                print(f"Attempt {attempt}/{retries}...")
                result = func()
                print(f"Success on attempt {attempt}!")
                return result, attempt

            except Exception as e:
                last_error = str(e)
                print(f"Attempt {attempt} failed: {e}")

                if attempt < retries:
                    wait_time = delay * (2 ** (attempt - 1))
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

        # All retries failed
        raise Exception(
            f"All {retries} attempts failed. "
            f"Last error: {last_error}"
        )