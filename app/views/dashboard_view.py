"""
app/views/dashboard_view.py — Comprehensive Profile Visualization Layout.
"""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING, Optional

import app.config as config
from app.models.auth_models import AuthSession

if TYPE_CHECKING:
    from app.controllers.fleet_controller import FleetController


class DashboardView(tk.Frame):
    """Detailed vehicle overview dashboard panel using an adaptive single-column schema."""

    def __init__(self, parent: tk.Misc, controller: FleetController) -> None:
        super().__init__(parent, bg=config.COLOR_BG_DARK)
        self._controller = controller
        self._root = parent
        self._session: Optional[AuthSession] = None
        self._fields: dict[str, tk.StringVar] = {}
        self._right_fields: dict[str, tk.StringVar] = {}
        self._raw_parenthesis_data: str = ""

        self._build_ui()

    def _build_ui(self) -> None:
        # ── TOP STRIP PANEL ──
        self._top_panel = tk.Frame(self, bg=config.COLOR_BG_PANEL, height=50)
        self._top_panel.pack(side="top", fill="x", padx=15, pady=(15, 5))
        self._top_panel.pack_propagate(False)

        self._user_label = tk.Label(
            self._top_panel,
            text="Welcome",
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_FG_PRIMARY,
            font=(config.FONT_FAMILY, config.FONT_SIZE_BODY, "bold"),
        )
        self._user_label.pack(side="left", padx=15)

        self._quit_btn = tk.Button(
            self._top_panel,
            text="EXIT",
            bg=config.COLOR_BORDER,
            fg=config.COLOR_ERROR,
            activebackground=config.COLOR_BG_DARK,
            activeforeground=config.COLOR_ERROR,
            font=(config.FONT_FAMILY, config.FONT_SIZE_BODY, "bold"),
            bd=0,
            cursor="hand2",
            padx=12,
            command=self._on_quit,
        )
        self._quit_btn.pack(side="right", padx=15)

        self._logout_btn = tk.Button(
            self._top_panel,
            text="LOGOUT",
            bg=config.COLOR_BORDER,
            fg=config.COLOR_ERROR,
            activebackground=config.COLOR_BG_DARK,
            activeforeground=config.COLOR_ERROR,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL, "bold"),
            bd=0,
            cursor="hand2",
            padx=12,
            command=self._on_logout,
        )
        self._logout_btn.pack(side="right", padx=(15, 0))

        self._copy_btn = tk.Button(
            self._top_panel,
            text="📋 COPY VALUES",
            command=self._on_copy_to_clipboard,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_ACCENT,
            activebackground=config.COLOR_ACCENT,
            activeforeground=config.COLOR_BG_DARK,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL, "bold"),
            relief="flat",
            padx=10,
            state="disabled",
        )
        self._copy_btn.pack(side="right", padx=5, pady=10)

        # ── ADAPTIVE WORKSPACE CONTAINER ──
        # Replaced the 3-column split with a clean, centered single-column layout
        workspace_container = tk.Frame(self, bg=config.COLOR_BG_DARK)
        workspace_container.pack(fill="both", expand=True, padx=15, pady=5)

        canvas = tk.Canvas(workspace_container, bg=config.COLOR_BG_DARK, bd=0, highlightthickness=0)
        self._scrollable_frame = tk.Frame(canvas, bg=config.COLOR_BG_DARK)

        self._scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._canvas_window_id = canvas.create_window((0, 0), window=self._scrollable_frame, anchor="nw")

        def _on_canvas_resize(event):
            # Keeps the scrollable inner content bound directly to the canvas window width bounds
            canvas.itemconfig(self._canvas_window_id, width=event.width)

        canvas.bind("<Configure>", _on_canvas_resize)
        canvas.pack(side="left", fill="both", expand=True)

        # ── MOUSE WHEEL GESTURE BINDINGS ──
        def _on_mouse_wheel(event):
            if event.num == 5 or event.delta < 0:
                canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")

        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
        canvas.bind_all("<Button-4>", _on_mouse_wheel)
        canvas.bind_all("<Button-5>", _on_mouse_wheel)

        # ── SEARCH CONTROL BLOCK ──
        search_outer = tk.Frame(self._scrollable_frame, bg=config.COLOR_BG_PANEL, pady=8)
        search_outer.pack(pady=(0, 10), fill="x", padx=10)  # Fills horizontal space smoothly

        search_frame = tk.Frame(search_outer, bg=config.COLOR_BG_PANEL)
        search_frame.pack(anchor="center")

        tk.Label(
            search_frame,
            text="Search by Limiter Serial or Vehicle Registration:",
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_ACCENT,
            font=(config.FONT_FAMILY, config.FONT_SIZE_BODY, "bold"),
        ).pack(side="left", padx=(0, 8))

        self._search_var = tk.StringVar()
        self._search_entry = tk.Entry(
            search_frame,
            textvariable=self._search_var,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_FG_PRIMARY,
            insertbackground=config.COLOR_FG_PRIMARY,
            font=(config.FONT_FAMILY, config.FONT_SIZE_BODY),
            bd=1,
            relief="solid",
            width=22,
        )
        self._search_entry.pack(side="left", padx=5, ipady=3)
        self._search_entry.bind("<Return>", lambda e: self._on_search_submit())

        self._search_btn = tk.Button(
            search_frame,
            text="SEARCH",
            bg=config.COLOR_ACCENT,
            fg=config.COLOR_BG_DARK,
            activebackground=config.COLOR_FG_PRIMARY,
            activeforeground=config.COLOR_BG_DARK,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL, "bold"),
            bd=0,
            cursor="hand2",
            padx=15,
            command=self._on_search_submit,
        )
        self._search_btn.pack(side="left", padx=10)

        # ── CONSOLIDATED DATA CARD BLOCK ──
        vehicle_details = self._create_section_card(" Vehicle Reset Details ")

        self._add_row(vehicle_details, "Limiter Serial No:", "limiter_serial", 0)
        self._add_row(vehicle_details, "Registered Owner / Corporation:", "owner_name", 1)
        self._add_row(vehicle_details, "Official Owner ID:", "official_id", 2)
        self._add_row(vehicle_details, "Owner Contact Line:", "telephone1", 3)
        self._add_row(vehicle_details, "Vehicle Registration:", "vehicle_registration", 4)
        self._add_row(vehicle_details, "Chassis Serial ID:", "chassis_number", 5)
        self._add_row(vehicle_details, "Vehicle Make and Type:", "vehicle_make_n_type", 6)
        self._add_row(vehicle_details, "Vehicle Certificate Number:", "certificate_number", 7)
        self._add_row(vehicle_details, "Vehicle Limiter Type:", "limiter_type", 8)
        self._add_row(vehicle_details, "Certificate Issue Date:", "issue_date", 9)
        self._add_row(vehicle_details, "Certificate Expiry Date:", "expiry_date", 10)
        self._add_row(vehicle_details, "Installation Location:", "installation_location", 11)
        self._add_row(vehicle_details, "Installation Agent ID:", "agent_id", 12)
        self._add_row(vehicle_details, "Company Location:", "company_location", 13)
        self._add_row(vehicle_details, "Company Email Address:", "company_email", 14)
        self._add_row(vehicle_details, "Company Phone Number:", "company_phone_number", 15)
        self._add_row(vehicle_details, "Company Street Address:", "company_street_address", 16)
        self._add_row(vehicle_details, "Speed Threshold:", "speed_threshold", 17)
        self._add_row(vehicle_details, "Fitting Technician Name:", "fitting_technician_nickname", 18)

        # ── STATUS FOOTER STRIP ──
        self._bottom_panel = tk.Frame(self, bg=config.COLOR_BG_DARK)
        self._bottom_panel.pack(side="bottom", fill="x", padx=15, pady=(5, 15))

        self._status_var = tk.StringVar()
        self._status_label = tk.Label(
            self._bottom_panel,
            textvariable=self._status_var,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_ERROR,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL),
        )
        self._status_label.pack(side="left")

    def _create_section_card(self, section_title: str) -> tk.LabelFrame:
        """Helper to build layout cards that dynamically expand horizontally."""
        card = tk.LabelFrame(
            self._scrollable_frame,
            text=section_title,
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_ACCENT,
            font=(config.FONT_FAMILY, config.FONT_SIZE_LABEL, "bold"),
            padx=15,
            pady=15,
            bd=1,
            relief="solid",
        )
        # Changed anchor="center" and explicit width configurations to layout-responsive configurations
        card.pack(pady=8, padx=10, fill="x", expand=True)
        card.columnconfigure(0, weight=1)
        return card

    def _add_row(self, parent: tk.Widget, visual_label: str, mapping_key: str, grid_row: int) -> None:
        """Helper mapping grid values into flexible percentage-based table items."""
        row_outer = tk.Frame(parent, bg=config.COLOR_BG_PANEL)
        row_outer.grid(row=grid_row, column=0, pady=4, padx=5, sticky="ew")

        # Configurations map columns evenly to split screen 50/50 cleanly across responsive frame modifications
        row_outer.columnconfigure(0, weight=1, uniform="dashboard_grid")
        row_outer.columnconfigure(1, weight=1, uniform="dashboard_grid")

        key_frame = tk.Frame(row_outer, bg=config.COLOR_BG_PANEL, bd=1, relief="solid")
        key_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 2))

        lbl = tk.Label(
            key_frame,
            text=visual_label,
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_FG_MUTED,
            font=(config.FONT_FAMILY, config.FONT_SIZE_BODY, "bold"),
            anchor="w",
        )
        lbl.pack(padx=12, pady=6, fill="both", expand=True)

        val_frame = tk.Frame(row_outer, bg=config.COLOR_BG_PANEL, bd=1, relief="solid")
        val_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 0))

        val_var = tk.StringVar(value="")
        self._fields[mapping_key] = val_var

        val_display = tk.Label(
            val_frame,
            textvariable=val_var,
            bg=config.COLOR_BG_PANEL,
            fg=config.COLOR_FG_PRIMARY,
            font=(config.FONT_FAMILY, config.FONT_SIZE_BODY),
            anchor="center",
            wraplength=400,  # Increased wrapping length capacity to fit max-width setups perfectly
            justify="center",
        )
        val_display.pack(padx=12, pady=6, fill="both", expand=True)

    def show(self, session: AuthSession) -> None:
        self._session = session
        self._user_label.config(text=f"👤  {session.full_name}  ({session.role})")
        self.lift()
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.clear_fields()
        self._status_var.set("Ready. Input a registration code or limiter serial to view metadata profiles.")

    def hide(self) -> None:
        self.place_forget()

    def clear_fields(self) -> None:
        self._search_var.set("")
        for field_var in self._fields.values():
            field_var.set("")

    def set_loading(self, loading: bool) -> None:
        if loading:
            self._search_btn.config(state="disabled", text="QUERYING...")
            self._status_var.set("Fetching full audit datastore records across systems...")
        else:
            self._search_btn.config(state="normal", text="SEARCH")

    def populate_profile(self, payload_item: dict) -> None:
        self._status_var.set("")
        for key, value_var in self._fields.items():
            raw_val = payload_item.get(key, "")

            if raw_val is None or raw_val == "":
                value_var.set("—")
            else:
                value_var.set(str(raw_val).strip())

        status_string = str(payload_item.get("status", "unknown")).upper()
        self._status_var.set(f"✔ Audit Success: Records verified! Asset status is: {status_string}")

    def show_status_error(self, message: str) -> None:
        self._status_var.set(f"! Lookup Failure: {message}")

    def _on_search_submit(self) -> None:
        query = self._search_var.get().strip()
        if not query:
            self._status_var.set("! Validation Error: Target text query field cannot be left blank.")
            return
        self._controller.search_by_registration(query)

    def _on_logout(self) -> None:
        self._controller.coordinator.force_logout()

    def _on_quit(self) -> None:
        self._controller.coordinator.force_quit()

    def set_parenthesis_payload(self, raw_string: str) -> None:
        self._raw_parenthesis_data = raw_string
        if raw_string:
            self._copy_btn.config(state="normal")
        else:
            self._copy_btn.config(state="disabled")

    def _on_copy_to_clipboard(self) -> None:
        if not self._raw_parenthesis_data:
            self._status_var.set("! Clipboard Error: No active system profile records loaded.")
            return

        try:
            self.clipboard_clear()
            self.clipboard_append(self._raw_parenthesis_data)
            self._status_var.set("✔ Success: Parenthesis asset string values copied to clipboard!")
        except Exception as e:
            self._status_var.set(f"! Hardware Fault: Failed to interact with OS clipboard: {e}")
