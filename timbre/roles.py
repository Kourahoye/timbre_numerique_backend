# roles.py
ROLES = {
    "user": [
        "buy_stamp",
        "view_own_stamps",
        "download_pdf",
    ],
    "controller": [
        "scan_qr",
        "verify_stamp",
        # "view_scan_history",
        "create_stamp",
        "sell_stamp",
        # "view_sales",
        "generate_qr",
        "view_dashboard_minimal"
    ],
    "admin": [
        # tout controller
        "scan_qr",
        "verify_stamp",
        "view_scan_history",
        "create_stamp",
        "sell_stamp",
        "view_sales",
        "generate_qr",

        # + admin
        "buy_stamp",
        "view_own_stamps",
        "download_pdf",
        "manage_users",
        "view_all_stamps",
        "view_dashboard_minimal",
        "view_dashboard_global"
    ],
}