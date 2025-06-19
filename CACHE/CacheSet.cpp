#include "CacheSet.h"
#include <algorithm>
#include <stdexcept>
#include <limits>

CacheSet::CacheSet(int associativity, int blockSize)
    : associativity(associativity),
      blockSize(blockSize)
{
    // Initialize cache lines
    lines.reserve(associativity);
    for (int i = 0; i < associativity; i++) {
        lines.emplace_back(blockSize);
    }
    
    // Initialize LRU counters (higher value = less recently used)
    lruCounter.resize(associativity, 0);
}

CacheSet::~CacheSet() {
    // Vector will clean up the CacheLine objects
}

CacheLine& CacheSet::getLine(int index) {
    if (index < 0 || index >= associativity) {
        throw std::out_of_range("Cache line index out of range");
    }
    return lines[index];
}

const CacheLine& CacheSet::getLine(int index) const {
    if (index < 0 || index >= associativity) {
        throw std::out_of_range("Cache line index out of range");
    }
    return lines[index];
}

int CacheSet::findLine(uint32_t tag) const {
    for (int i = 0; i < associativity; i++) {
        if (lines[i].isValid() && lines[i].getTag() == tag) {
            return i;
        }
    }
    return -1;  // Not found
}

int CacheSet::allocateLine(uint32_t tag) {
    // First, check for an invalid line
    for (int i = 0; i < associativity; i++) {
        if (!lines[i].isValid()) {
            lines[i].setTag(tag);
            updateLRU(i);
            return i;
        }
    }
    
    // If all lines are valid, use LRU replacement policy
    int lruIndex = getLRUIndex();
    lines[lruIndex].setTag(tag);
    updateLRU(lruIndex);
    return lruIndex;
}

void CacheSet::updateLRU(int lineIndex) {
    if (lineIndex < 0 || lineIndex >= associativity) {
        throw std::out_of_range("Cache line index out of range");
    }
    
    // Increment all counters
    for (int i = 0; i < associativity; i++) {
        lruCounter[i]++;
    }
    
    // Reset the counter for the accessed line
    lruCounter[lineIndex] = 0;
}

int CacheSet::getLRUIndex() const {
    int maxCounter = -1;
    int lruIndex = 0;
    
    for (int i = 0; i < associativity; i++) {
        if (lruCounter[i] > maxCounter) {
            maxCounter = lruCounter[i];
            lruIndex = i;
        }
    }
    
    return lruIndex;
}

int CacheSet::getLRUValue(int lineIndex) const {
    if (lineIndex < 0 || lineIndex >= associativity) {
        throw std::out_of_range("Cache line index out of range");
    }
    return lruCounter[lineIndex];
}

bool CacheSet::isFull() const {
    for (int i = 0; i < associativity; i++) {
        if (!lines[i].isValid()) {
            return false;
        }
    }
    return true;
}

int CacheSet::getAssociativity() const {
    return associativity;
}

int CacheSet::getBlockSize() const {
    return blockSize;
}

void CacheSet::invalidateLine(int lineIndex) {
    if (lineIndex < 0 || lineIndex >= associativity) {
        throw std::out_of_range("Cache line index out of range");
    }
    lines[lineIndex].invalidate();
}

void CacheSet::invalidateTag(uint32_t tag) {
    int index = findLine(tag);
    if (index != -1) {
        invalidateLine(index);
    }
}

bool CacheSet::hasLineInState(CacheState state) const {
    for (int i = 0; i < associativity; i++) {
        if (lines[i].getState() == state) {
            return true;
        }
    }
    return false;
}

int CacheSet::findLineInState(CacheState state) const {
    for (int i = 0; i < associativity; i++) {
        if (lines[i].getState() == state) {
            return i;
        }
    }
    return -1;  // Not found
}

int CacheSet::findLRULine() const {
    return getLRUIndex();
}

void CacheSet::updateLRUCounters(int accessedLineIndex) {
    updateLRU(accessedLineIndex);
}