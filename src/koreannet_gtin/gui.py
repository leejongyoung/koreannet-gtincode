"""데스크톱 창(tkinter). Windows · macOS · Linux에서 추가 설치 없이 동작합니다."""

from __future__ import annotations

import json
import queue
import sys
import threading
from typing import List, Optional

from . import __version__
from .client import Product, lookup
from .errors import KoreannetError
from .gtin import is_valid

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:  # tkinter가 빠진 Python(일부 Linux, Termux)
    tk = None  # type: ignore[assignment]
    ttk = None  # type: ignore[assignment]

NO_TK_MESSAGE = (
    "이 Python에는 tkinter가 없어 창을 열 수 없습니다.\n"
    "  - Debian/Ubuntu: sudo apt install python3-tk\n"
    "  - 대신 브라우저 화면을 쓰려면: koreannet-gtin web"
)


def _enable_hidpi() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # type: ignore[attr-defined]
    except Exception:  # 오래된 Windows
        pass


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.results: queue.Queue[object] = queue.Queue()
        self.product: Optional[Product] = None
        self.history: List[str] = []

        root.title(f"GTIN 조회 · 코리안넷 {__version__}")
        root.minsize(460, 360)
        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        ttk.Label(frame, text="바코드(GTIN) 번호").grid(row=0, column=0, columnspan=3, sticky="w")

        self.var = tk.StringVar()
        self.entry = ttk.Combobox(
            frame, textvariable=self.var, values=self.history, font=("TkDefaultFont", 14)
        )
        self.entry.grid(row=1, column=0, sticky="ew", pady=(4, 8))
        self.entry.bind("<Return>", lambda _e: self.search())
        self.var.trace_add("write", lambda *_: self._on_edit())
        self.paste_button = ttk.Button(frame, text="붙여넣기", command=self.paste)
        self.paste_button.grid(row=1, column=1, padx=(8, 0), pady=(4, 8))
        self.search_button = ttk.Button(frame, text="조회", command=self.search)
        self.search_button.grid(row=1, column=2, padx=(8, 0), pady=(4, 8))

        self.table = ttk.Treeview(frame, columns=("value",), show="tree", selectmode="browse", height=8)
        self.table.column("#0", width=110, stretch=False)
        self.table.column("value", width=300)
        self.table.grid(row=2, column=0, columnspan=3, sticky="nsew")

        self.status = tk.StringVar(value="번호를 입력하고 Enter를 누르세요.")
        ttk.Label(frame, textvariable=self.status, wraplength=420).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )

        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, columnspan=3, sticky="w", pady=(8, 0))
        self.copy_name = ttk.Button(buttons, text="상품명 복사", command=self.copy_name_cmd, state="disabled")
        self.copy_name.pack(side="left")
        self.copy_json = ttk.Button(buttons, text="JSON 복사", command=self.copy_json_cmd, state="disabled")
        self.copy_json.pack(side="left", padx=8)

        self.entry.focus_set()
        self._poll()

    def _on_edit(self) -> None:
        text = self.var.get().strip().replace("-", "").replace(" ", "")
        if text.isdigit() and len(text) in (8, 12, 13, 14) and not is_valid(text):
            self.status.set("체크디지트가 맞지 않는 번호입니다.")

    def paste(self) -> None:
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            self.status.set("클립보드가 비어 있습니다.")
            return
        self.var.set(text.strip())
        self.entry.icursor("end")

    def search(self) -> None:
        code = self.var.get()
        self.search_button.state(["disabled"])
        self.status.set("조회 중…")
        self._fill([])
        threading.Thread(target=self._worker, args=(code,), daemon=True).start()

    def _worker(self, code: str) -> None:
        try:
            self.results.put(lookup(code))
        except KoreannetError as exc:
            self.results.put(exc)
        except Exception as exc:  # 예기치 못한 오류도 창이 멈추지 않게 전달
            self.results.put(exc)

    def _poll(self) -> None:
        try:
            item = self.results.get_nowait()
        except queue.Empty:
            pass
        else:
            self.search_button.state(["!disabled"])
            if isinstance(item, Product):
                self._show(item)
            else:
                self.product = None
                self.copy_name.state(["disabled"])
                self.copy_json.state(["disabled"])
                self.status.set(str(item))
        self.root.after(100, self._poll)

    def _show(self, product: Product) -> None:
        self.product = product
        self._fill([("상품명", product.name)] + [r for r in product.rows() if r[0] != "상품명"])
        self.status.set("조회했습니다.")
        self.copy_name.state(["!disabled"])
        self.copy_json.state(["!disabled"])
        if product.gtin not in self.history:
            self.history.insert(0, product.gtin)
            self.entry.configure(values=self.history[:20])

    def _fill(self, rows: list) -> None:
        self.table.delete(*self.table.get_children())
        for label, value in rows:
            self.table.insert("", "end", text=label, values=(value,))

    def _copy(self, text: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status.set("복사했습니다.")

    def copy_name_cmd(self) -> None:
        if self.product:
            self._copy(self.product.name)

    def copy_json_cmd(self) -> None:
        if self.product:
            self._copy(json.dumps(self.product.to_dict(), ensure_ascii=False, indent=2))


def main() -> int:
    if tk is None:
        print(NO_TK_MESSAGE, file=sys.stderr)
        return 1
    _enable_hidpi()
    try:
        root = tk.Tk()
    except tk.TclError as exc:  # DISPLAY 없음 등
        print(f"창을 열 수 없습니다: {exc}\n브라우저 화면을 쓰려면: koreannet-gtin web", file=sys.stderr)
        return 1
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
