// Part of the Concrete Compiler Project, under the BSD3 License with Zama Exceptions.
// See https://github.com/zama-ai/homomorphizer/blob/master/LICENSE.txt for license information.

#include <zamalang/Support/logging.h>

namespace mlir {
namespace zamalang {
static bool verbose = false;
static StreamWrap<llvm::raw_ostream> errWrap(&llvm::errs());
static StreamWrap<llvm::raw_ostream> nullWrap(&llvm::nulls());

// Returns a stream for logging errors
StreamWrap<llvm::raw_ostream> &log_error(void) { return errWrap; }

// Returns a stream that either shows or discards messages depending
// on the setup through `setupLogging`.
StreamWrap<llvm::raw_ostream> &log_verbose(void) {
  return (verbose) ? errWrap : nullWrap;
}

// Sets up logging. If `verbose` is false, messages passed to
// `log_verbose` will be discarded.
void setupLogging(bool verbose) { ::mlir::zamalang::verbose = verbose; }
bool isVerbose() { return verbose; }
} // namespace zamalang
} // namespace mlir
