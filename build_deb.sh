#!/bin/bash

APP_NAME="xeditor"
VERSION="1.0"
BUILD_DIR="${APP_NAME}_deb_build"

echo "🛠️ Створення структури .deb пакету з іконкою..."

# Очистити старе
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/opt/$APP_NAME"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/128x128/apps"

# Створити control файл
cat <<EOF > "$BUILD_DIR/DEBIAN/control"
Package: $APP_NAME
Version: $VERSION
Section: editors
Priority: optional
Architecture: all
Depends: python3, python3-pyqt5, python3-jedi, python3-pip
Maintainer: Ти
Description: XEditor — багатомовний редактор коду в стилі VS Code
EOF

# Копіювати файл програми
cp xeditor.py "$BUILD_DIR/opt/$APP_NAME/"

# Створити скрипт запуску
cat <<EOF > "$BUILD_DIR/usr/bin/xeditor"
#!/bin/bash
python3 /opt/$APP_NAME/xeditor.py
EOF
chmod +x "$BUILD_DIR/usr/bin/xeditor"

# Копіювати іконку (перевір, щоб вона була поруч!)
cp xeditor.png "$BUILD_DIR/usr/share/icons/hicolor/128x128/apps/"

# Створити desktop файл
cat <<EOF > "$BUILD_DIR/usr/share/applications/xeditor.desktop"
[Desktop Entry]
Name=XEditor
Comment=Простий редактор коду
Exec=xeditor
Icon=xeditor
Terminal=false
Type=Application
Categories=Development;TextEditor;
EOF

# Збірка
echo "📦 Створення пакету..."
dpkg-deb --build "$BUILD_DIR"
mv "$BUILD_DIR.deb" "${APP_NAME}_${VERSION}_all.deb"
echo "✅ Готово: ${APP_NAME}_${VERSION}_all.deb"
