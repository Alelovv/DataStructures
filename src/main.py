import tkinter as tk
from tkinter import ttk, messagebox
import datetime

# Палитра цветов
CLR = {
    "bg": "#f4f5f7", "panel": "#ffffff", "accent": "#6c5ce7", "accent2": "#00b894",
    "text": "#2d3436", "text_dim": "#636e72", "error": "#d63031", "ok": "#27ae60",
    "warn": "#e17055", "border": "#dfe6e9", "node_fill": "#f1f2f6", "edge": "#b2bec3"
}

#  СТРУКТУРЫ ДАННЫХ
class Stack:
    def __init__(self): self._data = []
    def push(self, v): self._data.append(v)
    def pop(self): return self._data.pop() if self._data else None
    def peek(self): return self._data[-1] if self._data else None
    def is_empty(self): return len(self._data) == 0
    def get_data(self): return list(self._data)
    def copy(self):
        s = Stack()
        s._data = list(self._data)
        return s

class Queue:
    def __init__(self): self._data = []
    def enqueue(self, v): self._data.append(v)
    def dequeue(self): return self._data.pop(0) if self._data else None
    def front(self): return self._data[0] if self._data else None
    def is_empty(self): return len(self._data) == 0
    def get_data(self): return list(self._data)
    def copy(self):
        q = Queue()
        q._data = list(self._data)
        return q

class BSTNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None
        self.last_path = []
        self.last_found = None

    def insert(self, value):
        self.root = self._insert(self.root, value)

    def _insert(self, node, value):
        if node is None: return BSTNode(value)
        if value < node.value: node.left = self._insert(node.left, value)
        elif value > node.value: node.right = self._insert(node.right, value)
        return node

    def delete(self, value):
        self.root, deleted = self._delete(self.root, value)
        return deleted

    def _delete(self, node, value):
        if node is None: return node, False
        if value < node.value: node.left, deleted = self._delete(node.left, value)
        elif value > node.value: node.right, deleted = self._delete(node.right, value)
        else:
            deleted = True
            if node.left is None: return node.right, deleted
            if node.right is None: return node.left, deleted
            min_node = node.right
            while min_node.left: min_node = min_node.left
            node.value = min_node.value
            node.right, _ = self._delete(node.right, min_node.value)
        return node, deleted

    def search(self, value):
        self.last_path = []
        node = self.root
        while node:
            self.last_path.append(node.value)
            if value == node.value:
                self.last_found = value
                return True
            node = node.left if value < node.value else node.right
        self.last_found = None
        return False

    def copy(self):
        b = BST()
        b.root = self._copy_node(self.root)
        return b

    def _copy_node(self, node):
        if node is None: return None
        new_node = BSTNode(node.value)
        new_node.left = self._copy_node(node.left)
        new_node.right = self._copy_node(node.right)
        return new_node

# ИНТЕРФЕЙС
class BasePanel(tk.Frame):
    def __init__(self, parent, log_cb, title, color):
        super().__init__(parent, bg=CLR["bg"])
        self.log_cb = log_cb
        self.history = []
        
        tk.Label(self, text=title, font=("Consolas", 12, "bold"), bg=CLR["bg"], fg=color).pack(pady=(10, 5))
        self._setup_canvas()
        
        # Контейнер для управления
        self.ctrl_frm = tk.Frame(self, bg=CLR["bg"])
        self.ctrl_frm.pack(fill="x", padx=16, pady=5)
        
        tk.Label(self.ctrl_frm, text="Значение:", bg=CLR["bg"], fg=CLR["text"], font=("Consolas", 10)).pack(side="left")
        self.entry = tk.Entry(self.ctrl_frm, width=8, font=("Consolas", 11), bg=CLR["node_fill"], fg=CLR["text"],
                              insertbackground=CLR["text"], relief="flat", highlightthickness=1, highlightbackground=CLR["border"])
        self.entry.pack(side="left", padx=6)
        
        self.btn_frm = tk.Frame(self, bg=CLR["bg"])
        self.btn_frm.pack(pady=5)

    def _setup_canvas(self):
        self.canvas = tk.Canvas(self, bg=CLR["panel"], highlightthickness=1, highlightbackground=CLR["border"])
        self.canvas.pack(padx=16, pady=5, fill="both", expand=True)

    def add_btn(self, text, cmd, color):
        tk.Button(self.btn_frm, text=text, command=cmd, bg=color, fg="#ffffff", font=("Consolas", 9, "bold"),
                  relief="flat", padx=10, pady=4, cursor="hand2").pack(side="left", padx=4)

    def get_input(self, is_int=False):
        val = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        if not val:
            messagebox.showwarning("Ввод", "Поле ввода пусто")
            return None
        if is_int:
            try: return int(val)
            except ValueError:
                messagebox.showerror("Ввод", "Требуется целое число")
                return None
        return val

