#include "Forwarding.hpp"
#include "ALU.hpp"
#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
using namespace std;
static uint8_t mainMemory[102400] = {}; // 1KB of memory, initialized to zero

// Implement the loadByte function to simulate memory access
uint8_t NoForwardProcessor::loadByte(uint32_t memoryAddress) {
    // Check if the address is within bounds (i.e., within the size of the memory array)
    if (memoryAddress >= sizeof(mainMemory)) {
    std::cerr << "M " << memoryAddress << std::endl;
    return 0;  // Return a dummy value (0) if the address is out of bounds
} else {
    return mainMemory[memoryAddress];  // Return the byte at the given address
}
}

NoForwardProcessor::NoForwardProcessor(const std::string& filename) : ProcessorBase(filename) {
    std::string currentLine;
    while (std::getline(instructionFile, currentLine)) {
        if (currentLine.empty()) continue;
        std::istringstream lineStream(currentLine);
        std::vector<std::string> tokens;
        std::string token;
        while (lineStream >> token) tokens.push_back(token);
        if (tokens.size() >= 3) {
            // Extract machine code (second token)
            std::string machineCodeStr = tokens[1];
            try {
                uint32_t machineCode = std::stoul(machineCodeStr, nullptr, 16);
                // Extract assembly (remaining tokens)
                std::string assemblyString;
                for (size_t i = 2; i < tokens.size(); ++i) { // Start from index 2
                    if (i != 2) assemblyString += " ";
                    assemblyString += tokens[i];
                }
                instructionMemory.push_back({assemblyString, machineCode});
            } catch (const std::exception& e) {
                std::cerr << "" << currentLine << "\n";
                exit(1);
            }
        } else {
            std::cerr << tokens.size();
            std::cerr << "" << currentLine << std::endl;
            exit(1);
        }
    }
}

