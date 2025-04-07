# main.py
# Entry point for the GINI Fetcher application.

import tkinter as tk
import gui # Import the module containing the GiniApp class
import sys

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = gui.GiniApp(root) # Instantiate the GUI app from the gui module
        root.mainloop()
    except tk.TclError as e:
         # Catch potential theme errors or other Tk initialization issues
         print(f"\nTkinter Error: {e}", file=sys.stderr)
         print("Could not initialize the Tkinter GUI.", file=sys.stderr)
         print("Ensure you have 'python3-tk' (or equivalent) installed.", file=sys.stderr)
         sys.exit(1)
    except ImportError as e:
        # Catch if gui or logic modules are not found
        print(f"\nImport Error: {e}", file=sys.stderr)
        print("Please ensure 'gui.py' and 'logic.py' are in the same directory or accessible via PYTHONPATH.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected startup errors
        print(f"\nUnexpected Error on Startup: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
