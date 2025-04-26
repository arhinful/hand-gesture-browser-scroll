let ws = null;
let reconnectInterval = 5000; // 5 seconds

const scrollDown = () => {
  // Get the active tab in the current window
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tab = tabs[0]; // Get the active tab

    if (!tab || tab.url.startsWith("chrome://") || tab.url.startsWith("about://")) {
      console.log("❌ No valid tab found or on a restricted page.");
      return;
    }

    const tabId = tab.id;

    // Inject the script into the active tab
    chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: () => {
        window.scrollBy({
          top: 40,
          behavior: 'smooth'
        });
        console.log("scrolled YH")
      }
    }).catch(err => {
      console.error("❌ Error executing script:", err);
    });
  });
};
const scrollUp = () => {
  // Get the active tab in the current window
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tab = tabs[0]; // Get the active tab

    if (!tab || tab.url.startsWith("chrome://") || tab.url.startsWith("about://")) {
      console.log("❌ No valid tab found or on a restricted page.");
      return;
    }

    const tabId = tab.id;

    // Inject the script into the active tab
    chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: () => {
        window.scrollBy({
          top: -40,
          behavior: 'smooth'
        });
        console.log("scrolled YH")
      }
    }).catch(err => {
      console.error("❌ Error executing script:", err);
    });
  });
};

const connectWebSocket = () => {
  ws = new WebSocket("ws://localhost:8765");

  ws.onopen = () => {
    console.log("✅ Connected to Python WebSocket");
  };

  ws.onmessage = (event) => {
    console.log("received data: ", event.data)
    console.log("re: ", "scroll-down" === event.data)
    if ("Scroll-Down" === event.data){
      scrollDown()
    }
    if ("Scroll-Up" === event.data){
      scrollUp()
    }
  };

  ws.onerror = (error) => {
    console.error("❌ WebSocket error:", error);
  };

  ws.onclose = () => {
    console.warn("🔌 WebSocket connection closed.");
    setTimeout(connectWebSocket, reconnectInterval); // Reconnect after delay
  };
};

chrome.action.onClicked.addListener(() => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    console.log("🟢 WebSocket already connected. Sending message...");
    ws.send("User clicked again");
  } else {
    connectWebSocket(); // Connect WebSocket if not already connected
  }
});
