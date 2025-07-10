import os
from groq import Groq

client=Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


chat_completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
        messages=[
      {
        "role": "user",
        "content": ""
      }
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

for chunk in chat_completion:
    print(chunk.choices[0].delta.content or "", end="")



