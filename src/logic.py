# logic.py
# Contains core data fetching and processing logic, NO GUI code.
# Includes CLI entry point and C library integration (using msl-loadlib Client64).

import requests
import sys
import argparse
import ctypes # Still needed for type definitions if not using __getattr__
import os
from typing import Optional, List, Dict, Any

# --- Import Client64 ---
try:
    from msl.loadlib import Client64
    # Import Server32Error to catch specific errors from the server
    from msl.loadlib.exceptions import Server32Error
except ImportError:
    print("ERROR: 'msl-loadlib' is not installed. Please run setup script or 'pip install msl-loadlib'", file=sys.stderr)
    sys.exit(1)

# --- Constants ---
BASE_URL = "https://api.worldbank.org/v2/en/country"
INDICATOR = "SI.POV.GINI"
DATE_RANGE = "2011:2020"
PER_PAGE = "100"

# --- C Library Integration using Client64 ---

# Name of the Python module file containing the Server32 class
SERVER_MODULE = 'server_32' # No .py extension needed

# Global client instance (lazy loaded)
_gini_client = None

class GiniAdderClient(Client64):
    """
    Client to communicate with the GiniAdderServer running in a 32-bit process.
    """
    def __init__(self):
        print(f"[Client64] Initializing GiniAdderClient...", file=sys.stderr)
        try:
            # Initialize Client64, specifying the 32-bit server module.
            # msl-loadlib will find SERVER_MODULE.py and run it in a 32-bit Python process.
            super().__init__(module32=SERVER_MODULE)
            print(f"[Client64] Successfully initialized Client64 for module '{SERVER_MODULE}'.", file=sys.stderr)
        except Exception as e:
            # Catch errors during Client64 initialization (e.g., cannot start server process)
            print(f"[Client64] FATAL ERROR during Client64 init: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise # Re-raise to prevent use of uninitialized client

    # --- Option 1: Define explicit methods (Good for clarity, IDE help) ---
    # def process_gini_pure_c(self, gini_value: float) -> int:
    #     """
    #     Sends a request to the 'process_gini_pure_c' method on the Server32.
    #     """
    #     print(f"[Client64] Sending request: 'process_gini_pure_c' with value {gini_value}", file=sys.stderr)
    #     # The first argument to request32 is the METHOD NAME on the Server32 class.
    #     # Subsequent arguments are passed to that method.
    #     return self.request32('process_gini_pure_c', gini_value)

    # --- Option 2: Use __getattr__ (Simpler if many functions just pass through) ---
    def __getattr__(self, name):
        """
        Dynamically creates methods that call request32 with the method name.
        This avoids writing a wrapper method for every function on the server.
        """
        # Check if the requested name is likely a method we want to proxy
        # Avoid proxying special methods like __deepcopy__, __getstate__ etc.
        if name.startswith('_'):
             raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        print(f"[Client64] __getattr__ creating proxy for '{name}'", file=sys.stderr)
        def send_request(*args, **kwargs):
            print(f"[Client64] Sending request via proxy: '{name}'", file=sys.stderr)
            # 'name' will be 'process_gini_pure_c' when called
            return self.request32(name, *args, **kwargs)
        return send_request
    # --- End Option 2 ---


def _get_client_instance() -> Optional[GiniAdderClient]:
    """Gets or creates the singleton GiniAdderClient instance."""
    global _gini_client
    if _gini_client is None:
        print("[Logic] Creating GiniAdderClient instance...", file=sys.stderr)
        try:
            _gini_client = GiniAdderClient()
        except Exception as e:
            # Handle client creation failure
             print(f"[Logic] Failed to create GiniAdderClient: {type(e).__name__}: {e}", file=sys.stderr)
             _gini_client = None # Ensure it's None if creation fails
    return _gini_client


# --- C Function Call (process_data_with_c) ---
# This function now uses the client instance to make the request
def process_data_with_c(gini_value: float) -> Optional[int]:
    """
    Uses the GiniAdderClient (Client64) to request the C processing
    from the 32-bit server.

    Args:
        gini_value: The float GINI value to process.

    Returns:
        The integer result from the C function via the server, or None if an error occurs.
    """
    client = _get_client_instance()
    if client is None:
        print("[Logic] Cannot process with C: Client instance is not available.", file=sys.stderr)
        return None

    try:
        # Call the method on the client instance.
        # If using explicit methods (Option 1):
        # result = client.process_gini_pure_c(gini_value)

        # If using __getattr__ (Option 2):
        # This looks like a direct method call, but __getattr__ intercepts it
        # and calls client.request32('process_gini_pure_c', gini_value)
        result = client.process_gini_pure_c(gini_value)

        print(f"[Logic] Received result from 32-bit server: {result}", file=sys.stderr)
        return result
    except Server32Error as e:
        # Catch errors specifically raised by the 32-bit server process
        print(f"[Logic] Error received from 32-bit server: {e}", file=sys.stderr)
        return None
    except Exception as e:
        # Catch other potential errors during the request (e.g., connection issues)
        print(f"[Logic] Error during request to 32-bit server: {type(e).__name__}: {e}", file=sys.stderr)
        return None


# --- Data Fetching (get_gini_data - NO CHANGES NEEDED) ---
def get_gini_data(country_code: str) -> tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    # ... (Keep the existing robust get_gini_data function) ...
    url = f"{BASE_URL}/{country_code}/indicator/{INDICATOR}"
    params = {
        "format": "json",
        "date": DATE_RANGE,
        "per_page": PER_PAGE
    }
    print(f"[Logic] Requesting URL: {url} with params: {params}", file=sys.stderr)
    error_message = None
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"[Logic] Response Status Code: {response.status_code}", file=sys.stderr)
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
             error_detail = f"API did not return JSON. Content-Type: {content_type}. Response: {response.text[:200]}..."
             print(f"Error: {error_detail}", file=sys.stderr)
             if response.text and 'Invalid format' in response.text: error_message = "World Bank API Error: Invalid format requested or resource not found."
             elif response.text and 'Invalid value' in response.text: error_message = f"World Bank API Error: Invalid country code '{country_code}'?"
             else: error_message = "Received non-JSON response from the server."
             return None, error_message
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or len(data) < 1:
            error_detail = "Unexpected API response format (not a list or empty)."
            print(f"Error: {error_detail}", file=sys.stderr)
            error_message = "Received unexpected data format from the server."
            return None, error_message
        if isinstance(data[0], dict) and "message" in data[0]:
            error_messages = [msg.get("value", "Unknown error") for msg in data[0]["message"]]
            error_text = "\n".join(error_messages)
            print(f"Error from World Bank API: {error_text}", file=sys.stderr)
            if any("No data available" in msg for msg in error_messages) or any("No matches" in msg for msg in error_messages): return [], None
            else: error_message = f"World Bank API Error:\n{error_text}"; return None, error_message
        if len(data) == 2:
            if data[1] is None: return [], None
            if not isinstance(data[1], list):
                 error_detail = f"Unexpected data format (data[1] is not list). Got: {type(data[1])}"; print(f"Error: {error_detail}", file=sys.stderr); error_message = "Received unexpected data structure from the server."; return None, error_message
            return data[1], None
        elif len(data) == 1 and isinstance(data[0], dict) and "total" in data[0] and data[0]["total"] == 0: return [], None
        else: print(f"Warning: Received unexpected response structure (length {len(data)}). Assuming no data.", file=sys.stderr); return [], None
    except requests.exceptions.HTTPError as e: error_detail = f"HTTP Error: {e.response.status_code} {e.response.reason} for URL {e.request.url}"; print(f"Error: {error_detail}", file=sys.stderr); error_message = f"HTTP Error: {e.response.status_code}\n{e.response.reason}"; return None, error_message
    except requests.exceptions.ConnectionError as e: error_detail = f"Connection Error: {e}"; print(f"Error: {error_detail}", file=sys.stderr); error_message = "Could not connect to the World Bank API.\nCheck internet connection."; return None, error_message
    except requests.exceptions.Timeout: error_detail = "Timeout Error"; print(f"Error: {error_detail}", file=sys.stderr); error_message = "The request to the World Bank API timed out."; return None, error_message
    except requests.exceptions.RequestException as e: error_detail = f"Request Exception: {e}"; print(f"Error: {error_detail}", file=sys.stderr); error_message = f"An error occurred during the request:\n{e}"; return None, error_message
    except requests.exceptions.JSONDecodeError:
        error_detail = "JSON Decode Error"; print(f"Error: {error_detail}", file=sys.stderr)
        try: raw_text = response.text; print(f"Raw response text: {raw_text[:500]}...", file=sys.stderr)
        except: pass
        error_message = "Could not decode the server's response (invalid JSON)."; return None, error_message
    except Exception as e:
        error_detail = f"Unexpected error in get_gini_data: {type(e).__name__}: {e}"; print(f"Error: {error_detail}", file=sys.stderr)
        import traceback; traceback.print_exc(file=sys.stderr); error_message = f"An unexpected error occurred:\n{type(e).__name__}"; return None, error_message


