#ifndef CACHE_UTILS_H
#define CACHE_UTILS_H

#include "CacheLine.h"

// Helper function to convert CacheState enum to string
inline std::string stateToString(CacheState state) {
    switch (state) {
        case CacheState::MODIFIED: return "MODIFIED";
        case CacheState::EXCLUSIVE: return "EXCLUSIVE";
        case CacheState::SHARED: return "SHARED";
        case CacheState::INVALID: return "INVALID";
        default: return "UNKNOWN";
    }
}

#endif // CACHE_UTILS_H