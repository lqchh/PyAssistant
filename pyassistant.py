
import customtkinter
import tkinter as tk
import openai
import os
import speech_recognition as sr
import threading


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Define a global flag variable to control the listening loop

listening_flag = {"value": True}


# Initialize OpenAI API key
openai.api_key = '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'

root = customtkinter.CTk()
root.title("Chatbot Sign In")
root.geometry("500x350")

def login():
    global logged_in_username
    username = entry1.get()
    password = entry2.get()

    if check_credentials(username, password):
        logged_in_username = username
        save_credentials_if_remembered(username, password)
        root.withdraw()
        show_menu(username)
    else:
        print("Invalid credentials")

def save_credentials_if_remembered(username, password):
    # Check if the "Remember Me" checkbox is checked
    if check_var.get() == "on":
        with open("savedinfo.txt", "a") as file:
            file.write(f"Username: {username}\nPassword: {password}\n\n")

# Check if saved credentials exist and automatically log in
def auto_login():
    with open("savedinfo.txt", "r") as file:
        lines = file.readlines()
        if len(lines) >= 2:  # Check if there are at least two lines in the file
            last_username_line = lines[-2].strip().split(": ")
            last_password_line = lines[-1].strip().split(": ")
            if len(last_username_line) == 2 and len(last_password_line) == 2:
                last_username = last_username_line[1]
                last_password = last_password_line[1]
                if check_credentials(last_username, last_password):
                    logged_in_username = last_username
                    root.withdraw()
                    show_menu(last_username)

auto_login()

def check_credentials(username, password):
    with open("savedinfo.txt", "r") as file:
        lines = file.readlines()
        for i in range(0, len(lines), 3):
            saved_username = lines[i].strip().split(": ")[1]
            saved_password = lines[i+1].strip().split(": ")[1]
            if saved_username == username and saved_password == password:
                return True
        return False

def gpt3_completion(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].text.strip()





def start_listening(chat_history, user_input):
    def recognize_speech_thread():
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print('Listening...')

            while listening_flag[0]:
                audio = r.listen(source)

                try:
                    query = r.recognize_google(audio)
                    user_input.delete(0, tk.END)
                    user_input.insert(tk.END, query)

                    # Add the recognized message to the conversation history on the GPT-3 screen
                    chat_history.config(state=tk.NORMAL)
                    chat_history.insert(tk.END, "User: " + query + "\n")
                    chat_history.config(state=tk.DISABLED)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    pass

        print("Stopped listening")

    # Start speech recognition in a separate thread
    threading.Thread(target=recognize_speech_thread).start()

    # Start speech recognition in a separate thread
    threading.Thread(target=recognize_speech_thread).start()



def stop_listening():
    global listening_flag
    listening_flag = False
    print ("Stopped listening")


def show_menu(username):
    logged_in_root = customtkinter.CTk()
    logged_in_root.geometry("600x800")
    logged_in_root.title(f"{username}'s Chatbot")

    chat_history = tk.Text(logged_in_root, height=20, width=90, bg="#333333", fg="#f1f1f1", font=("Roboto", 12))
    chat_history.pack(pady=20)

    user_input = customtkinter.CTkEntry(logged_in_root, width=70, font=("Roboto", 12))
    user_input.pack()

    send_button = customtkinter.CTkButton(logged_in_root, text="Send", command=lambda: send_message(chat_history, user_input))
    send_button.pack(pady=10)

    save_button = customtkinter.CTkButton(logged_in_root, text="Save Chat", command=lambda: save_chat(chat_history, username))
    save_button.pack(pady=5)

    load_button = customtkinter.CTkButton(logged_in_root, text="Load Chat")
    load_button.pack(pady=5)
    
    load_menu = tk.Menu(logged_in_root, tearoff=0)
    load_button["menu"] = load_menu

    stop_button = customtkinter.CTkButton(logged_in_root, text="Stop Listening", command=stop_listening)
    stop_button.pack(pady=10)


    mic = customtkinter.CTkButton(logged_in_root, text="Mic", command=lambda: start_listening(chat_history, user_input))
    mic.pack(pady=10)
    
    load_chat_menu(chat_history, username, load_menu)

    logged_in_root.mainloop()



def load_chat_menu(chat_history, username, load_menu):
    chat_files = []
    for filename in os.listdir():
        if filename.startswith(f"{logged_in_username}_") and filename.endswith(".txt"):
            chat_files.append(filename)

    if not chat_files:
        print("No chat files found.")
        return

    for chat_file in chat_files:
        load_menu.add_command(label=chat_file, command=lambda f=chat_file: load_chat(chat_history, f))

def send_message(chat_history, user_input):
    message = user_input.get()
    user_input.delete(0, tk.END)

    chat_history.config(state="normal")
    chat_history.insert(tk.END, f"User: {message}\n")
    chat_history.config(state="disabled")

    # Read the content of "prompt.txt"
    with open("prompt.txt", 'r') as file:
        prompt = file.read()
    prompt = prompt + f"User:{message}\nAI:"

    ai_response = gpt3_completion(prompt)
    chat_history.config(state="normal")
    chat_history.insert(tk.END, f"AI: {ai_response}\n")
    chat_history.config(state="disabled")

def save_chat(chat_history, username):
    chat_content = chat_history.get("1.0", tk.END)
    chat_name = tk.simpledialog.askstring("Chat Name", "Enter a name for the chat:")
    if chat_name:
        with open(f"{logged_in_username}_{chat_name}.txt", "w") as file:
            file.write(chat_content)

def load_chat(chat_history, chat_filename):
    try:
        with open(chat_filename, "r") as file:
            chat_content = file.read()
            chat_history.config(state="normal")
            chat_history.delete("1.0", tk.END)
            chat_history.insert(tk.END, chat_content)
            chat_history.config(state="disabled")
    except FileNotFoundError:
        print("Chat history not found.")












logged_in_username = None



frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="Sign In")
label.pack(pady=12, padx=10)

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="Username")
entry1.pack(pady=12, padx=10)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text="Password", show="")
entry2.pack(pady=15, padx=10)

check_var = customtkinter.StringVar(value="on")

def showpassword():
    if check_var.get() == "on":
        entry2.configure(show="")  # Show password characters
    else:
        entry2.configure(show="*")  # Hide password characters
  # Hide password characters

# Create the checkbox
checkbox = customtkinter.CTkCheckBox(root, text="Show Password", command=showpassword,
                                     variable=check_var, onvalue="on", offvalue="off")
checkbox.pack()


login_button = customtkinter.CTkButton(master=frame, text="Log In", command=login)
login_button.pack(pady=12, padx=10)

remember_me_checkbox = customtkinter.CTkCheckBox(root, text="Remember Me", variable=check_var, onvalue="on", offvalue="off")
remember_me_checkbox.pack(pady=5)


auto_login()




root.mainloop()
