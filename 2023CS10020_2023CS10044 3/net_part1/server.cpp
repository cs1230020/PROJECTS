// server.cpp
// Build: g++ -std=c++17 -O2 -o server server.cpp

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>
#include <cstring>
#include <cerrno>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <nlohmann/json.hpp>

class WordServer {
private:
    std::vector<std::string> words;
    int server_fd = -1;
    struct sockaddr_in address;
    std::string filename;
    int port = 0;
    std::string server_ip;

    static std::string trim(const std::string& s) {
        const char* ws = " \t\r\n";
        size_t start = s.find_first_not_of(ws);
        if (start == std::string::npos) return "";
        size_t end = s.find_last_not_of(ws);
        return s.substr(start, end - start + 1);
    }

    void loadWords() {
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "Error: Cannot open file " << filename << std::endl;
            exit(1);
        }

        std::string line;
        // Read entire file as single comma-separated line(s)
        std::string content;
        while (std::getline(file, line)) {
            if (!content.empty()) content += ",";
            content += line;
        }
        file.close();

        std::stringstream ss(content);
        std::string word;
        while (std::getline(ss, word, ',')) {
            std::string t = trim(word);
            if (!t.empty()) words.push_back(t);
        }
        std::cout << "Loaded " << words.size() << " words from " << filename << std::endl;
    }

    void loadConfig(const std::string& config_file) {
        std::ifstream file(config_file);
        if (!file.is_open()) {
            std::cerr << "Error: Cannot open config file " << config_file << std::endl;
            exit(1);
        }

        nlohmann::json config;
        file >> config;
        file.close();

        // use value() to provide defaults if keys missing
        server_ip = config.value("server_ip", "0.0.0.0");
        port = config.value("server_port", 5000);
        filename = config.value("filename", "words.txt");

        std::cout << "Server config: IP=" << server_ip << ", Port=" << port << ", File=" << filename << std::endl;
    }

public:
    WordServer(const std::string& config_file) {
        loadConfig(config_file);
        loadWords();

        // Create socket
        if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
            perror("socket failed");
            exit(1);
        }

        // Allow rebind
        int opt = 1;
        if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
            perror("setsockopt(SO_REUSEADDR) failed");
        }
#ifdef SO_REUSEPORT
        if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt)) < 0) {
            perror("setsockopt(SO_REUSEPORT) failed");
        }
#endif

        // Zero address and set
        std::memset(&address, 0, sizeof(address));
        address.sin_family = AF_INET;
        address.sin_port = htons(port);

        if (server_ip.empty() || server_ip == "0.0.0.0") {
            address.sin_addr.s_addr = INADDR_ANY;
        } else {
            if (inet_pton(AF_INET, server_ip.c_str(), &address.sin_addr) <= 0) {
                std::cerr << "Warning: invalid server_ip '" << server_ip << "' - binding to INADDR_ANY" << std::endl;
                address.sin_addr.s_addr = INADDR_ANY;
            }
        }

        if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
            perror("bind failed");
            close(server_fd);
            exit(1);
        }

        if (listen(server_fd, 10) < 0) {
            perror("listen");
            close(server_fd);
            exit(1);
        }

        std::cout << "Server listening on " << server_ip << ":" << port << std::endl;
    }

    std::string handleRequest(int offset, int k) {
        std::stringstream response;

        if (offset >= (int)words.size()) {
            response << "EOF\n";
            return response.str();
        }

        int end_pos = std::min(offset + k, (int)words.size());
        bool eof_reached = (end_pos == (int)words.size() && (end_pos - offset) < k);

        for (int i = offset; i < end_pos; i++) {
            response << words[i];
            if (i < end_pos - 1) response << ",";
        }

        if (eof_reached) {
            response << ",EOF";
        }

        response << "\n";
        return response.str();
    }

    void run() {
        while (true) {
            int new_socket;
            socklen_t addrlen = sizeof(address);

            std::cout << "Waiting for connection..." << std::endl;
            if ((new_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen)) < 0) {
                perror("accept");
                continue;
            }
            std::cout << "Client connected" << std::endl;

            // Read client request
            std::string received;
            char buffer[4096];
            ssize_t r;
            // read until newline or EOF
            r = read(new_socket, buffer, sizeof(buffer) - 1);
            if (r <= 0) {
                close(new_socket);
                std::cout << "Client disconnected (no data)\n" << std::endl;
                continue;
            }
            buffer[r] = '\0';
            received = std::string(buffer);
            // Trim trailing newline
            if (!received.empty() && (received.back() == '\n' || received.back() == '\r')) {
                while (!received.empty() && (received.back() == '\n' || received.back() == '\r')) received.pop_back();
            }

            std::cout << "Received request: " << received << std::endl;

            size_t comma_pos = received.find(',');
            if (comma_pos != std::string::npos) {
                int offset = std::stoi(received.substr(0, comma_pos));
                int k = std::stoi(received.substr(comma_pos + 1));
                std::cout << "Request: offset=" << offset << ", k=" << k << std::endl;
                std::string response = handleRequest(offset, k);
                ssize_t s = send(new_socket, response.c_str(), response.size(), 0);
                if (s < 0) perror("send");
                std::cout << "Sent response: " << response;
            } else {
                std::string error_response = "Error: Invalid request format\n";
                send(new_socket, error_response.c_str(), error_response.length(), 0);
            }

            close(new_socket);
            std::cout << "Client disconnected\n" << std::endl;
        }
    }

    ~WordServer() {
        if (server_fd >= 0) close(server_fd);
    }
};

int main(int argc, char* argv[]) {
    std::string config_file = "config.json";
    for (int i = 1; i < argc; ++i) {
        if (std::string(argv[i]) == "--config" && i + 1 < argc) {
            config_file = argv[i + 1];
            ++i;
        }
    }

    try {
        WordServer server(config_file);
        server.run();
    } catch (const std::exception& e) {
        std::cerr << "Server error: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
