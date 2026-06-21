import os
from locust import HttpUser, task, between


class ResumeMatchUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # In a real scenario, you'd log in and get a token.
        # For the load test, we'll assume we have a pre-provisioned token.
        self.token = os.environ.get("LOCUST_TEST_TOKEN", "fake_token_for_load_test")
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def get_analyses(self):
        """Test listing analyses with rate limits"""
        with self.client.get("/api/v1/analysis", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.failure("Rate limited (expected under heavy load)")
            elif response.status_code in (401, 403):
                response.failure("Unauthorized - make sure LOCUST_TEST_TOKEN is valid")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def check_health(self):
        """Test the public health endpoint"""
        self.client.get("/api/v1/health")

    @task(1)
    def test_metrics(self):
        """Test the prometheus metrics endpoint"""
        self.client.get("/metrics")
