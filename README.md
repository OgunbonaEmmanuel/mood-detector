# Mood Tracker

An experimental Streamlit webcam app that sends a captured frame to an OpenAI model, displays a facial-expression-based label, and reads the result aloud with local text-to-speech.

The project demonstrates webcam capture, multimodal prompting through LangChain, and speech output. Its labels are model guesses about visible expressions, not reliable measurements of a person's actual mood or mental health.

## Features

- Live video through Streamlit WebRTC, with microphone capture disabled.
- User-triggered analysis through a **Detect Mood** button.
- JPEG encoding and base64 image input.
- A `ChatOpenAI` client configured with `gpt-4o` and temperature 0.
- A prompt requesting one of 20 labels.
- Text output in Streamlit and spoken output through `pyttsx3`.

## Required source fixes before upload

### Load the API key from the environment

Remove the hardcoded API-key assignment from `app.py`. Revoke the exposed key and create a replacement. Add this before constructing `ChatOpenAI`:

```python
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY is not set.")
    st.stop()
```

Keep the replacement key only in your local `.env` or configured environment. Ignoring `.env` does not protect credentials embedded in Python source.

### Check for an available camera frame

The supplied code may access `image` before it is defined or try to use `.size` on `None`. Remove the earlier block that assigns `image` outside the button handler, and replace the button handler with:

```python
if st.button("Detect Mood"):
    processor = ctx.video_processor
    image = processor.frame if processor is not None else None

    if image is None or image.size == 0:
        st.warning("Start the camera and wait for a frame...")
    else:
        mood = predict_mood(image.copy()).strip()
        st.success(f"Expression-based estimate: {mood}")
        speak(f"The expression-based estimate is {mood}")
```

These snippets describe edits to apply to the supplied application; this documentation does not modify `app.py` automatically.

## Files

Place these files in the folder containing `app.py` (shown as `frontend` in the project screenshot):

| File | Purpose |
| --- | --- |
| `app.py` | Webcam, prediction, interface, and speech logic |
| `requirements.txt` | Python dependencies |
| `.env.example` | Placeholder configuration to copy locally |
| `.env` | Your private API key; excluded from Git |
| `.gitignore` | Excludes secrets, virtual environments, and caches |

## Setup

### 1. Create an environment

Run from the app folder:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

Dependencies are unpinned because tested versions were not supplied. Speech output also depends on a working speech engine and installed voices on the host computer.

### 3. Configure the key

Apply the source fixes above, then copy `.env.example` to `.env` and replace the placeholder:

```dotenv
OPENAI_API_KEY=your_replacement_api_key_here
```

Your API account needs access to the configured image-capable model. Model calls require internet access and may incur charges.

### 4. Run

```bash
python -m streamlit run app.py
```

Start the webcam component, grant camera access, wait for video to appear, and click **Detect Mood**.

## How it works

1. The video callback retains the latest frame as an OpenCV BGR array and returns the original video frame for display.
2. A button click selects an available frame.
3. OpenCV encodes the image as JPEG; Python encodes those bytes as base64.
4. A LangChain `HumanMessage` carries the prompt and image to the configured model.
5. The response appears on the page and is passed to `pyttsx3` for speech.

The prompt lists Happy, Sad, Angry, Fearful, Surprised, Disgusted, Neutral, Excited, Calm, Anxious, Confused, Bored, Frustrated, Relaxed, Worried, Embarrassed, Proud, Curious, Tired, and Amused. The application does not validate that the returned text belongs to this list.

## Privacy and limitations

- Clicking **Detect Mood** sends a JPEG of the captured frame to OpenAI. The supplied code does not save images to disk.
- A facial expression cannot establish someone's internal emotional state. Treat labels as experimental outputs rather than facts about the person.
- No accuracy evaluation, face-presence check, or confidence score is implemented.
- API inference and speech run synchronously after the button click; no background inference thread is implemented.
- `pyttsx3` speaks on the computer running Python, not through a browser audio player. Remote hosting would require a different speech-delivery approach.
- `voices[1]` assumes at least two installed voices. If unavailable, use an existing voice or remove the explicit voice selection.
- API failures and speech-engine errors are not handled by the supplied code.
- Hosted webcam access needs suitable browser permissions and WebRTC networking; the current app provides STUN configuration but no TURN relay.

The source was reviewed for documentation. The webcam, API call, and speech output were not executed during preparation.

## Dependencies

Streamlit provides the interface; streamlit-webrtc handles video; OpenCV handles image encoding; LangChain packages construct messages and call the model; pyttsx3 handles local speech; python-dotenv loads configuration after the key-loading fix. NumPy is included because the supplied application imports it, though it is not directly used.

Python's `os` and `base64` modules require no separate installation.
