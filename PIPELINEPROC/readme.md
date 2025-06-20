NonForwarding.hpp
1.) The pipeline follows a 5-stage structure: Fetch, Decode, Execute, Memory, and WriteBack.
2.) We used pipeline registers (fetchDecode, decodeExec, execMem, memWrite) to store the intermediate results.
3.) There was no data forwarding, handled instead using pipeline stalls (bubbles in registers).
4.) The Register file (struct RegisterBank) has 32 registers, with R0 read-only (always 0).
5.) The decoding of an instruction is handled separately in parseInstruction(), and immediate values are extracted using extractImmediate().
6.) Since there was no forwarding operands are fetched only after full completion of the previous stage.
7.) InstructionPhases and PipelinePhases track execution stages of each instruction.
8.) Command structure stores both assembly and binary representations.
9.) readMemory() provides explicit memory access; no memory forwarding mechanism.
10.) Simulation is cycle-based (simulate(uint32_t cycles)) and tracks execution flow in executionTrace.
11.) ProcessorCore is an abstract base class, and BasicProcessor extends it with full instruction handling.
12.) Instructions are read from a file (input.txt), and errors result in program termination.

NonForwarding.cpp
1.) Here we have included headers: ALU.hpp, NonForwarding.hpp, and standard C++ libraries.
2.) We defined dataMemory (102400 bytes) for memory storage.
3.) Also implemented readMemory() to read from dataMemory with bounds checking.
4.) The BasicProcessor constructor reads instructions from a file, converts them to machine code, and stores them.
5.) parseInstruction() decodes RISC-V instructions into their components.
6.) extractImmediate() retrieves immediate values from assembly code.
7.) simulate() function runs the processor simulation for a given number of cycles.
8.) Implemented a five-stage pipeline: Fetch, Decode, Execute, Memory, WriteBack.
9.) For functioning through the various cycles implemented pipelineState and stageHistory to track execution across cycles.
10.) Implemented hazard detection and stalls when necessary and there was no forwarding.
11.) In this file we have also supported arithmetic, logical, branch, and jump instructions using an ALU.
12.) There is also handling of BEQ, JAL, JALR, and other control flow instructions.
13.) Memory operations (LB) fetch data from dataMemory.
14.) regBank.store() writes back results to the registers.
15.) There was detection and resolving of data hazards using stalls.
16.) Tracked instruction execution order using counters.
17.) Used error handling for invalid instructions and memory accesses.

Forwarding.hpp
1.) We have defined a 5-stage pipeline: Fetch (IF), Decode (ID), Execute (EX), Memory (MEM), and Writeback (WB).
2.) Here again we used pipeline register structures (IF_ID, ID_EX, EX_MEM, MEM_WB) to store the intermediate results.
3.) Implemented instruction tracking using PipelineStageState and InstructionPipelineState structures.
4.) Instructions are stored as both assembly and machine code using InstructionEntry.
5.) The RegisterFile class manages 32 registers, with x0 hardwired to 0.
6.) The ProcessorBase is an abstract class which handles file reading, program counter, and pipeline visualization.
7.) The NoForwardProcessor extends the ProcessorBase and simulates execution without data forwarding.
8.) Pipeline stalls are introduced when required due to data dependencies.
9.) decodeInstruction() extracts opcode, registers, and immediate values.
10.) Also defined parseImmediateValue() which retrieves immediate values from assembly instructions.
11.) Instructions are read from an input file and stored in instructionMemory.
12.) Also usd a pipelineTable to track instruction progression through stages.
13.) simulate() executes the pipeline cycle-by-cycle for a given number of cycles.
14.) Implemented loadByte() to simulate memory access for byte-sized loads.
15.) Also there is error handling for invalid file operations or instruction parsing errors.

Forwarding.cpp
1.) We have included headers: ALU.hpp, Forwarding.hpp, and standard C++ libraries.
2.) There is definition dataMemory (102400 bytes) for memory storage.
3.) Also implemented readMemory() with bounds checking for safe memory access.
4.) The BasicProcessor constructor reads instructions from a file, converts them to machine code, and stores them.
5.) parseInstruction() decodes RISC-V instructions into their components.
6.) extractImmediate() retrieves immediate values from assembly code.
7.) simulate() function runs the processor simulation for a given number of cycles.
8.) Also implemented a five-stage pipeline: Fetch, Decode, Execute, Memory, WriteBack.
9.) We have used pipelineState and stageHistory to track execution across cycles.
10.) Implemented data forwarding from EX/MEM/WB stages to reduce stalls.
11.) Supported arithmetic, logical, branch, and jump instructions using an ALU.
12.) Handled BEQ, JAL, JALR, and other control flow instructions.
13.) Memory operations (LB) fetch data from dataMemory.
14.) regBank.store() writes back results to the registers.
15.) Used forwarding paths to resolve data hazards dynamically.
16.) Tracked instruction execution order using counters.
17.) Implemented error handling for invalid instructions and memory accesses.

Sources:
Referred to the book: Computer Organization and Design
The Hardware/Software Interface: RISC-V Edition

- for concept application for stalling and forwarding 
- implementing the various structures to handle the pipeline phases and the instruction phases


Also referred to  ChatGPT incase any error occured in the running of the file.
Though it wasn't really useful. 
