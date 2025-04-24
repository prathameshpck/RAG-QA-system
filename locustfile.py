# # from locust import HttpUser, task, between 

# # class ChatUser(HttpUser):
# #     wait_time = between(1,2)

# #     @task
# #     def send_single_message(self):
# #         payload = {
# #             "model": "Qwen/Qwen2.5-3B-Instruct-GPTQ-Int8",
# #             "messages": [
# #                 {
# #                     "role": "user",
# #                     "content": "What are mitochondria?"
# #                 }
# #             ]
# #         }
# #         with self.client.post(
# #             "/v1/chat/completions",
# #             json=payload,
# #             headers={"Content-Type": "application/json"},
# #             catch_response=True
# #         ) as response:
# #             if response.status_code != 200:
# #                 response.failure(f"Failed: {response.status_code}")
# #             else:
# #                 response.success()
        
# from locust import HttpUser, task, between
# import time

# class RAGUser(HttpUser):
#     wait_time = between(1, 2)  # Simulates user think time between messages

#     @task
#     def multi_turn_chat(self):
#         messages = [
#             {"role": "system", "content": "You are a helpful assistant."}
#         ]
        
#         user_prompts = [
#             "What is neuroplasticity?",
#             "How does it change with age?",
#             "Can it be improved with training?",
#             "Does sleep affect it?",
#             "Summarize in two lines."
#         ]

#         total_latency = 0

#         for prompt in user_prompts:
#             messages.append({"role": "user", "content": prompt})

#             start = time.time()
#             with self.client.post(
#                 "/v1/chat/completions",
#                 json={"model": "Qwen/Qwen2.5-0.5B-Instruct", "messages": messages},
#                 catch_response=True
#             ) as response:
#                 end = time.time()
#                 latency = end - start
#                 total_latency += latency

#                 if response.status_code == 200:
#                     try:
#                         reply = response.json()["choices"][0]["message"]["content"]
#                         messages.append({"role": "assistant", "content": reply})
#                         response.success()
#                     except Exception as e:
#                         response.failure(f"Malformed response: {e}")
#                 else:
#                     response.failure(f"Status {response.status_code}: {response.text}")

#         avg_latency = total_latency / len(user_prompts)
#         print(f"[User] Avg latency for 5-turn chat: {avg_latency:.3f} seconds")

from locust import HttpUser, task, between
import time
import json

class SSEChatUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def chat_with_streaming(self):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain how neuroplasticity works."}
        ]

        payload = {
            "model": "Qwen/Qwen2.5-0.5B-Instruct",
            "messages": messages
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

        try:
            start = time.time()
            first_token_time = None
            token_count = 0

            with self.client.post("/v1/chat/completions", json=payload, headers=headers, stream=True, catch_response=True) as response:
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith("data:"):
                        content = line[5:].strip()

                        if content == "[DONE]":
                            break
                        if not content:
                            continue

                        try:
                            parsed = json.loads(content)  # ✅ fixed
                            delta = parsed["choices"][0]["delta"]["content"]
                            token_count += 1

                            if first_token_time is None:
                                first_token_time = time.time()

                        except Exception as e:
                            response.failure(f"Malformed SSE line: {e}")
                            return

                total_time = time.time() - start
                first_latency = (first_token_time - start) if first_token_time else total_time

                print(f"[User] First token latency: {first_latency:.3f}s, Tokens: {token_count}, Total time: {total_time:.3f}s")
                response.success()

        except Exception as e:
            print(f"[User] Request failed: {e}")
