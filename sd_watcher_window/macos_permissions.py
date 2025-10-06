import logging
import subprocess
from multiprocessing import Process


logger = logging.getLogger(__name__)
# Supported browsers with their bundle IDs
BROWSERS = {
    "Google Chrome": "com.google.Chrome",
    "Microsoft Edge": "com.microsoft.edgemac",
    "Safari": "com.apple.Safari"
}

def background_ensure_permissions() -> None:
    """
     Ensure permissions are set in the background. This is a blocking call. The process will be killed when the background process exits.
     
     
     @return None ( Nothing in Visual Studio ) or the PID of the process that was spawned ( int
    """
    permission_process = Process(target=ensure_permissions, args=(()))
    permission_process.start()
    
    for browser_name, bundle_id in BROWSERS.items():
        try:
            # AppleScript to trigger Automation popup via bundle ID
            script = f'''
            tell application id "{bundle_id}"
                if it is running then
                    get name of windows
                end if
            end tell
            '''
            subprocess.run(["osascript", "-e", script], check=True)
            logger.info(f"Triggered Automation prompt for {browser_name} ({bundle_id})")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to trigger {browser_name} ({bundle_id}): {e}")
    return


def ensure_permissions() -> None:
    """
     Ensure activitywatch accessibility permissions are available prompting if they are not. This is a hack to avoid accidental use of ActivityWatch's permission dialog which is very inefficient in the event that the user doesn't have permission to access the activitywatch window
     
     
     @return ` ` None ` ` if permissions are available otherwise an error
    """
    # noreorder
    from AppKit import (  # fmt: skip
        NSURL,
        NSAlert,
        NSAlertFirstButtonReturn,
        NSWorkspace,
    )
    from ApplicationServices import AXIsProcessTrusted  # fmt: skip

    accessibility_permissions = AXIsProcessTrusted()
    # If the user has accessibility permissions and the user has not already set accessibility permissions.
    if not accessibility_permissions:
        logger.info("No accessibility permissions, prompting user")
        title = "Missing accessibility permissions"
        info = "To let ActivityWatch capture window titles grant it accessibility permissions. \n If you've already given ActivityWatch accessibility permissions and are still seeing this dialog, try removing and re-adding them."

        alert = NSAlert.new()
        alert.setMessageText_(title)
        alert.setInformativeText_(info)

        alert.addButtonWithTitle_("Open accessibility settings")
        alert.addButtonWithTitle_("Close")

        choice = alert.runModal()
        # If the user clicks on the first button return the user s accessibility accessibility.
        if choice == NSAlertFirstButtonReturn:
            NSWorkspace.sharedWorkspace().openURL_(
                NSURL.URLWithString_(
                    "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
                )
            )
