// Part of the Concrete Compiler Project, under the BSD3 License with Zama Exceptions.
// See https://github.com/zama-ai/homomorphizer/blob/master/LICENSE.txt for license information.


#ifndef ZAMALANG_CONVERSION_LOWLFHEUNPARAMETRIZE_PASS_H_
#define ZAMALANG_CONVERSION_LOWLFHEUNPARAMETRIZE_PASS_H_

#include "mlir/Pass/Pass.h"

namespace mlir {
namespace zamalang {
std::unique_ptr<OperationPass<ModuleOp>>
createConvertLowLFHEUnparametrizePass();
} // namespace zamalang
} // namespace mlir

#endif