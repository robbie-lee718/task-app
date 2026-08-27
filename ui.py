import sys
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QScrollArea, QFrame, QMessageBox, QDialog,
    QLineEdit, QTextEdit, QFormLayout
)
from PyQt5.QtCore import Qt
from sqlite import Sqlite

class TaskDetailDialog(QDialog):
    def __init__(self, name, description, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Details")
        self.resize(400, 300)
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: white; }
            QLabel { color: white; }
            QTextEdit { 
                background-color: #1e1e1e; color: #ddd; 
                border: 1px solid #3c3c3c; border-radius: 4px; padding: 8px;
                font-size: 13px;
            }
            QPushButton { 
                background-color: #0d6efd; color: white; border: none; 
                padding: 6px 16px; border-radius: 4px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #0b5ed7; }
        """)

        layout = QVBoxLayout(self)

        title_label = QLabel(name)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 5px;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setPlainText(description if description else "No description provided.")
        layout.addWidget(desc_text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

# Task Input Dialog for Add & Edit
class TaskDialog(QDialog):
    def __init__(self, title="Task", name="", description="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(350)
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: white; }
            QLabel { color: white; font-weight: bold; }
            QLineEdit, QTextEdit { 
                background-color: #1e1e1e; color: white; 
                border: 1px solid #3c3c3c; border-radius: 4px; padding: 6px; 
            }
            QPushButton { 
                background-color: #0d6efd; color: white; border: none; 
                padding: 6px 12px; border-radius: 4px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #0b5ed7; }
        """)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit(name)
        self.desc_input = QTextEdit(description)
        self.desc_input.setMaximumHeight(100)

        form_layout.addRow("Task Name:", self.name_input)
        form_layout.addRow("Description:", self.desc_input)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #6c757d;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def get_values(self):
        return self.name_input.text().strip(), self.desc_input.toPlainText().strip()


class TaskItemWidget(QFrame):
    def __init__(self, task_id, name, description, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.name = name
        self.description = description

        self.setCursor(Qt.PointingHandCursor)

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                padding: 6px;
            }
            QLabel { color: #ffffff; }
            QPushButton {
                border-radius: 4px;
                padding: 4px 12px;
                font-weight: bold;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        text_container = QVBoxLayout()
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        text_container.addWidget(self.name_label)

        layout.addLayout(text_container)
        layout.addStretch()

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setStyleSheet("""
            QPushButton { background-color: #0d6efd; color: white; border: none; }
            QPushButton:hover { background-color: #0b5ed7; }
        """)
        self.edit_btn.clicked.connect(lambda _, tid=self.task_id: on_edit(tid))
        layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("""
            QPushButton { background-color: #dc3545; color: white; border: none; }
            QPushButton:hover { background-color: #bb2d3b; }
        """)
        self.delete_btn.clicked.connect(lambda _, tid=self.task_id: on_delete(tid))
        layout.addWidget(self.delete_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            dialog = TaskDetailDialog(self.name, self.description, parent=self)
            dialog.exec_()
        super().mousePressEvent(event)


class TaskListApp(QMainWindow):
    def __init__(self, db_path="tasks.db", table_name="tasks"):
        super().__init__()
        self.db_path = db_path
        self.table_name = table_name

        self.init_db()

        self.setWindowTitle("TaskApp")
        self.resize(450, 550)
        self.setStyleSheet("background-color: #1e1e1e;")

        # Set Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add Button
        self.add_btn = QPushButton("+ Add New Task")
        self.add_btn.setStyleSheet("""
            QPushButton { 
                background-color: #198754; color: white; border: none; 
                padding: 10px; font-weight: bold; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #157347; }
        """)
        self.add_btn.clicked.connect(self.handle_add_task)
        main_layout.addWidget(self.add_btn)

        # Scroll Area for Task Items
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.task_list_container = QWidget()
        self.task_list_layout = QVBoxLayout(self.task_list_container)
        self.task_list_layout.setAlignment(Qt.AlignTop)
        self.task_list_layout.setSpacing(8)

        self.scroll_area.setWidget(self.task_list_container)
        main_layout.addWidget(self.scroll_area)

        self.load_tasks_from_db()

    def init_db(self):
        schema = {
            "name": "TEXT NOT NULL",
            "description": "TEXT"
        }
        with Sqlite(self.db_path, self.table_name) as db:
            db.create_table(schema)

    def load_tasks_from_db(self):
        # Clear existing list widgets
        while self.task_list_layout.count():
            item = self.task_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Query items from Database
        with Sqlite(self.db_path, self.table_name) as db:
            records = db.get_all()

        for record in records:
            task_widget = TaskItemWidget(
                task_id=record["id"],
                name=record["name"],
                description=record["description"] or "",
                on_edit=self.handle_edit,
                on_delete=self.handle_delete
            )
            self.task_list_layout.addWidget(task_widget)

    def handle_add_task(self):
        dialog = TaskDialog(title="Add New Task", parent=self)
        if dialog.exec_() == QDialog.Accepted:
            name, description = dialog.get_values()
            if not name:
                QMessageBox.warning(self, "Validation Error", "Task name cannot be empty.")
                return

            with Sqlite(self.db_path, self.table_name) as db:
                db.insert({"name": name, "description": description})

            self.load_tasks_from_db()

    def handle_edit(self, task_id):
        # Fetch target task details
        with Sqlite(self.db_path, self.table_name) as db:
            task = db.get(task_id)

        if not task:
            return

        dialog = TaskDialog(
            title="Edit Task", 
            name=task["name"], 
            description=task["description"] or "", 
            parent=self
        )
        if dialog.exec_() == QDialog.Accepted:
            name, description = dialog.get_values()
            if not name:
                QMessageBox.warning(self, "Validation Error", "Task name cannot be empty.")
                return

            with Sqlite(self.db_path, self.table_name) as db:
                db.update(task_id, {"name": name, "description": description})

            self.load_tasks_from_db()

    def handle_delete(self, task_id):
        reply = QMessageBox.question(
            self, 'Confirm Delete', 
            'Are you sure you want to delete this task?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            with Sqlite(self.db_path, self.table_name) as db:
                db.delete(task_id)
            self.load_tasks_from_db()


def main():
    app = QApplication(sys.argv)
    window = TaskListApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()