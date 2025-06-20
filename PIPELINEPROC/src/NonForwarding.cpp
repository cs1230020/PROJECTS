#include "ALU.hpp"
#include "NonForwarding.hpp"
#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
using namespace std;

static uint8_t dataMemory[102400] = {};

uint8_t BasicProcessor::readMemory(uint32_t addr) {
    if (addr >= sizeof(dataMemory)) {
        std::cerr << "Memory access violation at address " << addr << std::endl;
        return 0;
    }
    return dataMemory[addr];
}

BasicProcessor::BasicProcessor(const std::string& filename) : ProcessorCore(filename) {
    std::string codeLine;
    while (std::getline(sourceFile, codeLine)) {
        if (codeLine.empty()) continue;
        std::istringstream lineStream(codeLine);
        std::vector<std::string> elements;
        std::string element;
        
        while (lineStream >> element) elements.push_back(element);
        
        if (elements.size() < 3) {
    std::cerr << "Invalid instruction format: " << codeLine << std::endl;
    exit(1);
}

std::string binaryStr = elements[1];
try {
    uint32_t machineCode = std::stoul(binaryStr, nullptr, 16);
    std::string assemblyCode;
    for (size_t i = 2; i < elements.size(); ++i) {
        if (i != 2) assemblyCode += " ";
        assemblyCode += elements[i];
    }
    programCommands.push_back({assemblyCode, machineCode});
} catch (const std::exception& e) {
    std::cerr << "Failed to parse instruction: " << codeLine << "\n";
    exit(1);
}
    }
}

void BasicProcessor::parseInstruction(uint32_t instruction, DecodeExec_Reg& decoded) {
    uint32_t opcode = instruction & 0x7F;

    decoded.operation = opcode;
    decoded.usesSource2 = false;
    decoded.writeEnabled = false;
    decoded.immediateType = false;

    decodeExec.operation = opcode;
    
    if (opcode == 0x33) { // R-type
    decoded.dest = (instruction >> 7) & 0x1F;
    decoded.control3 = (instruction >> 12) & 0x7;
    decoded.src1 = (instruction >> 15) & 0x1F;
    decoded.src2 = (instruction >> 20) & 0x1F;
    decoded.control7 = (instruction >> 25) & 0x7F;
    decoded.usesSource2 = true;
    
    if (decoded.control3 == 0x0 && decoded.control7 == 0x00)
        decoded.execOperation = "ADD";
    decoded.writeEnabled = true;
}
else if (opcode == 0x13) { // I-type
    decoded.dest = (instruction >> 7) & 0x1F;
    decoded.control3 = (instruction >> 12) & 0x7;
    decoded.src1 = (instruction >> 15) & 0x1F;
    decoded.immediate = (int32_t)(instruction & 0xFFF00000) >> 20;
    
    if (decoded.control3 == 0x0)
        decoded.execOperation = "ADDI";
    decoded.immediateType = true;
    decoded.writeEnabled = true;
}
else if (opcode == 0x03) { // Load
    decoded.dest = (instruction >> 7) & 0x1F;
    decoded.control3 = (instruction >> 12) & 0x7;
    decoded.src1 = (instruction >> 15) & 0x1F;
    decoded.immediate = (int32_t)(instruction & 0xFFF00000) >> 20;
    
    decoded.immediateType = true;
    decoded.execOperation = "LB";
    decoded.writeEnabled = true;
}
else if (opcode == 0x63) { // Branch
    decoded.control3 = (instruction >> 12) & 0x7;
    decoded.src1 = (instruction >> 15) & 0x1F;
    decoded.src2 = (instruction >> 20) & 0x1F;

    uint32_t offset = 0;
    offset |= ((instruction >> 31) & 0x1) << 12;
    offset |= ((instruction >> 7) & 0x1) << 11;
    offset |= ((instruction >> 25) & 0x3F) << 5;
    offset |= ((instruction >> 8) & 0xF) << 1;
    offset = (offset << 19) >> 19;
    offset = offset << 1;

    decoded.immediate = offset;
    decoded.usesSource2 = true;
    decoded.execOperation = "BEQ";
}
else if (opcode == 0x6F) { // JAL
    decoded.dest = (instruction >> 7) & 0x1F;
    int32_t offset = 0;
    offset |= ((instruction >> 31) & 0x1) << 20;
    offset |= ((instruction >> 12) & 0xFF) << 12;
    offset |= ((instruction >> 20) & 0x1) << 11;
    offset |= ((instruction >> 21) & 0x3FF) << 1;

    if (offset & (1 << 20)) {
        offset |= 0xFFF00000;
    }
    decoded.immediate = offset;
    decoded.execOperation = "JAL";
    decoded.writeEnabled = true;
}
else if (opcode == 0x67) { // JALR
    decoded.dest = (instruction >> 7) & 0x1F;
    decoded.control3 = (instruction >> 12) & 0x7;
    decoded.src1 = (instruction >> 15) & 0x1F;
    decoded.immediate = (int32_t)(instruction & 0xFFF00000) >> 20;
    
    decoded.execOperation = "JALR";
    decoded.immediateType = true;
    decoded.writeEnabled = true;
}
else { // default case
    decoded.usesSource2 = false;
    decoded.execOperation = "";
}
}
int32_t BasicProcessor::extractImmediate(const std::string& assemblyCode) {
    std::string processed = assemblyCode;
    for (char& c : processed) {
        if (c == ',' || c == '(' || c == ')') {
            c = ' ';
        }
    }
    
    std::vector<std::string> elements;
    std::istringstream tokenStream(processed);
    std::string element;
    
    while (tokenStream >> element) {
        elements.push_back(element);
    }
    
    for (auto it = elements.rbegin(); it != elements.rend(); ++it) {
        try {
            size_t pos;
            int32_t value = std::stol(*it, &pos, 0);
            if (pos == it->size()) {
                return value;
            }
        } catch (const std::exception& e) {
            continue;
        }
    }
    
    std::cerr << "Failed to extract immediate value from: " << assemblyCode << std::endl;
    return 0;
}

