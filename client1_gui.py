import customtkinter as ctk
import requests
import threading
import time

SERVER_URL = "http://127.0.0.1:5000"
SENDER = "user1"
RECEIVER = "user2"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"💬 FriendDFriends - {SENDER}")
        self.geometry("500x620")
        self.resizable(False, False)

        # Header
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#1e1e2f", height=60)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"👤 {RECEIVER}", font=("Arial", 18, "bold")).pack(side="left", padx=15, pady=15)
        self.status_label = ctk.CTkLabel(header, text="🟢 Online", text_color="lightgreen")
        self.status_label.pack(side="right", padx=15, pady=15)

        # Chat display
        self.chat_frame = ctk.CTkScrollableFrame(self, width=480, height=460, corner_radius=10)
        self.chat_frame.pack(pady=10)

        # Entry + Send Button
        entry_frame = ctk.CTkFrame(self, fg_color="#222", corner_radius=10)
        entry_frame.pack(pady=10, fill="x", padx=10)
        self.message_entry = ctk.CTkEntry(entry_frame, placeholder_text="Type a message...", width=380)
        self.message_entry.pack(side="left", padx=10, pady=8)
        self.send_button = ctk.CTkButton(entry_frame, text="📤 Send", command=self.send_message)
        self.send_button.pack(side="right", padx=5)

        # Thread control
        self.running = True
        self.displayed_ids = set()
        threading.Thread(target=self.poll_messages, daemon=True).start()

    def add_message_bubble(self, text, sender_type, timestamp=None):
        timestamp = timestamp or ""
        bubble_frame = ctk.CTkFrame(self.chat_frame, corner_radius=15)
        bubble_frame.pack(anchor="e" if sender_type == "sent" else "w", pady=5, padx=10)

        color = "#0078FF" if sender_type == "sent" else "#333"
        text_color = "white"
        msg_label = ctk.CTkLabel(
            bubble_frame,
            text=text,
            fg_color=color,
            corner_radius=12,
            text_color=text_color,
            wraplength=300,
            justify="left",
            padx=10,
            pady=6
        )
        msg_label.pack(anchor="e" if sender_type == "sent" else "w")
        time_label = ctk.CTkLabel(bubble_frame, text=timestamp, text_color="gray", font=("Arial", 10))
        time_label.pack(anchor="e" if sender_type == "sent" else "w")

        self.chat_frame._parent_canvas.yview_moveto(1)

    def send_message(self):
        text = self.message_entry.get().strip()
        if not text:
            return
        payload = {"sender": SENDER, "receiver": RECEIVER, "text": text}
        try:
            res = requests.post(f"{SERVER_URL}/send", json=payload, timeout=5)
            if res.status_code == 200:
                try:
                    msg_data = res.json()
                    text_to_show = msg_data.get("text", text)
                    timestamp = msg_data.get("timestamp")
                except:
                    text_to_show = text
                    timestamp = None
                self.add_message_bubble(text_to_show, "sent", timestamp)
                self.message_entry.delete(0, "end")
                self.status_label.configure(text="🟢 Online", text_color="lightgreen")
            else:
                self.status_label.configure(text=f"⚠️ Failed to send ({res.status_code})", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"❌ Server not reachable: {e}", text_color="red")

    def poll_messages(self):
        while self.running:
            try:
                res = requests.get(f"{SERVER_URL}/messages/{SENDER}", timeout=5)
                if res.status_code == 200:
                    try:
                        messages = res.json()
                        if not isinstance(messages, list):
                            messages = []
                    except:
                        messages = []
                    for msg in messages:
                        if msg["id"] not in self.displayed_ids and msg["sender"] == RECEIVER:
                            self.displayed_ids.add(msg["id"])
                            self.add_message_bubble(msg["text"], "recv", msg.get("timestamp"))
                    self.status_label.configure(text="🟢 Online", text_color="lightgreen")
                else:
                    self.status_label.configure(text=f"⚠️ Server error ({res.status_code})", text_color="red")
            except Exception as e:
                self.status_label.configure(text=f"🔴 Disconnected: {e}", text_color="red")
            time.sleep(1.5)

    def on_close(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = ChatApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()