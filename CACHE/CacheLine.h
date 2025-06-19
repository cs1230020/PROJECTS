#ifndef CACHELINE_H
#define CACHELINE_H

#include <cstdint>
#include <string>  // Add this include for std::string

// MESI cache coherence protocol states
enum class CacheState {
    MODIFIED,   // Line is modified (dirty) and exclusive to this cache
    EXCLUSIVE,  // Line is clean and exclusive to this cache
    SHARED,     // Line is clean and may be present in other caches
    INVALID     // Line does not contain valid data
};

class CacheLine {
private:
    uint32_t tag;           // Tag bits of the address
    CacheState state;       // MESI state of the cache line
    uint8_t* data;          // Actual data stored in the cache line
    int blockSize;  
     // Size of the cache line in bytes

public:
    // Constructor and destructor
    CacheLine(int blockSize = 0);
    ~CacheLine();
    
    // Copy constructor and assignment operator
    CacheLine(const CacheLine& other);
    CacheLine& operator=(const CacheLine& other);
    
    // Move constructor and assignment operator
    CacheLine(CacheLine&& other) noexcept;
    CacheLine& operator=(CacheLine&& other) noexcept;
    
    // Basic accessors and mutators
    uint32_t getTag() const;
    void setTag(uint32_t tag);
    
    CacheState getState() const;
    void setState(CacheState state);
    
    // Data access methods
    uint8_t* getData();
    const uint8_t* getData() const;
    
    // Utility methods
    bool isValid() const;

    void invalidate();
    bool isdirty() const;

    // Setter for dirty bit
    void setDirty(bool value) {
  // Set the dirty flag to the given value
        if (value) {
            state = CacheState::MODIFIED;  // If dirty is true, set the state to MODIFIED
        }
    }
    
    // Word-level access (for 4-byte words)
    uint32_t readWord(int offset) const;
    void writeWord(int offset, uint32_t value);
};

// Helper function to convert CacheState enum to string
std::string stateToString(CacheState state);

#endif // CACHELINE_H