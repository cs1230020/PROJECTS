#ifndef TRACEREADER_H
#define TRACEREADER_H

#include <string>
#include <fstream>
#include <vector>
#include <queue>
#include "Processor.h"

// Forward declaration
struct MemoryReference;

class TraceReader {
private:
    std::string traceFilePath;      // Path to the trace file
    std::ifstream traceFile;        // File stream for reading the trace
    bool fileOpen;                  // Flag indicating if file is open
    bool endOfFile;                 // Flag indicating if end of file has been reached
    
    // Queue of pre-read memory references
    std::queue<MemoryReference> referenceQueue;
    
    // Helper method to parse a line from the trace file
    bool parseLine(const std::string& line, MemoryReference& reference);
    
    // Helper method to preload some references
    void preloadReferences(int count);
    
public:
    // Constructor and destructor
    TraceReader(const std::string& filePath);
    ~TraceReader();
    
    // Open and close the trace file
    bool open();
    void close();
    
    // Check if the file is open and if we've reached the end
    bool isOpen() const;
    bool isEndOfFile() const;
    
    // Read the next memory reference from the trace
    bool getNextReference(MemoryReference& reference);
    
    // Get multiple references at once
    int getReferences(std::vector<MemoryReference>& references, int maxCount);
    
    // Reset the reader to the beginning of the file
    bool reset();
    
    // Get the trace file path
    std::string getTraceFilePath() const;
    
    // Static method to create trace file paths for a given application and core
    static std::string createTraceFilePath(const std::string& appName, int coreId);
};

#endif // TRACEREADER_H