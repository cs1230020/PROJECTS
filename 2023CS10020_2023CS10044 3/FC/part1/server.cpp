#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <vector>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <signal.h>
#include <json/json.h>

using namespace std;

// Global flag for graceful shutdown
volatile bool keepRunning = true;

// Signal handler for graceful shutdown
void signalHandler(int signum) {
    keepRunning = false;
}

struct Config {
    string server_ip;
    int server_port;
    string filename;
};

// Parse config.json
Config parseConfig(const string& configFile) {
    Config config;
    ifstream file(configFile);
    if (!file.is_open()) {
        cerr << "Error opening config file: " << configFile << endl;
        exit(1);
    }
    
    Json::Value root;
    Json::Reader reader;
    
    if (!reader.parse(file, root)) {
        cerr << "Error parsing config.json: " << reader.getFormattedErrorMessages() << endl;
        exit(1);
    }
    
    config.server_ip = root["server_ip"].asString();
    config.server_port = root["server_port"].asInt();
    config.filename = root["filename"].asString();
    
    file.close();
    return config;
}

// Load words from file
vector<string> loadWords(const string& filename) {
    vector<string> words;
    ifstream file(filename);
    
    if (!file.is_open()) {
        cerr << "Error opening words file: " << filename << endl;
        exit(1);
    }
    
    string line;
    // Read the entire file
    while (getline(file, line)) {
        // Split by comma
        stringstream ss(line);
        string word;
        
        while (getline(ss, word, ',')) {
            // Trim whitespace
            size_t start = word.find_first_not_of(" \t\r\n");
            size_t end = word.find_last_not_of(" \t\r\n");
            
            if (start != string::npos && end != string::npos) {
                word = word.substr(start, end - start + 1);
                if (!word.empty()) {
                    words.push_back(word);
                }
            }
        }
    }
    
    file.close();
    cout << "Server: Loaded " << words.size() << " words from " << filename << endl;
    return words;
}

// Parse client request (p,k\n format)
pair<int, int> parseRequest(const string& request) {
    string cleanRequest = request;
    
    // Remove newline if present
    if (!cleanRequest.empty() && cleanRequest.back() == '\n') {
        cleanRequest.pop_back();
    }
    
    // Find comma position
    size_t commaPos = cleanRequest.find(',');
    if (commaPos == string::npos) {
        throw invalid_argument("Invalid request format");
    }
    
    // Parse p and k
    int p = stoi(cleanRequest.substr(0, commaPos));
    int k = stoi(cleanRequest.substr(commaPos + 1));
    
    if (p < 0 || k < 0) {
        throw invalid_argument("Negative values not allowed");
    }
    
    return make_pair(p, k);
}

// Build response based on request
string buildResponse(const vector<string>& words, int p, int k) {
    string response;
    int totalWords = words.size();
    
    // If offset is beyond file size, return EOF
    if (p >= totalWords) {
        response = "EOF\n";
        return response;
    }
    
    // Add words starting from position p
    int wordsAdded = 0;
    for (int i = p; i < totalWords && wordsAdded < k; i++) {
        if (wordsAdded > 0) {
            response += ",";
        }
        response += words[i];
        wordsAdded++;
    }
    
    // If we've sent fewer than k words, add EOF
    if (wordsAdded < k) {
        if (wordsAdded > 0) {
            response += ",";
        }
        response += "EOF";
    }
    
    response += "\n";
    return response;
}

// Handle a single client connection
void handleClient(int clientSocket, const vector<string>& words, const string& clientAddr) {
    cout << "Server: New connection from " << clientAddr << endl;
    
    char buffer[1024];
    memset(buffer, 0, sizeof(buffer));
    
    // Receive request
    int bytesReceived = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
    if (bytesReceived <= 0) {
        cout << "Server: Client disconnected or error receiving data" << endl;
        close(clientSocket);
        return;
    }
    
    string request(buffer);
    cout << "Server: Received request: " << request;
    
    try {
        // Parse request
        pair<int, int> params = parseRequest(request);
        int p = params.first;
        int k = params.second;
        
        cout << "Server: Parsed request - offset: " << p << ", count: " << k << endl;
        
        // Build and send response
        string response = buildResponse(words, p, k);
        
        int bytesSent = send(clientSocket, response.c_str(), response.length(), 0);
        if (bytesSent < 0) {
            cerr << "Server: Error sending response" << endl;
        } else {
            cout << "Server: Sent " << bytesSent << " bytes" << endl;
        }
        
    } catch (const exception& e) {
        cerr << "Server: Error handling request: " << e.what() << endl;
        string errorResponse = "ERROR\n";
        send(clientSocket, errorResponse.c_str(), errorResponse.length(), 0);
    }
    
    // Close connection
    close(clientSocket);
    cout << "Server: Connection closed" << endl;
}

int main() {
    // Set up signal handler for graceful shutdown
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);
    
    // Parse config
    Config config = parseConfig("config.json");
    
    // Load words from file
    vector<string> words = loadWords(config.filename);
    
    // Create socket
    int serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket < 0) {
        cerr << "Error creating socket: " << strerror(errno) << endl;
        exit(1);
    }
    
    // Allow socket reuse
    int opt = 1;
    if (setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, 
               &opt, sizeof(opt)) < 0) {
    cerr << "Error setting socket options: " << strerror(errno) << endl;
    exit(1);
}
    
    // Set up server address
    struct sockaddr_in serverAddr;
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(config.server_port);
    
    // Convert IP address
    if (inet_pton(AF_INET, config.server_ip.c_str(), &serverAddr.sin_addr) <= 0) {
        cerr << "Invalid IP address: " << config.server_ip << endl;
        exit(1);
    }
    
    // Bind socket
    if (::bind(serverSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        cerr << "Error binding socket: " << strerror(errno) << endl;
        cerr << "Make sure no other process is using port " << config.server_port << endl;
        exit(1);
    }
    
    // Listen for connections
    if (listen(serverSocket, 10) < 0) {
        cerr << "Error listening on socket: " << strerror(errno) << endl;
        exit(1);
    }
    
    cout << "Server: Listening on " << config.server_ip << ":" << config.server_port << endl;
    cout << "Server: Press Ctrl+C to stop" << endl;
    
    // Accept connections
    while (keepRunning) {
        struct sockaddr_in clientAddr;
        socklen_t clientLen = sizeof(clientAddr);
        
        // Set timeout for accept to allow periodic checking of keepRunning
        struct timeval timeout;
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;
        
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(serverSocket, &readfds);
        
        int activity = select(serverSocket + 1, &readfds, NULL, NULL, &timeout);
        
        if (activity < 0 && errno != EINTR) {
            cerr << "Select error" << endl;
            break;
        }
        
        if (activity > 0 && FD_ISSET(serverSocket, &readfds)) {
            int clientSocket = accept(serverSocket, (struct sockaddr*)&clientAddr, &clientLen);
            if (clientSocket < 0) {
                if (errno != EINTR) {
                    cerr << "Error accepting connection: " << strerror(errno) << endl;
                }
                continue;
            }
            
            // Get client IP address
            char clientIP[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &clientAddr.sin_addr, clientIP, sizeof(clientIP));
            string clientAddrStr = string(clientIP) + ":" + to_string(ntohs(clientAddr.sin_port));
            
            // Handle client
            handleClient(clientSocket, words, clientAddrStr);
        }
    }
    
    close(serverSocket);
    cout << "\nServer: Shutting down gracefully" << endl;
    
    return 0;
}
