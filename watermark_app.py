import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QSpinBox, QMessageBox, QGroupBox, QListWidget, 
                             QSlider, QRadioButton, QButtonGroup)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor
from PyQt5.QtCore import Qt, QCoreApplication
from PIL import Image, ImageDraw, ImageFont
import os

class WatermarkApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.files = []
        self.watermark_image = None

    def initUI(self):
        self.setWindowTitle('水印')
        self.setGeometry(300, 300, 600, 600)  # 增加窗口高度

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

        main_layout = QVBoxLayout()

        # 1. 文件选择
        file_group = QGroupBox("选择文件")
        file_layout = QVBoxLayout()
        file_button_layout = QHBoxLayout()
        self.file_label = QLabel('选择的文件: 0')
        self.file_btn = QPushButton('选择文件')
        self.file_btn.clicked.connect(self.select_files)
        file_button_layout.addWidget(self.file_label)
        file_button_layout.addWidget(self.file_btn)
        file_layout.addLayout(file_button_layout)
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # 2. 水印设置
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

        # 透明度设置
        opacity_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)
        self.opacity_label = QLabel('透明度: 50%')
        self.opacity_slider.valueChanged.connect(self.update_opacity_label)
        opacity_layout.addWidget(QLabel('水印透明度:'))
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        watermark_layout.addLayout(opacity_layout)

        watermark_group.setLayout(watermark_layout)
        main_layout.addWidget(watermark_group)

        # 3. 水印位置
        position_group = QGroupBox("水印位置")
        position_layout = QVBoxLayout()

        # 固定位置 vs 重复位置 (改为横向排列)
        position_type_layout = QHBoxLayout()
        self.position_type_group = QButtonGroup()
        self.fixed_position_radio = QRadioButton("固定位置")
        self.repeat_position_radio = QRadioButton("重复位置")
        self.position_type_group.addButton(self.fixed_position_radio)
        self.position_type_group.addButton(self.repeat_position_radio)
        self.fixed_position_radio.setChecked(True)
        position_type_layout.addWidget(self.fixed_position_radio)
        position_type_layout.addWidget(self.repeat_position_radio)
        position_layout.addLayout(position_type_layout)

        # 固定位置设置
        self.fixed_position_widget = QWidget()
        fixed_layout = QVBoxLayout()
        
        position_combo_layout = QHBoxLayout()
        self.position_combo = QComboBox()
        self.position_combo.addItems(['左上', '右上', '左下', '右下', '中心'])
        position_combo_layout.addWidget(QLabel('位置:'))
        position_combo_layout.addWidget(self.position_combo)
        fixed_layout.addLayout(position_combo_layout)

        angle_layout = QHBoxLayout()
        self.angle_spin = QSpinBox()
        self.angle_spin.setRange(0, 359)
        angle_layout.addWidget(QLabel('旋转角度:'))
        angle_layout.addWidget(self.angle_spin)
        fixed_layout.addLayout(angle_layout)

        self.fixed_position_widget.setLayout(fixed_layout)
        position_layout.addWidget(self.fixed_position_widget)

        # 重复位置设置
        self.repeat_position_widget = QWidget()
        repeat_layout = QVBoxLayout()

        repeat_spacing_layout = QHBoxLayout()
        self.repeat_spacing_spin = QSpinBox()
        self.repeat_spacing_spin.setRange(50, 500)
        self.repeat_spacing_spin.setValue(100)
        repeat_spacing_layout.addWidget(QLabel('重复间隔:'))
        repeat_spacing_layout.addWidget(self.repeat_spacing_spin)
        repeat_layout.addLayout(repeat_spacing_layout)

        repeat_angle_layout = QHBoxLayout()
        self.repeat_angle_spin = QSpinBox()
        self.repeat_angle_spin.setRange(0, 359)
        self.repeat_angle_spin.setValue(0)
        repeat_angle_layout.addWidget(QLabel('旋转角度:'))
        repeat_angle_layout.addWidget(self.repeat_angle_spin)
        repeat_layout.addLayout(repeat_angle_layout)

        self.repeat_position_widget.setLayout(repeat_layout)
        position_layout.addWidget(self.repeat_position_widget)

        self.fixed_position_radio.toggled.connect(self.toggle_position_options)
        self.repeat_position_radio.toggled.connect(self.toggle_position_options)

        position_group.setLayout(position_layout)
        main_layout.addWidget(position_group)

        # 添加水印按钮
        self.watermark_btn = QPushButton('添加水印')
        self.watermark_btn.clicked.connect(self.add_watermark)
        main_layout.addWidget(self.watermark_btn)

        self.setLayout(main_layout)
        self.toggle_position_options()

    def toggle_position_options(self):
        is_fixed = self.fixed_position_radio.isChecked()
        self.fixed_position_widget.setVisible(is_fixed)
        self.repeat_position_widget.setVisible(not is_fixed)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择图片文件", "", "图片文件 (*.png *.jpg *.bmp)")
        self.files = files
        self.file_label.setText(f'选择的文件: {len(self.files)}')
        self.file_list.clear()
        for file in self.files:
            self.file_list.addItem(os.path.basename(file))

    def select_watermark_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择水印图片", "", "图片文件 (*.png *.jpg *.bmp)")
        if file:
            self.watermark_image = file
            self.image_label.setText(os.path.basename(file))

    def update_opacity_label(self, value):
        self.opacity_label.setText(f'透明度: {value}%')

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
        opacity = self.opacity_slider.value() / 100.0
        is_fixed_position = self.fixed_position_radio.isChecked()
        
        if is_fixed_position:
            angle = self.angle_spin.value()
            position = self.position_combo.currentText()
            repeat = False
            repeat_angle = 0
            repeat_spacing = 0
        else:
            angle = self.repeat_angle_spin.value()  # 使用重复位置的旋转角度
            position = 'left_top'  # 默认值，实际上不会使用
            repeat = True
            repeat_angle = angle  # 重复角度与单个水印的旋转角度相同
            repeat_spacing = self.repeat_spacing_spin.value()
        
        for file in self.files:
            img = Image.open(file)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # 创建一个与原图大小相同的透明图层
            watermark = Image.new('RGBA', img.size, (0,0,0,0))

            if text or self.watermark_image:
                if repeat:
                    self.add_repeated_watermark(watermark, text, self.watermark_image, angle, opacity, repeat_angle, repeat_spacing)
                else:
                    self.add_single_watermark(watermark, text, self.watermark_image, angle, opacity, position)

            # 将水印图层与原图合并
            out = Image.alpha_composite(img, watermark)
            
            # 如果原图是JPEG格式，转换回RGB模式
            filename, ext = os.path.splitext(file)
            if ext.lower() in ['.jpg', '.jpeg']:
                out = out.convert('RGB')
            
            # 保存结果
            out.save(f"{filename}_watermarked{ext}")

        QMessageBox.information(self, "成功", "水印添加完成")

    def add_single_watermark(self, watermark, text, watermark_image, angle, opacity, position):
        if text:
            self.add_text_watermark(watermark, text, angle, opacity, position)
        if watermark_image:
            self.add_image_watermark(watermark, watermark_image, angle, opacity, position)

    def add_repeated_watermark(self, watermark, text, watermark_image, angle, opacity, repeat_angle, repeat_spacing):
        # 创建单个水印
        watermark_single = Image.new('RGBA', (repeat_spacing, repeat_spacing), (0,0,0,0))
        self.add_single_watermark(watermark_single, text, watermark_image, repeat_angle, opacity, 'left_top')
        
        # 对单个水印进行旋转
        watermark_single = watermark_single.rotate(repeat_angle, expand=True)
        
        # 计算旋转后的水印大小
        rotated_size = watermark_single.size
        
        for y in range(0, watermark.height, repeat_spacing):
            for x in range(0, watermark.width, repeat_spacing):
                # 直接粘贴旋转后的水印，不再进行额外旋转
                watermark.paste(watermark_single, (x, y), watermark_single)

    def add_text_watermark(self, watermark, text, angle, opacity, position):
        font = ImageFont.load_default()
        draw = ImageDraw.Draw(watermark)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_width = right - left
        text_height = bottom - top
        text_position = self.get_watermark_position(watermark.size, (text_width, text_height))
        rotated_text = Image.new('RGBA', (text_width, text_height), (0,0,0,0))
        draw_text = ImageDraw.Draw(rotated_text)
        draw_text.text((0, 0), text, font=font, fill=(255,255,255,int(255*opacity)))
        rotated_text = rotated_text.rotate(angle, expand=1)
        watermark.paste(rotated_text, text_position, rotated_text)

    def add_image_watermark(self, watermark, watermark_image, angle, opacity, position):
        img = Image.open(watermark_image).convert('RGBA')
        img = img.resize((100, 100))  # 调整大小
        img = img.rotate(angle, expand=1)
        # 应用透明度
        img_with_opacity = Image.new('RGBA', img.size, (0,0,0,0))
        for x in range(img.width):
            for y in range(img.height):
                r, g, b, a = img.getpixel((x, y))
                img_with_opacity.putpixel((x, y), (r, g, b, int(a * opacity)))
        img_position = self.get_watermark_position(watermark.size, img.size)
        watermark.paste(img_with_opacity, img_position, img_with_opacity)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置应用程序名称和组织
    QCoreApplication.setApplicationName("水印")
    QCoreApplication.setOrganizationName("YourCompanyName")
    QCoreApplication.setOrganizationDomain("yourcompany.com")
    
    # 为整个应用程序设置图标
    icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'app_icon.jpg')
    app.setWindowIcon(QIcon(icon_path))
    
    ex = WatermarkApp()
    ex.show()
    sys.exit(app.exec_())
