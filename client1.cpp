// ===============================
// 💬 FriendDFriends - User1 Client (Enhanced UI + Logic)
// ===============================
#include <iostream>
#include <string>
#include <ctime>
#include <curl/curl.h>
#include <windows.h>
#include <iomanip>

std::string SERVER_URL = "http://127.0.0.1:5000";

// 🎨 Console Colors
#define RESET   "\033[0m"
#define CYAN    "\033[36m"
#define GREEN   "\033[32m"
#define RED     "\033[31m"
#define YELLOW  "\033[33m"
#define MAGENTA "\033[35m"
#define BLUE    "\033[34m"

// 🕒 Current Time
std::string currentTime() {
    time_t now = time(0);
    tm* ltm = localtime(&now);
    char buffer[9];
    sprintf(buffer, "%02d:%02d:%02d", ltm->tm_hour, ltm->tm_min, ltm->tm_sec);
    return std::string(buffer);
}

// 📦 Write callback for cURL
static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

// 📨 Send Message
void sendMessage(const std::string& sender, const std::string& receiver, const std::string& text) {
    CURL* curl = curl_easy_init();
    if (curl) {
        std::string json = "{\"sender\":\"" + sender + "\",\"receiver\":\"" + receiver + "\",\"text\":\"" + text + "\"}";
        curl_easy_setopt(curl, CURLOPT_URL, (SERVER_URL + "/send").c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json.c_str());
        struct curl_slist* headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        std::cout << MAGENTA << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << RESET << "\n";
        std::cout << BLUE << "📤 Sending message..." << RESET << "\n";

        CURLcode res = curl_easy_perform(curl);
        if (res == CURLE_OK) {
            std::cout << GREEN << "✅ Delivered successfully!" << RESET << "\n";
            Beep(900, 100);
        } else {
            std::cout << RED << "❌ Failed to send message!" << RESET << "\n";
        }

        curl_easy_cleanup(curl);
    }
}

// 📥 Fetch messages
void fetchMessages(const std::string& username) {
    CURL* curl = curl_easy_init();
    if (curl) {
        std::string readBuffer;
        curl_easy_setopt(curl, CURLOPT_URL, (SERVER_URL + "/messages/" + username).c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
        CURLcode res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);

        if (!readBuffer.empty() && readBuffer.find("text") != std::string::npos) {
            std::cout << YELLOW << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << RESET << "\n";
            std::cout << CYAN << "💬 New message received (" << currentTime() << ")\n" << RESET;
            std::cout << BLUE << readBuffer << RESET << "\n";
            std::cout << YELLOW << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" << RESET;
            Beep(700, 120);
        }
    }
}

int main() {
    std::string sender = "user1";
    std::string receiver = "user2";
    std::string text;

    // ✨ Startup Screen
    system("cls");
    std::cout << CYAN;
    std::cout << "=====================================\n";
    std::cout << "  💬 FriendDFriends Chat (User1)\n";
    std::cout << "=====================================\n" << RESET;
    std::cout << YELLOW << "Type 'exit' to quit.\n" << RESET;
    std::cout << GREEN << "Connected as " << sender << " → chatting with " << receiver << "\n" << RESET;

    // 🔄 Main chat loop
    while (true) {
        std::cout << GREEN << "\n[" << currentTime() << "] You: " << RESET;
        std::getline(std::cin, text);

        if (text == "exit") {
            std::cout << RED << "🚪 Chat closed.\n" << RESET;
            break;
        }

        if (text.empty()) continue;

        sendMessage(sender, receiver, text);
        Sleep(1200);  // wait a bit
        fetchMessages(sender);
    }

    return 0;
}