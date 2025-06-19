# Cache Coherence Simulator

A cycle-accurate multiprocessor cache coherence simulator that models a system with private L1 caches connected via a shared bus implementing the MESI (Modified-Exclusive-Shared-Invalid) cache coherence protocol.

## Overview

This simulator allows detailed analysis of cache coherence behavior in multiprocessor systems. It models:

- Multiple processor cores, each with a private L1 cache
- A central shared bus connecting all caches
- MESI cache coherence protocol
- Write-back, write-allocate caching policy
- LRU (Least Recently Used) replacement policy

The simulator processes memory access traces for each processor and produces detailed statistics on cache behavior, bus traffic, and execution time.

## Project Structure

```
.
├── Bus.cpp            # Bus implementation for inter-cache communication
├── Cache.cpp          # Cache implementation with MESI protocol
├── CacheLine.cpp      # Individual cache line implementation
├── CacheSet.cpp       # Set associative cache set implementation
├── Processor.cpp      # Processor model for executing memory traces
├── Simulator.cpp      # Main simulator controller
├── Statistics.cpp     # Performance metrics collection
├── TraceReader.cpp    # Trace file parser
├── main.cpp           # Command-line interface
├── matrix_vector_mult.cpp  # Trace generator for false sharing examples
├── Makefile           # Build configuration
└── various header files (.h)
```

## Building the Simulator

To build the simulator, run:

```bash
make
```

This will compile all source files and generate the executable `L1simulate`.

To clean the build files:

```bash
make clean
```

This removes all object files, the simulator executable, and any generated trace files.

## Generating Trace Files

The simulator comes with a built-in trace generator to demonstrate cache coherence scenarios, particularly false sharing:

```bash
make trace
```

This compiles and runs the `matrix_trace_gen` program, which generates memory access traces in the required format. It produces multiple trace files (one for each processor core) that can be used to observe false sharing and its mitigation through proper data structure padding.

## Running the Simulator

Basic usage:

```bash
./L1simulate -t <tracefile_prefix> -s <set_bits> -E <associativity> -b <block_bits> [-o <output_file>]
```

### Command-line Parameters

- `-t <tracefile_prefix>`: Name of the application whose traces will be used (e.g., "app1" for traces named "app1_proc0.trace", "app1_proc1.trace", etc.)
- `-s <s>`: Number of set index bits (number of sets = 2^s)
- `-E <E>`: Associativity (number of cache lines per set)
- `-b <b>`: Number of block bits (block size = 2^b bytes)
- `-o <outfilename>`: Optional. Logs output to the specified file
- `-h`: Prints help message

### Example

```bash
# Run with 64 sets (s=6), 2-way associativity, and 32-byte blocks (b=5)
./L1simulate -t matmul -s 6 -E 2 -b 5
```

This will simulate a system with four processors, each with a 4KB L1 cache (64 sets × 2 ways × 32 bytes).

## Trace File Format

The simulator processes memory access traces with a simple format:

```
<operation> <address>
```

Where:
- `<operation>` is either `R` (read) or `W` (write)
- `<address>` is a memory address in hexadecimal (0x...) or decimal format

Example:
```
R 0x1000
W 0x2000
R 4096
```

## Output and Statistics

The simulator outputs comprehensive statistics for each processor core:

- Total instructions executed (reads and writes)
- Total execution cycles and idle cycles
- Cache performance: misses, miss rate, evictions, writebacks
- Bus traffic: invalidations, data transferred
- Overall bus transactions

Example output:
```
Simulation Parameters:
Trace Prefix: matmul
Set Index Bits: 6
Associativity: 2
Block Bits: 5
Block Size (Bytes): 32
Number of Sets: 64
Cache Size (KB per core): 4.00
MESI Protocol: Enabled
Write Policy: Write-back, Write-allocate
Replacement Policy: LRU
Bus: Central snooping bus

Core 0 Statistics:
Total Instructions: 8
Total Reads: 4
Total Writes: 4
Total Execution Cycles: 8
Idle Cycles: 732
Cache Misses: 4
Cache Miss Rate: 50.00%
Cache Evictions: 0
Writebacks: 3
Bus Invalidations: 3
Data Traffic (Bytes): 416

[Statistics for other cores...]

Overall Bus Summary:
Total Bus Transactions: 26
Total Bus Traffic (Bytes): 576
```

## MESI Protocol Implementation

The simulator implements the full MESI protocol:

- **M**odified: Line is valid, owned exclusively, and has been modified (dirty)
- **E**xclusive: Line is valid, owned exclusively, and matches memory (clean)
- **S**hared: Line is valid, may exist in other caches, and matches memory
- **I**nvalid: Line does not contain valid data

The protocol handles all state transitions based on processor requests and bus snooping operations.

## Analyzing False Sharing

The included trace generator (`matrix_vector_mult.cpp`) creates traces that demonstrate false sharing - a performance issue where processors access different data elements that reside on the same cache line.

When running these traces through the simulator, you can observe:

1. High cache miss rates despite accessing the same addresses repeatedly
2. Frequent invalidations due to coherence protocol
3. Elevated bus traffic and execution time

The trace generator also produces a version with proper padding to avoid false sharing, allowing for direct comparison.

## Experimenting with Cache Parameters

The simulator allows exploration of various cache configurations by adjusting:

1. Cache size (through set index bits `-s`)
2. Associativity (through `-E` parameter)
3. Block size (through block bits `-b`)

Try different configurations to observe how they affect performance metrics and coherence traffic.

## Additional Information

For a deeper understanding of cache coherence and this simulator's implementation details, refer to the comprehensive report included with this project. It provides detailed explanations of the MESI protocol, bus operation, and simulation algorithms.