// Helper function to decode instructions based on the type
void NoForwardProcessor::decodeInstruction(uint32_t instruction, ID_EX_Reg& decodedInstr) {
    uint32_t opcode = instruction & 0x7F;  // Extract opcode (bits [6:0])
    decodedInstr.instructionType = "OTHER";
    decodedInstr.isLoad = false;
    decodedInstr.opcode = opcode;
    decodedInstr.usesRs2 = false;
    decodedInstr.writeEnable = false;
    decodedInstr.isIType = false;

    ID_EX.opcode = opcode;
    
    // First check for I-type instructions (ADDI, etc.) as they are most common
if (opcode == 0x13) {  // I-type instructions
    decodedInstr.destReg = (instruction >> 7) & 0x1F;
    decodedInstr.funct3 = (instruction >> 12) & 0x7;
    decodedInstr.sourceReg1 = (instruction >> 15) & 0x1F;
    decodedInstr.immediate = (int32_t)(instruction & 0xFFF00000) >> 20;
    decodedInstr.isIType = true;
    decodedInstr.writeEnable = true;
    decodedInstr.instructionType = "I";

    if (decodedInstr.funct3 == 0x0) {
        decodedInstr.aluOperation = "ADDI";
    } else if (decodedInstr.funct3 == 0x1) {
        decodedInstr.aluOperation = "SLLI";
    } else if (decodedInstr.funct3 == 0x2) {
        decodedInstr.aluOperation = "SLTI";
    } else if (decodedInstr.funct3 == 0x3) {
        decodedInstr.aluOperation = "SLTIU";
    } else if (decodedInstr.funct3 == 0x4) {
        decodedInstr.aluOperation = "XORI";
    } else if (decodedInstr.funct3 == 0x5) {
        if (((instruction >> 30) & 0x1) == 0) {
            decodedInstr.aluOperation = "SRLI";
        } else {
            decodedInstr.aluOperation = "SRAI";
        }
    } else if (decodedInstr.funct3 == 0x6) {
        decodedInstr.aluOperation = "ORI";
    } else if (decodedInstr.funct3 == 0x7) {
        decodedInstr.aluOperation = "ANDI";
    }
}
// Then R-type instructions (ADD, SUB)
else if (opcode == 0x33) {  // R-type instruction
    decodedInstr.destReg = (instruction >> 7) & 0x1F;
    decodedInstr.funct3 = (instruction >> 12) & 0x7;
    decodedInstr.sourceReg1 = (instruction >> 15) & 0x1F;
    decodedInstr.sourceReg2 = (instruction >> 20) & 0x1F;
    decodedInstr.funct7 = (instruction >> 25) & 0x7F;
    decodedInstr.usesRs2 = true;
    
    if (decodedInstr.funct3 == 0x0) {
        if (decodedInstr.funct7 == 0x00) {
            decodedInstr.aluOperation = "ADD";
        } else if (decodedInstr.funct7 == 0x20) {
            decodedInstr.aluOperation = "SUB";
        }
    }
    decodedInstr.writeEnable = true;
    decodedInstr.instructionType = "R";
}
// Branch instructions
else if (opcode == 0x63) {  // B-type instructions
    decodedInstr.funct3 = (instruction >> 12) & 0x7;
    decodedInstr.sourceReg1 = (instruction >> 15) & 0x1F;
    decodedInstr.sourceReg2 = (instruction >> 20) & 0x1F;

    uint32_t immediate = 0;
    immediate |= ((instruction >> 31) & 0x1) << 12;
    immediate |= ((instruction >> 7)  & 0x1) << 11;
    immediate |= ((instruction >> 25) & 0x3F) << 5;
    immediate |= ((instruction >> 8)  & 0xF)  << 1;
    immediate = (immediate << 19) >> 19;
    immediate = immediate << 1;

    decodedInstr.immediate = immediate;
    decodedInstr.usesRs2 = true;

    if (decodedInstr.funct3 == 0x0) {
        decodedInstr.aluOperation = "BEQ";
    } else if (decodedInstr.funct3 == 0x1) {
        decodedInstr.aluOperation = "BNE";
    } else if (decodedInstr.funct3 == 0x4) {
        decodedInstr.aluOperation = "BLT";
    } else if (decodedInstr.funct3 == 0x5) {
        decodedInstr.aluOperation = "BGE";
    } else if (decodedInstr.funct3 == 0x6) {
        decodedInstr.aluOperation = "BLTU";
    } else if (decodedInstr.funct3 == 0x7) {
        decodedInstr.aluOperation = "BGEU";
    }
    
    decodedInstr.instructionType = "B";
}
// Store instructions
else if (opcode == 0x23) {  // S-type instruction
    uint32_t immHigh = (instruction >> 25) & 0x7F;
    uint32_t immLow  = (instruction >> 7) & 0x1F;
    decodedInstr.sourceReg1 = (instruction >> 15) & 0x1F;
    decodedInstr.sourceReg2 = (instruction >> 20) & 0x1F;
    decodedInstr.funct3 = (instruction >> 12) & 0x7;
    
    decodedInstr.immediate = (int32_t)((immHigh << 5) | immLow);
    decodedInstr.immediate = (decodedInstr.immediate << 20) >> 20;
    
    decodedInstr.aluOperation = "SB";
    decodedInstr.writeEnable = false;
    decodedInstr.isIType = false;
    decodedInstr.usesRs2 = true;
    decodedInstr.instructionType = "STORE";
    decodedInstr.isLoad = false;
}
// Jump instructions
else if (opcode == 0x6F) {  // JAL
    decodedInstr.destReg = (instruction >> 7) & 0x1F;
    int32_t immediate = 0;
    immediate |= ((instruction >> 31) & 0x1) << 20;
    immediate |= ((instruction >> 12) & 0xFF) << 12;
    immediate |= ((instruction >> 20) & 0x1) << 11;
    immediate |= ((instruction >> 21) & 0x3FF) << 1;

    if (immediate & (1 << 20)) {
        immediate |= 0xFFF00000;
    }

    decodedInstr.immediate = immediate;
    decodedInstr.aluOperation = "JAL";
    decodedInstr.writeEnable = true;
}
else if (opcode == 0x67) {  // JALR
    decodedInstr.destReg = (instruction >> 7) & 0x1F;
    decodedInstr.funct3 = (instruction >> 12) & 0x7;
    decodedInstr.sourceReg1 = (instruction >> 15) & 0x1F;
    
    decodedInstr.immediate = (int32_t)(instruction & 0xFFF00000) >> 20;
    
    decodedInstr.aluOperation = "JALR";
    decodedInstr.isIType = true;
    decodedInstr.writeEnable = true;
}
// Default case for unsupported instructions
else {
    decodedInstr.usesRs2 = false;
    decodedInstr.aluOperation = "";
}
}


