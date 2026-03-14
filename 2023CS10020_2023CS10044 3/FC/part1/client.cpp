#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <map>
#include <vector>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <chrono>
#include <json/json.h> // You'll need to install jsoncpp: sudo apt-get install libjsoncpp-dev

using namespace std;
using namespace std::chrono;

struct Config {
    string server_ip;
    int server_port;
    int k;
    int p;
    string filename;
    int num_repetitions;
};

// Function to parse config.json
Config parseConfig(const string& configFile) {
    Config config;
    ifstream file(configFile);
    Json::Value root;
    Json::Reader reader;
    
    if (!reader.parse(file, root)) {
        cerr << "Error parsing config.json" << endl;
        exit(1);
    }
    
    config.server_ip = root["server_ip"].asString();
    config.server_port = root["server_port"].asInt();
    config.k = root["k"].asInt();
    config.p = root["p"].asInt();
    config.filename = root["filename"].asString();
    config.num_repetitions = root["num_repetitions"].asInt();
    
    return config;
}

// Function to split string by delimiter
vector<string> split(const string& str, char delimiter) {
    vector<string> tokens;
    stringstream ss(str);
    string token;
    
    while (getline(ss, token, delimiter)) {
        if (!token.empty()) {
            tokens.push_back(token);
        }
    }
    
    return tokens;
}

// Function to count word frequencies
map<string, int> countWords(const vector<string>& words) {
    map<string, int> wordCount;
    
    for (const string& word : words) {
        // Trim whitespace
        string trimmed = word;
        trimmed.erase(0, trimmed.find_first_not_of(" \t\r\n"));
        trimmed.erase(trimmed.find_last_not_of(" \t\r\n") + 1);
        
        if (!trimmed.empty() && trimmed != "EOF") {
            wordCount[trimmed]++;
        }
    }
    
    return wordCount;
}

// Function to download words from server
vector<string> downloadWords(const Config& config) {
    vector<string> allWords;
    int offset = config.p;
    bool done = false;
    
    while (!done) {
        // Create socket
        int sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (sockfd < 0) {
            cerr << "Error creating socket" << endl;
            exit(1);
        }
        
        // Server address setup
        struct sockaddr_in serverAddr;
        memset(&serverAddr, 0, sizeof(serverAddr));
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(config.server_port);
        
        if (inet_pton(AF_INET, config.server_ip.c_str(), &serverAddr.sin_addr) <= 0) {
            cerr << "Invalid address" << endl;
            close(sockfd);
            exit(1);
        }
        
        // Connect to server
        if (connect(sockfd, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
            cerr << "Connection failed" << endl;
            close(sockfd);
            exit(1);
        }
        
        // Send request: p,k\n
        string request = to_string(offset) + "," + to_string(config.k) + "\n";
        if (send(sockfd, request.c_str(), request.length(), 0) < 0) {
            cerr << "Send failed" << endl;
            close(sockfd);
            exit(1);
        }
        
        // Receive response
        char buffer[4096];
        memset(buffer, 0, sizeof(buffer));
        string response;
        
        // Read until we get a newline
        while (response.find('\n') == string::npos) {
            int bytesReceived = recv(sockfd, buffer, sizeof(buffer) - 1, 0);
            if (bytesReceived <= 0) {
                break;
            }
            buffer[bytesReceived] = '\0';
            response += buffer;
        }
        
        // Remove the newline
        if (!response.empty() && response.back() == '\n') {
            response.pop_back();
        }
        
        // Close connection
        close(sockfd);
        
        // Parse response
        vector<string> words = split(response, ',');
        
        // Check for EOF
        bool hasEOF = false;
        for (const string& word : words) {
            string trimmed = word;
            trimmed.erase(0, trimmed.find_first_not_of(" \t\r\n"));
            trimmed.erase(trimmed.find_last_not_of(" \t\r\n") + 1);
            
            if (trimmed == "EOF") {
                hasEOF = true;
                done = true;
            } else if (!trimmed.empty()) {
                allWords.push_back(trimmed);
            }
        }
        
        // If we got EOF as the only response, we're done
        if (words.size() == 1 && hasEOF) {
            done = true;
        }
        
        // Update offset for next request
        if (!done) {
            offset += config.k;
        }
    }
    
    return allWords;
}

// Function to print word frequencies
void printWordFrequencies(const map<string, int>& wordCount) {
    for (const auto& pair : wordCount) {
        cout << pair.first << ", " << pair.second << endl;
    }
}

int main(int argc, char* argv[]) {
    // Parse config
    Config config = parseConfig("config.json");
    
    // Start timing
    auto start = high_resolution_clock::now();
    
    // Download words
    vector<string> words = downloadWords(config);
    
    // Count word frequencies
    map<string, int> wordCount = countWords(words);
    
    // End timing
    auto end = high_resolution_clock::now();
    //auto duration = duration_cast<milliseconds>(end - start);
    
    // Print word frequencies
    printWordFrequencies(wordCount);
    
    // For analysis, you might want to output timing to a file
    // Uncomment the following lines if needed for analysis
    /*
    ofstream timeFile("timing.csv", ios::app);
    timeFile << config.k << "," << duration.count() << endl;
    timeFile.close();
    */
    
    return 0;
}