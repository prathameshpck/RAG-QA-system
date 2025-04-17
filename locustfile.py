# from locust import HttpUser, task, between 

# class ChatUser(HttpUser):
#     wait_time = between(1,2)

#     @task
#     def send_single_message(self):
#         payload = {
#             "model": "Qwen/Qwen2.5-3B-Instruct-GPTQ-Int8",
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": "What are mitochondria?"
#                 }
#             ]
#         }
#         with self.client.post(
#             "/v1/chat/completions",
#             json=payload,
#             headers={"Content-Type": "application/json"},
#             catch_response=True
#         ) as response:
#             if response.status_code != 200:
#                 response.failure(f"Failed: {response.status_code}")
#             else:
#                 response.success()
        
from locust import HttpUser, task, between
import time

class RAGUser(HttpUser):
    wait_time = between(1, 2)  # Simulates user think time between messages

    @task
    def multi_turn_chat(self):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        user_prompts = [
            "What is neuroplasticity?",
            "How does it change with age?",
            "Can it be improved with training?",
            "Does sleep affect it?",
            "Summarize in two lines."
        ]

        total_latency = 0

        for prompt in user_prompts:
            messages.append({"role": "user", "content": prompt})

            start = time.time()
            with self.client.post(
                "/v1/chat/completions",
                json={"model": "Qwen/Qwen2.5-0.5B-Instruct", "messages": messages},
                catch_response=True
            ) as response:
                end = time.time()
                latency = end - start
                total_latency += latency

                if response.status_code == 200:
                    try:
                        reply = response.json()["choices"][0]["message"]["content"]
                        messages.append({"role": "assistant", "content": reply})
                        response.success()
                    except Exception as e:
                        response.failure(f"Malformed response: {e}")
                else:
                    response.failure(f"Status {response.status_code}: {response.text}")

        avg_latency = total_latency / len(user_prompts)
        print(f"[User] Avg latency for 5-turn chat: {avg_latency:.3f} seconds")