void BasicProcessor::simulate(uint32_t cycles) {
    std::string pipelineState = "";
    vector<vector<string>> stageHistory(cycles, vector<string>(5, "-"));
    uint32_t jumpTarget = 0;
    uint32_t instructionPtr = 0;

    // Initialize pipeline registers
    fetchDecode.bubble = true;
    decodeExec.bubble = true;
    execMem.bubble = true;
    memWrite.bubble = true;
    uint32_t cycle=0;
    while(cycle < cycles){
        bool jumpTaken = false;
        bool stallFetch = false;
        int hazardIndex = -1;
        bool hazardDetected = false;

        //----------WriteBack stage-------------------
        if (!memWrite.bubble && memWrite.writeEnabled) {
            regBank.store(memWrite.dest, memWrite.writeData);
            pipelineState += "WB(" + std::to_string(memWrite.counter) + ") ";
            stageHistory[cycle][0] = "WB(" + std::to_string(memWrite.counter/4) + ")";
        } else {
            pipelineState += "-";
        }

        //-----------Memory stage---------------------
        MemWrite_Reg newMemWrite = {};
        newMemWrite.bubble = execMem.bubble;
        if (!execMem.bubble) {
            if (execMem.memRead) {
                // Load operation: read 4 bytes from memory
                uint32_t data = 0;
                data |= readMemory(execMem.execResult);
                data |= readMemory(execMem.execResult + 1) << 8;
                data |= readMemory(execMem.execResult + 2) << 16;
                data |= readMemory(execMem.execResult + 3) << 24;
                newMemWrite.writeData = data;
            } else {
                // Arithmetic operation: forward ALU result
                newMemWrite.writeData = execMem.execResult;
            }
            pipelineState += "MEM(" + std::to_string(execMem.counter) + ") ";
            stageHistory[cycle][1] = "MEM(" + std::to_string(execMem.counter/4) + ")";
            newMemWrite.dest = execMem.dest;
            newMemWrite.counter = execMem.counter;
            newMemWrite.writeEnabled = execMem.writeEnabled;
        } else {
            pipelineState += "-";
        }


 //-----------------Execute Stage---------------------
ExecMem_Reg newExecMem = {};
newExecMem.bubble = decodeExec.bubble;
if (!decodeExec.bubble) {
    uint32_t srcVal1 = regBank.fetch(decodeExec.src1);
    uint32_t srcVal2 = regBank.fetch(decodeExec.src2);
    if (decodeExec.immediateType) {
        srcVal2 = static_cast<uint32_t>(decodeExec.immediate);
    }

    // Basic arithmetic and logical operations
    if (decodeExec.execOperation == "ADD" || decodeExec.execOperation == "ADDI" || 
        decodeExec.execOperation == "SUB" || 
        decodeExec.execOperation == "AND" || 
        decodeExec.execOperation == "OR"  || 
        decodeExec.execOperation == "XOR" ||
        decodeExec.execOperation == "SLL" || 
        decodeExec.execOperation == "SRL" || 
        decodeExec.execOperation == "SRA" ||
        decodeExec.execOperation == "LB") {
        // Use ALU for all arithmetic, logical, and shift operations
        newExecMem.execResult = ALU::execute(decodeExec.execOperation, srcVal1, srcVal2);
    }
    // Branch operations
    else if (decodeExec.execOperation == "BEQ" || 
             decodeExec.execOperation == "BNE" || 
             decodeExec.execOperation == "BLT" || 
             decodeExec.execOperation == "BGE") {
        if (ALU::branchCondition(decodeExec.execOperation, srcVal1, srcVal2)) {
            jumpTaken = true;
            // Calculate branch target using ALU
            jumpTarget = ALU::execute("ADD", decodeExec.counter, decodeExec.immediate);
        }
        newExecMem.execResult = 0;
    }
    // Jump operations
    else if (decodeExec.execOperation == "JAL") {
        std::cerr << "JAL at cycle " << cycle << "\n";
        uint32_t currentPC = decodeExec.counter;
        uint32_t targetAddr = 0;
        // Calculate return address (PC+4)
        uint32_t nextPC = ALU::execute("ADD", currentPC, 4);
        newExecMem.execResult = nextPC;

        uint32_t index = currentPC / 4;
        if (index < programCommands.size()) {
            std::string assemblyCode = programCommands[index].assemblyCode;
            int32_t offset = extractImmediate(assemblyCode);
            // Calculate jump target
            targetAddr = ALU::execute("ADD", currentPC, offset);
        } else {
            std::cerr << "Invalid PC in JAL: " << currentPC << std::endl;
        }

        if (ALU::execute("BNE", targetAddr, nextPC)) {
            jumpTaken = true;
            jumpTarget = targetAddr;
        }
    } 
    else if (decodeExec.execOperation == "JALR") {
        uint32_t currentPC = decodeExec.counter;
        uint32_t targetAddr = 0;
        // Calculate return address (PC+4)
        uint32_t nextPC = ALU::execute("ADD", currentPC, 4);
        newExecMem.execResult = nextPC;

        uint32_t index = currentPC / 4;
        if (index < programCommands.size()) {
            std::string assemblyCode = programCommands[index].assemblyCode;
            int32_t offset = extractImmediate(assemblyCode);
            // Calculate jump target (rs1 + offset)
            targetAddr = ALU::execute("ADD", srcVal1, offset);
            // Clear least significant bit for JALR
            targetAddr = targetAddr & ~(uint32_t)1;
        } else {
            std::cerr << "Invalid PC in JALR: " << currentPC << std::endl;
        }

        if (ALU::execute("BNE", targetAddr, nextPC)) {
            jumpTaken = true;
            jumpTarget = targetAddr;
        }
    }
    // Compare operations
    else if (decodeExec.execOperation == "SLT" || 
             decodeExec.execOperation == "SLTU") {
        newExecMem.execResult = ALU::execute(decodeExec.execOperation, srcVal1, srcVal2);
    }
    // Default case
    else {
        newExecMem.execResult = 0;
    }

    pipelineState += "EX(" + std::to_string(decodeExec.counter) + ")";
    stageHistory[cycle][2] = "EX(" + std::to_string(decodeExec.counter/4) + ") ";
    newExecMem.dest = decodeExec.dest;
    newExecMem.writeEnabled = decodeExec.writeEnabled;
    newExecMem.memRead = (decodeExec.execOperation == "LB");
    newExecMem.counter = decodeExec.counter;
    newExecMem.memWrite = false;
} else {
    pipelineState += "-";
}


         // --------------------- Decode Stage ---------------------
        DecodeExec_Reg newDecodeExec = {};
        newDecodeExec.bubble = fetchDecode.bubble;
        bool localJumpTaken = false;
        uint32_t localJumpTarget = 0;

        if (!fetchDecode.bubble) {
            uint32_t instruction = fetchDecode.instruction;
            DecodeExec_Reg decodedInstr;
            parseInstruction(instruction, decodedInstr);

            // Hazard detection
            bool executeHazard = (decodeExec.writeEnabled && decodeExec.dest != 0 && 
                               (decodeExec.dest == decodedInstr.src1 || 
                               (decodedInstr.usesSource2 && decodeExec.dest == decodedInstr.src2)));
            
            bool memoryHazard = (execMem.writeEnabled && execMem.dest != 0 && 
                               (execMem.dest == decodedInstr.src1 || 
                               (decodedInstr.usesSource2 && execMem.dest == decodedInstr.src2)));
            
            bool writebackHazard = (memWrite.writeEnabled && memWrite.dest != 0 && 
                                 (memWrite.dest == decodedInstr.src1 || 
                                 (decodedInstr.usesSource2 && memWrite.dest == decodedInstr.src2)));

            if (executeHazard) {
                stallFetch = true;
                pipelineState += "ID(" + std::to_string(fetchDecode.counter) + ") ";
                stageHistory[cycle][3] = "ID(" + std::to_string(fetchDecode.counter/4) + ")";
                newDecodeExec.bubble = true;
                hazardIndex = 0;
                hazardDetected = true;
            }
            else if (memoryHazard) {
                stallFetch = true;
                pipelineState += "-";
                newDecodeExec.bubble = true;
                hazardIndex = 1;
                hazardDetected = true;
            }
            else if (writebackHazard) {
                hazardIndex = 2;
                stallFetch = false;
                hazardDetected = true;
                pipelineState += "-";
                newDecodeExec = decodedInstr;
                newDecodeExec.counter = fetchDecode.counter;
                newDecodeExec.immediateType = (decodedInstr.execOperation == "ADDI" || 
                                             decodedInstr.execOperation == "LB" || 
                                             decodedInstr.execOperation == "JALR");
                newDecodeExec.writeEnabled = (decodedInstr.execOperation != "BEQ");
            }
            else {
                pipelineState += "ID(" + std::to_string(fetchDecode.counter) + ") ";
                stageHistory[cycle][3] = "ID(" + std::to_string(fetchDecode.counter/4) + ")";
                hazardDetected = false;
                newDecodeExec = decodedInstr;
                newDecodeExec.counter = fetchDecode.counter;
                newDecodeExec.immediateType = (decodedInstr.execOperation == "ADDI" || 
                                             decodedInstr.execOperation == "LB" || 
                                             decodedInstr.execOperation == "JALR");
                newDecodeExec.writeEnabled = (decodedInstr.execOperation != "BEQ");
            }
        }
        else {
            pipelineState += "-";
        }

        // --------------------- Fetch Stage ---------------------
        FetchDecode_Reg newFetchDecode = {};

        if (!jumpTaken) {
            if (hazardDetected) {
                if (stallFetch && hazardIndex == 0) {
                    uint32_t currentIndex = instructionPtr / 4;
                    if (currentIndex < programCommands.size()) {
                        newFetchDecode = fetchDecode;
                        pipelineState += "IF(" + std::to_string(currentIndex) + ") ";
                        stageHistory[cycle][4] = "IF(" + std::to_string(currentIndex) + ")";
                    }
                    else {
                        newFetchDecode = fetchDecode;
                        pipelineState += "- ";
                    }
                }
                else if (stallFetch && hazardIndex == 1) {
                    newFetchDecode = fetchDecode;
                    pipelineState += "-";
                }
                else if (!stallFetch && hazardIndex == 2) {
                    uint32_t currentIndex = instructionPtr / 4;
                    if (currentIndex < programCommands.size()) {
                        newFetchDecode.instruction = programCommands[currentIndex].binaryCode;
                        newFetchDecode.bubble = false;
                        newFetchDecode.counter = instructionPtr;
                        instructionPtr += 4;
                        pipelineState += "-";
                    }
                    else {
                        newFetchDecode.bubble = true;
                        pipelineState += "-";
                    }
                }
            }
            else {
                uint32_t currentIndex = instructionPtr / 4;
                if (currentIndex < programCommands.size()) {
                    newFetchDecode.instruction = programCommands[currentIndex].binaryCode;
                    newFetchDecode.bubble = false;
                    newFetchDecode.counter = instructionPtr;
                    instructionPtr += 4;
                    pipelineState += "IF(" + std::to_string(currentIndex) + ") ";
                    stageHistory[cycle][4] = "IF(" + std::to_string(currentIndex) + ")";
                }
                else {
                    newFetchDecode.bubble = true;
                    pipelineState += "-";
                }
            }
        }

        if (jumpTaken) {
            instructionPtr = jumpTarget;
            newFetchDecode.counter = instructionPtr;
            newDecodeExec.bubble = true;
            newDecodeExec.dest = 2400;
            newFetchDecode.bubble = true;
            pipelineState += "IF(" + std::to_string(instructionPtr/4) + ") ";
            jumpTaken = false;
        }

        // --------------------- Pipeline Register Update ---------------------
        memWrite = newMemWrite;
        execMem = newExecMem;
        decodeExec = newDecodeExec;
        fetchDecode = newFetchDecode;

        pipelineState += "\n";
        cycle++;
    }

    // Generate pipeline diagram
    int commandCount = programCommands.size();
    std::vector<std::vector<std::string>> diagram(commandCount, std::vector<std::string>(cycles, "-"));

    for (int cycle = 0; cycle < cycles; ++cycle) {
        for (int stage = 0; stage < 5; ++stage) {
            std::string entry = stageHistory[cycle][stage];
            if (entry == "-") continue;

            size_t pos = entry.find('(');
            if (pos == std::string::npos) continue;

            std::string stageName = entry.substr(0, pos);
            size_t pos2 = entry.find(')', pos);
            if (pos2 == std::string::npos) continue;

            int cmdIndex = std::stoi(entry.substr(pos + 1, pos2 - pos - 1));
            if (cmdIndex >= commandCount) continue;

            diagram[cmdIndex][cycle] = stageName;
        }
    }

    // Print pipeline diagram
    std::cout << "Pipeline Diagram:\n";
    for (int i = 0; i < commandCount; ++i) {
        std::cout << programCommands[i].assemblyCode << ";";
        for (int cycle = 0; cycle < cycles; ++cycle) {
            std::cout << diagram[i][cycle] << ";";
        }
        std::cout << "\n";
    }
}