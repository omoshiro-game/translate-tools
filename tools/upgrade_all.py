from pywinauto import Application
import time
from datetime import datetime
from contextlib import contextmanager
import os
import glob

# --- Configuration ---
# Directory where your stage files are stored
STAGES_DIR = os.path.join(os.getcwd(), "data", "stg4") 

# Global variables
app = None
dlg = None

def find_main_editor_window():
    """
    Finds the main editor window and updates the global 'dlg' variable.
    This is more robust for finding the window after its title has changed.
    """
    global dlg
    for w in app.windows():
        title = w.window_text()
        # Find window that starts with the editor name and contains a stage file path
        if title.startswith("アクションエディター4"):
            dlg = w
            print(f"✅ Found and set active editor window: {title}")
            return True
    
    print("❌ Could not find main editor window.")
    dlg = None # Ensure dlg is None if not found
    return False

def init_editor(exe_path="Editor_v1020.exe"):
    """Initialize the editor application and find the main window"""
    global app, dlg
    try:
        app = Application(backend="win32").start(exe_path)
    except Exception as e:
        print(f"❌ Failed to start the application: {e}")
        print("Is the exe_path correct and is the application not already running?")
        return False
    
    # Wait a bit for the window to appear
    time.sleep(4)

    # Use the new robust function to find the window
    return find_main_editor_window()

# -------------------------------------------------------------------
# NEW: File Listing Functions
# -------------------------------------------------------------------

def list_stages():
    """Lists all current version stage files in the STAGES_DIR."""
    pattern = os.path.join(STAGES_DIR, "*.stg4_1020")
    files = glob.glob(pattern)
    print(f"Found {len(files)} current stages (.stg4_1020).")
    return files

def list_old_stages():
    """Lists all stage files that are not the current version."""
    all_stages_pattern = os.path.join(STAGES_DIR, "*.stg4_*")
    current_stages_set = set(list_stages())
    
    all_stages = glob.glob(all_stages_pattern)
    old_stages = [f for f in all_stages if f not in current_stages_set]
    
    print(f"Found {len(old_stages)} old stages (non-.stg4_1020).")
    return old_stages

# -------------------------------------------------------------------
# NEW: Core Automation Functions for File Operations
# -------------------------------------------------------------------

def open_stage(filepath):
    """
    Opens a stage file using Ctrl+O.
    """
    global dlg
    if not dlg:
        print("❌ No main dialog selected.")
        return False

    print(f"-> Opening stage: {os.path.basename(filepath)}")
    dlg.set_focus()
    time.sleep(0.5)

    # Use Ctrl+O shortcut to open the file dialog
    dlg.type_keys("^o")
    time.sleep(1)

    # Find the Open dialog window
    # NOTE: The title "ファイルを開く" (Open File) might be different on your system.
    open_dlg = app.window(title="読み込むファイルの選択")
    if not open_dlg.exists(timeout=5):
        print("❌ '読み込むファイルの選択' (Open File) dialog not found!")
        return False
    
    print("   ... '読み込むファイルの選択' dialog found.")
    open_dlg.set_focus()
    time.sleep(0.3)
    
    # Type the full path to the file
    # Using 'with_spaces=True' can help with paths containing spaces
    open_dlg.type_keys(filepath, with_spaces=True)
    time.sleep(0.3)
    
    # Press Enter to open
    open_dlg.type_keys("{ENTER}")
    print(f"✅ Sent open command for '{os.path.basename(filepath)}'.")
    return True

def save_common_and_palette():
    """
    Saves the common stage and palette using Ctrl+S.
    """
    global dlg
    if not dlg:
        print("❌ No main dialog selected.")
        return False

    print("-> Saving common stage and palette (Ctrl+S)...")
    dlg.set_focus()
    time.sleep(0.5)

    # Use Ctrl+S shortcut
    dlg.type_keys("^s")
    time.sleep(1)

    try:
        # Find the "Save File" dialog. Use a timeout for robustness.
        save_dlg = app.window(title="保存先のファイルの選択")
        
        # This check waits up to 5 seconds for the dialog to exist.
        if not save_dlg.exists(timeout=5):
            print("⚠️  '保存先のファイルの選択' (Save File) dialog did not appear after Ctrl+S.")
            print("   This might mean the file was already up-to-date and saved silently.")
            return True # Assume success if no dialog appeared, as the state is likely correct.
        
        print("   ... '保存先のファイルの選択' dialog found. Confirming save.")
        save_dlg.set_focus()
        time.sleep(0.3)
        
        # Press Enter to click the default "Save" button
        save_dlg.type_keys("{ENTER}")
        
        # For added robustness, wait for the dialog to close before continuing.
        # This confirms the save operation was accepted and has finished.
        print("   ... Waiting for save confirmation dialog to close.")
        save_dlg.wait_not('visible', timeout=10)
        
        print("✅ Save command successfully completed.")
        return True

    except Exception as e:
        print(f"❌ An error occurred while handling the save dialog: {e}")
        return False

