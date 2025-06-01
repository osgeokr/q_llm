from PyQt5.QtWidgets import QDialog, QTextEdit, QPushButton, QVBoxLayout, QLabel, QTextBrowser, QCheckBox
from PyQt5.QtGui import QTextCursor
import threading
from PyQt5.QtCore import QTimer

from .gemma_client import ask_gemma_stream, go_to_location

class QLLMDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Q-LLM: LLM-based AI Assistant")

        # Text input area for the prompt
        self.prompt_edit = QTextEdit()
        self.send_button = QPushButton("Send")
        self.result_box = QTextBrowser()
        self.loc_checkbox = QCheckBox("Find and move to location on map")

        # Layout configuration
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter prompt:"))
        layout.addWidget(self.prompt_edit)
        layout.addWidget(self.loc_checkbox)
        layout.addWidget(self.send_button)
        layout.addWidget(QLabel("Response:"))
        layout.addWidget(self.result_box)
        self.setLayout(layout)

        self.send_button.clicked.connect(self.handle_prompt)

    def handle_prompt(self):
        # Handle send button click
        prompt = self.prompt_edit.toPlainText()
        self.result_box.clear()

        if self.loc_checkbox.isChecked():
            # Execute map-based location movement in a background thread
            QTimer.singleShot(0, lambda: self.handle_location_move(prompt))
        else:
            # Query the LLM using a background thread
            threading.Thread(target=self.ask_gemma, args=(prompt,), daemon=True).start()

    def ask_gemma(self, prompt):
        def on_chunk(text):
            self.result_box.moveCursor(QTextCursor.End)
            self.result_box.insertPlainText(text)

        ask_gemma_stream(prompt, on_chunk)        

    def handle_location_move(self, prompt):
        def log_to_result_box(message):
            self.result_box.moveCursor(QTextCursor.End)
            self.result_box.insertPlainText(message + '\n')

        log_to_result_box("[📡 Starting map movement process...]\n")
        # Use QTimer to execute the map movement in the main thread
        QTimer.singleShot(0, lambda: go_to_location(prompt, log=log_to_result_box))
