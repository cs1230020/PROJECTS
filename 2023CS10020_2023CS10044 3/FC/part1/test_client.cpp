#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

using namespace std;

int main() {
    // Hardcoded values for testing
    string server_ip = "127.0.0.1";
    int server_port = 8080;
    
    cout << "Creating socket..." << endl;
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        cerr << "Error creating socket" << endl;
        return 1;
    }
    
    struct sockaddr_in serverAddr;
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(server_port);
    
    if (inet_pton(AF_INET, server_ip.c_str(), &serverAddr.sin_addr) <= 0) {
        cerr << "Invalid address" << endl;
        return 1;
    }
    
    cout << "Connecting to " << server_ip << ":" << server_port << "..." << endl;
    if (connect(sockfd, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        cerr << "Connection failed: " << strerror(errno) << endl;
        return 1;
    }
    
    cout << "Connected successfully!" << endl;
    
    // Send a test request
    string request = "0,5\n";
    send(sockfd, request.c_str(), request.length(), 0);
    
    // Receive response
    char buffer[1024];
    memset(buffer, 0, sizeof(buffer));
    int bytes = recv(sockfd, buffer, sizeof(buffer)-1, 0);
    
    if (bytes > 0) {
        cout << "Received: " << buffer << endl;
    }
    
    close(sockfd);
    return 0;
}