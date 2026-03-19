import config
from GUI.gui_builders import GUIBuilders
from GUI.gui_helpers import GUIHelpers
from GUI.gui_workflows import GUIWorkflows


class PasswordManagerGUI(GUIBuilders, GUIHelpers, GUIWorkflows):
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        self.root.resizable(config.RESIZABLE_WIDTH, config.RESIZABLE_HEIGHT)

        self.ip_vars = []
        self.discovered_ips = []
        self.checked_ips = set()

        self.loading = False
        self.loading_texts = config.LOADING_TEXTS
        self.loading_index = 0

        self.current_password_visible = False
        self.new_password_visible = False
        self.confirm_password_visible = False

        self.setup_styles()
        self.build_ui()
        self.refresh_devices()