# --- Data Processing (find_latest_valid_gini - NO CHANGES NEEDED) ---
def find_latest_valid_gini(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    # ... (Keep the existing find_latest_valid_gini function) ...
    latest_valid_record = None; latest_year = -1
    if not records: return None
    for record in records:
        if not isinstance(record, dict): continue
        value = record.get('value'); date_str = record.get('date')
        if value is not None and date_str:
            try:
                current_year = int(date_str); _ = float(value)
                if current_year > latest_year:
                    latest_year = current_year
                    record['country_name'] = record.get('country', {}).get('value', 'N/A')
                    latest_valid_record = record
            except (ValueError, TypeError, KeyError) as e: print(f"[Logic] Warning: Skipping record with invalid format/keys: {record}, Error: {e}", file=sys.stderr); continue
    return latest_valid_record


# --- CLI Entry Point (__main__ - NO CHANGES NEEDED) ---
if __name__ == "__main__":
    # ... (Keep the existing argparse CLI code) ...
    parser = argparse.ArgumentParser(description=f"Fetch GINI index data ({DATE_RANGE}) from the World Bank API.")
    parser.add_argument("country_code", help="The 3-letter ISO country code (e.g., ARG, USA, BRA).")
    parser.add_argument("-H", "--history", action="store_true", help="Show historical data in addition to the latest value.")
    parser.add_argument("-C", "--process-c", action="store_true", help="Also process the latest value using the C function.")
    args = parser.parse_args()
    code = args.country_code.strip().upper()
    if len(code) != 3 or not code.isalpha(): print(f"Error: Invalid country code format '{args.country_code}'. Please use a 3-letter code.", file=sys.stderr); sys.exit(1)
    print(f"Fetching GINI data for {code}...", file=sys.stderr)
    records, fetch_error = get_gini_data(code)
    if fetch_error: print(f"\nError fetching data: {fetch_error}", file=sys.stderr); sys.exit(1)
    if records is None: print(f"\nError: An unknown issue occurred while fetching data for {code}.", file=sys.stderr); sys.exit(1)
    if not records: print(f"\nNo GINI data points found for {code} in the period {DATE_RANGE}."); sys.exit(0)
    latest_record = find_latest_valid_gini(records)
    if not latest_record:
        print(f"\nData found for {code}, but no records had a valid GINI value in the period {DATE_RANGE}.")
        if args.history:
             print("\n--- Historical Data (raw/invalid values might be present) ---")
             valid_records_sorted = sorted([r for r in records if isinstance(r, dict)], key=lambda x: x.get('date', ''))
             if valid_records_sorted:
                 for entry in valid_records_sorted: print(f"  Year: {entry.get('date', 'N/A')}, Index: {entry.get('value', 'N/A')}")
             else: print("  (No historical records found in response)")
        sys.exit(0)
    print("\n--- GINI Index Summary ---"); print(f"Country:      {latest_record.get('country_name', code)}"); print(f"Latest Year:  {latest_record['date']}")
    try:
        latest_gini_float = float(latest_record['value']); print(f"Latest GINI:  {latest_gini_float:.2f}")
        if args.process_c:
             print("\n--- C Processing (via Client64/Server32) ---");
             c_result = process_data_with_c(latest_gini_float) # Calls the modified function
             if c_result is not None: print(f"Input to C:   {latest_gini_float:.2f}"); print(f"Output: {c_result}")
             else: print("Error during C processing (check logs).", file=sys.stderr)
    except (ValueError, TypeError):
        print(f"Latest GINI:  {latest_record['value']} (Error: Not a valid number)", file=sys.stderr)

        if args.process_c: print("\nCannot perform C processing: Latest GINI value is not a valid number.", file=sys.stderr)
    if args.history:
        print("\n--- Historical Data (Oldest First, Valid Only) ---")
        valid_records_sorted = sorted([r for r in records if r and r.get('value') is not None and r.get('date')], key=lambda x: x.get('date', ''))
        if valid_records_sorted:
            for entry in valid_records_sorted:
                 try: print(f"  Year: {entry['date']}, Index: {float(entry['value']):>6.2f}")
                 except (ValueError, TypeError): print(f"  Year: {entry['date']}, Index: {entry['value']} (invalid?)")
        else: print("  (No valid historical records found)")
    sys.exit(0)
