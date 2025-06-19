#ifndef CACHESET_H
#define CACHESET_H

#include <vector>
#include "CacheLine.h"

class CacheSet {
private:
    std::vector<CacheLine> lines;       // Cache lines in this set
    std::vector<int> lruCounter;        // LRU counters for each line
    int associativity;                  // Number of lines in the set
    int blockSize;                      // Size of each cache line in bytes
    
    // Helper method to find the least recently used line
    int findLRULine() const;
    
    // Helper method to update LRU counters
    void updateLRUCounters(int accessedLineIndex);

public:
    // Constructor
    CacheSet(int associativity = 1, int blockSize = 64);
    
    // Destructor
    ~CacheSet();
    
    // Line access methods
    CacheLine& getLine(int index);
    const CacheLine& getLine(int index) const;
    
    // Find a line with the given tag
    // Returns the index if found, -1 otherwise
    int findLine(uint32_t tag) const;
    
    // Allocate a line for a new tag
    // Returns the index of the allocated line
    int allocateLine(uint32_t tag);
    
    // LRU management
    void updateLRU(int lineIndex);
    int getLRUIndex() const;
    int getLRUValue(int lineIndex) const;
    
    // Utility methods
    bool isFull() const;
    int getAssociativity() const;
    int getBlockSize() const;
    
    // Invalidate a specific line
    void invalidateLine(int lineIndex);
    
    // Invalidate all lines with the given tag
    void invalidateTag(uint32_t tag);
    
    // Check if any line in the set is in a specific state
    bool hasLineInState(CacheState state) const;
    
    // Find a line in a specific state
    // Returns the index if found, -1 otherwise
    int findLineInState(CacheState state) const;
};

#endif // CACHESET_H