#include "CacheLine.h"
#include <cstring>
#include <cassert>
#include <stdexcept>
#include "CacheUtils.h"
CacheLine::CacheLine(int blockSize)
    : tag(0),
      state(CacheState::INVALID),
      data(nullptr),
      blockSize(blockSize)

{
    if (blockSize > 0) {
        data = new uint8_t[blockSize]();  // Initialize to zeros
    }
}

CacheLine::~CacheLine() {
    delete[] data;
}

// Copy constructor
CacheLine::CacheLine(const CacheLine& other)
    : tag(other.tag),
      state(other.state),
      data(nullptr),
      blockSize(other.blockSize)

{
    if (blockSize > 0) {
        data = new uint8_t[blockSize];
        if (other.data) {
            std::memcpy(data, other.data, blockSize);
        } else {
            std::memset(data, 0, blockSize);
        }
    }
}

// Copy assignment operator
CacheLine& CacheLine::operator=(const CacheLine& other) {
    if (this != &other) {
        tag = other.tag;
        state = other.state;
        
        // Reallocate data if block sizes differ
        if (blockSize != other.blockSize) {
            delete[] data;
            blockSize = other.blockSize;
            data = blockSize > 0 ? new uint8_t[blockSize] : nullptr;
        }
        
        // Copy data if it exists
        if (data && other.data) {
            std::memcpy(data, other.data, blockSize);
        } else if (data) {
            std::memset(data, 0, blockSize);
        }
    }
    return *this;
}

// Move constructor
CacheLine::CacheLine(CacheLine&& other) noexcept
    : tag(other.tag),
      state(other.state),
      data(other.data),
      blockSize(other.blockSize)

{
    other.data = nullptr;
    other.blockSize = 0;
    other.tag = 0;
    other.state = CacheState::INVALID;
}

// Move assignment operator
CacheLine& CacheLine::operator=(CacheLine&& other) noexcept {
    if (this != &other) {
        delete[] data;
        
        tag = other.tag;
        state = other.state;
        blockSize = other.blockSize;
        data = other.data;
        
        other.data = nullptr;
        other.blockSize = 0;
        other.tag = 0;
        other.state = CacheState::INVALID;
    }
    return *this;
}

uint32_t CacheLine::getTag() const {
    return tag;
}

void CacheLine::setTag(uint32_t newTag) {
    tag = newTag;
}

CacheState CacheLine::getState() const {
    return state;
}

void CacheLine::setState(CacheState newState) {
    state = newState;
}

uint8_t* CacheLine::getData() {
    return data;
}

const uint8_t* CacheLine::getData() const {
    return data;
}

bool CacheLine::isValid() const {
    return state != CacheState::INVALID;
}

bool CacheLine::isdirty() const {
    return state == CacheState::MODIFIED;
}

void CacheLine::invalidate() {
    state = CacheState::INVALID;
}

uint32_t CacheLine::readWord(int offset) const {
    if (!isValid()) {
        throw std::runtime_error("Attempting to read from invalid cache line");
    }
    
    if (offset < 0 || offset + 3 >= blockSize) {
        throw std::out_of_range("Word offset out of range");
    }
    
    // Assuming little-endian byte order
    uint32_t word = 0;
    for (int i = 0; i < 4; i++) {
        word |= (static_cast<uint32_t>(data[offset + i]) << (i * 8));
    }
    
    return word;
}



void CacheLine::writeWord(int offset, uint32_t value) {
    if (state == CacheState::INVALID) {
        throw std::runtime_error("Attempting to write to invalid cache line");
    }
    
    if (state == CacheState::SHARED || state == CacheState::EXCLUSIVE) {
        // Writing to a shared or exclusive line makes it modified
        state = CacheState::MODIFIED;
    }
    
    if (offset < 0 || offset + 3 >= blockSize) {
        throw std::out_of_range("Word offset out of range");
    }
    
    // Assuming little-endian byte order
    for (int i = 0; i < 4; i++) {
        data[offset + i] = static_cast<uint8_t>((value >> (i * 8)) & 0xFF);
    }
}

// Helper function to convert CacheState enum to string
