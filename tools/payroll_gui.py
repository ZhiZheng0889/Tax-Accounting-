import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import scrolledtext
import json
from pathlib import Path

try:
    # Import from the sibling module to reuse the core logic
    from payroll_calculator import (
        compute_paycheck,
        PayrollConfig,
        _parse_rate,
    )
except Exception as e:
    raise SystemExit(f"Error importing payroll_calculator: {e}")


class PayrollGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Payroll Calculator (with Overtime)")
        self.resizable(False, False)
        self._last_result = None
        self._settings_file = Path.home() / ".payroll_gui_settings.json"

        # Variables
        self.pay_type = tk.StringVar(value="hourly")
        self.hourly_rate = tk.StringVar()
        self.hours = tk.StringVar()
        self.overtime_hours = tk.StringVar(value="0")
        self.overtime_multiplier = tk.StringVar(value="1.5")
        self.doubletime_hours = tk.StringVar(value="0")
        self.doubletime_multiplier = tk.StringVar(value="2.0")
        self.daily_hours = tk.StringVar()
        self.use_ca_daily_ot = tk.BooleanVar(value=False)
        self.salary = tk.StringVar()

        self.year = tk.StringVar(value="2025")
        self.ytd_wages = tk.StringVar(value="0")
        self.withholding_method = tk.StringVar(value="flat")
        self.federal_rate = tk.StringVar()
        self.state_rate = tk.StringVar()

        # W-4 style variables (percentage method)
        self.filing_status = tk.StringVar(value="single")
        self.pay_periods = tk.StringVar(value="26")
        self.w4_step2 = tk.BooleanVar(value=False)
        self.w4_step3 = tk.StringVar(value="0")
        self.w4_step4a = tk.StringVar(value="0")
        self.w4_step4b = tk.StringVar(value="0")
        self.w4_step4c = tk.StringVar(value="0")

        # Pre-tax deductions
        self.pretax_401k = tk.StringVar(value="0")
        self.pretax_hsa = tk.StringVar(value="0")
        self.pretax_section125 = tk.StringVar(value="0")
        
        # Explanation toggle
        self.show_explain = tk.BooleanVar(value=True)

        self._build_ui()
        self._load_settings()
        self._toggle_fields()
        self._toggle_explain()

    def _build_ui(self):
        pad = {"padx": 6, "pady": 4}

        # Pay type
        frm_type = ttk.LabelFrame(self, text="Pay Type")
        frm_type.grid(row=0, column=0, sticky="ew", **pad)
        ttk.Radiobutton(frm_type, text="Hourly", variable=self.pay_type, value="hourly", command=self._toggle_fields).grid(row=0, column=0, sticky="w", **pad)
        ttk.Radiobutton(frm_type, text="Salary", variable=self.pay_type, value="salary", command=self._toggle_fields).grid(row=0, column=1, sticky="w", **pad)

        # Hourly inputs
        frm_hourly = ttk.LabelFrame(self, text="Hourly Inputs")
        frm_hourly.grid(row=1, column=0, sticky="ew", **pad)
        self.frm_hourly = frm_hourly

        ttk.Label(frm_hourly, text="Hourly Rate ($)").grid(row=0, column=0, sticky="e", **pad)
        ttk.Entry(frm_hourly, textvariable=self.hourly_rate, width=12).grid(row=0, column=1, **pad)

        ttk.Label(frm_hourly, text="Regular Hours").grid(row=1, column=0, sticky="e", **pad)
        ttk.Entry(frm_hourly, textvariable=self.hours, width=12).grid(row=1, column=1, **pad)

        ttk.Label(frm_hourly, text="Overtime Hours").grid(row=2, column=0, sticky="e", **pad)
        ttk.Entry(frm_hourly, textvariable=self.overtime_hours, width=12).grid(row=2, column=1, **pad)

        ttk.Label(frm_hourly, text="OT Multiplier").grid(row=3, column=0, sticky="e", **pad)
        ttk.Entry(frm_hourly, textvariable=self.overtime_multiplier, width=12).grid(row=3, column=1, **pad)

        ttk.Label(frm_hourly, text="Double-time Hours").grid(row=4, column=0, sticky="e", **pad)
        ttk.Entry(frm_hourly, textvariable=self.doubletime_hours, width=12).grid(row=4, column=1, **pad)

        ttk.Label(frm_hourly, text="DT Multiplier").grid(row=5, column=0, sticky="e", **pad)
        ttk.Entry(frm_hourly, textvariable=self.doubletime_multiplier, width=12).grid(row=5, column=1, **pad)

        ttk.Label(frm_hourly, text="Daily Hours (CSV)").grid(row=6, column=0, sticky="e", **pad)
        ttk.Entry(frm_hourly, textvariable=self.daily_hours, width=20).grid(row=6, column=1, **pad)
        ttk.Checkbutton(frm_hourly, text="Use CA daily OT", variable=self.use_ca_daily_ot).grid(row=6, column=2, sticky="w", **pad)

        # Salary input
        frm_salary = ttk.LabelFrame(self, text="Salary Input")
        frm_salary.grid(row=2, column=0, sticky="ew", **pad)
        self.frm_salary = frm_salary

        ttk.Label(frm_salary, text="Salary ($ per period)").grid(row=0, column=0, sticky="e", **pad)
        ttk.Entry(frm_salary, textvariable=self.salary, width=16).grid(row=0, column=1, **pad)

        # Tax / config
        frm_cfg = ttk.LabelFrame(self, text="Config & Withholding")
        frm_cfg.grid(row=3, column=0, sticky="ew", **pad)

        ttk.Label(frm_cfg, text="Year").grid(row=0, column=0, sticky="e", **pad)
        ttk.Entry(frm_cfg, textvariable=self.year, width=8).grid(row=0, column=1, **pad)

        ttk.Label(frm_cfg, text="YTD Wages ($)").grid(row=0, column=2, sticky="e", **pad)
        ttk.Entry(frm_cfg, textvariable=self.ytd_wages, width=12).grid(row=0, column=3, **pad)

        ttk.Label(frm_cfg, text="Withholding Method").grid(row=1, column=0, sticky="e", **pad)
        self.cbo_method = ttk.Combobox(frm_cfg, textvariable=self.withholding_method, values=("flat","irs_percentage"), width=14, state="readonly")
        self.cbo_method.grid(row=1, column=1, **pad)
        self.cbo_method.bind("<<ComboboxSelected>>", lambda e: self._toggle_fields())

        ttk.Label(frm_cfg, text="Federal Rate").grid(row=1, column=2, sticky="e", **pad)
        self.entry_federal_rate = ttk.Entry(frm_cfg, textvariable=self.federal_rate, width=8)
        self.entry_federal_rate.grid(row=1, column=3, **pad)
        ttk.Label(frm_cfg, text="(flat mode)").grid(row=1, column=4, sticky="w", **pad)

        ttk.Label(frm_cfg, text="State Rate").grid(row=2, column=0, sticky="e", **pad)
        ttk.Entry(frm_cfg, textvariable=self.state_rate, width=8).grid(row=2, column=1, **pad)

        # W-4 (percentage method)
        ttk.Label(frm_cfg, text="Filing Status").grid(row=3, column=0, sticky="e", **pad)
        self.cbo_status = ttk.Combobox(frm_cfg, textvariable=self.filing_status, values=("single","married","head"), width=10, state="readonly")
        self.cbo_status.grid(row=3, column=1, **pad)
        ttk.Label(frm_cfg, text="Pay Periods/yr").grid(row=3, column=2, sticky="e", **pad)
        self.entry_periods = ttk.Entry(frm_cfg, textvariable=self.pay_periods, width=6)
        self.entry_periods.grid(row=3, column=3, **pad)
        self.chk_step2 = ttk.Checkbutton(frm_cfg, text="W-4 Step 2 (multiple jobs)", variable=self.w4_step2)
        self.chk_step2.grid(row=3, column=4, sticky="w", **pad)

        ttk.Label(frm_cfg, text="Step 3 credit (annual)").grid(row=4, column=0, sticky="e", **pad)
        self.entry_w4s3 = ttk.Entry(frm_cfg, textvariable=self.w4_step3, width=10)
        self.entry_w4s3.grid(row=4, column=1, **pad)
        ttk.Label(frm_cfg, text="Step 4a other income").grid(row=4, column=2, sticky="e", **pad)
        self.entry_w4s4a = ttk.Entry(frm_cfg, textvariable=self.w4_step4a, width=10)
        self.entry_w4s4a.grid(row=4, column=3, **pad)
        ttk.Label(frm_cfg, text="Step 4b deductions").grid(row=4, column=4, sticky="e", **pad)
        self.entry_w4s4b = ttk.Entry(frm_cfg, textvariable=self.w4_step4b, width=10)
        self.entry_w4s4b.grid(row=4, column=5, **pad)
        ttk.Label(frm_cfg, text="Step 4c extra/period").grid(row=4, column=6, sticky="e", **pad)
        self.entry_w4s4c = ttk.Entry(frm_cfg, textvariable=self.w4_step4c, width=10)
        self.entry_w4s4c.grid(row=4, column=7, **pad)

        # Pre-tax deductions
        frm_pre = ttk.LabelFrame(self, text="Pre-tax Deductions (per period)")
        frm_pre.grid(row=4, column=0, sticky="ew", **pad)
        ttk.Label(frm_pre, text="401(k)").grid(row=0, column=0, sticky="e", **pad)
        ttk.Entry(frm_pre, textvariable=self.pretax_401k, width=10).grid(row=0, column=1, **pad)
        ttk.Label(frm_pre, text="HSA").grid(row=0, column=2, sticky="e", **pad)
        ttk.Entry(frm_pre, textvariable=self.pretax_hsa, width=10).grid(row=0, column=3, **pad)
        ttk.Label(frm_pre, text="Section 125").grid(row=0, column=4, sticky="e", **pad)
        ttk.Entry(frm_pre, textvariable=self.pretax_section125, width=10).grid(row=0, column=5, **pad)

        # Actions
        frm_actions = ttk.Frame(self)
        frm_actions.grid(row=6, column=0, sticky="ew", **pad)
        ttk.Button(frm_actions, text="Calculate", command=self._calculate).grid(row=0, column=0, **pad)
        ttk.Button(frm_actions, text="Overtime Rules", command=self._show_ot_rules).grid(row=0, column=1, **pad)
        ttk.Button(frm_actions, text="Copy Breakdown", command=self._copy_breakdown).grid(row=0, column=2, **pad)
        ttk.Button(frm_actions, text="Export CSV", command=self._export_csv).grid(row=0, column=3, **pad)
        ttk.Button(frm_actions, text="Reset", command=self._reset).grid(row=0, column=4, **pad)
        ttk.Checkbutton(frm_actions, text="Show Explanation", variable=self.show_explain, command=self._toggle_explain).grid(row=0, column=5, sticky="w", **pad)

        # Results
        frm_res = ttk.LabelFrame(self, text="Results")
        frm_res.grid(row=7, column=0, sticky="ew", **pad)
        self.lbl_gross = ttk.Label(frm_res, text="Gross: -")
        self.lbl_gross.grid(row=0, column=0, sticky="w", **pad)
        self.lbl_tax_fica = ttk.Label(frm_res, text="FICA Taxable: -")
        self.lbl_tax_fica.grid(row=1, column=0, sticky="w", **pad)
        self.lbl_tax_fit = ttk.Label(frm_res, text="FIT Taxable: -")
        self.lbl_tax_fit.grid(row=2, column=0, sticky="w", **pad)
        self.lbl_ss = ttk.Label(frm_res, text="Social Security: -")
        self.lbl_ss.grid(row=3, column=0, sticky="w", **pad)
        self.lbl_medi = ttk.Label(frm_res, text="Medicare: -")
        self.lbl_medi.grid(row=4, column=0, sticky="w", **pad)
        self.lbl_fit = ttk.Label(frm_res, text="Federal Income Tax: -")
        self.lbl_fit.grid(row=5, column=0, sticky="w", **pad)
        self.lbl_sit = ttk.Label(frm_res, text="State Income Tax: -")
        self.lbl_sit.grid(row=6, column=0, sticky="w", **pad)
        self.lbl_total = ttk.Label(frm_res, text="Total Deductions: -")
        self.lbl_total.grid(row=7, column=0, sticky="w", **pad)
        self.lbl_net = ttk.Label(frm_res, text="Net Pay: -")
        self.lbl_net.grid(row=8, column=0, sticky="w", **pad)
        self.lbl_erss = ttk.Label(frm_res, text="Employer Social Security: -")
        self.lbl_erss.grid(row=9, column=0, sticky="w", **pad)
        self.lbl_ermedi = ttk.Label(frm_res, text="Employer Medicare: -")
        self.lbl_ermedi.grid(row=10, column=0, sticky="w", **pad)
        self.lbl_ertotal = ttk.Label(frm_res, text="Employer Total Payroll Taxes: -")
        self.lbl_ertotal.grid(row=11, column=0, sticky="w", **pad)
        self.lbl_delta = ttk.Label(frm_res, text="Compared to previous: -")
        self.lbl_delta.grid(row=12, column=0, sticky="w", **pad)

        # Explanation panel
        self.frm_explain = ttk.LabelFrame(self, text="Explanation")
        self.frm_explain.grid(row=8, column=0, sticky="nsew", **pad)
        self.txt_explain = scrolledtext.ScrolledText(self.frm_explain, width=80, height=18)
        self.txt_explain.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # Error banner
        self.lbl_error = ttk.Label(self, text="", foreground="red")
        self.lbl_error.grid(row=9, column=0, sticky="w", padx=8)

    def _toggle_fields(self):
        hourly = self.pay_type.get() == "hourly"
        for child in self.frm_hourly.winfo_children():
            try:
                child.configure(state=("normal" if hourly else "disabled"))
            except tk.TclError:
                pass
        for child in self.frm_salary.winfo_children():
            try:
                child.configure(state=("disabled" if hourly else "normal"))
            except tk.TclError:
                pass
        # Withholding method toggles
        method = self.withholding_method.get()
        flat = (method == "flat")
        try:
            self.entry_federal_rate.configure(state=("normal" if flat else "disabled"))
        except tk.TclError:
            pass
        for ctrl in [self.cbo_status, self.entry_periods, self.chk_step2, self.entry_w4s3, self.entry_w4s4a, self.entry_w4s4b, self.entry_w4s4c]:
            try:
                ctrl.configure(state=("disabled" if flat else "normal"))
            except tk.TclError:
                pass

    def _calculate(self):
        try:
            pay_type = self.pay_type.get()
            year = int(self.year.get() or 2025)
            ytd = float(self.ytd_wages.get() or 0.0)
            method = self.withholding_method.get()
            fed_rate = _parse_rate(self.federal_rate.get()) if (self.federal_rate.get() and method == "flat") else None
            st_rate = _parse_rate(self.state_rate.get()) if self.state_rate.get() else None

            if pay_type == "hourly":
                rate = float(self.hourly_rate.get())
                hrs = float(self.hours.get()) if self.hours.get() else 0.0
                ot_hrs = float(self.overtime_hours.get()) if self.overtime_hours.get() else 0.0
                ot_mult = float(self.overtime_multiplier.get()) if self.overtime_multiplier.get() else 1.5
                dt_hrs = float(self.doubletime_hours.get()) if self.doubletime_hours.get() else 0.0
                dt_mult = float(self.doubletime_multiplier.get()) if self.doubletime_multiplier.get() else 2.0
                daily = self.daily_hours.get().strip() if self.daily_hours.get() else None
                use_ca = bool(self.use_ca_daily_ot.get())
                salary = None
            else:
                rate = None
                hrs = None
                ot_hrs = 0.0
                ot_mult = 1.5
                dt_hrs = 0.0
                dt_mult = 2.0
                daily = None
                use_ca = False
                salary = float(self.salary.get())

            config = PayrollConfig(
                year=year,
                ytd_wages=ytd,
                withholding_method=method,
                federal_rate=fed_rate,
                state_rate=st_rate,
                filing_status=self.filing_status.get(),
                pay_periods_per_year=int(self.pay_periods.get() or 26),
                w4_step2=bool(self.w4_step2.get()),
                w4_step3_dependents_credit=float(self.w4_step3.get() or 0.0),
                w4_step4a_other_income=float(self.w4_step4a.get() or 0.0),
                w4_step4b_deductions=float(self.w4_step4b.get() or 0.0),
                w4_step4c_extra_withholding=float(self.w4_step4c.get() or 0.0),
                pretax_401k=float(self.pretax_401k.get() or 0.0),
                pretax_hsa=float(self.pretax_hsa.get() or 0.0),
                pretax_section125=float(self.pretax_section125.get() or 0.0),
            )

            result = compute_paycheck(
                pay_type,
                hourly_rate=rate,
                hours=hrs,
                overtime_hours=ot_hrs,
                overtime_multiplier=ot_mult,
                doubletime_hours=dt_hrs,
                doubletime_multiplier=dt_mult,
                daily_hours=daily,
                use_ca_daily_ot=use_ca,
                salary=salary,
                config=config,
            )

            self.lbl_gross.configure(text=f"Gross: ${result['gross']:.2f}")
            self.lbl_tax_fica.configure(text=f"FICA Taxable: ${result['taxable_wages_fica']:.2f}")
            self.lbl_tax_fit.configure(text=f"FIT Taxable: ${result['taxable_wages_fit']:.2f}")
            self.lbl_ss.configure(text=f"Social Security: ${result['social_security']:.2f}")
            self.lbl_medi.configure(text=f"Medicare: ${result['medicare']:.2f}")
            if method == "irs_percentage":
                self.lbl_fit.configure(text=f"Federal Income Tax (IRS %): ${result['federal_income_tax']:.2f}")
            else:
                self.lbl_fit.configure(text=f"Federal Income Tax: ${result['federal_income_tax']:.2f}" if fed_rate else "Federal Income Tax: -")
            self.lbl_sit.configure(text=f"State Income Tax: ${result['state_income_tax']:.2f}" if st_rate else "State Income Tax: -")
            self.lbl_total.configure(text=f"Total Deductions: ${result['total_deductions']:.2f}")
            self.lbl_net.configure(text=f"Net Pay: ${result['net']:.2f}")
            self.lbl_erss.configure(text=f"Employer Social Security: ${result['employer_social_security']:.2f}")
            self.lbl_ermedi.configure(text=f"Employer Medicare: ${result['employer_medicare']:.2f}")
            self.lbl_ertotal.configure(text=f"Employer Total Payroll Taxes: ${result['employer_total']:.2f}")
            
            # Compare vs previous
            if self._last_result is not None:
                dnet = result['net'] - self._last_result.get('net', 0)
                sign = "+" if dnet >= 0 else ""
                self.lbl_delta.configure(text=f"Compared to previous: Net {sign}{dnet:.2f}")
            self._last_result = result

            # Explanation
            if self.show_explain.get():
                from payroll_calculator import build_explanation_text
                explain = build_explanation_text(
                    pay_type,
                    hourly_rate=rate,
                    hours=hrs,
                    overtime_hours=ot_hrs,
                    overtime_multiplier=ot_mult,
                    doubletime_hours=dt_hrs,
                    doubletime_multiplier=dt_mult,
                    daily_hours=daily,
                    use_ca_daily_ot=use_ca,
                    salary=salary,
                    config=config,
                )
                self.txt_explain.delete("1.0", tk.END)
                self.txt_explain.insert(tk.END, explain)

            # Save settings
            self._save_settings()

        except Exception as e:
            self.lbl_error.configure(text=str(e))

    def _show_ot_rules(self):
        text = (
            "Overtime Basics (U.S. FLSA)\n\n"
            "- For most non-exempt employees, overtime is paid at not less than 1.5x the regular rate for hours worked over 40 in a workweek.\n"
            "- Some states add daily overtime or double-time rules (e.g., California).\n"
            "- This calculator uses your input for overtime hours and a multiplier (default 1.5x). If your state has daily OT/double-time, compute those hours separately and enter them here with the right multiplier.\n\n"
            "Examples:\n"
            "1) $20/hr, 45 hours in the week (5 OT):\n"
            "   Regular: 40 x $20 = $800\n"
            "   Overtime: 5 x $20 x 1.5 = $150\n"
            "   Gross = $950\n\n"
            "2) $30/hr, 38 hours (no OT):\n"
            "   Gross = 38 x $30 = $1,140\n\n"
            "3) $30/hr, 50 hours (10 OT):\n"
            "   Regular: 40 x $30 = $1,200\n"
            "   Overtime: 10 x $30 x 1.5 = $450\n"
            "   Gross = $1,650\n\n"
            "Note: Salaried employees may still be non-exempt and eligible for overtime depending on duties and salary thresholds. This simple tool does not determine exemption status."
        )
        messagebox.showinfo("Overtime Rules", text)

    def _toggle_explain(self):
        if self.show_explain.get():
            self.frm_explain.grid()
        else:
            self.frm_explain.grid_remove()

    def _copy_breakdown(self):
        data = self.txt_explain.get("1.0", tk.END).strip()
        if not data:
            messagebox.showinfo("Copy Breakdown", "Run Calculate to generate explanation first.")
            return
        self.clipboard_clear()
        self.clipboard_append(data)
        self.update()  # keep clipboard
        messagebox.showinfo("Copy Breakdown", "Copied to clipboard.")

    def _export_csv(self):
        if self._last_result is None:
            messagebox.showinfo("Export CSV", "No results yet. Calculate first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if not path:
            return
        import csv
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "gross","taxable_wages_fica","taxable_wages_fit","social_security","medicare",
                    "federal_income_tax","state_income_tax","total_deductions","net",
                    "employer_social_security","employer_medicare","employer_total"
                ],
            )
            writer.writeheader()
            writer.writerow(self._last_result)
        messagebox.showinfo("Export CSV", f"Saved: {path}")

    def _reset(self):
        # Minimal reset of key fields
        self.hourly_rate.set("")
        self.hours.set("")
        self.overtime_hours.set("0")
        self.overtime_multiplier.set("1.5")
        self.doubletime_hours.set("0")
        self.doubletime_multiplier.set("2.0")
        self.daily_hours.set("")
        self.use_ca_daily_ot.set(False)
        self.salary.set("")
        self.federal_rate.set("")
        self.state_rate.set("")
        self.w4_step2.set(False)
        self.w4_step3.set("0")
        self.w4_step4a.set("0")
        self.w4_step4b.set("0")
        self.w4_step4c.set("0")
        self.pretax_401k.set("0")
        self.pretax_hsa.set("0")
        self.pretax_section125.set("0")
        self.txt_explain.delete("1.0", tk.END)
        self.lbl_error.configure(text="")

    def _save_settings(self):
        try:
            data = {
                "pay_type": self.pay_type.get(),
                "hourly_rate": self.hourly_rate.get(),
                "hours": self.hours.get(),
                "overtime_hours": self.overtime_hours.get(),
                "overtime_multiplier": self.overtime_multiplier.get(),
                "doubletime_hours": self.doubletime_hours.get(),
                "doubletime_multiplier": self.doubletime_multiplier.get(),
                "daily_hours": self.daily_hours.get(),
                "use_ca_daily_ot": bool(self.use_ca_daily_ot.get()),
                "salary": self.salary.get(),
                "year": self.year.get(),
                "ytd_wages": self.ytd_wages.get(),
                "withholding_method": self.withholding_method.get(),
                "federal_rate": self.federal_rate.get(),
                "state_rate": self.state_rate.get(),
                "filing_status": self.filing_status.get(),
                "pay_periods": self.pay_periods.get(),
                "w4_step2": bool(self.w4_step2.get()),
                "w4_step3": self.w4_step3.get(),
                "w4_step4a": self.w4_step4a.get(),
                "w4_step4b": self.w4_step4b.get(),
                "w4_step4c": self.w4_step4c.get(),
                "pretax_401k": self.pretax_401k.get(),
                "pretax_hsa": self.pretax_hsa.get(),
                "pretax_section125": self.pretax_section125.get(),
                "show_explain": bool(self.show_explain.get()),
            }
            self._settings_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def _load_settings(self):
        try:
            if not self._settings_file.exists():
                return
            data = json.loads(self._settings_file.read_text())
            self.pay_type.set(data.get("pay_type", self.pay_type.get()))
            self.hourly_rate.set(data.get("hourly_rate", ""))
            self.hours.set(data.get("hours", ""))
            self.overtime_hours.set(data.get("overtime_hours", "0"))
            self.overtime_multiplier.set(data.get("overtime_multiplier", "1.5"))
            self.doubletime_hours.set(data.get("doubletime_hours", "0"))
            self.doubletime_multiplier.set(data.get("doubletime_multiplier", "2.0"))
            self.daily_hours.set(data.get("daily_hours", ""))
            self.use_ca_daily_ot.set(bool(data.get("use_ca_daily_ot", False)))
            self.salary.set(data.get("salary", ""))
            self.year.set(data.get("year", self.year.get()))
            self.ytd_wages.set(data.get("ytd_wages", "0"))
            self.withholding_method.set(data.get("withholding_method", self.withholding_method.get()))
            self.federal_rate.set(data.get("federal_rate", ""))
            self.state_rate.set(data.get("state_rate", ""))
            self.filing_status.set(data.get("filing_status", self.filing_status.get()))
            self.pay_periods.set(data.get("pay_periods", self.pay_periods.get()))
            self.w4_step2.set(bool(data.get("w4_step2", False)))
            self.w4_step3.set(data.get("w4_step3", "0"))
            self.w4_step4a.set(data.get("w4_step4a", "0"))
            self.w4_step4b.set(data.get("w4_step4b", "0"))
            self.w4_step4c.set(data.get("w4_step4c", "0"))
            self.pretax_401k.set(data.get("pretax_401k", "0"))
            self.pretax_hsa.set(data.get("pretax_hsa", "0"))
            self.pretax_section125.set(data.get("pretax_section125", "0"))
            self.show_explain.set(bool(data.get("show_explain", True)))
        except Exception:
            pass


def main():
    app = PayrollGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
