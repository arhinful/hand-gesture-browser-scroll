# ✋ Hand Gesture Recognition App (WebSocket + Chrome Extension)

This Python-based application uses OpenCV and MediaPipe to recognize hand gestures via webcam and streams the recognized gestures over WebSocket. It also integrates with a Chrome Extension via Native Messaging.

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
```

Activate it:

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

## 🧩 Set Up the Chrome Extension

1. Open **Google Chrome**.
2. Navigate to `chrome://extensions/`.
3. Enable **Developer mode** (top right).
4. Click **“Load unpacked”** and select the `chrome-extension` folder from the project.
5. Chrome will now load your custom extension.

---

## 🖥️ Run the App

Start the app with:

```bash
python app.py
```

This will:
- Launch the webcam for gesture detection.
- Start a WebSocket server on `ws://localhost:8765`.
- Automatically add a Windows registry entry for the native messaging host.

---

## 🔄 Pull Updates from GitHub

```bash
git pull origin main
```

---

## 📁 File Structure

```
├── app.py
├── model/
├── chrome-extension/
├── com.gs.app.json
├── keypoint_classifier_label.csv
├── set-registry.reg
├── requirements.txt
└── README.md
```

---

## ⚠️ Notes

- Native Messaging works only on **Windows**.
- Ensure your webcam is connected before running the app.
- Tested with **Python 3.10+**.

---

## 👨‍💻 Author

**Emmanuel Arhinful**  
[GitHub Profile](https://github.com/arhinful)
