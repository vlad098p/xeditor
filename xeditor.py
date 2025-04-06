from PyQt5.QtCore import QDir
import sys, os, json, subprocess
from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog, QTabWidget, QAction,
                             QPlainTextEdit, QTreeView, QFileSystemModel, QSplitter, QVBoxLayout,
                             QWidget, QMessageBox, QLineEdit, QToolBar, QLabel)
from PyQt5.QtGui import QFont, QKeySequence, QIcon
from PyQt5.QtCore import Qt, QTimer, QSettings, QFile, QTextStream
import jedi
import qdarkstyle

SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.cpp': 'cpp',
    '.c': 'c',
    '.h': 'cpp',
    '.java': 'java',
    '.html': 'html',
    '.js': 'js',
    '.css': 'css',
    '.cs': 'csharp'
}

class CodeEditor(QPlainTextEdit):
    def __init__(self, path=""):
        super().__init__()
        self.path = path
        self.setFont(QFont("Fira Code", 11))
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
        self.textChanged.connect(self.auto_save)
        self.setStyleSheet("padding: 10px;")

    def auto_save(self):
        if self.path:
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())

    def get_language(self):
        ext = os.path.splitext(self.path)[1]
        return SUPPORTED_EXTENSIONS.get(ext, 'plaintext')

    def suggest(self):
        if self.get_language() == 'python':
            source = self.toPlainText()
            line, col = self.textCursor().blockNumber() + 1, self.textCursor().columnNumber()
            script = jedi.Script(source, path=self.path)
            return [c.name for c in script.complete(line, col)]
        return []

class XEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XEditor")
        self.setGeometry(100, 100, 1200, 800)
        self.settings = QSettings("XEditor", "Session")
        self.init_ui()
        self.restore_session()

    def init_ui(self):
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.editor_tabs)

        self.create_toolbar()
        self.create_project_explorer()
        self.load_plugins()
        self.set_dark_theme()

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        open_file = QAction("📂 Відкрити файл", self)
        open_file.triggered.connect(self.open_file)
        toolbar.addAction(open_file)

        open_folder = QAction("🗂️ Відкрити папку", self)
        open_folder.triggered.connect(self.open_folder)
        toolbar.addAction(open_folder)

        run_code = QAction("▶️ Запустити Python", self)
        run_code.triggered.connect(self.run_current_file)
        toolbar.addAction(run_code)

        self.status = QLabel("Готово")
        toolbar.addWidget(self.status)

    def create_project_explorer(self):
        self.splitter = QSplitter()
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.homePath())

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.homePath()))
        self.tree.doubleClicked.connect(self.on_file_open)

        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.editor_tabs)
        self.setCentralWidget(self.splitter)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Відкрити файл")
        if path:
            self.load_file(path)

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Відкрити папку")
        if folder:
            self.tree.setRootIndex(self.model.index(folder))

    def load_file(self, path):
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.widget(i).path == path:
                self.editor_tabs.setCurrentIndex(i)
                return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            QMessageBox.warning(self, "Помилка", f"Не вдалося відкрити файл:\n{e}")
            return

        editor = CodeEditor(path)
        editor.setPlainText(content)
        self.editor_tabs.addTab(editor, os.path.basename(path))
        self.editor_tabs.setCurrentWidget(editor)

    def on_file_open(self, index):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            self.load_file(path)

    def close_tab(self, index):
        self.editor_tabs.removeTab(index)

    def run_current_file(self):
        editor = self.editor_tabs.currentWidget()
        if editor and editor.get_language() == 'python':
            try:
                output = subprocess.check_output(['python3', editor.path], stderr=subprocess.STDOUT, text=True)
            except subprocess.CalledProcessError as e:
                output = e.output
            QMessageBox.information(self, "Результат виконання", output)
        else:
            QMessageBox.warning(self, "Увага", "Запуск доступний лише для Python-файлів.")

    def set_dark_theme(self):
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def load_plugins(self):
        plugin_dir = "plugins"
        if not os.path.exists(plugin_dir):
            return
        sys.path.insert(0, plugin_dir)
        for f in os.listdir(plugin_dir):
            if f.endswith(".py"):
                __import__(f[:-3])

    def closeEvent(self, event):
        self.save_session()
        event.accept()

    def save_session(self):
        files = [self.editor_tabs.widget(i).path for i in range(self.editor_tabs.count())]
        self.settings.setValue("open_files", files)

    def restore_session(self):
        files = self.settings.value("open_files", [])
        if files:
            for path in files:
                if os.path.exists(path):
                    self.load_file(path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = XEditor()
    editor.show()
    sys.exit(app.exec_())
