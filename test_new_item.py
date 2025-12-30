import sys
from PySide6.QtWidgets import QApplication, QDialog
from gui.NewItem_ui import Ui_Dialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create a dialog window
    dialog = QDialog()
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    
    # Show the dialog
    dialog.show()
    
    sys.exit(app.exec())
