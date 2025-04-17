# gini_server32.py
# Runs in a 32-bit Python environment managed by msl-loadlib.
# Loads the 32-bit C library and exposes its functions.

import os
import ctypes
import sys

try:
    from msl.loadlib import Server32
except ImportError:
    # This error won't typically be seen by the user, but is good practice
    print("ERROR: msl.loadlib not found in the 32-bit server environment.", file=sys.stderr)
    sys.exit(1)

# --- Configuration ---
# Assume the .so is in the same directory as this server script
# The client (logic.py) will ensure this script is found.
LIB_NAME = 'libginiadder.so'
C_FUNC_NAME = 'process_gini_pure_c'

class GiniAdderServer(Server32):
    """
    Server that loads the 32-bit libginiadder.so library and exposes
    the process_gini_pure_c function.
    """
    def __init__(self, host, port, **kwargs):
        """
        Initializes the server and loads the C library.

        host: Host address provided by msl-loadlib.
        port: Port number provided by msl-loadlib.
        kwargs: Extra arguments (quiet, authkey) from msl-loadlib.
        """
        library_path = os.path.join(os.path.dirname(__file__), LIB_NAME)
        print(f"[Server32] Initializing GiniAdderServer...", file=sys.stderr)
        print(f"[Server32] Attempting to load library: {library_path}", file=sys.stderr)

        if not os.path.exists(library_path):
            print(f"[Server32] FATAL ERROR: Library '{library_path}' not found.", file=sys.stderr)
            # Raise an exception to prevent the server from starting improperly
            raise FileNotFoundError(f"32-bit library not found: {library_path}")

        try:
            # --- Load the 32-bit library using ctypes.CDLL ---
            # This works because *this* script runs in a 32-bit process.
            # Use 'cdll' for standard cdecl convention expected from gcc -m32
            super().__init__(library_path, 'cdll', host, port, **kwargs)
            print(f"[Server32] Successfully loaded '{LIB_NAME}' via ctypes.CDLL.", file=sys.stderr)

            # --- Define signature for the C function accessed via self.lib ---
            # self.lib is the ctypes CDLL object created by Server32
            c_func = getattr(self.lib, C_FUNC_NAME)
            c_func.argtypes = [ctypes.c_float]
            c_func.restype = ctypes.c_int
            print(f"[Server32] Set signature for function '{C_FUNC_NAME}'.", file=sys.stderr)

        except OSError as e:
            print(f"[Server32] FATAL ERROR: OSError loading library '{library_path}': {e}", file=sys.stderr)
            raise # Re-raise the exception
        except AttributeError as e:
             print(f"[Server32] FATAL ERROR: Function '{C_FUNC_NAME}' not found in library: {e}", file=sys.stderr)
             raise # Re-raise the exception
        except Exception as e:
            print(f"[Server32] FATAL ERROR: Unexpected error during server init: {type(e).__name__}: {e}", file=sys.stderr)
            raise # Re-raise the exception


    # --- Expose methods callable by the Client64 ---
    # The method name here ('process_gini_pure_c') is what the client will request.
    def process_gini_pure_c(self, gini_value_float):
        """
        Receives the float value from the Client64, calls the C function,
        and returns the integer result back to the client.
        """
        print(f"[Server32] Received request: process_gini_pure_c({gini_value_float})", file=sys.stderr)
        try:
            # Access the C function via the self.lib (ctypes) object
            result = self.lib.process_gini_pure_c(ctypes.c_float(gini_value_float))
            print(f"[Server32] C function returned: {result}", file=sys.stderr)
            return result
        except Exception as e:
            # Catch errors during the actual C call
            print(f"[Server32] ERROR calling C function '{C_FUNC_NAME}': {type(e).__name__}: {e}", file=sys.stderr)
            # Raise the exception so Client64 receives a Server32Error
            raise

# The Server32 base class handles the main server loop when executed.
# No explicit server start code is needed here.
