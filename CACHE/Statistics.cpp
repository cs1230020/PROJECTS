#include "Statistics.h"
#include <iostream>
#include <iomanip>
#include <sstream>

Statistics::Statistics()
{
    // Initialize all statistics to zero
    reset();
}

void Statistics::reset()
{
    // Reset cache statistics
    accesses = 0;
    misses = 0;
    readMisses = 0;
    writeMisses = 0;
    evictions = 0;
    writebacks = 0;
    
    // Reset processor statistics
    totalInstructions = 0;
    readInstructions = 0;
    writeInstructions = 0;
    
    // Reset bus statistics
    busReads = 0;
    busReadXs = 0;
    busUpgrades = 0;
    busFlushes = 0;
    invalidations = 0;
    busTraffic = 0;
}

// Cache statistics methods
void Statistics::incrementAccesses(uint64_t count)
{
    accesses += count;
}

void Statistics::incrementMisses(uint64_t count)
{
    misses += count;
}

void Statistics::incrementReadMisses(uint64_t count)
{
    readMisses += count;
    misses += count;
}

void Statistics::incrementWriteMisses(uint64_t count)
{
    writeMisses += count;
    misses += count;
}

void Statistics::incrementEvictions(uint64_t count)
{
    evictions += count;
}

void Statistics::incrementWritebacks(uint64_t count)
{
    writebacks += count;
}
void Statistics::incrementReads(uint64_t count)
{
    // This method is called when a cache read operation occurs
    // You might want to update other related statistics here
    // For example, if you want to track read operations separately from read instructions
    // For now, we'll just increment read instructions
    incrementReadInstructions(count);
}

void Statistics::incrementWrites(uint64_t count)
{
    // This method is called when a cache write operation occurs
    // You might want to update other related statistics here
    // For example, if you want to track write operations separately from write instructions
    // For now, we'll just increment write instructions
    incrementWriteInstructions(count);
}

uint64_t Statistics::getAccesses() const
{
    return accesses;
}

uint64_t Statistics::getMisses() const
{
    return misses;
}

uint64_t Statistics::getReadMisses() const
{
    return readMisses;
}

uint64_t Statistics::getWriteMisses() const
{
    return writeMisses;
}

uint64_t Statistics::getEvictions() const
{
    return evictions;
}

uint64_t Statistics::getWritebacks() const
{
    return writebacks;
}

// Processor statistics methods
void Statistics::incrementTotalInstructions(uint64_t count)
{
    totalInstructions += count;
}

void Statistics::incrementReadInstructions(uint64_t count)
{
    readInstructions += count;
    totalInstructions += count;
}

void Statistics::incrementWriteInstructions(uint64_t count)
{
    writeInstructions += count;
    totalInstructions += count;
}

uint64_t Statistics::getTotalInstructions() const
{
    return totalInstructions;
}

uint64_t Statistics::getReadInstructions() const
{
    return readInstructions;
}

uint64_t Statistics::getWriteInstructions() const
{
    return writeInstructions;
}

// Bus statistics methods
void Statistics::incrementBusReads(uint64_t count)
{
    busReads += count;
}

void Statistics::incrementBusReadXs(uint64_t count)
{
    busReadXs += count;
}

void Statistics::incrementBusUpgrades(uint64_t count)
{
    busUpgrades += count;
}

void Statistics::incrementBusFlushes(uint64_t count)
{
    busFlushes += count;
}

void Statistics::incrementInvalidations(uint64_t count)
{
    invalidations += count;

}

void Statistics::incrementBusTraffic(uint64_t bytes)
{
    busTraffic += bytes;
}

uint64_t Statistics::getBusReads() const
{
    return busReads;
}

uint64_t Statistics::getBusReadXs() const
{
    return busReadXs;
}

uint64_t Statistics::getBusUpgrades() const
{
    return busUpgrades;
}

uint64_t Statistics::getBusFlushes() const
{
    return busFlushes;
}

uint64_t Statistics::getInvalidations() const
{
    return invalidations;
}

uint64_t Statistics::getBusTraffic() const
{
    return busTraffic;
}

// Derived statistics
double Statistics::getMissRate() const
{
    if (accesses == 0) {
        return 0.0;
    }
    return static_cast<double>(misses) / accesses;
}

double Statistics::getReadMissRate() const
{
    if (readInstructions == 0) {
        return 0.0;
    }
    return static_cast<double>(readMisses) / readInstructions;
}

double Statistics::getWriteMissRate() const
{
    if (writeInstructions == 0) {
        return 0.0;
    }
    return static_cast<double>(writeMisses) / writeInstructions;
}

// Utility methods
std::string Statistics::toString() const
{
    std::ostringstream oss;
    
    oss << "Cache Statistics:" << std::endl;
    oss << "  Accesses: " << accesses << std::endl;
    oss << "  Misses: " << misses << std::endl;
    oss << "  Miss Rate: " << std::fixed << std::setprecision(2) << (getMissRate() * 100.0) << "%" << std::endl;
    oss << "  Read Misses: " << readMisses << std::endl;
    oss << "  Write Misses: " << writeMisses << std::endl;
    oss << "  Evictions: " << evictions << std::endl;
    oss << "  Writebacks: " << writebacks << std::endl;
    
    oss << "Processor Statistics:" << std::endl;
    oss << "  Total Instructions: " << totalInstructions << std::endl;
    oss << "  Read Instructions: " << readInstructions << std::endl;
    oss << "  Write Instructions: " << writeInstructions << std::endl;
    
    oss << "Bus Statistics:" << std::endl;
    oss << "  Bus Reads: " << busReads << std::endl;
    oss << "  Bus ReadXs: " << busReadXs << std::endl;
    oss << "  Bus Upgrades: " << busUpgrades << std::endl;
    oss << "  Bus Flushes: " << busFlushes << std::endl;
    oss << "  Invalidations: " << invalidations << std::endl;
    oss << "  Bus Traffic: " << busTraffic << " bytes" << std::endl;
    
    return oss.str();
}

void Statistics::print() const
{
    std::cout << toString();
}