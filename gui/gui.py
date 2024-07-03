import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QCheckBox, QSpinBox, QTableWidget, QTableWidgetItem
import threading
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from advanced_options_gui import AdvancedOptionsWindow
from launcher import process_file
from launcher import run_script
from launcher import run_script_in_thread


class ScriptLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # File Path
        self.file_label = QLabel("File Path:")
        self.file_entry = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_entry)
        file_layout.addWidget(self.browse_button)

        # Output Folder
        self.output_folder_label = QLabel("Output Folder:")
        self.output_folder_entry = QLineEdit()
        self.output_folder_button = QPushButton("Browse")
        self.output_folder_button.clicked.connect(self.browse_output_folder)
        output_folder_layout = QHBoxLayout()
        output_folder_layout.addWidget(self.output_folder_label)
        output_folder_layout.addWidget(self.output_folder_entry)
        output_folder_layout.addWidget(self.output_folder_button)

        # Start Number
        self.start_label = QLabel("Start Number:")
        self.start_entry = QLineEdit()
        start_layout = QHBoxLayout()
        start_layout.addWidget(self.start_label)
        start_layout.addWidget(self.start_entry)

        # End Number
        self.end_label = QLabel("End Number:")
        self.end_entry = QLineEdit()
        end_layout = QHBoxLayout()
        end_layout.addWidget(self.end_label)
        end_layout.addWidget(self.end_entry)

        # Output Format
        self.output_format_label = QLabel("Output Format:")
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["default", "smi", "sdf"])
        output_format_layout = QHBoxLayout()
        output_format_layout.addWidget(self.output_format_label)
        output_format_layout.addWidget(self.output_format_combo)

        # Multithreading Checkbox and Threads
        self.thread_checkbox = QCheckBox("Multithreading")
        self.thread_checkbox.stateChanged.connect(self.show_threads)
        self.thread_spinbox = QSpinBox()
        self.thread_spinbox.setMinimum(1)
        self.thread_spinbox.setMaximum(100)
        self.thread_spinbox.setValue(1)
        self.thread_spinbox.setEnabled(False)
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(self.thread_checkbox)
        thread_layout.addWidget(self.thread_spinbox)

        # Text File Checkbox
        self.text_file_checkbox = QCheckBox("Use Text File")
        self.text_file_checkbox.stateChanged.connect(self.show_file_button)
        self.text_file_button = QPushButton("Choose Text File")
        self.text_file_button.clicked.connect(self.browse_text_file)
        self.text_file_button.setEnabled(False)
        text_file_layout = QHBoxLayout()
        text_file_layout.addWidget(self.text_file_checkbox)
        text_file_layout.addWidget(self.text_file_button)

        # Advanced Options Button
        self.advanced_options_button = QPushButton("Advanced Options")
        self.advanced_options_button.clicked.connect(self.show_advanced_options)

        # Analyze Button
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.analyze_file)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(file_layout)
        main_layout.addLayout(text_file_layout)        
        main_layout.addLayout(output_folder_layout)
        main_layout.addLayout(start_layout)
        main_layout.addLayout(end_layout)
        main_layout.addLayout(output_format_layout)
        main_layout.addWidget(self.advanced_options_button)
        main_layout.addLayout(thread_layout)

        main_layout.addWidget(self.analyze_button)

        self.setLayout(main_layout)
        self.setWindowTitle("Patent Analyzer Tool")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_path:
            self.file_entry.setText(file_path)

    def browse_output_folder(self):
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if output_folder:
            self.output_folder_entry.setText(output_folder)

    def browse_text_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt)")
        if file_path:
            self.text_file_entry.setText(file_path)

    def show_threads(self, state):
        if state == 2:
            self.thread_spinbox.setEnabled(True)
        else:
            self.thread_spinbox.setEnabled(False)

    def show_file_button(self, state):
        if state == 2:
            self.text_file_button.setEnabled(True)
            self.file_label.setEnabled(False)
            self.file_entry.setEnabled(False)
            self.browse_button.setEnabled(False)
        else:
            self.text_file_button.setEnabled(False)
            self.file_label.setEnabled(True)
            self.file_entry.setEnabled(True)
            self.browse_button.setEnabled(True)
    
    def show_advanced_options(self):
        self.advanced_options_window = AdvancedOptionsWindow()
        self.advanced_options_window.show()


    def analyze_file(self):
        file_path = self.file_entry.text()
        start_num = self.start_entry.text()
        end_num = self.end_entry.text()
        output_format = self.output_format_combo.currentText()

        # Check if multithreading is enabled and get the number of threads
        if self.thread_checkbox.isChecked():
            threads = self.thread_spinbox.value()
        else:
            threads = 1

        # Check if text file is enabled and get the file paths and ranges
        if self.text_file_checkbox.isChecked():
            with open(self.text_file_entry.text(), 'r') as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip().split(",")
                file_path = line[0]
                start_num = line[1]
                end_num = line[2]
                threading.Thread(target=process_file, args=(file_path, start_num, end_num, output_format), daemon=True).start()
        else:
            output_folder = self.output_folder_entry.text()
            threading.Thread(target=process_file, args=(file_path, start_num, end_num, output_format, output_folder), daemon=True).start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScriptLauncher()
    window.show()
    sys.exit(app.exec_())