# ПАНЕЛИ
class StackPanel(BasePanel):
    def __init__(self, parent, log_cb):
        super().__init__(parent, log_cb, "СТЕК (LIFO)", CLR["accent"])
        self.stack = Stack()
        
        self.add_btn("Push ↑", self._push, CLR["accent"])
        self.add_btn("Pop ↓", self._pop, CLR["error"])
        self.add_btn("Peek 👁", self._peek, CLR["accent2"])
        self.add_btn("Undo ↩", self._undo, CLR["warn"])
        self.entry.bind("<Return>", lambda e: self._push())

    def _push(self):
        val = self.get_input()
        if val is not None:
            self.history.append(self.stack.copy())
            self.stack.push(val)
            self.log_cb(f"[Стек] Добавлено значение: {val}", "ok")
            self._draw()

    def _pop(self):
        if self.stack.is_empty():
            self.log_cb("[Стек] Ошибка: стек пуст", "error")
            return
        self.history.append(self.stack.copy())
        val = self.stack.pop()
        self.log_cb(f"[Стек] Удалено значение: {val}", "warn")
        self._draw()

    def _peek(self):
        top = self.stack.peek()
        self.log_cb(f"[Стек] Вершина: {top}" if top else "[Стек] Стек пуст", "info" if top else "error")
        self._draw(hl=True)

    def _undo(self):
        if not self.history: return self.log_cb("[Стек] История пуста", "error")
        self.stack = self.history.pop()
        self.log_cb("[Стек] Действие отменено", "warn")
        self._draw()

    def _draw(self, hl=False):
        self.canvas.delete("all")
        data = self.stack.get_data()
        cw, ch = self.canvas.winfo_width() or 200, self.canvas.winfo_height() or 300
        x0, w, h = (cw - 120) // 2, 120, 35
        base_y = ch - 20
        
        self.canvas.create_line(x0 - 5, base_y, x0 + w + 5, base_y, fill=CLR["border"], width=2)
        for i, val in enumerate(data):
            y1, y2 = base_y - (i + 1) * h, base_y - i * h
            is_top = (i == len(data) - 1)
            fill = CLR["accent"] if (is_top and hl) else CLR["node_fill"]
            self.canvas.create_rectangle(x0, y1, x0 + w, y2, fill=fill, outline=CLR["accent"] if is_top else CLR["border"])
            self.canvas.create_text(x0 + w // 2, (y1 + y2) // 2, text=str(val), fill=CLR["text"])
        if not data: self.canvas.create_text(cw // 2, ch // 2, text="(пусто)", fill=CLR["text_dim"])

class QueuePanel(BasePanel):
    def __init__(self, parent, log_cb):
        super().__init__(parent, log_cb, "ОЧЕРЕДЬ (FIFO)", CLR["accent2"])
        self.queue = Queue()
        
        self.add_btn("Enqueue →", self._enqueue, CLR["accent2"])
        self.add_btn("Dequeue ←", self._dequeue, CLR["error"])
        self.add_btn("Front 👁", self._front, CLR["accent"])
        self.add_btn("Undo ↩", self._undo, CLR["warn"])
        self.entry.bind("<Return>", lambda e: self._enqueue())

    def _enqueue(self):
        val = self.get_input()
        if val is not None:
            self.history.append(self.queue.copy())
            self.queue.enqueue(val)
            self.log_cb(f"[Очередь] Встал в хвост: {val}", "ok")
            self._draw()

    def _dequeue(self):
        if self.queue.is_empty():
            self.log_cb("[Очередь] Ошибка: очередь пуста", "error")
            return
        self.history.append(self.queue.copy())
        val = self.queue.dequeue()
        self.log_cb(f"[Очередь] Вышел из очереди: {val}", "warn")
        self._draw()

    def _front(self):
        f = self.queue.front()
        self.log_cb(f"[Очередь] Первый элемент: {f}" if f else "[Очередь] Очередь пуста", "info" if f else "error")
        self._draw(hl=True)

    def _undo(self):
        if not self.history: return self.log_cb("[Очередь] История пуста", "error")
        self.queue = self.history.pop()
        self.log_cb("[Очередь] Действие отменено", "warn")
        self._draw()

    def _draw(self, hl=False):
        self.canvas.delete("all")
        data = self.queue.get_data()
        cw, ch = self.canvas.winfo_width() or 500, self.canvas.winfo_height() or 150
        cy, w, h = ch // 2, 60, 40
        
        for i, val in enumerate(data):
            x1 = 50 + i * (w + 8)
            fill = CLR["accent2"] if (i == 0 and hl) else CLR["node_fill"]
            self.canvas.create_rectangle(x1, cy - h // 2, x1 + w, cy + h // 2, fill=fill, outline=CLR["border"])
            self.canvas.create_text(x1 + w // 2, cy, text=str(val), fill=CLR["text"])
            if i == 0: self.canvas.create_text(x1 + w // 2, cy - h // 2 - 10, text="front", fill=CLR["accent2"])
            if i == len(data) - 1: self.canvas.create_text(x1 + w // 2, cy + h // 2 + 10, text="back", fill=CLR["accent"])
        if not data: self.canvas.create_text(cw // 2, cy, text="(пусто)", fill=CLR["text_dim"])

class BSTPanel(BasePanel):
    def __init__(self, parent, log_cb):
        super().__init__(parent, log_cb, "ДВОИЧНОЕ ДЕРЕВО ПОИСКА (BST)", CLR["warn"])
        self.bst = BST()
        
        self.add_btn("Insert ➕", self._insert, CLR["ok"])
        self.add_btn("Delete 🗑", self._delete, CLR["error"])
        self.add_btn("Search 🔍", self._search, CLR["accent"])
        self.add_btn("Clear", self._clear, CLR["text_dim"])
        self.add_btn("Undo ↩", self._undo, CLR["warn"])
        self.entry.bind("<Return>", lambda e: self._insert())

    def _insert(self):
        val = self.get_input(is_int=True)
        if val is not None:
            self.history.append(self.bst.copy())
            self.bst.insert(val)
            self.bst.last_path, self.bst.last_found = [], None
            self.log_cb(f"[BST] Вставлен узел: {val}", "ok")
            self._draw()

    def _delete(self):
        val = self.get_input(is_int=True)
        if val is not None:
            self.history.append(self.bst.copy())
            if self.bst.delete(val): self.log_cb(f"[BST] Удален узел: {val}", "warn")
            else: self.log_cb(f"[BST] Узел {val} не найден", "error")
            self.bst.last_path, self.bst.last_found = [], None
            self._draw()

    def _search(self):
        val = self.get_input(is_int=True)
        if val is not None:
            found = self.bst.search(val)
            self.log_cb(f"[BST] Поиск {val}: {'найден' if found else 'не найден'}. Путь: {self.bst.last_path}", "ok" if found else "error")
            self._draw()

    def _clear(self):
        self.history.append(self.bst.copy())
        self.bst = BST()
        self.log_cb("[BST] Дерево очищено", "warn")
        self._draw()

    def _undo(self):
        if not self.history: return self.log_cb("[BST] История пуста", "error")
        self.bst = self.history.pop()
        self._draw()

    def _draw(self):
        self.canvas.delete("all")
        if not self.bst.root:
            self.canvas.create_text(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, text="(дерево пусто)", fill=CLR["text_dim"])
            return
        
        cw, ch = self.canvas.winfo_width() or 600, self.canvas.winfo_height() or 350
        positions = {}
        # ОШИБКА ИСПРАВЛЕНА: Передаем index=1 вместо 0, чтобы сбалансировать дерево по центру экрана
        self._calc_positions(self.bst.root, 0, 1, 1, positions, cw)
        
        h_tree = self._height(self.bst.root)
        level_h = min(60, (ch - 60) // (h_tree if h_tree > 0 else 1))
        coords = {node: (x, 40 + lvl * level_h) for node, (x, lvl) in positions.items()}
        
        # Рисование ребер
        for node, (x, y) in coords.items():
            if node.left: self.canvas.create_line(x, y, coords[node.left][0], coords[node.left][1], fill=CLR["edge"])
            if node.right: self.canvas.create_line(x, y, coords[node.right][0], coords[node.right][1], fill=CLR["edge"])
            
        # Рисование узлов
        for node, (x, y) in coords.items():
            in_path = node.value in self.bst.last_path
            is_found = (node.value == self.bst.last_found)
            fill = CLR["ok"] if is_found else CLR["warn"] if in_path else CLR["node_fill"]
            self.canvas.create_oval(x - 16, y - 16, x + 16, y + 16, fill=fill, outline=CLR["accent"])
            self.canvas.create_text(x, y, text=str(node.value), fill=CLR["bg"] if (in_path or is_found) else CLR["text"], font=("Consolas", 9, "bold"))

    def _calc_positions(self, node, level, index, total, positions, cw):
        if not node: return
        positions[node] = (cw * (index / (total + 1)), level)
        self._calc_positions(node.left, level + 1, index * 2 - 1, total * 2, positions, cw)
        self._calc_positions(node.right, level + 1, index * 2, total * 2, positions, cw)

    def _height(self, node):
        return 1 + max(self._height(node.left), self._height(node.right)) if node else 0

#  ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Демонстратор структур данных")
        self.geometry("800x650")
        self.configure(bg=CLR["bg"])
        
        # Вкладки
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TNotebook", background=CLR["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=CLR["panel"], foreground=CLR["text_dim"], padding=[15, 5], font=("Consolas", 10))
        style.map("TNotebook.Tab", background=[("selected", CLR["accent"])], foreground=[("selected", "#ffffff")])
        
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)
        
        # Общая панель логов
        log_frm = tk.Frame(self, bg=CLR["bg"])
        log_frm.pack(fill="x", side="bottom", padx=10, pady=5)
        tk.Label(log_frm, text="ЛОГ ОПЕРАЦИЙ:", font=("Consolas", 9, "bold"), bg=CLR["bg"], fg=CLR["text_dim"]).pack(anchor="w")
        
        self.log_text = tk.Text(log_frm, height=6, bg=CLR["panel"], fg=CLR["text"], font=("Consolas", 9), relief="flat", state="disabled")
        self.log_text.pack(fill="x", pady=2)
        
        # Инициализация табов
        self.tabs = [StackPanel(self.nb, self.log), QueuePanel(self.nb, self.log), BSTPanel(self.nb, self.log)]
        self.nb.add(self.tabs[0], text=" Стек (Stack) ")
        self.nb.add(self.tabs[1], text=" Очередь (Queue) ")
        self.nb.add(self.tabs[2], text=" Дерево (BST) ")
        
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.after(50, self._redraw))
        self.bind("<Configure>", lambda e: self.after(100, self._redraw))

    def log(self, msg, lvl="info"):
        colors = {"ok": CLR["ok"], "warn": CLR["warn"], "error": CLR["error"], "info": CLR["accent"]}
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{ts}] {msg}\n")
        self.log_text.config(state="disabled")
        self.log_text.see("end")

    def _redraw(self):
        try: self.tabs[self.nb.index(self.nb.select())]._draw()
        except Exception: pass

if __name__ == "__main__":
    App().mainloop()