# -------------------------------------------------------------------
# Original Helper and Context Manager Functions (Unchanged)
# -------------------------------------------------------------------

def select_window_by_title(title_part):
    """
    Helper function to select a window that contains the given title part
    Returns the window object if found, None otherwise
    """
    global dlg
    for w in app.windows():
        if title_part in w.window_text():
            dlg = w
            print(f"Selected window: {w.window_text()}")
            return w
    print(f"❌ No window found containing '{title_part}'")
    return None

def save_scene_as(filename):
    """
    Save the current scene with the given filename
    """
    global dlg
    if not dlg:
        print("❌ No dialog selected")
        return False
    
    # Open File menu with Alt, F
    dlg.type_keys("%")
    dlg.type_keys("f")
    time.sleep(0.5)
    
    # Press down arrow key 4 times to navigate to "Save"
    for i in range(3):
        dlg.type_keys("{DOWN}")
        time.sleep(0.1)
    
    # Press Enter to select the menu item
    dlg.type_keys("{ENTER}")
    
    # Wait for save dialog to appear
    time.sleep(1)
    
    save_dlg = app.window(title="保存先のファイルの選択")
    if not save_dlg.exists(timeout=5):
        print("❌ Save dialog not found!")
        return False
    
    print(f"Found Save dialog: '{save_dlg.window_text()}'")
    
    # Focus the save dialog and type
    save_dlg.set_focus()
    save_dlg.type_keys(filename, with_spaces=True)
    time.sleep(0.3)
    
    # Press Enter to save
    save_dlg.type_keys("{ENTER}")
    
    print(f"✅ File '{filename}' saved successfully!")
    return True

