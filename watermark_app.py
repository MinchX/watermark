import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QSpinBox, QMessageBox, QGroupBox)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor
from PyQt5.QtCore import Qt
from PIL import Image, ImageDraw, ImageFont
import os

class WatermarkApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.files = []
        self.watermark_image = None

    def initUI(self):
        self.setWindowTitle('批量水印添加器')
        self.setGeometry(300, 300, 500, 400)

        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'app_icon.jpg')
        self.setWindowIcon(QIcon(icon_path))

        # 设置样式表
        self.setStyleSheet("""
            QWidget {
                background-color: #FFF0E6;
                color: #4A4A4A;
                font-family: Arial, sans-serif;
            }
            QGroupBox {
                border: 2px solid #FF7F50;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #FF7F50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #FF6347;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 1px solid #FF7F50;
                border-radius: 3px;
                padding: 2px;
            }
            QLabel {
                color: #4A4A4A;
            }
        """)

        layout = QVBoxLayout()

        # 文件选择
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout()
        self.file_label = QLabel('选择的文件: 0')
        self.file_btn = QPushButton('选择文件')
        self.file_btn.clicked.connect(self.select_files)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # 水印设置
        watermark_group = QGroupBox("水印设置")
        watermark_layout = QVBoxLayout()

        # 文字水印
        text_layout = QHBoxLayout()
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText('输入文字水印')
        text_layout.addWidget(QLabel('文字水印:'))
        text_layout.addWidget(self.text_input)
        watermark_layout.addLayout(text_layout)

        # 图片水印
        image_layout = QHBoxLayout()
        self.image_label = QLabel('未选择图片水印')
        self.image_btn = QPushButton('选择图片水印')
        self.image_btn.clicked.connect(self.select_watermark_image)
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.image_btn)
        watermark_layout.addLayout(image_layout)

        # 水印位置
        position_layout = QHBoxLayout()
        self.position_combo = QComboBox()
        self.position_combo.addItems(['左上', '右上', '左下', '右下', '中心'])
        position_layout.addWidget(QLabel('水印位置:'))
        position_layout.addWidget(self.position_combo)
        watermark_layout.addLayout(position_layout)

        # 水印角度
        angle_layout = QHBoxLayout()
        self.angle_spin = QSpinBox()
        self.angle_spin.setRange(0, 359)
        angle_layout.addWidget(QLabel('水印角度:'))
        angle_layout.addWidget(self.angle_spin)
        watermark_layout.addLayout(angle_layout)

        watermark_group.setLayout(watermark_layout)
        layout.addWidget(watermark_group)

        # 添加水印按钮
        self.watermark_btn = QPushButton('添加水印')
        self.watermark_btn.clicked.connect(self.add_watermark)
        layout.addWidget(self.watermark_btn)

        self.setLayout(layout)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择图片文件", "", "图片文件 (*.png *.jpg *.bmp)")
        self.files = files
        self.file_label.setText(f'选择的文件: {len(self.files)}')

    def select_watermark_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择水印图片", "", "图片文件 (*.png *.jpg *.bmp)")
        if file:
            self.watermark_image = file
            self.image_label.setText(os.path.basename(file))

    def get_watermark_position(self, img_size, watermark_size):
        position = self.position_combo.currentText()
        if position == '左上':
            return (10, 10)
        elif position == '右上':
            return (img_size[0] - watermark_size[0] - 10, 10)
        elif position == '左下':
            return (10, img_size[1] - watermark_size[1] - 10)
        elif position == '右下':
            return (img_size[0] - watermark_size[0] - 10, img_size[1] - watermark_size[1] - 10)
        else:  # 中心
            return ((img_size[0] - watermark_size[0]) // 2, (img_size[1] - watermark_size[1]) // 2)

    def add_watermark(self):
        if not self.files:
            QMessageBox.warning(self, "警告", "请先选择要添加水印的文件")
            return

        text = self.text_input.text()
        angle = self.angle_spin.value()
        
        for file in self.files:
            img = Image.open(file)
            original_mode = img.mode
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # 创建一个与原图大小相同的透明图层
            watermark = Image.new('RGBA', img.size, (0,0,0,0))
            draw = ImageDraw.Draw(watermark)

            if text:
                # 添加文字水印
                font = ImageFont.load_default()
                left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
                text_width = right - left
                text_height = bottom - top
                text_position = self.get_watermark_position(img.size, (text_width, text_height))
                rotated_text = Image.new('RGBA', (text_width, text_height), (0,0,0,0))
                draw_text = ImageDraw.Draw(rotated_text)
                draw_text.text((0, 0), text, font=font, fill=(255,255,255,128))
                rotated_text = rotated_text.rotate(angle, expand=1)
                watermark.paste(rotated_text, text_position, rotated_text)

            if self.watermark_image:
                # 添加图片水印
                watermark_img = Image.open(self.watermark_image).convert('RGBA')
                watermark_img = watermark_img.resize((100, 100))  # 调整大小
                watermark_img = watermark_img.rotate(angle, expand=1)
                img_position = self.get_watermark_position(img.size, watermark_img.size)
                watermark.paste(watermark_img, img_position, watermark_img)

            # 将水印图层与原图合并
            out = Image.alpha_composite(img, watermark)
            
            # 如果原图是JPEG格式，转换回RGB模式
            filename, ext = os.path.splitext(file)
            if ext.lower() in ['.jpg', '.jpeg']:
                out = out.convert('RGB')
            
            # 保存结果
            out.save(f"{filename}_watermarked{ext}")

        QMessageBox.information(self, "成功", "水印添加完成")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 为整个应用程序设置图标
    icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'app_icon.jpg')
    app.setWindowIcon(QIcon(icon_path))
    
    ex = WatermarkApp()
    ex.show()
    sys.exit(app.exec_())