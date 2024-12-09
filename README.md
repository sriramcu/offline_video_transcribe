# Locally Transcribe Videos and Analyse Transcriptions

A GUI based program to transcribe a video file and analyse the transcript without internet or API keys.

Run the GUI using `python video_local_transcribe.py`. Click on the 'Select Video' button and select a video file. 
Enter a prompt in the 'Enter Prompt' field and click 'Process Prompt'. Or click 'Transcribe Only' if you only want to transcribe the video.

The GUI will display the output in the 'Output' field.
Transcriptions will be saved to the 'transcriptions' folder. The file names of these will be based on the absolute path of the video file.

## Setup Instructions

1. Sign up for a HuggingFace account and setup an access token. Save this token for later use. 
2. Setup CUDA 12.1, CUDNN 9.3, PyTorch '2.4.1+cu121', transformers 4.47.0, use Python 3.10.
3. `pip install -r requirements.txt`
4. `pip install huggingface_hub` for logging in via the terminal/cmd.
5. Login to your HuggingFace account in your terminal/cmd where you are running the program, by running 
   `huggingface-cli login` and enter your access token saved earlier. 
6. Request access to the gated repo for `meta-llama/Llama-3.2-1B-Instruct` on the Huggingface portal, by filling in your details.