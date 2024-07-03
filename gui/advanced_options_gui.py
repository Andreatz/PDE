import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem

class AdvancedOptionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Advanced Options")
        self.setGeometry(100, 100, 400, 300)

        self.symbol_label = QLabel("Symbol:")
        self.symbol_entry = QLineEdit()
        self.activity_label = QLabel("Activity Range:")
        self.activity_entry = QLineEdit()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_row)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Symbol", "Activity Range"])

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.symbol_label)
        self.layout.addWidget(self.symbol_entry)
        self.layout.addWidget(self.activity_label)
        self.layout.addWidget(self.activity_entry)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

    def add_row(self):
        symbol = self.symbol_entry.text()
        activity_range = self.activity_entry.text()
        if symbol and activity_range:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(symbol))
            self.table.setItem(row_position, 1, QTableWidgetItem(activity_range))
            self.symbol_entry.clear()
            self.activity_entry.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdvancedOptionsWindow()
    window.show()
    sys.exit(app.exec_())
