#include "TraceReader.h"
#include <iostream>
#include <sstream>
#include <algorithm>
#include <cctype>

TraceReader::TraceReader(const std::string& filePath)
    : traceFilePath(filePath),
      fileOpen(false),
      endOfFile(false)
{
    // Try to open the file immediately
    open();
    
    // Preload some references if the file is open
    if (fileOpen) {
        preloadReferences(10);
    }
}

TraceReader::~TraceReader() {
    close();
}

bool TraceReader::open() {
    // If already open, close it first
    if (fileOpen) {
        close();
    }
    
    // Open the trace file
    traceFile.open(traceFilePath);
    fileOpen = traceFile.is_open();
    endOfFile = false;
    
    if (!fileOpen) {
        std::cerr << "Error: Could not open trace file: " << traceFilePath << std::endl;
    }
    
    return fileOpen;
}

void TraceReader::close() {
    if (fileOpen) {
        traceFile.close();
        fileOpen = false;
    }
    
    // Clear the reference queue
    while (!referenceQueue.empty()) {
        referenceQueue.pop();
    }
}

bool TraceReader::isOpen() const {
    return fileOpen;
}

bool TraceReader::isEndOfFile() const {
    return endOfFile && referenceQueue.empty();
}

bool TraceReader::parseLine(const std::string& line, MemoryReference& reference) {
    // Skip empty lines and comments
    if (line.empty() || line[0] == '#') {
        return false;
    }
    
    std::istringstream iss(line);
    char opType;
    std::string addressStr;
    
    // Read operation type and address
    if (!(iss >> opType >> addressStr)) {
        return false;
    }
    
    // Convert operation type to MemoryOperation
    MemoryOperation op;
    opType = std::toupper(opType);
    if (opType == 'R') {
        op = MemoryOperation::READ;
    } else if (opType == 'W') {
        op = MemoryOperation::WRITE;
    } else {
        std::cerr << "Error: Unknown operation type: " << opType << " in file: " << traceFilePath << std::endl;
        return false;
    }
    
    // Parse the address
    uint32_t address = 0;
    try {
        // Check if the address is in hex format
        if (addressStr.substr(0, 2) == "0x" || addressStr.substr(0, 2) == "0X") {
            address = std::stoul(addressStr, nullptr, 16);
        } else {
            address = std::stoul(addressStr);
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: Failed to parse address: " << addressStr << " in file: " << traceFilePath << std::endl;
        return false;
    }
    
    // Create the memory reference
    reference = MemoryReference(op, address);
    return true;
}

void TraceReader::preloadReferences(int count) {
    if (!fileOpen) {
        return;
    }
    
    // Read up to 'count' references
    for (int i = 0; i < count && !traceFile.eof(); i++) {
        std::string line;
        if (std::getline(traceFile, line)) {
            MemoryReference reference(MemoryOperation::READ, 0);
            if (parseLine(line, reference)) {
                referenceQueue.push(reference);
            } else {
                // If parsing failed, try the next line
                i--;
            }
        }
    }
    
    // Check if we've reached the end of the file
    endOfFile = traceFile.eof();
}

bool TraceReader::getNextReference(MemoryReference& reference) {
    // If the queue is empty, try to load more references
    if (referenceQueue.empty() && !endOfFile) {
        preloadReferences(10);
    }
    
    // If the queue is still empty, we've reached the end of the file
    if (referenceQueue.empty()) {
        return false;
    }
    
    // Get the next reference from the queue
    reference = referenceQueue.front();
    referenceQueue.pop();
    
    // If the queue is getting low and we haven't reached the end of the file, preload more
    if (referenceQueue.size() < 5 && !endOfFile) {
        preloadReferences(10);
    }
    
    return true;
}

int TraceReader::getReferences(std::vector<MemoryReference>& references, int maxCount) {
    int count = 0;
    
    // Get up to maxCount references
    for (int i = 0; i < maxCount; i++) {
        MemoryReference reference(MemoryOperation::READ, 0);
        if (getNextReference(reference)) {
            references.push_back(reference);
            count++;
        } else {
            break;
        }
    }
    
    return count;
}

bool TraceReader::reset() {
    // Close and reopen the file
    close();
    return open();
}

std::string TraceReader::getTraceFilePath() const {
    return traceFilePath;
}

std::string TraceReader::createTraceFilePath(const std::string& appName, int coreId) {
    std::ostringstream oss;
    oss << appName << "_proc" << coreId << ".trace";
    return oss.str();
}