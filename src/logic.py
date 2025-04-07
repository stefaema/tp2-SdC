# logic.py
# Contains core data fetching and processing logic, NO GUI code.
# Includes CLI entry point and C library integration.

import requests
import sys
import argparse
import ctypes # Import ctypes
import os      # Import os for path manipulation
from typing import Optional, List, Dict, Any

# --- Constants ---
BASE_URL = "https://api.worldbank.org/v2/en/country"
INDICATOR = "SI.POV.GINI"
DATE_RANGE = "2011:2020"
PER_PAGE = "100"

# --- C Library Setup ---
LIB_NAME = 'libginiadder.so'
C_FUNC_NAME = 'process_gini_pure_c'
_c_library = None
_c_process_func = None

def _load_c_library():
    """Loads the C library and sets up the function signature."""
    global _c_library, _c_process_func
    if _c_process_func: # Already loaded
        return True

    try:
        # Construct path relative to this file's location
        lib_path = os.path.join(os.path.dirname(__file__), LIB_NAME)
        print(f"[Logic] Attempting to load C library from: {lib_path}", file=sys.stderr)
        _c_library = ctypes.CDLL(lib_path)

        # Get the function pointer
        _c_process_func = getattr(_c_library, C_FUNC_NAME) # Use getattr for safer access

        # --- Define function signature (CRUCIAL) ---
        # Corresponds to: int process_gini_pure_c(float gini_value)
        _c_process_func.argtypes = [ctypes.c_float] # Expects a C float
        _c_process_func.restype = ctypes.c_int      # Returns a C int
        # -------------------------------------------

        print(f"[Logic] Successfully loaded C function '{C_FUNC_NAME}'", file=sys.stderr)
        return True

    except OSError as e:
        print(f"[Logic] Error loading C library '{LIB_NAME}': {e}", file=sys.stderr)
        print(f"[Logic] Ensure '{LIB_NAME}' is compiled correctly (esp. -m32) and exists at the expected path.", file=sys.stderr)
        _c_library = None
        _c_process_func = None
        return False
    except AttributeError as e:
         print(f"[Logic] Error finding C function '{C_FUNC_NAME}' in library '{LIB_NAME}': {e}", file=sys.stderr)
         _c_library = None
         _c_process_func = None
         return False
    except Exception as e: # Catch any other loading errors
        print(f"[Logic] Unexpected error loading C library or function: {e}", file=sys.stderr)
        _c_library = None
        _c_process_func = None
        return False


# --- Data Fetching (Keep the robust get_gini_data function from previous step) ---
def get_gini_data(country_code: str) -> tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    # ... (robust get_gini_data function as before) ...
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


# --- Data Processing (Keep find_latest_valid_gini function from previous step) ---
def find_latest_valid_gini(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    # ... (find_latest_valid_gini function as before) ...
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


# --- C Function Call ---
def process_data_with_c(gini_value: float) -> Optional[int]:
    """
    Calls the C function 'process_gini_pure_c' from the shared library.

    Args:
        gini_value: The float GINI value to process.

    Returns:
        The integer result from the C function, or None if the library
        cannot be loaded or the function call fails.
    """
    if not _load_c_library(): # Try to load if not already loaded
        return None # Loading failed

    if _c_process_func is None: # Check again after loading attempt
         print("[Logic] Error: C function reference is not available.", file=sys.stderr)
         return None

    try:
        # Call the C function, passing the Python float wrapped as c_float
        result = _c_process_func(ctypes.c_float(gini_value))
        print(f"[Logic] C function '{C_FUNC_NAME}' called with {gini_value}, returned {result}", file=sys.stderr)
        return result
    except Exception as e:
        # Catch potential errors during the actual function call
        print(f"[Logic] Error calling C function '{C_FUNC_NAME}': {e}", file=sys.stderr)
        return None

# --- CLI Entry Point (Keep the argparse section from previous step) ---
if __name__ == "__main__":
    # ... (argparse CLI code as before) ...
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
             print("\n--- C Processing ---"); c_result = process_data_with_c(latest_gini_float)
             if c_result is not None: print(f"Input to C:   {latest_gini_float:.2f}"); print(f"Output: {c_result}")
             else: print("Error during C processing.", file=sys.stderr)
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
