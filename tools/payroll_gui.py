import tkinter as tk
from tkinter import ttk, messagebox

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

        # Variables
        self.pay_type = tk.StringVar(value="hourly")
        self.hourly_rate = tk.StringVar()
        self.hours = tk.StringVar()
        self.overtime_hours = tk.StringVar(value="0")
        self.overtime_multiplier = tk.StringVar(value="1.5")
        self.salary = tk.StringVar()

        self.year = tk.StringVar(value="2025")
        self.ytd_wages = tk.StringVar(value="0")
        self.federal_rate = tk.StringVar()
        self.state_rate = tk.StringVar()

        self._build_ui()
        self._toggle_fields()

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

        ttk.Label(frm_cfg, text="Federal Rate").grid(row=1, column=0, sticky="e", **pad)
        ttk.Entry(frm_cfg, textvariable=self.federal_rate, width=8).grid(row=1, column=1, **pad)
        ttk.Label(frm_cfg, text="(e.g., 12 or 12%)").grid(row=1, column=2, sticky="w", **pad)

        ttk.Label(frm_cfg, text="State Rate").grid(row=1, column=3, sticky="e", **pad)
        ttk.Entry(frm_cfg, textvariable=self.state_rate, width=8).grid(row=1, column=4, **pad)

        # Actions
        frm_actions = ttk.Frame(self)
        frm_actions.grid(row=4, column=0, sticky="ew", **pad)
        ttk.Button(frm_actions, text="Calculate", command=self._calculate).grid(row=0, column=0, **pad)
        ttk.Button(frm_actions, text="Overtime Rules", command=self._show_ot_rules).grid(row=0, column=1, **pad)

        # Results
        frm_res = ttk.LabelFrame(self, text="Results")
        frm_res.grid(row=5, column=0, sticky="ew", **pad)
        self.lbl_gross = ttk.Label(frm_res, text="Gross: -")
        self.lbl_gross.grid(row=0, column=0, sticky="w", **pad)
        self.lbl_ss = ttk.Label(frm_res, text="Social Security: -")
        self.lbl_ss.grid(row=1, column=0, sticky="w", **pad)
        self.lbl_medi = ttk.Label(frm_res, text="Medicare: -")
        self.lbl_medi.grid(row=2, column=0, sticky="w", **pad)
        self.lbl_fit = ttk.Label(frm_res, text="Federal Income Tax: -")
        self.lbl_fit.grid(row=3, column=0, sticky="w", **pad)
        self.lbl_sit = ttk.Label(frm_res, text="State Income Tax: -")
        self.lbl_sit.grid(row=4, column=0, sticky="w", **pad)
        self.lbl_total = ttk.Label(frm_res, text="Total Deductions: -")
        self.lbl_total.grid(row=5, column=0, sticky="w", **pad)
        self.lbl_net = ttk.Label(frm_res, text="Net Pay: -")
        self.lbl_net.grid(row=6, column=0, sticky="w", **pad)

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

    def _calculate(self):
        try:
            pay_type = self.pay_type.get()
            year = int(self.year.get() or 2025)
            ytd = float(self.ytd_wages.get() or 0.0)
            fed_rate = _parse_rate(self.federal_rate.get()) if self.federal_rate.get() else None
            st_rate = _parse_rate(self.state_rate.get()) if self.state_rate.get() else None

            if pay_type == "hourly":
                rate = float(self.hourly_rate.get())
                hrs = float(self.hours.get()) if self.hours.get() else 0.0
                ot_hrs = float(self.overtime_hours.get()) if self.overtime_hours.get() else 0.0
                ot_mult = float(self.overtime_multiplier.get()) if self.overtime_multiplier.get() else 1.5
                salary = None
            else:
                rate = None
                hrs = None
                ot_hrs = 0.0
                ot_mult = 1.5
                salary = float(self.salary.get())

            config = PayrollConfig(year=year, ytd_wages=ytd, federal_rate=fed_rate, state_rate=st_rate)

            result = compute_paycheck(
                pay_type,
                hourly_rate=rate,
                hours=hrs,
                overtime_hours=ot_hrs,
                overtime_multiplier=ot_mult,
                salary=salary,
                config=config,
            )

            self.lbl_gross.configure(text=f"Gross: ${result['gross']:.2f}")
            self.lbl_ss.configure(text=f"Social Security: ${result['social_security']:.2f}")
            self.lbl_medi.configure(text=f"Medicare: ${result['medicare']:.2f}")
            self.lbl_fit.configure(text=f"Federal Income Tax: ${result['federal_income_tax']:.2f}" if fed_rate else "Federal Income Tax: -")
            self.lbl_sit.configure(text=f"State Income Tax: ${result['state_income_tax']:.2f}" if st_rate else "State Income Tax: -")
            self.lbl_total.configure(text=f"Total Deductions: ${result['total_deductions']:.2f}")
            self.lbl_net.configure(text=f"Net Pay: ${result['net']:.2f}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

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


def main():
    app = PayrollGUI()
    app.mainloop()


if __name__ == "__main__":
    main()

