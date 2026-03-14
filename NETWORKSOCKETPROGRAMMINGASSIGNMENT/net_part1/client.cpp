// client.cpp
// Build: g++ -std=c++17 -O2 -o client client.cpp

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <chrono>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <nlohmann/json.hpp>

class WordClient {
private:
    std::string server_ip;
    int server_port = 0;
    int k = 5;
    int p = 0;
    int num_iterations = 1;
    bool quiet_mode = false;

    void loadConfig(const std::string& config_file) {
        std::ifstream file(config_file);
        if (!file.is_open()) {
            std::cerr << "Error: Cannot open config file " << config_file << std::endl;
            exit(1);
        }

        nlohmann::json config;
        file >> config;
        file.close();

        server_ip = config.value("server_ip", "127.0.0.1");
        server_port = config.value("server_port", 5000);
        k = config.value("k", k);
        p = config.value("p", p);
        num_iterations = config.value("num_iterations", num_iterations);

        if (!quiet_mode) {
            std::cout << "Client config: Server=" << server_ip << ":" << server_port
                      << ", k=" << k << ", p=" << p << ", iterations=" << num_iterations << std::endl;
        }
    }

    std::vector<std::string> requestWords(int offset, int count) {
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            std::cerr << "Socket creation error" << std::endl;
            return {};
        }

        struct sockaddr_in serv_addr;
        std::memset(&serv_addr, 0, sizeof(serv_addr));
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(server_port);

        if (inet_pton(AF_INET, server_ip.c_str(), &serv_addr.sin_addr) <= 0) {
            std::cerr << "Invalid address/ Address not supported: " << server_ip << std::endl;
            close(sock);
            return {};
        }

        if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
            std::cerr << "Connection Failed to " << server_ip << ":" << server_port << " (" << strerror(errno) << ")" << std::endl;
            close(sock);
            return {};
        }

        std::string request = std::to_string(offset) + "," + std::to_string(count) + "\n";
        send(sock, request.c_str(), request.length(), 0);

        char buffer[8192];
        ssize_t valread = read(sock, buffer, sizeof(buffer) - 1);
        close(sock);
        if (valread <= 0) return {};

        buffer[valread] = '\0';
        std::string response(buffer);
        // Trim newline(s)
        while (!response.empty() && (response.back() == '\n' || response.back() == '\r')) response.pop_back();

        if (response == "EOF") return {};

        std::vector<std::string> res;
        std::stringstream ss(response);
        std::string token;
        while (std::getline(ss, token, ',')) {
            if (token == "EOF") break;
            res.push_back(token);
        }
        return res;
    }

    void printWordFrequencies(const std::map<std::string, int>& freq) {
        if (!quiet_mode) {
            std::cout << "\nWord Frequencies:" << std::endl;
            for (const auto& p : freq) {
                std::cout << p.first << ", " << p.second << std::endl;
            }
        }
    }

public:
    WordClient(const std::string& config_file, bool quiet = false) : quiet_mode(quiet) {
        loadConfig(config_file);
    }

    void setK(int new_k) { k = new_k; }

    void run() {
        auto start_time = std::chrono::high_resolution_clock::now();

        std::map<std::string, int> word_frequencies;
        int current_offset = p;

        while (true) {
            std::vector<std::string> words = requestWords(current_offset, k);

            if (words.empty()) break;

            for (const auto& w : words) {
                word_frequencies[w]++;
            }

            current_offset += (int)words.size();

            if ((int)words.size() < k) break;
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);

        printWordFrequencies(word_frequencies);

        // Print elapsed time in a parse-friendly format
        std::cout << "ELAPSED_MS:" << duration.count() << std::endl;
    }
};

int main(int argc, char* argv[]) {
    std::string config_file = "config.json";
    bool quiet_mode = false;
    int override_k = -1;

    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--config" && i + 1 < argc) {
            config_file = argv[++i];
        } else if (a == "--quiet") {
            quiet_mode = true;
        } else if (a == "--k" && i + 1 < argc) {
            override_k = std::stoi(argv[++i]);
        }
    }

    try {
        WordClient client(config_file, quiet_mode);
        if (override_k > 0) client.setK(override_k);
        client.run();
    } catch (const std::exception& e) {
        std::cerr << "Client error: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
