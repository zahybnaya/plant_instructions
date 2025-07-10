import os
from groq import Groq

#read the file
def read_plant_care(filename): 
    try:
        with open(filename, encoding='UTF-8') as file:
            return file.read()
    except FileNotFoundError:
        print ("no file for u my dear")
        return None
    
    
#client message 
#if custom_prompt: 
#    message_content = "{custom_prompt}\n\n```python\n{file_content}\n```"
#
#else: 
#    print("nope")
    

#groq client - calling api
def analyze_python_file(filename, custom_prompt=None):
    client=Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    file_content = read_plant_care(filename)

    message_content = file_content

    chat_completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
            messages=[
        {
            "role": "user",
            "content": message_content
        }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    return chat_completion  



#import the file
if __name__ == "__main__":
    filename="plant_care.py"
    custom_prompt = input ("Enter your plant: ")

chat_completion = analyze_python_file(filename, custom_prompt)

if chat_completion:
    print(f"Analysis of '{filename}':")

    for chunk in chat_completion:
        print(chunk.choices[0].delta.content or "", end="")

    #analysing file + content of message
    print(f"Analysis of '{filename}':")

    print()  
else:
    print("Could not analyze the file.")




