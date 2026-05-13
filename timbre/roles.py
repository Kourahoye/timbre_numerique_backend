# roles.py
ROLES = {
    "USER": [
        "buy_stamp",
        "view_own_stamps",
        "download_pdf",
    ],
    "CONTROLLER": [
        "scan_qr",
        "verify_stamp",
        "view_scan_history",
        "create_stamp",
        "sell_stamp",
        "view_sales",
        "generate_qr",
        "view_dashboard_minimal"
    ],
    "ADMIN": [
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
        "view_dashboard_global"
    ],
}