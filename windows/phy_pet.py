import ctypes
import faulthandler
import json
import logging
import math
import os
import subprocess
from pathlib import Path
import sys
import time
import tkinter as tk
from tkinter import messagebox
import traceback

from PIL import Image, ImageTk


APP_NAME = "PhyDesktopPet"
TRANSPARENT = "#01ff01"
BASE_HEIGHT = 240
SIZES = {"小": 180, "中": 240, "大": 320}


def resource_path(name):
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / name


def settings_path():
    folder = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "settings.json"


def start_diagnostics():
    log_path = settings_path().with_name("pet.log")
    logging.basicConfig(
        filename=log_path, level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8",
    )
    crash_log = open(settings_path().with_name("crash.log"), "a", encoding="utf-8")
    faulthandler.enable(file=crash_log, all_threads=True)
    logging.info("Starting %s pid=%s", APP_NAME, os.getpid())
    return crash_log


class WinPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class WinRect(ctypes.Structure):
    _fields_ = [(name, ctypes.c_long) for name in ("left", "top", "right", "bottom")]


class MonitorInfo(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong), ("rcMonitor", WinRect),
                ("rcWork", WinRect), ("dwFlags", ctypes.c_ulong)]


def monitor_work_area(x, y, full=False):
    user = ctypes.WinDLL("user32", use_last_error=True)
    user.MonitorFromPoint.argtypes = (WinPoint, ctypes.c_ulong)
    user.MonitorFromPoint.restype = ctypes.c_void_p
    user.GetMonitorInfoW.argtypes = (ctypes.c_void_p, ctypes.POINTER(MonitorInfo))
    user.GetMonitorInfoW.restype = ctypes.c_bool
    user.GetSystemMetrics.argtypes = (ctypes.c_int,)
    monitor = user.MonitorFromPoint(WinPoint(x, y), 2)
    info = MonitorInfo()
    info.cbSize = ctypes.sizeof(MonitorInfo)
    if monitor and user.GetMonitorInfoW(monitor, ctypes.byref(info)):
        r = info.rcMonitor if full else info.rcWork
        return r.left, r.top, r.right, r.bottom
    return 0, 0, user.GetSystemMetrics(0), user.GetSystemMetrics(1)


def taskbar_surface(x, y):
    """Reserve the taskbar's full height even when it is automatically hidden."""
    left, top, right, bottom = monitor_work_area(x, y, full=True)
    surface = monitor_work_area(x, y)[3]
    user = ctypes.WinDLL("user32", use_last_error=True)
    user.GetClassNameW.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int)
    user.GetWindowRect.argtypes = (ctypes.c_void_p, ctypes.POINTER(WinRect))
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    @callback_type
    def collect(hwnd, _data):
        nonlocal surface
        name = ctypes.create_unicode_buffer(128)
        user.GetClassNameW(hwnd, name, len(name))
        if name.value in ("Shell_TrayWnd", "Shell_SecondaryTrayWnd"):
            rect = WinRect()
            if user.GetWindowRect(hwnd, ctypes.byref(rect)):
                if (rect.left < right and rect.right > left and
                        rect.top >= top + (bottom - top) // 2 and
                        rect.right - rect.left > rect.bottom - rect.top):
                    surface = min(surface, bottom - (rect.bottom - rect.top))
        return True

    user.EnumWindows.argtypes = (callback_type, ctypes.c_void_p)
    user.EnumWindows(collect, None)
    return surface


