import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import piexif
import io
import os
from datetime import datetime
import customtkinter as ctk

# Настройка customtkinter
ctk.set_appearance_mode("system")  # Светлая/темная тема в зависимости от системы
ctk.set_default_color_theme("blue")  # Синяя цветовая тема

class MetaWipeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройки окна
        self.title("MetaWipe - Очистка метаданных из фото")
        self.geometry("900x650")
        self.minsize(800, 600)
        
        # Переменные для хранения данных
        self.current_image_path = None
        self.current_image = None
        self.cleaned_image = None
        self.metadata_info = {}
        
        # Создаем интерфейс
        self.create_widgets()
        
    def create_widgets(self):
        # Основной фрейм
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Верхняя панель с кнопками
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill="x", pady=(0, 15))
        
        # Кнопка загрузки изображения
        self.load_btn = ctk.CTkButton(
            top_frame, 
            text="📂 Загрузить фото", 
            command=self.load_image,
            font=("Arial", 14, "bold"),
            height=40
        )
        self.load_btn.pack(side="left", padx=5)
        
        # Кнопка очистки метаданных
        self.clean_btn = ctk.CTkButton(
            top_frame, 
            text="✅ Очистить метаданные", 
            command=self.clean_metadata,
            font=("Arial", 14, "bold"),
            height=40,
            state="disabled"
        )
        self.clean_btn.pack(side="left", padx=5)
        
        # Кнопка сохранения очищенного изображения
        self.save_btn = ctk.CTkButton(
            top_frame, 
            text="💾 Сохранить очищенное фото", 
            command=self.save_cleaned_image,
            font=("Arial", 14, "bold"),
            height=40,
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=5)
        
        # Информационная панель
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_text = "MetaWipe - приложение для защиты персональных данных.\n" \
                   "Загрузите фото, чтобы увидеть скрытые метаданные (GPS, дата, модель устройства), " \
                   "и очистите их перед публикацией в интернете."
        info_label = ctk.CTkLabel(
            info_frame, 
            text=info_text,
            wraplength=850,
            font=("Arial", 12),
            justify="center"
        )
        info_label.pack(padx=10, pady=10)
        
        # Основная область с двумя колонками
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # Левая колонка - изображение
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        image_label = ctk.CTkLabel(left_frame, text="Изображение", font=("Arial", 14, "bold"))
        image_label.pack(pady=(5, 10))
        
        self.image_preview = ctk.CTkLabel(
            left_frame, 
            text="Изображение отсутствует\n(загрузите фото)",
            width=400,
            height=350,
            fg_color=("gray85", "gray25"),
            corner_radius=8,
            font=("Arial", 14)
        )
        self.image_preview.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Правая колонка - метаданные
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        metadata_label = ctk.CTkLabel(right_frame, text="Обнаруженные метаданные", font=("Arial", 14, "bold"))
        metadata_label.pack(pady=(5, 10))
        
        self.metadata_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#f0f0f0" if ctk.get_appearance_mode() == "Light" else "#333333",
            fg="#000000" if ctk.get_appearance_mode() == "Light" else "#ffffff",
            relief="flat",
            padx=10,
            pady=10
        )
        self.metadata_text.pack(padx=10, pady=10, fill="both", expand=True)
        self.metadata_text.insert(tk.END, "Здесь будут отображены метаданные после загрузки фото...")
        self.metadata_text.config(state=tk.DISABLED)
        
        # Футер с информацией о безопасности
        footer_frame = ctk.CTkFrame(main_frame)
        footer_frame.pack(fill="x", pady=(15, 0))
        
        security_text = "🔒 Вся обработка происходит на вашем компьютере. Никакие данные не передаются в интернет."
        security_label = ctk.CTkLabel(
            footer_frame, 
            text=security_text,
            font=("Arial", 11, "italic"),
            text_color="green"
        )
        security_label.pack(pady=5)
    
    def load_image(self):
        """Загрузка изображения с диска"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.jpg *.jpeg *.png *.heic"),
                ("Все файлы", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            self.current_image_path = file_path
            self.current_image = Image.open(file_path)
            
            # Отображаем превью изображения
            self.display_image_preview()
            
            # Анализируем метаданные
            self.analyze_metadata()
            
            # Активируем кнопку очистки
            self.clean_btn.configure(state="normal")
            self.save_btn.configure(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")
    
    def display_image_preview(self):
        """Отображение превью изображения"""
        if not self.current_image:
            return
        
        # Создаем копию для превью (чтобы не изменять оригинальное изображение)
        preview_img = self.current_image.copy()
        
        # Ограничиваем размер превью
        max_width = 400
        max_height = 350
        
        # Сохраняем пропорции
        ratio = min(max_width / preview_img.width, max_height / preview_img.height)
        new_width = int(preview_img.width * ratio)
        new_height = int(preview_img.height * ratio)
        
        preview_img = preview_img.resize((new_width, new_height), Image.LANCZOS)
        
        # Конвертируем в формат для Tkinter
        photo = ImageTk.PhotoImage(preview_img)
        
        # Отображаем изображение
        self.image_preview.configure(image=photo, text="")
        self.image_preview.image = photo  # Сохраняем ссылку для предотвращения сборки мусора
    
    def convert_gps_info(self, gps_data):
        """Конвертация GPS координат в человекочитаемый формат"""
        if not gps_data or piexif.GPSIFD.GPSLatitude not in gps_data or piexif.GPSIFD.GPSLongitude not in gps_data:
            return None
        
        lat = gps_data[piexif.GPSIFD.GPSLatitude]
        lat_ref = gps_data.get(piexif.GPSIFD.GPSLatitudeRef, b'N')
        lon = gps_data[piexif.GPSIFD.GPSLongitude]
        lon_ref = gps_data.get(piexif.GPSIFD.GPSLongitudeRef, b'E')
        
        # Конвертируем из формата (градусы, минуты, секунды) в десятичные градусы
        def convert_to_degrees(value):
            d = value[0][0] / value[0][1]
            m = value[1][0] / value[1][1]
            s = value[2][0] / value[2][1]
            return d + (m / 60.0) + (s / 3600.0)
        
        lat_decimal = convert_to_degrees(lat)
        lon_decimal = convert_to_degrees(lon)
        
        if lat_ref == b'S':
            lat_decimal = -lat_decimal
        if lon_ref == b'W':
            lon_decimal = -lon_decimal
        
        # Округляем до 6 знаков для приватности
        return f"{lat_decimal:.6f}, {lon_decimal:.6f}"
    
    def format_datetime(self, exif_date):
        """Форматирование даты для отображения"""
        try:
            if isinstance(exif_date, bytes):
                exif_date = exif_date.decode('utf-8', 'ignore')
            dt = datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        except:
            return str(exif_date)
    
    def analyze_metadata(self):
        """Анализ метаданных изображения"""
        self.metadata_info = {}
        metadata_text = ""
        
        try:
            # Для JPEG анализируем EXIF
            if self.current_image.format == "JPEG" and "exif" in self.current_image.info:
                exif_dict = piexif.load(self.current_image.info["exif"])
                
                # GPS данные
                if "GPS" in exif_dict and exif_dict["GPS"]:
                    gps_info = self.convert_gps_info(exif_dict["GPS"])
                    if gps_info:
                        self.metadata_info["gps"] = gps_info
                        metadata_text += f"📍 GPS-координаты: {gps_info}\n"
                
                # Дата и время съемки
                if "Exif" in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
                    date_info = self.format_datetime(exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal])
                    self.metadata_info["datetime"] = date_info
                    metadata_text += f"🕒 Дата и время съемки: {date_info}\n"
                
                # Модель устройства
                if "0th" in exif_dict:
                    device_info = ""
                    if piexif.ImageIFD.Make in exif_dict["0th"]:
                        make = exif_dict["0th"][piexif.ImageIFD.Make]
                        if isinstance(make, bytes):
                            device_info += make.decode('utf-8', 'ignore').strip()
                    if piexif.ImageIFD.Model in exif_dict["0th"]:
                        model = exif_dict["0th"][piexif.ImageIFD.Model]
                        if isinstance(model, bytes):
                            model_str = model.decode('utf-8', 'ignore').strip()
                            if device_info:
                                device_info += " " + model_str
                            else:
                                device_info = model_str
                    if device_info:
                        self.metadata_info["device"] = device_info
                        metadata_text += f"📱 Устройство: {device_info}\n"
            
            # Размер изображения - для всех форматов
            self.metadata_info["size"] = f"{self.current_image.width}×{self.current_image.height}"
            metadata_text += f"🖼️ Размер изображения: {self.current_image.width}×{self.current_image.height} пикселей\n"
            
            # Для PNG проверяем дополнительные метаданные
            if self.current_image.format == "PNG" and hasattr(self.current_image, 'info'):
                if 'Software' in self.current_image.info:
                    software = self.current_image.info['Software']
                    self.metadata_info["software"] = software
                    metadata_text += f"🛠️ Программа: {software}\n"
                if 'Source' in self.current_image.info:
                    source = self.current_image.info['Source']
                    self.metadata_info["source"] = source
                    metadata_text += f"🔗 Источник: {source}\n"
            
            # Если метаданных не найдено
            if not metadata_text:
                metadata_text = "✅ В изображении не обнаружено опасных метаданных.\n\n"
                metadata_text += "Однако для полной безопасности вы можете очистить фото от всех скрытых данных."
            
        except Exception as e:
            metadata_text = f"⚠️ Ошибка при анализе метаданных:\n{str(e)}\n\n"
            metadata_text += "Возможно, изображение повреждено или имеет нестандартный формат."
        
        # Обновляем текстовое поле с метаданными
        self.metadata_text.config(state=tk.NORMAL)
        self.metadata_text.delete(1.0, tk.END)
        self.metadata_text.insert(tk.END, metadata_text)
        self.metadata_text.config(state=tk.DISABLED)
    
    def clean_metadata(self):
        """Очистка метаданных из изображения"""
        if not self.current_image:
            return
        
        try:
            # Создаем копию изображения для очистки
            cleaned_image = self.current_image.copy()
            output = io.BytesIO()
            
            # Очищаем метаданные в зависимости от формата
            if cleaned_image.format == "JPEG":
                # Полностью удаляем EXIF для JPEG
                cleaned_image.save(output, format="JPEG", exif=b"", quality=95)
            elif cleaned_image.format == "PNG":
                # Для PNG сохраняем без дополнительных метаданных
                png_info = cleaned_image.info.copy()
                if 'icc_profile' in png_info:
                    # Сохраняем только профиль цвета, если он есть
                    cleaned_image.save(output, format="PNG", icc_profile=png_info['icc_profile'])
                else:
                    cleaned_image.save(output, format="PNG")
            else:
                # Для других форматов (HEIC конвертируем в JPEG)
                if cleaned_image.mode in ("RGBA", "P"):
                    cleaned_image.save(output, format="PNG")
                else:
                    cleaned_image.convert("RGB").save(output, format="JPEG", quality=95)
            
            # Загружаем очищенное изображение
            output.seek(0)
            self.cleaned_image = Image.open(output)
            
            # Обновляем превью
            self.display_cleaned_preview()
            
            # Обновляем метаданные (должно быть пусто)
            self.metadata_text.config(state=tk.NORMAL)
            self.metadata_text.delete(1.0, tk.END)
            self.metadata_text.insert(tk.END, "✅ Все метаданные успешно удалены!\n\n"
                                           "Это изображение теперь безопасно для публикации\n"
                                           "в социальных сетях и мессенджерах.")
            self.metadata_text.config(state=tk.DISABLED)
            
            # Активируем кнопку сохранения
            self.save_btn.configure(state="normal")
            
            messagebox.showinfo("Успех", "Метаданные успешно удалены!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось очистить метаданные:\n{str(e)}")
    
    def display_cleaned_preview(self):
        """Отображение превью очищенного изображения"""
        if not self.cleaned_image:
            return
        
        # Создаем копию для превью
        preview_img = self.cleaned_image.copy()
        
        # Ограничиваем размер превью
        max_width = 400
        max_height = 350
        
        # Сохраняем пропорции
        ratio = min(max_width / preview_img.width, max_height / preview_img.height)
        new_width = int(preview_img.width * ratio)
        new_height = int(preview_img.height * ratio)
        
        preview_img = preview_img.resize((new_width, new_height), Image.LANCZOS)
        
        # Конвертируем в формат для Tkinter
        photo = ImageTk.PhotoImage(preview_img)
        
        # Отображаем изображение
        self.image_preview.configure(image=photo, text="")
        self.image_preview.image = photo  # Сохраняем ссылку
    
    def save_cleaned_image(self):
        """Сохранение очищенного изображения"""
        if not self.cleaned_image:
            return
        
        # Определяем имя файла по умолчанию
        original_name = os.path.basename(self.current_image_path)
        name_without_ext = os.path.splitext(original_name)[0]
        default_name = f"{name_without_ext}_clean.jpg"
        
        # Диалог сохранения файла
        save_path = filedialog.asksaveasfilename(
            title="Сохранить очищенное изображение",
            initialfile=default_name,
            defaultextension=".jpg",
            filetypes=[
                ("JPEG изображение", "*.jpg *.jpeg"),
                ("PNG изображение", "*.png"),
                ("Все файлы", "*.*")
            ]
        )
        
        if not save_path:
            return
        
        try:
            # Определяем формат по расширению файла
            ext = os.path.splitext(save_path)[1].lower()
            save_format = "JPEG" if ext in [".jpg", ".jpeg"] else "PNG"
            
            # Сохраняем изображение
            if save_format == "JPEG":
                self.cleaned_image.save(save_path, format="JPEG", quality=95)
            else:
                self.cleaned_image.save(save_path, format="PNG")
            
            messagebox.showinfo("Успех", f"Очищенное изображение сохранено:\n{save_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

if __name__ == "__main__":
    # Устанавливаем DPI awareness для Windows (чтобы интерфейс не был размытым)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = MetaWipeApp()
    app.mainloop()