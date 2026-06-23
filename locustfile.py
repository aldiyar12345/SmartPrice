from locust import HttpUser, task, between

class SmartPriceUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def view_home(self):
        self.client.get("/")
        self.client.get("/api/products/")
        self.client.get("/api/categories/")

    @task(2)
    def view_catalog(self):
        self.client.get("/api/products/?category=Смартфоны")
        self.client.get("/api/products/?search=Apple")

    @task(1)
    def view_chat(self):
        self.client.post("/api/chat/query/", json={"message": "Какой айфон лучше?"})

    @task(1)
    def auth_flow(self):
        # Simulate checking metrics or profile page
        self.client.get("/api/subscriptions/plans/")