int32_t NoForwardProcessor::parseImmediateValue(const std::string& assemblyString) {
    std::string processedString = assemblyString;
    // Replace commas, parentheses, and brackets with spaces to handle different formats
    for (char& c : processedString) {
        if (c == ',' || c == '(' || c == ')') {
            c = ' ';
        }
    }
    std::vector<std::string> tokens;
    std::istringstream tokenStream(processedString);
    std::string currentToken;
    while (tokenStream >> currentToken) {
        tokens.push_back(currentToken);
    }
    // Iterate tokens in reverse to find the last numeric token (immediate)
    for (auto it = tokens.rbegin(); it != tokens.rend(); ++it) {
        std::string token = *it;
        try {
            size_t position;
            int32_t immediateValue = std::stol(token, &position, 0); // Allow decimal and hex (0x) formats
            if (position == token.size()) {
                return immediateValue;
            }
        } catch (const std::exception& e) {
            // Not a valid number, continue to next token
            continue;
        }
    }
    std::cerr << "Error: Could not parse immediate from assembly string: " << assemblyString << std::endl;
    return 0; // Return 0 as a fallback
}

void NoForwardProcessor::simulate(uint32_t cycleCount) {
    std::string outputString = "";
    vector<vector<string>> pipelineStages(cycleCount, vector<string>(5,"-"));
    uint32_t targetPC = 0;
    uint32_t programCounter = 0;
    int stallFlag = 0;   

    IF_ID.isNop = true;
    ID_EX.isNop = true;
    EX_MEM.isNop = true;
    MEM_WB.isNop = true;
    uint32_t currentCycle = 0;
    while(currentCycle < cycleCount) {
        bool isBranchTaken = false;
        bool skipFetch = false;
        int hazardIndicator = -1;
        bool hasDataHazard = false;
    
        //----------WB stage-------------------
        if (!MEM_WB.isNop && MEM_WB.writeEnable) {
            // Write the result back to the register file
            registerFile.write(MEM_WB.destReg, MEM_WB.writebackData);
            outputString += "WB(" + std::to_string(MEM_WB.pc) + ") ";
            pipelineStages[currentCycle][0] = "WB(" + std::to_string(MEM_WB.pc/4) + ")";
        }
        else {
            outputString += "-";
        }

        //-----------MEM stage---------------------
        MEM_WB_Reg nextMemWb = {};
        nextMemWb.isNop = EX_MEM.isNop;
        if (!EX_MEM.isNop) {
            if (EX_MEM.readMemory) {
                // For a load, read 4 bytes from memory using loadByte and combine them
                uint32_t memoryData = 0;
                memoryData |= loadByte(EX_MEM.aluResult);
                memoryData |= loadByte(EX_MEM.aluResult + 1) << 8;
                memoryData |= loadByte(EX_MEM.aluResult + 2) << 16;
                memoryData |= loadByte(EX_MEM.aluResult + 3) << 24;
                nextMemWb.writebackData = memoryData;
            } else {
                // For arithmetic instructions, simply forward the ALU result
                nextMemWb.writebackData = EX_MEM.aluResult;
            }
            outputString += "MEM(" + std::to_string(EX_MEM.pc) + ") ";
            pipelineStages[currentCycle][1] = "MEM(" + std::to_string(EX_MEM.pc/4) + ")";
            nextMemWb.destReg = EX_MEM.destReg;
            nextMemWb.pc = EX_MEM.pc;
            nextMemWb.writeEnable = EX_MEM.writeEnable;
        }
        else {
            outputString += "-";
        }

//-----------------EX STAGE---------------------
    EX_MEM_Reg nextExMem = {};
    nextExMem.isNop = ID_EX.isNop;
    if (!ID_EX.isNop) {
        // Fetch operand values from the register file
        uint32_t sourceOperand1 = registerFile.read(ID_EX.sourceReg1);
        uint32_t sourceOperand2 = registerFile.read(ID_EX.sourceReg2);
        if (!EX_MEM.isNop && EX_MEM.writeEnable && EX_MEM.destReg != 0) {
            if (EX_MEM.destReg == ID_EX.sourceReg1) {
                sourceOperand1 = EX_MEM.aluResult;
            }
            if (ID_EX.usesRs2 && EX_MEM.destReg == ID_EX.sourceReg2) {
                sourceOperand2 = EX_MEM.aluResult;
            }
        }
        if (!MEM_WB.isNop && MEM_WB.writeEnable && MEM_WB.destReg != 0) {
            if (MEM_WB.destReg == ID_EX.sourceReg1 && 
                !(EX_MEM.writeEnable && EX_MEM.destReg != 0 && EX_MEM.destReg == ID_EX.sourceReg1)) {
                sourceOperand1 = MEM_WB.writebackData;
            }
            if (ID_EX.usesRs2 && MEM_WB.destReg == ID_EX.sourceReg2 && 
                !(EX_MEM.writeEnable && EX_MEM.destReg != 0 && EX_MEM.destReg == ID_EX.sourceReg2)) {
                sourceOperand2 = MEM_WB.writebackData;
            }
        }
        if (ID_EX.isIType) {
            sourceOperand2 = static_cast<uint32_t>(ID_EX.immediate);
        }
        // Simple ALU operations based on the aluOperation string
        if (ID_EX.aluOperation == "ADD" || ID_EX.aluOperation == "ADDI") {
            nextExMem.aluResult = sourceOperand1 + sourceOperand2;
        } else if (ID_EX.aluOperation == "LB") {
            // For LB, compute effective address
            nextExMem.aluResult = sourceOperand1 + sourceOperand2;
        } else if (ID_EX.aluOperation == "JAL") {
            std::cerr << "here in " << currentCycle << "\n";
            // Calculate target and return address
            uint32_t currentPC = ID_EX.pc;
            uint32_t computedTarget = 0;
            uint32_t nextSequentialPC = currentPC + 4;
            nextExMem.aluResult = nextSequentialPC;  

            uint32_t instructionIndex = currentPC / 4;
            if (instructionIndex < instructionMemory.size()) {
                std::string assemblyString = instructionMemory[instructionIndex].assemblyString;
                int32_t parsedImmediate = parseImmediateValue(assemblyString);
                computedTarget = currentPC + parsedImmediate;
            } else {
                std::cerr << "Invalid PC for JAL/JALR instruction: " << currentPC << std::endl;
            }
 
            // Determine if branch is taken
            if (computedTarget != nextSequentialPC) {
                isBranchTaken = true;
                targetPC = computedTarget;
            }
        } 
        else if(ID_EX.aluOperation == "JALR") {
            uint32_t currentPC = ID_EX.pc;
            uint32_t computedTarget = 0;
            uint32_t nextSequentialPC = currentPC + 4;
            nextExMem.aluResult = nextSequentialPC;  

            uint32_t instructionIndex = currentPC / 4;
            if (instructionIndex < instructionMemory.size()) {
                std::string assemblyString = instructionMemory[instructionIndex].assemblyString;
                int32_t parsedImmediate = parseImmediateValue(assemblyString);
                computedTarget = ID_EX.sourceReg1 + parsedImmediate;
            } else {
                std::cerr << "Invalid PC for JAL/JALR instruction: " << currentPC << std::endl;
            }
 
            // Determine if branch is taken
            if (computedTarget != nextSequentialPC) {
                isBranchTaken = true;
                targetPC = computedTarget;
            }
        }
        else {
            nextExMem.aluResult = 0;
        }
        outputString += "EX(" + std::to_string(ID_EX.pc) + ")";
        pipelineStages[currentCycle][2] = "EX(" + std::to_string(ID_EX.pc/4) + ") ";
        nextExMem.destReg = ID_EX.destReg;
        nextExMem.writeEnable = ID_EX.writeEnable;
        // Set memory read flag for load instructions
        nextExMem.readMemory = (ID_EX.aluOperation == "LB");
        nextExMem.pc = ID_EX.pc;
        // For simplicity, we are not implementing store instructions here
        nextExMem.writeMemory = false;
    }
    else {
        outputString += "-";
    }

    // --------------------- ID Stage ---------------------
    ID_EX_Reg nextIdEx = {};
    nextIdEx.isNop = IF_ID.isNop;
    
    
    
    if (!IF_ID.isNop) {
        uint32_t currentInstruction = IF_ID.instruction;
        ID_EX_Reg decodedInstruction;
        decodeInstruction(currentInstruction, decodedInstruction);
        
        bool executeHazard = 
            (ID_EX.isLoad && ID_EX.writeEnable &&
            ((ID_EX.destReg == decodedInstruction.sourceReg1) || 
             (decodedInstruction.usesRs2 && ID_EX.destReg == decodedInstruction.sourceReg2)));
            
        bool memoryHazard = 
            (ID_EX.isLoad && ID_EX.writeEnable && ID_EX.destReg != 0 &&
            ((ID_EX.destReg == decodedInstruction.sourceReg1) || 
             (decodedInstruction.usesRs2 && ID_EX.destReg == decodedInstruction.sourceReg2)));

        std::cerr << currentCycle << " " << executeHazard << " " << stallFlag << "\n";
        
        if(executeHazard && stallFlag == 0) {
            std::cerr << "hello " << "\n";
            skipFetch = true;
            outputString += "ID(" + std::to_string(IF_ID.pc) + ") ";
            pipelineStages[currentCycle][3] = "ID(" + std::to_string(IF_ID.pc/4) + ")";
            nextIdEx.isNop = true;
            hazardIndicator = 0;
            hasDataHazard = true;
            stallFlag += 1;
        }
        else if(stallFlag == 1) {
            std::cerr << "hello1 " << "\n";
            hazardIndicator = 2;
            skipFetch = false;
            hasDataHazard = true;
            outputString += "- ";
            
            // Copy decoded instruction fields
            nextIdEx.isLoad = decodedInstruction.isLoad;
            nextIdEx.opcode = decodedInstruction.opcode;
            nextIdEx.destReg = decodedInstruction.destReg;
            nextIdEx.pc = IF_ID.pc;
            nextIdEx.sourceReg1 = decodedInstruction.sourceReg1;
            nextIdEx.sourceReg2 = decodedInstruction.sourceReg2;
            nextIdEx.immediate = decodedInstruction.immediate;
            nextIdEx.aluOperation = decodedInstruction.aluOperation;
            
            // Determine if it is an I-type instruction
            nextIdEx.isIType = (decodedInstruction.aluOperation == "ADDI" || 
                               decodedInstruction.aluOperation == "LB" || 
                               decodedInstruction.aluOperation == "JALR");
            
            // Set write enable for non-branch instructions
            nextIdEx.writeEnable = (decodedInstruction.aluOperation != "BEQZ");
            stallFlag = 0;
        }
        else {
            outputString += "ID(" + std::to_string(IF_ID.pc) + ") ";
            pipelineStages[currentCycle][3] = "ID(" + std::to_string(IF_ID.pc/4) + ")";
            hasDataHazard = false;
            
            // Copy decoded instruction fields
            nextIdEx.isLoad = decodedInstruction.isLoad;
            nextIdEx.opcode = decodedInstruction.opcode;
            nextIdEx.destReg = decodedInstruction.destReg;
            nextIdEx.pc = IF_ID.pc;
            nextIdEx.sourceReg1 = decodedInstruction.sourceReg1;
            nextIdEx.sourceReg2 = decodedInstruction.sourceReg2;
            nextIdEx.immediate = decodedInstruction.immediate;
            nextIdEx.aluOperation = decodedInstruction.aluOperation;
            
            // Determine if it is an I-type instruction
            nextIdEx.isIType = (decodedInstruction.aluOperation == "ADDI" || 
                               decodedInstruction.aluOperation == "LB" || 
                               decodedInstruction.aluOperation == "JALR");
            
            // Set write enable for non-branch instructions
            nextIdEx.writeEnable = (decodedInstruction.aluOperation != "BEQZ");
        }
    }
    else {
        outputString += "-";
    }
    
     // --------------------- IF Stage ---------------------
    IF_ID_Reg nextIfId = {};

    if(!isBranchTaken) {
        if(hasDataHazard) {
            if(skipFetch && hazardIndicator == 0) {
                uint32_t currentIndex = programCounter / 4;
                if (currentIndex < instructionMemory.size()) {
                    nextIfId = IF_ID;
                    outputString += "IF(" + std::to_string(currentIndex) + ") ";
                    pipelineStages[currentCycle][4] = "IF(" + std::to_string(currentIndex) + ")";
                }
                else {
                    nextIfId = IF_ID;
                    outputString += "- ";
                }
            }
            
            else if(!skipFetch && hazardIndicator == 2) {
                uint32_t currentIndex = programCounter / 4;
                if (currentIndex < instructionMemory.size()) {
                    nextIfId.instruction = instructionMemory[currentIndex].machineCode;
                    nextIfId.isNop = false;
                    nextIfId.pc = programCounter;
                    programCounter += 4;
                    outputString += "-";
                } else {
                    nextIfId.isNop = true;
                    outputString += "-";
                }
            }
        }
        else {
            uint32_t currentIndex = programCounter / 4;
            if (currentIndex < instructionMemory.size()) {
                nextIfId.instruction = instructionMemory[currentIndex].machineCode;
                nextIfId.isNop = false;
                nextIfId.pc = programCounter;
                programCounter += 4;
                outputString += "IF(" + std::to_string(currentIndex) + ") ";
                pipelineStages[currentCycle][4] = "IF(" + std::to_string(currentIndex) + ")";
            } else {
                nextIfId.isNop = true;
                outputString += "-";
            }
        }
    }

    if (isBranchTaken) {
        programCounter = targetPC;           // Update PC to target
        nextIfId.pc = programCounter;
        nextIdEx.isNop = true;
        nextIdEx.destReg = 2400;
        nextIfId.isNop = true;
        outputString += "IF(" + std::to_string(programCounter/4) + ") ";
        pipelineStages[currentCycle][4] = "IF(" + std::to_string(programCounter) + ")";
        isBranchTaken = false;
    }

    // --------------------- Pipeline Register Update ---------------------
    MEM_WB = nextMemWb;
    EX_MEM = nextExMem;
    ID_EX = nextIdEx;
    IF_ID = nextIfId;

    outputString += "\n";
    currentCycle++;
}

// Generate pipeline diagram
int instructionCount = instructionMemory.size();
std::vector<std::vector<std::string>> pipelineDiagram(instructionCount, 
    std::vector<std::string>(cycleCount, "-"));

// Process pipeline stages for visualization
for (uint32_t currentCycle = 0; currentCycle < cycleCount; ++currentCycle) {
    
    for (int stageIndex = 0; stageIndex < 5; ++stageIndex) {
        std::string stageEntry = pipelineStages[currentCycle][stageIndex];
        if (stageEntry == "-") continue;
        
        size_t openParenPos = stageEntry.find('(');
        if (openParenPos == std::string::npos) continue;
        
        std::string stageName = stageEntry.substr(0, openParenPos);
        size_t closeParenPos = stageEntry.find(')', openParenPos);
        if (closeParenPos == std::string::npos) continue;
        
        int instructionIndex = std::stoi(stageEntry.substr(openParenPos + 1, 
            closeParenPos - openParenPos - 1));
        if (instructionIndex >= instructionCount) continue;
        
        pipelineDiagram[instructionIndex][currentCycle] = stageName;
    }
}

// Print final pipeline diagram (only this part should be printed)
std::cout << "Pipeline Diagram:\n";
for (int instructionIndex = 0; instructionIndex < instructionCount; ++instructionIndex) {
    std::cout << instructionMemory[instructionIndex].assemblyString << ";";
    for (uint32_t currentCycle = 0; currentCycle < cycleCount; ++currentCycle) {
        std::cout << pipelineDiagram[instructionIndex][currentCycle] << ";";
    }
    std::cout << "\n";
}
}