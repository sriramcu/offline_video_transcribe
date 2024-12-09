import os
import tkinter as tk
from tkinter import filedialog, messagebox
from transformers import pipeline
import torch

import whisper

# Load Whisper model globally to avoid reloading each time
MODEL = whisper.load_model("base")

# Constants
LLAMA_3_2_1B = "meta-llama/Llama-3.2-1B-Instruct"
LLAMA_3_2_3B = "meta-llama/Llama-3.2-3B-Instruct"
LLAMA_3_1_8B = "meta-llama/Llama-3.1-8B-Instruct"
DEFAULT_MODEL = LLAMA_3_2_1B
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.8
TOP_K = 50
TOP_P = 0.95
TRANSCRIPTION_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcriptions")


def ensure_transcription_folder_exists():
    """Ensure the folder for storing transcriptions exists."""
    if not os.path.exists(TRANSCRIPTION_FOLDER):
        os.makedirs(TRANSCRIPTION_FOLDER)


def generate_text_file(video_path):
    """Generate a transcription text file for the video."""
    ensure_transcription_folder_exists()

    # Create a filename based on the video's absolute path
    sanitized_name = video_path.replace('/', '_').replace('\\', '_').replace(":", "_") + ".txt"
    text_file_path = os.path.join(TRANSCRIPTION_FOLDER, sanitized_name)

    if os.path.exists(text_file_path):
        print(f"Transcription already exists: {text_file_path}")
        return text_file_path, True  # File already exists

    # Transcribe the video
    transcription_result = MODEL.transcribe(video_path)
    transcription_text = transcription_result.get("text", "")

    # Save the transcription to a text file
    with open(text_file_path, "w", encoding="utf-8") as f:
        f.write(transcription_text)

    return text_file_path, False  # File was newly created


def transcribe_only(video_path):
    """Handle the transcription-only logic."""
    if not video_path:
        messagebox.showerror("Error", "Please select a video file.")
        return

    text_file_path, exists = generate_text_file(video_path)
    if exists:
        messagebox.showinfo("Info", f"Transcription already exists: {text_file_path}")
    else:
        messagebox.showinfo("Success", f"Transcription saved to: {text_file_path}")


def respond_to_prompt(prompt, model_id=DEFAULT_MODEL):
    """
    Runs the generated prompt on the Llama model.
    """
    print("Generating response...")
    messages = [{"role": "user", "content": prompt}]
    pipe = pipeline(
        "text-generation",
        model=model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    outputs = pipe(
        messages,
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        top_k=TOP_K,
        top_p=TOP_P,
        do_sample=True,
    )
    result = outputs[0]["generated_text"][-1]['content']
    return result


def process_prompt(video_path, prompt):
    """Handle the transcription and prompt-based processing."""
    if not video_path:
        messagebox.showerror("Error", "Please select a video file.")
        return
    if not prompt.strip():
        messagebox.showerror("Error", "Please enter a prompt.")
        return

    # Generate the transcription file
    text_file_path, _ = generate_text_file(video_path)

    # Read the transcription from the file
    with open(text_file_path, "r", encoding="utf-8") as f:
        transcription_text = f.read()

    # Process the transcription with the prompt
    # Query the local LLM
    full_prompt = f"Video Transcription: {transcription_text}\n\nPrompt: {prompt}\n\nProvide a detailed response:"
    response = respond_to_prompt(full_prompt)
    result_output.delete("1.0", tk.END)
    result_output.insert("1.0", response)


# GUI Setup
root = tk.Tk()
root.title("Offline Video Transcription and Prompt Processor")

# File Picker
file_label = tk.Label(root, text="Selected Video:")
file_label.pack(anchor="w", padx=10, pady=(10, 0))

file_path_var = tk.StringVar()
file_path_entry = tk.Entry(root, textvariable=file_path_var, width=50, state="readonly")
file_path_entry.pack(anchor="w", padx=10)

def choose_file():
    path = filedialog.askopenfilename(
        filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv *.flv")]
    )
    if path:
        file_path_var.set(path)

file_picker_button = tk.Button(root, text="Select Video", command=choose_file)
file_picker_button.pack(anchor="w", padx=10, pady=(5, 10))

# Prompt Input
prompt_label = tk.Label(root, text="Enter Prompt:")
prompt_label.pack(anchor="w", padx=10)

prompt_entry = tk.Entry(root, width=50)
prompt_entry.pack(anchor="w", padx=10, pady=(5, 10))

# Result Output
result_label = tk.Label(root, text="Output:")
result_label.pack(anchor="w", padx=10)

result_output = tk.Text(root, height=10, width=60)
result_output.pack(anchor="w", padx=10, pady=(5, 10))

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(anchor="w", padx=10, pady=(10, 10))

transcribe_button = tk.Button(
    button_frame, text="Transcribe Only", command=lambda: transcribe_only(file_path_var.get())
)
transcribe_button.pack(side="left", padx=5)

process_button = tk.Button(
    button_frame, text="Process Prompt", command=lambda: process_prompt(file_path_var.get(), prompt_entry.get())
)
process_button.pack(side="left", padx=5)

root.mainloop()