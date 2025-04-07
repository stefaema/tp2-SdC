# gui.py
# Defines the Tkinter GUI application class. Imports logic.py.

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys # Import sys for stderr logging in GUI context if needed
from typing import Optional, List, Dict, Any
import logic # Import the core logic module

class GiniApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("GINI Index Fetcher")
        master.geometry("550x480")
        master.config(bg="#f0f0f0")

        # Inject logic functions
        self.get_gini_data = logic.get_gini_data
        self.find_latest_valid_gini = logic.find_latest_valid_gini
        # Use the actual C processing function from logic
        self.process_with_c = logic.process_data_with_c

        self._setup_styles()
        self._create_widgets()
        self._layout_widgets()

        self.latest_gini_value_for_c = None
        self.entry_code.focus_set()

    # _setup_styles, _create_widgets, _layout_widgets as before...
    def _setup_styles(self):
        """Configure ttk styles."""
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        if 'clam' in available_themes: self.style.theme_use('clam')
        elif 'alt' in available_themes: self.style.theme_use('alt')
        self.style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10), padding=5)
        self.style.configure("TEntry", font=("Segoe UI", 10), padding=5)
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        self.style.configure("Summary.TLabel", font=("Segoe UI", 11))
        self.style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="gray")

    def _create_widgets(self):
        """Create all the GUI widgets."""
        self.country_code_var = tk.StringVar(); self.status_var = tk.StringVar(value="Enter a 3-letter country code and click Fetch."); self.summary_country_var = tk.StringVar(value="-"); self.summary_year_var = tk.StringVar(value="-"); self.summary_gini_var = tk.StringVar(value="-")
        self.input_frame = ttk.Frame(self.master, padding="15 10 15 5"); self.summary_frame = ttk.Frame(self.master, padding="15 5 15 10", borderwidth=1, relief="solid"); self.history_frame = ttk.Frame(self.master, padding="15 0 15 5"); self.status_frame = ttk.Frame(self.master, padding="15 5 15 10")
        self.label_code = ttk.Label(self.input_frame, text="Country Code:"); self.entry_code = ttk.Entry(self.input_frame, textvariable=self.country_code_var, width=8); self.fetch_button = ttk.Button(self.input_frame, text="Fetch GINI Data", command=self.fetch_and_display_handler)
        self.label_summary_country_title = ttk.Label(self.summary_frame, text="Country:", style="Summary.TLabel"); self.label_summary_country_value = ttk.Label(self.summary_frame, textvariable=self.summary_country_var, style="Summary.TLabel", anchor="w"); self.label_summary_year_title = ttk.Label(self.summary_frame, text="Latest Year:", style="Summary.TLabel"); self.label_summary_year_value = ttk.Label(self.summary_frame, textvariable=self.summary_year_var, style="Summary.TLabel"); self.label_summary_gini_title = ttk.Label(self.summary_frame, text="Latest GINI:", style="Summary.TLabel"); self.label_summary_gini_value = ttk.Label(self.summary_frame, textvariable=self.summary_gini_var, style="Summary.TLabel")
        self.label_history_header = ttk.Label(self.history_frame, text="Historical Data (Oldest First)", style="Header.TLabel"); self.result_text = scrolledtext.ScrolledText(self.history_frame, wrap=tk.WORD, state='disabled', height=10, width=60, font=("Consolas", 9), relief=tk.SUNKEN, borderwidth=1)
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, style="Status.TLabel")
        self.entry_code.bind("<Return>", self.fetch_and_display_handler)

    def _layout_widgets(self):
        """Arrange widgets using the grid layout manager."""
        self.master.grid_columnconfigure(0, weight=1); self.master.grid_rowconfigure(0, weight=0); self.master.grid_rowconfigure(1, weight=0); self.master.grid_rowconfigure(2, weight=1); self.master.grid_rowconfigure(3, weight=0)
        self.input_frame.grid(row=0, column=0, sticky="ew"); self.input_frame.grid_columnconfigure(1, weight=1); self.label_code.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w"); self.entry_code.grid(row=0, column=1, padx=5, pady=5, sticky="ew"); self.fetch_button.grid(row=0, column=2, padx=(5, 0), pady=5, sticky="e")
        self.summary_frame.grid(row=1, column=0, sticky="ew", pady=(5,10)); self.summary_frame.grid_columnconfigure(1, weight=1); self.label_summary_country_title.grid(row=0, column=0, sticky="w", padx=5, pady=2); self.label_summary_country_value.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=2); self.label_summary_year_title.grid(row=1, column=0, sticky="w", padx=5, pady=2); self.label_summary_year_value.grid(row=1, column=1, sticky="w", padx=5, pady=2); self.label_summary_gini_title.grid(row=1, column=2, sticky="e", padx=(10,5), pady=2); self.label_summary_gini_value.grid(row=1, column=3, sticky="w", padx=5, pady=2)
        self.history_frame.grid(row=2, column=0, sticky="nsew"); self.history_frame.grid_rowconfigure(1, weight=1); self.history_frame.grid_columnconfigure(0, weight=1); self.label_history_header.grid(row=0, column=0, sticky="w", pady=(0,5)); self.result_text.grid(row=1, column=0, sticky="nsew")
        self.status_frame.grid(row=3, column=0, sticky="ew"); self.status_label.pack(fill=tk.X)


    # update_status, clear_output_fields, display_history_in_textbox as before...
    def update_status(self, message: str, is_error=False):
        self.status_var.set(message); self.status_label.config(foreground="red" if is_error else "gray"); self.master.update_idletasks()
    def clear_output_fields(self):
        self.summary_country_var.set("-"); self.summary_year_var.set("-"); self.summary_gini_var.set("-"); self.latest_gini_value_for_c = None
        try: self.result_text.config(state='normal'); self.result_text.delete('1.0', tk.END); self.result_text.config(state='disabled')
        except tk.TclError as e: print(f"Error clearing text widget: {e}", file=sys.stderr)
    def display_history_in_textbox(self, records: Optional[List[Dict[str, Any]]]):
        text_to_display = ""
        if records:
            valid_records = sorted([r for r in records if r and r.get('value') is not None and r.get('date')], key=lambda x: x.get('date', ''))
            if valid_records: lines = []; [lines.append(f"  Year: {e['date']}, Index: {float(e['value']):>6.2f}") if isinstance(e.get('value'), (int, float, str)) and str(e.get('value')).replace('.','',1).isdigit() else lines.append(f"  Year: {e.get('date','?')}, Index: {e.get('value','?')} (invalid?)") for e in valid_records]; text_to_display = "\n".join(lines)
            else: text_to_display = "(No valid historical data points found)"
        elif records == []: text_to_display = "(No data points available for this period)"
        else: text_to_display = "(Could not load historical data)"
        try: self.result_text.config(state='normal'); self.result_text.delete('1.0', tk.END); self.result_text.insert(tk.END, text_to_display); self.result_text.config(state='disabled')
        except tk.TclError as e: print(f"Error updating text widget: {e}", file=sys.stderr)


    # --- Event Handler ---
    def fetch_and_display_handler(self, event=None):
        """Handles the button click/Enter key press event."""
        country_code = self.country_code_var.get().strip().upper()
        if len(country_code) != 3 or not country_code.isalpha():
            messagebox.showerror("Input Error", "Please enter a valid 3-letter alphabetic country code (e.g., ARG)."); return

        self.fetch_button.config(state='disabled'); self.entry_code.config(state='disabled')
        self.clear_output_fields(); self.update_status(f"Fetching data for {country_code}...")

        # --- Call Logic Layer ---
        gini_records, error_msg = self.get_gini_data(country_code) # Uses logic.get_gini_data
        # ------------------------

        self.fetch_button.config(state='normal'); self.entry_code.config(state='normal'); self.entry_code.focus_set()

        if error_msg:
            messagebox.showerror("API/Network Error", error_msg) # Show error from logic layer
            self.update_status(f"Failed to retrieve data for {country_code}.", is_error=True); self.display_history_in_textbox(None)
        elif gini_records is not None:
            latest_record = self.find_latest_valid_gini(gini_records) # Uses logic.find_latest_valid_gini
            if latest_record:
                self.summary_country_var.set(latest_record.get('country_name', country_code)); self.summary_year_var.set(latest_record.get('date', 'N/A'))
                try:
                    gini_float = float(latest_record['value'])
                    self.summary_gini_var.set(f"{gini_float:.2f}"); self.latest_gini_value_for_c = gini_float
                    # --- Trigger C processing ---
                    self._trigger_c_processing(gini_float) # Call the method below
                    # -----------------------------
                except (ValueError, TypeError):
                    self.summary_gini_var.set("Invalid"); self.update_status("Warning: Latest GINI value is not a valid number.", is_error=True); self.latest_gini_value_for_c = None
                self.update_status("Data fetched successfully.")
            elif not gini_records: self.update_status(f"No GINI data points found for {country_code} in {DATE_RANGE}.", is_error=False)
            else: self.update_status(f"Found records for {country_code}, but none had valid GINI values.", is_error=True)
            self.display_history_in_textbox(gini_records)


    def _trigger_c_processing(self, gini_value: float):
        """Calls the C processing function from logic.py and shows result/error."""
        print(f"[GUI] Triggering C processing with value: {gini_value}", file=sys.stderr)
        try:
            # Call the function imported from the logic module
            c_result = self.process_with_c(gini_value)

            if c_result is not None:
                 messagebox.showinfo("C Processing Result",
                                     f"Input GINI: {gini_value:.2f}\nResult from C Library: {c_result}")
                 self.update_status(f"Data processed by C. Result: {c_result}")
            else:
                 # Error occurred during C call (e.g., library load failed)
                 # logic.py already printed details to stderr
                 messagebox.showerror("C Processing Error", "Failed to execute C function.\nCheck console/stderr for details (e.g., missing library).")
                 self.update_status("Error during C library processing.", is_error=True)

        except Exception as e:
            # Catch unexpected errors specifically during the trigger/call phase in GUI
            print(f"[GUI] Error calling C processing function: {e}", file=sys.stderr)
            messagebox.showerror("C Processing Error", f"Unexpected error setting up C call:\n{e}")
            self.update_status("Error setting up C library processing.", is_error=True)