def open_block_modal_at(current_tile_x = 1, current_tile_y = 1):
    dlg_main = select_window_by_title('アクションエディター4  .')
    dlg_main.set_focus()
    time.sleep(0.5)

    rect = dlg_main.rectangle()
    window_width = rect.right - rect.left
    window_height = rect.bottom - rect.top

    top_toolbar_height = 75 # 45 ?
    side_margin_sz = 1
    scrollbar_sz = 16
    footer_height = 20

    grid_top = top_toolbar_height # + rect.top
    grid_left = 0 # + rect.left # + side_margin_sz

    grid_width = window_width - side_margin_sz - scrollbar_sz  # subtract left toolbar and right scrollbar
    grid_height = window_height - top_toolbar_height - scrollbar_sz - footer_height  # subtract top toolbar and bottom status bar

    rows = 15
    cols = 20
    cell_width = grid_width // cols
    cell_height = grid_height // rows

    cell_x = grid_left + (cell_width * current_tile_x) - (cell_width // 2)
    cell_y = grid_top + (cell_height * current_tile_y) - ( cell_height // 2)

    dlg_main.set_focus()
    dlg.move_mouse_input(coords=(cell_x, cell_y), absolute=True) #
    time.sleep(0.3)

    # Double right-click (fast)
    dlg_main.double_click_input(coords=(cell_x, cell_y), button='right')
    time.sleep(0.5)


@contextmanager
def browse_block_data():
    dlg_block = select_window_by_title("ブロックデータ")
    dlg_block.set_focus()
    time.sleep(0.3)

    # Try to find the "挿入" button by searching through descendants
    insert_button = None
    try:
        descendants = dlg_block.descendants()

        for control in descendants:
            try:
                if control.window_text() == "挿入" and control.class_name() == "Button":
                    insert_button = control
                    break
            except:
                continue

        if not insert_button:
            print("NO '挿入' button !!!")
            pass
        else:
            print("> Clicking '挿入' button...")
            insert_button.click_input()
            time.sleep(0.5)
        yield dlg_block

    finally:
        print("CloseOperation: Closing Block Data dialog...")
        try:
            dlg_block.close()
        except:
            try:
                dlg_block.type_keys("%{F4}")
            except:
                print("Could not close Block Data dialog")


@contextmanager
def get_conditions_list():
    cond_dlg = select_window_by_title("条件")
    cond_dlg.set_focus()

    button_texts = []
    try:
        descendants = cond_dlg.descendants()

        for control in descendants:
            try:
                class_name = control.class_name()
                text = control.window_text().strip()

                if class_name == "Button" and text:
                    is_enabled = control.is_enabled()

                    if is_enabled:
                        button_texts.append(text)

                    print(f"  ➤ Button found: '{text}'")

            except Exception as e:
                # Skip controls that cause errors
                continue

        yield button_texts, cond_dlg

    finally:
        print("CloseOperation: Closing Condition dialog...")
        try:
            cond_dlg.close()
        except:
            try:
                cond_dlg.type_keys("%{F4}")
            except:
                print("Could not close Condition dialog")

def click_button_by_text(dlg, button_text):
    for c in dlg.descendants():
        if c.class_name() == "Button" and c.window_text().strip() == button_text:
            print(f"> Clicking button: '{button_text}'")
            c.click_input()
            time.sleep(0.4)
            return True
    print(f"❌ Button '{button_text}' not found!")
    return False

def find_edit_limits(edit_control):
    """
    Find the actual min/max limits of an Edit control by testing with extreme values.
    Returns (min_val, max_val, original_value).
    """
    original_value = edit_control.window_text().strip()

    try:
        edit_control.set_edit_text("999999999999")
        max_text = edit_control.window_text().strip()
        max_val = int(max_text) if max_text.lstrip('-').isdigit() else 999999

        edit_control.set_edit_text("-999999999999")
        min_text = edit_control.window_text().strip()
        min_val = int(min_text) if min_text.lstrip('-').isdigit() else -999999

        edit_control.set_edit_text(original_value)

        return min_val, max_val, original_value
    except Exception as e:
        edit_control.set_edit_text(original_value)
        return -999999, 999999, original_value

@contextmanager
def explore_common_var_dlg():
    var_dlg = select_window_by_title("コモン変数条件")
    var_dlg.set_focus()
    time.sleep(0.1)

    try:
        values = {}
        for c in var_dlg.descendants():
            if c.class_name() == "ComboBox":
                try:
                    # Get current selected item
                    current_item = c.window_text().strip()

                    # Get all items in dropdown
                    items = []
                    for i, text in enumerate(c.item_texts()):
                        try:
                            items.append([text, c.item_data(i)])
                        except:
                            continue

                    values[f"Dropdown_{len(values)+1}"] = {
                        "current": current_item,
                        "all_items": items[:99]
                    }

                    print(f"  # Dropdown {len(values)}:")
                    print(f"    Current: '{current_item}'")
                    print(f"    All items: {items[:99]}")

                except Exception as e:
                    print(f"    ❌ Could not read dropdown: {e}")

            elif c.class_name() == "msctls_updown32":
                updown_min_val, updown_max_val = c.get_range()
                values[f"UpDown_{len(values)+1}"] = {
                        "min": updown_min_val,
                        "max": updown_max_val
                    }

            elif c.class_name() == "Edit":
                min_val, max_val, original_value = find_edit_limits(c)
                values[f"UpDown_{len(values)+1}"] = {
                        "min": min_val,
                        "max": max_val,
                        "default": original_value
                    }


        yield values, var_dlg

    finally:
        print("CloseOperation: Closing 'コモン変数条件' dialog...")
        try:
            var_dlg.close()
        except:
            var_dlg.type_keys("%{F4}")


# ===================================================================
# NEW Main Script Logic
# ===================================================================
if __name__ == "__main__":
    # Initialize the editor
    if not init_editor():
        exit()
    
    # Get the list of old stages to process
    stages_to_process = list_old_stages()
    
    if not stages_to_process:
        print("\nNo old stages found to process. Exiting.")
        exit()

    print(f"\nStarting batch process for {len(stages_to_process)} old stages...")
    print("-" * 50)
    
    # Loop through each old stage file
    for i, stage_path in enumerate(stages_to_process):
        print(f"\nProcessing file {i+1}/{len(stages_to_process)}: {os.path.basename(stage_path)}")
        
        # 1. Open the old stage
        if not open_stage(stage_path):
            print(f"SKIPPING: Could not open {os.path.basename(stage_path)}.")
            continue # Move to the next file
            
        time.sleep(2) # Wait for the stage to fully load
        if not find_main_editor_window():
            print(f"SKIPPING: Lost track of the main editor window after opening.")
            continue
        
        # 2. Save the common data (which should update it)
        save_common_and_palette()
        
        time.sleep(2) # Wait for the save operation to complete

    print("-" * 50)
    print("✅ Batch processing complete!")
    
    # Optional: Close the application when done
    # print("Closing the editor in 5 seconds...")
    # time.sleep(5)
    # app.kill()