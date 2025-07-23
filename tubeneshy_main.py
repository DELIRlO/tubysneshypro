import yt_dlp
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import timedelta
from queue import Queue
from urllib.request import urlopen
from io import BytesIO
from PIL import Image, ImageTk
import subprocess
import platform
from itertools import cycle

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Tubys Neshy Pro")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variáveis de controle
        self.url = tk.StringVar()
        self.save_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.format = tk.StringVar(value="mp4")
        self.quality = tk.StringVar(value="720p")
        self.download_thread = None
        self.stop_download = False
        self.current_download = None
        self.download_queue = Queue()
        self.is_downloading = False
        self.video_info = None
        self.thumbnail_image = None
        self.fetching_info = False
        
        # Variáveis de progresso
        self.current_progress = 0
        self.target_progress = 0
        self.start_time = 0
        self.last_bytes = 0
        self.last_update_time = 0
        self.download_speed = 0
        self.time_remaining = "Calculando..."
        
        # Variáveis para animação do título
        self.title_colors = [
            "#6495ED", "#4169E1", "#1E90FF", "#00BFFF", 
            "#87CEFA", "#87CEEB", "#ADD8E6", "#4682B4"
        ]
        self.title_labels = []
        self.title_text = "< TubYs Neshy PRO >"
        self.title_index = 0
        
        self.setup_ui()
        self.animate_progress()
        self.root.after(500, self.setup_title_animation)

    def setup_title_animation(self):
        """Configura os labels individuais para cada letra do título"""
        for label in self.title_labels:
            label.destroy()
        self.title_labels = []
        
        self.title_center_frame = tk.Frame(self.title_frame)
        self.title_center_frame.pack(expand=True)
        
        for i, char in enumerate(self.title_text):
            color = self.title_colors[i % len(self.title_colors)]
            label = tk.Label(
                self.title_center_frame,
                text=char,
                font=("Impact", 24, "bold"),
                fg=color
            )
            label.pack(side=tk.LEFT, padx=0)
            self.title_labels.append(label)
        
        self.root.after(300, self.animate_title)

    def animate_title(self):
        """Anima as cores das letras do título"""
        for i, label in enumerate(self.title_labels):
            color_index = (i + self.title_index) % len(self.title_colors)
            color = self.title_colors[color_index]
            label.config(fg=color)
        
        self.title_index = (self.title_index + 1) % len(self.title_colors)
        self.root.after(200, self.animate_title)

    def setup_ui(self):
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        
        self.title_frame = tk.Frame(main_frame)
        self.title_frame.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="nsew")
        
        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=5)
        
        url_frame = tk.Frame(left_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            url_frame,
            text="URL do Vídeo:",
            font=("Arial", 10),
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.url_entry = tk.Entry(
            url_frame,
            textvariable=self.url,
            font=("Arial", 10),
            width=50
        )
        self.url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        right_frame = tk.Frame(main_frame, padx=10)
        right_frame.grid(row=1, column=1, sticky="nsew")
        
        self.add_queue_btn = tk.Button(
            right_frame,
            text="Adicionar à Fila",
            command=self.add_to_queue,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10),
            width=15
        )
        self.add_queue_btn.pack(pady=(5, 10), fill=tk.X)
        
        self.fetch_btn = tk.Button(
            right_frame,
            text="Buscar Info",
            command=self.fetch_video_info_threaded,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10),
            width=15
        )
        self.fetch_btn.pack(pady=(0, 10), fill=tk.X)
        
        self.download_btn = tk.Button(
            right_frame,
            text="INICIAR DOWNLOADS",
            command=self.start_download_queue,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15
        )
        self.download_btn.pack(pady=(0, 5), fill=tk.X)
        
        self.preview_frame = tk.LabelFrame(left_frame, text="Preview", bd=2, relief=tk.GROOVE)
        self.preview_frame.pack(fill=tk.X, pady=10)
        
        self.thumbnail_label = tk.Label(self.preview_frame)
        self.thumbnail_label.pack(pady=5)
        
        self.info_frame = tk.Frame(self.preview_frame)
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.video_title_label = tk.Label(
            self.info_frame,
            text="Título: N/A",
            font=("Arial", 10, "bold"),
            anchor="w",
            wraplength=500
        )
        self.video_title_label.pack(fill=tk.X)
        
        info_subframe = tk.Frame(self.info_frame)
        info_subframe.pack(fill=tk.X)
        
        self.duration_label = tk.Label(
            info_subframe,
            text="Duração: N/A",
            font=("Arial", 9),
            anchor="w"
        )
        self.duration_label.pack(side=tk.LEFT, padx=5)
        
        self.views_label = tk.Label(
            info_subframe,
            text="Visualizações: N/A",
            font=("Arial", 9),
            anchor="w"
        )
        self.views_label.pack(side=tk.LEFT, padx=5)
        
        self.channel_label = tk.Label(
            info_subframe,
            text="Canal: N/A",
            font=("Arial", 9),
            anchor="w"
        )
        self.channel_label.pack(side=tk.LEFT, padx=5)
        
        settings_frame = tk.LabelFrame(left_frame, text="Configurações", bd=2, relief=tk.GROOVE)
        settings_frame.pack(fill=tk.X, pady=10)
        
        save_frame = tk.Frame(settings_frame)
        save_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            save_frame,
            text="Salvar em:",
            font=("Arial", 10),
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.path_entry = tk.Entry(
            save_frame,
            textvariable=self.save_path,
            font=("Arial", 9),
            state="readonly",
            width=40
        )
        self.path_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.select_btn = tk.Button(
            save_frame,
            text="Selecionar",
            command=self.select_folder,
            font=("Arial", 9),
            width=10
        )
        self.select_btn.pack(side=tk.LEFT)
        
        format_frame = tk.Frame(settings_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            format_frame,
            text="Formato:",
            font=("Arial", 10),
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        formats = ["MP4 (Vídeo)", "MP3 (Áudio)", "WhatsApp (Vídeo)"]
        for fmt in formats:
            tk.Radiobutton(
                format_frame,
                text=fmt,
                variable=self.format,
                value=fmt.split()[0].lower(),
                font=("Arial", 9),
                command=self.update_quality_options
            ).pack(side=tk.LEFT, padx=5)
        
        self.quality_frame = tk.Frame(settings_frame)
        self.quality_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            self.quality_frame,
            text="Qualidade:",
            font=("Arial", 10),
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.quality_options = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p (4K)"]
        self.quality_buttons = []
        
        quality_btn_frame = tk.Frame(self.quality_frame)
        quality_btn_frame.pack(side=tk.LEFT, expand=True)
        
        for i, qual in enumerate(self.quality_options):
            btn = tk.Radiobutton(
                quality_btn_frame,
                text=qual,
                variable=self.quality,
                value=qual.split()[0],
                font=("Arial", 8),
                state=tk.NORMAL
            )
            btn.grid(row=i//4, column=i%4, padx=2, pady=2, sticky="w")
            self.quality_buttons.append(btn)
        
        queue_btn_frame = tk.Frame(right_frame)
        queue_btn_frame.pack(fill=tk.X, pady=5)
        
        self.remove_queue_btn = tk.Button(
            queue_btn_frame,
            text="Remover",
            command=self.remove_selected_from_queue,
            font=("Arial", 9),
            width=8,
            state=tk.DISABLED
        )
        self.remove_queue_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.clear_queue_btn = tk.Button(
            queue_btn_frame,
            text="Limpar",
            command=self.clear_queue,
            font=("Arial", 9),
            width=8
        )
        self.clear_queue_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        queue_list_frame = tk.LabelFrame(right_frame, text="Fila de Downloads", bd=2, relief=tk.GROOVE)
        queue_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.queue_listbox = tk.Listbox(
            queue_list_frame,
            height=12,
            selectmode=tk.SINGLE,
            font=("Arial", 9)
        )
        self.queue_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.cancel_btn = tk.Button(
            right_frame,
            text="CANCELAR",
            command=self.cancel_download,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            state=tk.DISABLED
        )
        self.cancel_btn.pack(fill=tk.X, pady=(5, 0))
        
        progress_frame = tk.Frame(left_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        info_frame = tk.Frame(progress_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.speed_var = tk.StringVar(value="Velocidade: 0 MB/s")
        tk.Label(
            info_frame,
            textvariable=self.speed_var,
            font=("Arial", 9),
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.time_var = tk.StringVar(value="Tempo restante: --:--")
        tk.Label(
            info_frame,
            textvariable=self.time_var,
            font=("Arial", 9),
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=500,
            mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.percent_var = tk.StringVar(value="0%")
        tk.Label(
            progress_frame,
            textvariable=self.percent_var,
            font=("Arial", 9),
            fg="#666"
        ).pack()
        
        self.status_var = tk.StringVar(value="Pronto para baixar vídeos")
        tk.Label(
            left_frame,
            textvariable=self.status_var,
            font=("Arial", 9),
            fg="#666"
        ).pack(fill=tk.X, pady=5)
        
        self.queue_listbox.bind("<<ListboxSelect>>", self.update_queue_buttons_state)
        self.url_entry.bind("<Return>", lambda e: self.fetch_video_info_threaded())
        
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Colar", command=self.paste_from_clipboard)
        self.url_entry.bind("<Button-3>", lambda e: self.context_menu.tk_popup(e.x_root, e.y_root))

    def add_to_queue(self):
        """Adiciona o vídeo atual à fila de downloads"""
        url = self.url.get().strip()
        if not url:
            messagebox.showerror("Erro", "Digite uma URL válida!")
            return
        
        if not self.video_info:
            download_item = {
                'url': url,
                'format': self.format.get(),
                'quality': self.quality.get(),
                'save_path': self.save_path.get(),
                'title': self.get_video_title_from_url(url),
                'thumbnail': ''
            }
        else:
            download_item = {
                'url': url,
                'format': self.format.get(),
                'quality': self.quality.get(),
                'save_path': self.save_path.get(),
                'title': self.video_info.get('title', 'video'),
                'thumbnail': self.video_info.get('thumbnail', '')
            }
        
        self.download_queue.put(download_item)
        self.update_queue_listbox()
        self.url.set("")
        self.clear_preview()
        self.status_var.set(f"Item adicionado à fila. Total: {self.download_queue.qsize()}")

    def get_video_title_from_url(self, url):
        """Tenta extrair um título razoável da URL"""
        try:
            if 'youtube.com' in url or 'youtu.be' in url:
                if 'v=' in url:
                    video_id = url.split('v=')[1].split('&')[0]
                    return f"Vídeo {video_id[:8]}..."
                elif 'youtu.be/' in url:
                    video_id = url.split('youtu.be/')[1].split('?')[0]
                    return f"Vídeo {video_id[:8]}..."
        except:
            pass
        return "Novo Vídeo"

    def update_queue_listbox(self):
        """Atualiza a lista de itens na fila de download"""
        self.queue_listbox.delete(0, tk.END)
        temp_queue = []
        
        while not self.download_queue.empty():
            item = self.download_queue.get()
            temp_queue.append(item)
        
        for item in temp_queue:
            self.download_queue.put(item)
            display_text = f"{item['title']} | {item['format'].upper()} | {item['quality']}"
            self.queue_listbox.insert(tk.END, display_text)

    def remove_selected_from_queue(self):
        """Remove o item selecionado da fila de downloads"""
        selection = self.queue_listbox.curselection()
        if not selection:
            return
        
        new_queue = Queue()
        index_to_remove = selection[0]
        current_index = 0
        
        while not self.download_queue.empty():
            item = self.download_queue.get()
            if current_index != index_to_remove:
                new_queue.put(item)
            current_index += 1
        
        self.download_queue = new_queue
        self.update_queue_listbox()
        self.status_var.set(f"Item removido. Itens na fila: {self.download_queue.qsize()}")

    def clear_queue(self):
        """Limpa toda a fila de downloads"""
        while not self.download_queue.empty():
            self.download_queue.get()
        self.queue_listbox.delete(0, tk.END)
        self.status_var.set("Fila de downloads limpa")

    def update_queue_buttons_state(self, event=None):
        """Atualiza o estado dos botões da fila com base na seleção"""
        selection = self.queue_listbox.curselection()
        if selection:
            self.remove_queue_btn.config(state=tk.NORMAL)
        else:
            self.remove_queue_btn.config(state=tk.DISABLED)

    def fetch_video_info_threaded(self):
        """Inicia a busca de informações em uma thread separada"""
        if self.fetching_info:
            return
            
        url = self.url.get().strip()
        if not url:
            messagebox.showerror("Erro", "Digite uma URL válida!")
            return
        
        self.fetching_info = True
        self.status_var.set("Buscando informações do vídeo...")
        self.fetch_btn.config(state=tk.DISABLED)
        
        threading.Thread(target=self._fetch_video_info, args=(url,), daemon=True).start()

    def _fetch_video_info(self, url):
        """Método interno que roda em thread separada para buscar informações"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                self.root.after(0, self._update_video_info, info)
                
        except Exception as e:
            self.root.after(0, self._fetch_info_error, str(e))
            
        finally:
            self.fetching_info = False

    def _update_video_info(self, info):
        """Atualiza a interface com as informações do vídeo (chamado na thread principal)"""
        self.video_info = info
        self.show_thumbnail(info.get('thumbnail'))
        
        self.video_title_label.config(text=f"Título: {info.get('title', 'N/A')}")
        
        duration = info.get('duration', 0)
        if duration:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
        else:
            duration_str = "N/A"
        self.duration_label.config(text=f"Duração: {duration_str}")
        
        views = info.get('view_count', 0)
        if views:
            views_str = f"{views:,}".replace(",", ".")
        else:
            views_str = "N/A"
        self.views_label.config(text=f"Visualizações: {views_str}")
        
        self.channel_label.config(text=f"Canal: {info.get('uploader', 'N/A')}")
        
        self.fetch_btn.config(state=tk.NORMAL)
        self.status_var.set("Informações do vídeo carregadas!")

    def _fetch_info_error(self, error_msg):
        """Lida com erros na busca de informações (chamado na thread principal)"""
        self.status_var.set("Erro ao buscar informações do vídeo")
        messagebox.showerror("Erro", f"Não foi possível obter informações do vídeo: {error_msg[:200]}")
        self.clear_preview()
        self.fetch_btn.config(state=tk.NORMAL)

    def show_thumbnail(self, thumbnail_url):
        """Exibe o thumbnail do vídeo (já roda na thread principal)"""
        try:
            if thumbnail_url:
                threading.Thread(target=self._download_thumbnail, args=(thumbnail_url,), daemon=True).start()
            else:
                self.thumbnail_label.config(image='', text="Thumbnail não disponível")
        except Exception as e:
            self.thumbnail_label.config(image='', text="Erro ao carregar thumbnail")
            print(f"Erro ao carregar thumbnail: {e}")

    def _download_thumbnail(self, thumbnail_url):
        """Baixa o thumbnail em uma thread separada com tamanho fixo de 250x150"""
        try:
            with urlopen(thumbnail_url) as response:
                image_data = response.read()
            
            image = Image.open(BytesIO(image_data))
            target_width, target_height = 250, 150
            original_width, original_height = image.size
            
            ratio = min(target_width / original_width, target_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            if new_width != target_width or new_height != target_height:
                new_image = Image.new("RGB", (target_width, target_height), (0, 0, 0))
                offset = ((target_width - new_width) // 2, (target_height - new_height) // 2)
                new_image.paste(image, offset)
                image = new_image
            
            self.thumbnail_image = ImageTk.PhotoImage(image)
            self.root.after(0, self._display_thumbnail)
            
        except Exception as e:
            self.root.after(0, lambda: self.thumbnail_label.config(image='', text="Erro ao carregar thumbnail"))

    def _display_thumbnail(self):
        """Exibe o thumbnail na interface (chamado na thread principal)"""
        self.thumbnail_label.config(image=self.thumbnail_image)

    def clear_preview(self):
        """Limpa a área de preview"""
        self.thumbnail_label.config(image='', text="Nenhum preview disponível")
        self.video_title_label.config(text="Título: N/A")
        self.duration_label.config(text="Duração: N/A")
        self.views_label.config(text="Visualizações: N/A")
        self.channel_label.config(text="Canal: N/A")
        self.video_info = None
        self.thumbnail_image = None

    def update_quality_options(self):
        """Atualiza as opções de qualidade com base no formato selecionado"""
        if self.format.get() == "whatsapp":
            for i, btn in enumerate(self.quality_buttons):
                if i <= 2:  # 144p, 240p, 360p
                    btn.config(state=tk.NORMAL)
                else:
                    btn.config(state=tk.DISABLED)
            self.quality.set("360p")
        elif self.format.get() == "mp3":
            for btn in self.quality_buttons:
                btn.config(state=tk.DISABLED)
            self.quality.set("")
        else:
            for btn in self.quality_buttons:
                btn.config(state=tk.NORMAL)
            self.quality.set("720p")

    def paste_from_clipboard(self):
        """Colar conteúdo do clipboard na entrada de URL"""
        try:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, self.root.clipboard_get())
        except tk.TclError:
            pass

    def select_folder(self):
        """Selecionar pasta para salvar os downloads"""
        folder = filedialog.askdirectory()
        if folder:
            self.save_path.set(folder)

    def animate_progress(self):
        """Anima a barra de progresso suavemente"""
        if self.current_progress < self.target_progress:
            difference = self.target_progress - self.current_progress
            
            if difference > 20:
                move_amount = difference * 0.2
            elif difference > 5:
                move_amount = difference * 0.4
            else:
                move_amount = difference * 0.8
                    
            self.current_progress += move_amount
            self.progress_bar['value'] = self.current_progress
            self.percent_var.set(f"{self.current_progress:.1f}%")
                
            if self.current_progress > self.target_progress:
                self.current_progress = self.target_progress
        
        self.root.after(30, self.animate_progress)

    def update_progress(self, d):
        """Atualiza o progresso do download"""
        if d['status'] == 'downloading':
            now = time.time()
            
            if self.start_time == 0:
                self.start_time = now
                self.last_update_time = now
                self.last_bytes = 0
            
            if now - self.last_update_time >= 0.5:
                elapsed = now - self.last_update_time
                
                if 'downloaded_bytes' in d and d['downloaded_bytes']:
                    current_bytes = d['downloaded_bytes']
                    bytes_diff = current_bytes - self.last_bytes
                    
                    if elapsed > 0:
                        self.download_speed = bytes_diff / elapsed / (1024 * 1024)
                        self.speed_var.set(f"Velocidade: {self.download_speed:.2f} MB/s")
                    
                    if 'total_bytes' in d and d['total_bytes'] and self.download_speed > 0:
                        remaining_bytes = d['total_bytes'] - current_bytes
                        seconds = remaining_bytes / (self.download_speed * 1024 * 1024)
                        
                        if seconds > 0:
                            time_obj = timedelta(seconds=int(seconds))
                            time_str = str(time_obj)
                            if time_obj.days > 0:
                                self.time_remaining = time_str
                            else:
                                self.time_remaining = time_str[2:7]
                            self.time_var.set(f"Tempo restante: {self.time_remaining}")
                    
                    self.last_bytes = current_bytes
                    self.last_update_time = now
                
                if '_percent_str' in d:
                    percent_str = d['_percent_str'].strip('%')
                elif 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes'] > 0:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    percent_str = f"{percent:.1f}"
                else:
                    percent_str = "0"
                
                try:
                    self.target_progress = float(percent_str)
                    self.status_var.set(f"Baixando... {self.target_progress:.1f}%")
                except (ValueError, AttributeError):
                    pass

    def start_download_queue(self):
        """Inicia o processo de download da fila"""
        if self.download_queue.empty():
            url = self.url.get().strip()
            if not url:
                messagebox.showinfo("Info", "Digite uma URL ou adicione itens à fila!")
                return
            
            download_item = {
                'url': url,
                'format': self.format.get(),
                'quality': self.quality.get(),
                'save_path': self.save_path.get(),
                'title': self.get_video_title_from_url(url),
                'thumbnail': ''
            }
            self.download_queue.put(download_item)
            self.update_queue_listbox()
        
        if self.is_downloading:
            messagebox.showinfo("Info", "Downloads já em andamento!")
            return
            
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.status_var.set("Iniciando downloads...")
        
        self.queue_thread = threading.Thread(target=self.process_queue)
        self.queue_thread.start()

    def process_queue(self):
        """Processa os itens da fila de download"""
        while not self.download_queue.empty() and not self.stop_download:
            self.current_download = self.download_queue.get()
            
            self.root.after(0, self.update_current_download_status)
            
            self.current_progress = 0
            self.target_progress = 0
            self.start_time = 0
            self.last_bytes = 0
            self.last_update_time = 0
            self.download_speed = 0
            self.time_remaining = "Calculando..."
            
            self.run_download_item(self.current_download)
            self.root.after(0, self.update_queue_listbox)
        
        self.is_downloading = False
        self.stop_download = False
        self.root.after(0, self.finish_download_queue)

    def update_current_download_status(self):
        """Atualiza o status do download atual"""
        display_text = f"Baixando: {self.current_download.get('title', self.current_download['url'])} | {self.current_download['format'].upper()} | {self.current_download['quality']}"
        self.status_var.set(display_text)

    def run_download_item(self, download_item):
        """Executa o download de um item específico"""
        try:
            ydl_opts = {
                'outtmpl': os.path.join(download_item['save_path'], '%(title)s.%(ext)s'),
                'progress_hooks': [self.update_progress],
                'quiet': True,
            }

            if download_item['format'] == "mp3":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif download_item['format'] == "whatsapp":
                ydl_opts.update({
                    'format': 'best[height<=360]',
                    'postprocessor_args': [
                        '-c:v', 'libx264',
                        '-profile:v', 'baseline',
                        '-level', '3.0',
                        '-preset', 'fast',
                        '-crf', '23',
                        '-c:a', 'aac',
                        '-b:a', '96k',
                        '-movflags', '+faststart',
                        '-vf', 'scale=640:-2',
                        '-strict', '-2'
                    ],
                })
            else:
                height = int(''.join(filter(str.isdigit, download_item['quality']))) if download_item['quality'] else None
                if height:
                    ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.root.after(0, lambda: self.status_var.set(f"Baixando: {download_item.get('title', download_item['url'])}"))
                ydl.download([download_item['url']])
                
                if not self.stop_download:
                    self.root.after(0, self.complete_download_item)
                    self.root.after(0, self.ask_open_folder, download_item['save_path'])

        except Exception as e:
            if not self.stop_download:
                error_msg = str(e).split('\n')[0]
                self.root.after(0, lambda: self.status_var.set(f"Erro: {error_msg[:100]}"))
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Falha no download: {error_msg[:200]}"))

    def ask_open_folder(self, folder_path):
        """Pergunta ao usuário se deseja abrir a pasta onde o vídeo foi salvo"""
        if messagebox.askyesno("Download concluído", "Deseja abrir a pasta onde o vídeo foi salvo?"):
            self.open_folder(folder_path)

    def open_folder(self, folder_path):
        """Abre a pasta no explorador de arquivos do sistema"""
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", folder_path])
            else:  # Linux e outros
                subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            print(f"Erro ao abrir pasta: {e}")

    def complete_download_item(self):
        """Finaliza o download de um item com sucesso"""
        self.target_progress = 100
        self.current_progress = 100
        self.progress_bar['value'] = 100
        self.percent_var.set("100%")
        self.speed_var.set("Velocidade: 0 MB/s")
        self.time_var.set("Tempo restante: 00:00")
        self.status_var.set(f"Download concluído! Itens restantes: {self.download_queue.qsize()}")

    def finish_download_queue(self):
        """Finaliza o processo de download da fila"""
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        
        if self.stop_download:
            self.status_var.set("Downloads cancelados pelo usuário")
        else:
            self.status_var.set("Todos os downloads foram concluídos!")
            messagebox.showinfo("Concluído", "Todos os downloads da fila foram concluídos!")

    def cancel_download(self):
        """Cancela o download em andamento"""
        self.stop_download = True
        self.is_downloading = False
        self.status_var.set("Cancelando downloads...")
        self.cancel_btn.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
