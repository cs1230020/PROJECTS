#ifndef FORWARDING_HPP
#define FORWARDING_HPP

#include <iostream>
#include <cstdint>
#include <array>
#include <vector>
#include <string>
#include <fstream>

// Forward declarations
class RegisterFile;
class ProcessorBase;
class NoForwardProcessor;

// Structure definitions
struct PipelineStageState {
    std::string fetchStage;      // IF stage
    std::string decodeStage;     // ID stage
    std::string executeStage;    // EX stage
    std::string memoryStage;     // MEM stage
    std::string writebackStage;  // WB stage
};

struct InstructionPipelineState {
    std::string instruction;                // Instruction string
    std::vector<std::string> stageHistory; // Pipeline stages history
};

struct InstructionEntry {
    std::string assemblyString;  
    uint32_t machineCode;
};

// Pipeline Register Structures
struct IF_ID_Reg {
    uint32_t instruction;
    uint32_t pc;
    bool isNop;
};

struct ID_EX_Reg {
    uint32_t opcode;
    uint32_t sourceReg1;
    uint32_t sourceReg2;
    uint32_t destReg;
    int32_t immediate;
    uint32_t funct3;
    uint32_t funct7;
    std::string aluOperation;
    bool isNop;
    bool writeEnable;
    bool isIType;
    bool isLoad;
    bool usesRs2;
    std::string instructionType;
    uint32_t pc;
};

struct EX_MEM_Reg {
    uint32_t destReg;
    uint32_t aluResult;
    bool readMemory;
    bool writeMemory;
    bool writeEnable;
    bool isNop;
    uint32_t pc;
    uint32_t storeData;
};

struct MEM_WB_Reg {
    uint32_t writebackData;
    uint32_t destReg;
    bool writeEnable;
    bool isNop;
    uint32_t pc;
    std::string instructionType;
};

// Register File class
class RegisterFile {
private:
    std::array<uint32_t, 32> registers;  // RISC-V 32 registers

public:
    RegisterFile() { registers.fill(0); }
    
    uint32_t read(uint8_t regIndex) const { 
        return registers[regIndex]; 
    }
    
    void write(uint8_t regIndex, uint32_t value) { 
        if (regIndex != 0) registers[regIndex] = value;  // x0 is hardwired to 0
    }
};

// Base Processor class
class ProcessorBase {
protected:
    std::ifstream instructionFile;        // Input file stream
    uint32_t programCounter = 0;          // Program Counter
    RegisterFile registerFile;            // Register File
    std::vector<PipelineStageState> pipelineDiagram;    // Pipeline visualization
    std::vector<InstructionPipelineState> instructions;  // Instruction states
    PipelineStageState currentPipelineState;            // Current pipeline state

    // Pipeline registers
    IF_ID_Reg IF_ID;
    ID_EX_Reg ID_EX;
    EX_MEM_Reg EX_MEM;
    MEM_WB_Reg MEM_WB = {0, 0, false, false, 0};

public:
    // Constructor
    ProcessorBase(const std::string& filename) {
        instructionFile.open(filename);
        if (!instructionFile) {
            std::cerr << "Failed to open file: " << filename << std::endl;
            exit(1);
        }
    }

    // Virtual simulation function
    virtual void simulate(uint32_t numCycles) = 0;

    // Virtual destructor
    virtual ~ProcessorBase() {
        if (instructionFile.is_open()) {
            instructionFile.close();
        }
    }
};

// No Forward Processor class
class NoForwardProcessor : public ProcessorBase {
private:
    // Helper function to decode instructions
    void decodeInstruction(uint32_t instruction, ID_EX_Reg& decodedInstruction);
    int32_t parseImmediateValue(const std::string& assemblyString);

public:
    // Constructor using base class constructor
    explicit NoForwardProcessor(const std::string& filename);
    std::vector<InstructionEntry> instructionMemory;   // loaded from file
    std::vector<std::vector<std::string>> pipelineTable; // pipeline table

    // Simulate the processor for a given number of cycles
    void simulate(uint32_t cycleCount) override;

    // Simulate memory byte access
    uint8_t loadByte(uint32_t memoryAddress);
};

#endif // FORWARDING_HPP