def show_running_pet():
    """A second shortcut click brings the existing pet into view near the pointer."""
    user = ctypes.WinDLL("user32", use_last_error=True)
    user.FindWindowW.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p)
    user.FindWindowW.restype = ctypes.c_void_p
    user.GetWindowRect.argtypes = (ctypes.c_void_p, ctypes.POINTER(WinRect))
    user.GetWindowRect.restype = ctypes.c_bool
    user.GetCursorPos.argtypes = (ctypes.POINTER(WinPoint),)
    user.GetCursorPos.restype = ctypes.c_bool
    user.SetWindowPos.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint)
    user.SetWindowPos.restype = ctypes.c_bool
    hwnd = user.FindWindowW(None, "Phy 桌寵")
    rect, cursor = WinRect(), WinPoint()
    if not hwnd or not user.GetWindowRect(hwnd, ctypes.byref(rect)) or not user.GetCursorPos(ctypes.byref(cursor)):
        logging.warning("Existing pet window was not found")
        return
    width, height = rect.right - rect.left, rect.bottom - rect.top
    left, top, right, bottom = monitor_work_area(cursor.x, cursor.y, full=True)
    x = max(left, min(cursor.x - width // 2, right - width))
    y = max(top, min(cursor.y - height // 2, bottom - height))
    if user.SetWindowPos(hwnd, ctypes.c_void_p(-1), x, y, width, height, 0x0040):
        logging.info("Brought existing pet into view at (%s, %s)", x, y)
    else:
        logging.error("Could not show existing pet: %s", ctypes.get_last_error())


class PhyPet:
    def __init__(self):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("Phy 桌寵")
        self.root.overrideredirect(True)
        self.root.configure(bg=TRANSPARENT)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT)
        self.root.wm_attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.report_callback_exception = self.callback_error
        try:
            self.settings = json.loads(settings_path().read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.settings = {}
        self.height = int(self.settings.get("height", BASE_HEIGHT))
        if self.height not in SIZES.values():
            self.height = BASE_HEIGHT
        self.frames = {}
        self.dock_taskbar = bool(self.settings.get("dock_taskbar", False))
        self.dock_offset = max(0, int(self.settings.get("dock_offset", 0)))
        self.resize_frames()

        self.label = tk.Label(self.root, bg=TRANSPARENT, bd=0, highlightthickness=0)
        self.label.pack()
        self.label.bind("<ButtonPress-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.drag)
        self.label.bind("<ButtonRelease-1>", self.end_drag)
        self.label.bind("<Double-Button-1>", self.greet)
        self.label.bind("<Button-3>", self.menu_popup)
        self.label.bind("<MouseWheel>", self.mouse_wheel)

        self.menu = tk.Menu(self.root, tearoff=False)
        size_menu = tk.Menu(self.menu, tearoff=False)
        for label, height in SIZES.items():
            size_menu.add_command(label=label, command=lambda value=height: self.set_size(value))
        self.menu.add_cascade(label="大小", menu=size_menu)
        self.dock_var = tk.BooleanVar(value=self.dock_taskbar)
        self.menu.add_checkbutton(label="貼齊工作列（可往下拖）", variable=self.dock_var, command=self.toggle_dock)
        self.menu.add_separator()
        self.menu.add_command(label="結束", command=self.close)

        x = self.settings.get("x", self.root.winfo_screenwidth() - self.width - 48)
        y = self.settings.get("y", self.root.winfo_screenheight() - self.height - 80)
        self.root.geometry(f"{self.width}x{self.height}+0+0")
        self.label.configure(image=self.photo)
        self.started = time.monotonic()
        self.last_tick = self.started
        self.look_x = 0
        self.look_y = 0
        self.happy_until = 0
        self.drag_start = None
        self.root.deiconify()
        self.root.update_idletasks()
        self.user32 = ctypes.windll.user32
        self.user32.GetAncestor.argtypes = (ctypes.c_void_p, ctypes.c_uint)
        self.user32.GetAncestor.restype = ctypes.c_void_p
        self.user32.SetWindowPos.argtypes = (
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_uint,
        )
        self.user32.GetSystemMetrics.argtypes = (ctypes.c_int,)
        self.user32.GetWindowRect.argtypes = (ctypes.c_void_p, ctypes.POINTER(WinRect))
        self.user32.GetWindowRect.restype = ctypes.c_bool
        self.hwnd = self.user32.GetAncestor(self.root.winfo_id(), 2)
        self.closed_intentionally = False
        self.position(*self.visible_position(int(x), int(y)))
        self.last_screen_check = time.monotonic()
        self.animate()

    def position(self, x, y):
        self.user32.SetWindowPos(self.hwnd, ctypes.c_void_p(-1), x, y, self.width, self.height, 0x0040)

    def current_position(self):
        rect = WinRect()
        if self.user32.GetWindowRect(self.hwnd, ctypes.byref(rect)):
            return rect.left, rect.top
        return self.root.winfo_x(), self.root.winfo_y()

    def visible_position(self, x, y):
        left, top, right, bottom = monitor_work_area(x, y, full=True)
        px = max(left, min(x, right - self.width))
        if self.dock_taskbar:
            surface = taskbar_surface(px + self.width // 2, y)
            offset = min(self.dock_offset, max(0, bottom - surface))
            py = max(top, min(surface + offset - self.feet_bottom, bottom - self.height))
        else:
            py = max(top, min(y, bottom - self.height))
        if (px, py) != (x, y):
            logging.info("Restored window to visible work area from (%s, %s) to (%s, %s)", x, y, px, py)
        return px, py

    def callback_error(self, exception_type, exception, error_traceback):
        logging.error("UI callback failed:\n%s", "".join(traceback.format_exception(
            exception_type, exception, error_traceback,
        )))

    def resize_frames(self):
        with Image.open(resource_path("assets/g21_0.png")) as source:
            source_width, source_height = source.size
        self.width = round(source_width * self.height / source_height)
        target = (self.width, self.height)

        def prepare(name):
            with Image.open(resource_path(f"assets/{name}.png")) as source:
                return source.convert("RGBA").resize(target, Image.Resampling.LANCZOS)

        self.frames = {
            (x, y): [prepare(f"g{x}{y}_{frame}") for frame in range(8)]
            for x in range(5) for y in range(3)
        }
        self.blink_frames = {(x, y): prepare(f"blink_{x}{y}") for x in range(5) for y in range(3)}
        self.happy_frames = {(x, y): prepare(f"happy_{x}{y}") for x in range(5) for y in range(3)}
        self.feet_bottom = max(frame.getchannel("A").point(
            lambda value: 255 if value >= 128 else 0
        ).getbbox()[3] for frames in self.frames.values() for frame in frames)
        self.photo = ImageTk.PhotoImage(self.frames[(2, 1)][0])
        if hasattr(self, "label"):
            self.label.configure(image=self.photo)

    def gaze_direction(self, elapsed):
        mouse_x, mouse_y = self.root.winfo_pointerxy()
        eye_x = self.current_position()[0] + self.width * 0.48
        eye_y = self.current_position()[1] + self.height * 0.42
        dx, dy = mouse_x - eye_x, mouse_y - eye_y
        distance = max(math.hypot(dx, dy), self.width * 0.6)
        easing = 1 - math.exp(-elapsed * 7)
        self.look_x += (dx / distance - self.look_x) * easing
        self.look_y += (dy / distance - self.look_y) * easing
        return max(0, min(4, self.look_x * 2 + 2)), max(0, min(2, self.look_y + 1))

    @staticmethod
    def blend_gaze(frames, x, y, index=None):
        left, top = int(x), int(y)
        right, bottom = min(left + 1, 4), min(top + 1, 2)
        horizontal, vertical = x - left, y - top

        def frame(direction):
            source = frames[direction]
            return source if index is None else source[index]

        upper = Image.blend(frame((left, top)), frame((right, top)), horizontal)
        if top == bottom:
            return upper
        lower = Image.blend(frame((left, bottom)), frame((right, bottom)), horizontal)
        return Image.blend(upper, lower, vertical)

    def animate(self):
        now = time.monotonic()
        if now - self.last_screen_check > 1 and not self.drag_start:
            self.last_screen_check = now
            x, y = self.current_position()
            visible = self.visible_position(x, y)
            if visible != (x, y):
                self.position(*visible)
        phase = (now - self.started) % 8
        index = int(phase)
        gaze = self.gaze_direction(min(now - self.last_tick, 0.2))
        self.last_tick = now
        if now < self.happy_until:
            image = self.blend_gaze(self.happy_frames, *gaze)
        elif (now - self.started) % 4.8 < 0.12:
            image = self.blend_gaze(self.blink_frames, *gaze)
        else:
            image = Image.blend(
                self.blend_gaze(self.frames, *gaze, index),
                self.blend_gaze(self.frames, *gaze, (index + 1) % 8),
                phase - index,
            )
        image.putalpha(image.getchannel("A").point(lambda value: 255 if value >= 128 else 0))
        self.photo.paste(image)
        self.root.after(33, self.animate)

    def start_drag(self, event):
        self.drag_start = (event.x_root - self.current_position()[0], event.y_root - self.current_position()[1])

    def drag(self, event):
        if self.drag_start:
            self.position(event.x_root - self.drag_start[0], event.y_root - self.drag_start[1])

    def end_drag(self, _event):
        self.drag_start = None
        self.dock_taskbar = False
        self.dock_var.set(False)
        self.save_settings()

    def toggle_dock(self):
        self.dock_taskbar = self.dock_var.get()
        self.position(*self.visible_position(*self.current_position()))
        self.save_settings()

    def greet(self, _event):
        self.happy_until = time.monotonic() + 1.5

    def menu_popup(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)
        self.menu.grab_release()

    def mouse_wheel(self, event):
        values = list(SIZES.values())
        index = values.index(self.height)
        self.set_size(values[max(0, min(len(values) - 1, index + (1 if event.delta > 0 else -1)))])

    def set_size(self, height):
        if height == self.height:
            return
        x, y = self.current_position()
        self.height = height
        self.resize_frames()
        self.position(*self.visible_position(x, y))
        self.save_settings()

    def save_settings(self):
        settings_path().write_text(json.dumps({
            "x": self.current_position()[0], "y": self.current_position()[1], "height": self.height,
            "dock_taskbar": self.dock_taskbar,
            "dock_offset": self.dock_offset,
        }), encoding="utf-8")

    def close(self):
        logging.info("Closed from menu or window command")
        self.closed_intentionally = True
        self.save_settings()
        self.root.destroy()


def pet_command():
    if getattr(sys, "frozen", False):
        return [sys.executable, "--pet"]
    return [sys.executable, str(Path(__file__).resolve()), "--pet"]


def acquire_supervisor_mutex():
    """Return a held named mutex, or None when another supervisor owns it."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = (ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p)
    kernel.CreateMutexW.restype = ctypes.c_void_p
    kernel.GetLastError.argtypes = ()
    kernel.GetLastError.restype = ctypes.c_ulong
    kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
    kernel.CloseHandle.restype = ctypes.c_bool
    ctypes.set_last_error(0)
    mutex = kernel.CreateMutexW(None, False, "Local\\PhyDesktopPetSupervisor")
    error = int(kernel.GetLastError())
    if not mutex:
        logging.error("Could not create supervisor mutex, winerror=%s", error)
        return None
    if error == 183:
        kernel.CloseHandle(ctypes.c_void_p(mutex))
        logging.info("Another supervisor is already running")
        show_running_pet()
        return None
    return kernel, mutex


def supervise():
    # One supervisor per login session, even if a shortcut is clicked twice.
    lock = acquire_supervisor_mutex()
    if lock is None:
        return
    kernel, mutex = lock
    recent_failures = []
    try:
        while True:
            child = subprocess.Popen(pet_command(), cwd=str(Path(sys.executable).parent))
            logging.info("Supervisor launched pet pid=%s", child.pid)
            started = time.monotonic()
            code = child.wait()
            duration = time.monotonic() - started
            logging.info("Pet process pid=%s exited code=%s after %.1fs", child.pid, code, duration)
            if code == 0:
                break
            recent_failures = [t for t in recent_failures if time.monotonic() - t < 60]
            recent_failures.append(time.monotonic())
            if len(recent_failures) >= 3:
                logging.error("Stopped after three failures within 60s")
                break
            time.sleep(1)
    finally:
        kernel.CloseHandle(ctypes.c_void_p(mutex))


def run_pet():
    crash_log = start_diagnostics()
    exit_code = 1
    pet = None
    try:
        pet = PhyPet()
        pet.root.mainloop()
        exit_code = 0 if pet.closed_intentionally else 1
    except Exception:
        logging.exception("Desktop pet exited after an error")
        messagebox.showerror("Phy 桌寵", "程式發生錯誤，詳細資料已存到 %APPDATA%\\PhyDesktopPet\\pet.log")
    finally:
        logging.info("Main loop exited code=%s", exit_code)
        crash_log.close()
    return exit_code


if __name__ == "__main__":
    if "--pet" in sys.argv:
        sys.exit(run_pet())
    start_diagnostics()
    supervise()
