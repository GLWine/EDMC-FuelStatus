import tkinter as tk
import logging
import l10n
import functools
import os

from typing import Optional, Tuple, Dict, Any
from config import appname, appversion

plugin_name = os.path.basename(os.path.dirname(__file__))  # Get the plugin name from the directory path
logger = logging.getLogger(f'{appname}.{plugin_name}')  # Set up logging for the plugin

# Check if the app version is 5.11.0 or higher
# Split version string into major, minor, and fix components
major, minor, fix = map(int, (str(appversion).split('+')[0]).split('.'))
if major >= 5 and minor >= 11 and fix >= 0: # check if version is 5.11.0 or higher
    # use the new translation method
    _ = functools.partial(l10n.translations.tl, context=__file__)
else:
    # use the old translation method
    _ = functools.partial(l10n.Translations.translate, context=__file__)

label: Optional[tk.Label]  # Main label for the plugin
status: Optional[tk.Label]  # Status label for the plugin

main_tank: Optional[float] = None  # Main tank fuel level
reservoir: Optional[float] = None  # Reservoir fuel level


def plugin_start3(plugin_dir: str) -> str:
    """
    Plugin startup method.

    Args:
    plugin_dir (str): The directory where the plugin is located.
    """
    logger.debug('fuelstatus plugin loaded')
    return "FuelStatus"


def plugin_stop() -> None:
    """
    Plugin stop method.
    """
    pass


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """
    Called when the user changes preferences in the plugin settings.
    This function is a placeholder and does not perform any actions.

    Args:
        cmdr: Current command name (unused).
        is_beta: if the game is currently in beta (unused).
    """
    update_status()


def plugin_app(parent) -> Tuple[tk.Label, tk.Label]:
    """
    Create and initialize the main and status labels for the plugin UI.

    This function creates two Tkinter Label widgets: one for the main label and one for the status.
    It assigns them to the global variables 'label' and 'status', updates their initial state,
    and returns them as a tuple.

    Args:
        parent: The parent Tkinter widget to which the labels will be attached.

    Returns:
        Tuple[tk.Label, tk.Label]: The main label and status label widgets.
    """
    global label, status

    # Create the main label and status label as children of the parent widget
    label = tk.Label(parent, text="")
    status = tk.Label(parent, text="")

    # Initialize the labels with the current fuel status
    update_status()

    return (label, status)


def dashboard_entry(cmdr: str, is_beta: bool, entry: Dict[str, Any]) -> None:
    """
    Update the fuel tank values from a dashboard entry.

    This function resets both main_tank and reservoir to None, then checks if the
    entry contains fuel data. If present, it updates main_tank and reservoir with
    the corresponding values from the entry. Finally, it calls update_status() to
    refresh the GUI labels.

    Args:
        cmdr: Current command name (unused).
        is_beta: if the game is currently in beta (unused).
        entry: Dictionary containing Data from status.json.
    """
    global main_tank, reservoir

    # Reset both main_tank and reservoir to ensure old values are cleared
    main_tank = None
    reservoir = None

    # Check if the entry contains fuel data
    if "Fuel" in entry:
        # If present, update main_tank with the value from the entry
        if "FuelMain" in entry["Fuel"]:
            main_tank = entry["Fuel"]["FuelMain"]
        # If present, update reservoir with the value from the entry
        if "FuelReservoir" in entry["Fuel"]:
            reservoir = entry["Fuel"]["FuelReservoir"]

    # Refresh the GUI labels with the updated tank values
    update_status()


def update_status() -> None:
    """
    Update the GUI labels with the current fuel levels.

    - If 'label' is set, updates its text to "Fuel levels".
    - If either tank value is missing, shows a waiting or error message.
    - If both tank values are present, displays their values.
    """
    global label, status

    # Update the main label if initialized
    if label is not None:
        label["text"] = f'{_("Fuel levels")}:'  # LANG: Label with the plugin name
    # Check if tank data is available
    if main_tank is None or reservoir is None:
        # No data for both tanks
        if main_tank is None and reservoir is None:
            if status is not None:
                status["text"] = _("waiting for data …")  # LANG: Waiting for the json file to be populated and made accessible
        else:
            # Only one value is missing: show error
            if status is not None:
                status["text"] = _("ERROR")  # LANG: Error message for missing tank data
            logger.error("One of main tank and reservoir fuel levels is None, the other isn’t … WTF?")
    else:
        # Both values are available: show levels
        if status is not None:
            status["text"] = (
                f"{round(main_tank, 3)} t ({_('main')}), "  # LANG: Quantity of fuel in the main tank
                f"{round(reservoir, 3)} t ({_('reservoir')})"  # LANG: Amount of fuel in the operating tank
            )
