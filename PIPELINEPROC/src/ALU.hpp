#ifndef ALU_HPP
#define ALU_HPP

#include <cstdint>
#include <string>

class ALU {
public:
    static uint32_t execute(const std::string& operation, uint32_t operand1, uint32_t operand2) {
        // Arithmetic operations
        if (operation == "ADD" || operation == "ADDI") {
            return operand1 + operand2;
        }
        else if (operation == "SUB") {
            return operand1 - operand2;
        }
        // Logical operations
        else if (operation == "AND") {
            return operand1 & operand2;
        }
        else if (operation == "OR") {
            return operand1 | operand2;
        }
        else if (operation == "XOR") {
            return operand1 ^ operand2;
        }
        // Shift operations
        else if (operation == "SLL") {
            return operand1 << (operand2 & 0x1F);  // Shift left logical
        }
        else if (operation == "SRL") {
            return operand1 >> (operand2 & 0x1F);  // Shift right logical
        }
        else if (operation == "SRA") {
            return static_cast<uint32_t>(static_cast<int32_t>(operand1) >> (operand2 & 0x1F));  // Shift right arithmetic
        }
        // Compare operations
        else if (operation == "SLT") {
            return (static_cast<int32_t>(operand1) < static_cast<int32_t>(operand2)) ? 1 : 0;
        }
        else if (operation == "SLTU") {
            return (operand1 < operand2) ? 1 : 0;
        }
        // Branch comparisons
        else if (operation == "BEQ") {
            return (operand1 == operand2) ? 1 : 0;
        }
        else if (operation == "BNE") {
            return (operand1 != operand2) ? 1 : 0;
        }
        else if (operation == "BLT") {
            return (static_cast<int32_t>(operand1) < static_cast<int32_t>(operand2)) ? 1 : 0;
        }
        else if (operation == "BGE") {
            return (static_cast<int32_t>(operand1) >= static_cast<int32_t>(operand2)) ? 1 : 0;
        }
        else if (operation == "BLTU") {
            return (operand1 < operand2) ? 1 : 0;
        }
        else if (operation == "BGEU") {
            return (operand1 >= operand2) ? 1 : 0;
        }
        // Memory and jump operations
        else if (operation == "LB" || operation == "JALR" || operation == "JAL") {
            return operand1 + operand2;  // Address calculation
        }

        // Default case
        return 0;
    }

    // Helper function for branch comparison
    static bool branchCondition(const std::string& operation, uint32_t operand1, uint32_t operand2) {
        if (operation == "BEQ") {
            return operand1 == operand2;
        }
        else if (operation == "BNE") {
            return operand1 != operand2;
        }
        else if (operation == "BLT") {
            return static_cast<int32_t>(operand1) < static_cast<int32_t>(operand2);
        }
        else if (operation == "BGE") {
            return static_cast<int32_t>(operand1) >= static_cast<int32_t>(operand2);
        }
        else if (operation == "BLTU") {
            return operand1 < operand2;
        }
        else if (operation == "BGEU") {
            return operand1 >= operand2;
        }
        return false;
    }
};

#endif // ALU_HPP