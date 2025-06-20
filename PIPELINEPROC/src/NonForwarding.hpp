#ifndef NOFORWARD_PROCESSOR_HPP
#define NOFORWARD_PROCESSOR_HPP

#include <iostream>
#include <cstdint>
#include <array>
#include <vector>
#include <string>
#include <fstream>

// Base class structures
struct PipelinePhases {
    std::string Fetch;
    std::string Decode;
    std::string Execute;
    std::string Memory;
    std::string WriteBack;
};

struct InstructionPhases {
    std::string command;
    std::vector<std::string> phases;
};

// Register bank class
class RegisterBank {
    private:
        std::array<uint32_t, 32> regArray;
    public:
        RegisterBank() { regArray.fill(0); }
        uint32_t fetch(uint8_t regNum) const { return regArray[regNum]; }
        void store(uint8_t regNum, uint32_t value) {
            if (regNum != 0) regArray[regNum] = value;
        }
};

// Base processor class
class ProcessorCore {
    protected:
        std::ifstream sourceFile;
        uint32_t instructionPtr = 0;
        RegisterBank regBank;
        std::vector<PipelinePhases> executionFlow;
        std::vector<InstructionPhases> commandList;
        PipelinePhases currentPhase;

        // Pipeline registers
        struct FetchDecode_Reg {
            uint32_t instruction, counter;
            bool bubble;
        } fetchDecode;
        
        struct DecodeExec_Reg {
            uint32_t operation, src1, src2, dest;
            int32_t immediate;
            uint32_t control3;
            uint32_t control7;
            std::string execOperation;
            bool bubble;
            bool writeEnabled;
            bool immediateType;
            bool usesSource2 = false;
            uint32_t counter;
        } decodeExec;
        
        struct ExecMem_Reg {
            uint32_t dest;
            uint32_t execResult;
            bool memRead;
            bool memWrite;
            bool writeEnabled;
            bool bubble;
            uint32_t counter;
        } execMem={0,0,false,false,false,false};
        
        struct MemWrite_Reg {
            uint32_t writeData;
            uint32_t dest;
            bool writeEnabled;
            bool bubble;
            uint32_t counter;
        } memWrite={0,0,false,false};

    public:
        ProcessorCore(const std::string& filename) {
            sourceFile.open(filename);
            if (!sourceFile) {
                std::cerr << "Error opening file: " << filename << std::endl;
                exit(1);
            }
        }
        virtual ~ProcessorCore() = default;
        virtual void simulate(uint32_t cycles) = 0;
};

// Command structure for derived class
struct Command {
    std::string assemblyCode;
    uint32_t binaryCode;
};

// Derived processor class
class BasicProcessor : public ProcessorCore {
    private:
        void parseInstruction(uint32_t code, DecodeExec_Reg& decodedInstr);
        int32_t extractImmediate(const std::string& assembly);

    public:
        explicit BasicProcessor(const std::string& filename);
        std::vector<Command> programCommands;
        std::vector<std::vector<std::string>> executionTrace;
        void simulate(uint32_t cycles) override;
        uint8_t readMemory(uint32_t location);
};

#endif // NOFORWARD_PROCESSOR_HPP