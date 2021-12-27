// Part of the Concrete Compiler Project, under the BSD3 License with Zama Exceptions.
// See https://github.com/zama-ai/homomorphizer/blob/master/LICENSE.txt for license information.

#ifndef ZAMALANG_DIALECT_RT_IR_RTOPS_H
#define ZAMALANG_DIALECT_RT_IR_RTOPS_H

#include <mlir/IR/BuiltinOps.h>
#include <mlir/IR/BuiltinTypes.h>
#include <mlir/Interfaces/ControlFlowInterfaces.h>
#include <mlir/Interfaces/SideEffectInterfaces.h>

#include "zamalang/Dialect/RT/IR/RTTypes.h"

#define GET_OP_CLASSES
#include "zamalang/Dialect/RT/IR/RTOps.h.inc"

#endif
