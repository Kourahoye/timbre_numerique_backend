# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from io import BytesIO
# import qrcode
# from django.conf import settings
# from django.core.files.base import ContentFile
# import os

# class TimbrePDFGenerator:
#     @staticmethod
#     def generate(timbre):
#         buffer = BytesIO()
#         p = canvas.Canvas(buffer, pagesize=A4)
#         width, height = A4

#         # Titre
#         p.setFont("Helvetica-Bold", 16)
#         p.drawString(50, height - 50, f"Timbre {timbre.reference}")

#         # Infos
#         p.setFont("Helvetica", 12)
#         p.drawString(50, height - 100, f"Type: {timbre.type.name}")
#         p.drawString(50, height - 120, f"Prix: {timbre.price.price} GNF")
#         p.drawString(50, height - 140, f"Propriétaire: {timbre.owned_by.username}")

#         # QR Code
#         qr = qrcode.QRCode(box_size=10, border=4) a
#         qr.add_data({
#             "reference": timbre.reference,
#             "secret": timbre.secret,
#             "url": f"{settings.FRONTEND_URL}/scan/{timbre.reference}"
#         })
#         qr.make(fit=True)
#         qr_img = qr.make_image(fill_color="black", back_color="white")
#         qr_path = f"/tmp/qr_{timbre.reference}.png"
#         qr_img.save(qr_path)
#         p.drawImage(qr_path, 50, height - 300, width=150, height=150)
#         os.remove(qr_path)

#         # Numéro secret
#         p.drawString(50, height - 330, f"Code secret: {timbre.secret}")

#         p.save()
#         buffer.seek(0)

#         # Sauvegarde dans le modèle
#         filename = f"timbre_{timbre.reference}.pdf"
#         timbre.pdf_file.save(filename, ContentFile(buffer.read()), save=True)
#         buffer.close()

#         return timbre.pdf_file.url
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from datetime import datetime
import os


class TimbrePDFGenerator:

    # ── Palette ──────────────────────────────────────────────────────────────
    NAVY       = colors.HexColor("#0d2b4e")
    GOLD       = colors.HexColor("#c9a84c")
    LIGHT_GOLD = colors.HexColor("#f0d080")
    CREAM      = colors.HexColor("#fdf8f0")
    LIGHT_GRAY = colors.HexColor("#f2f4f7")
    MID_GRAY   = colors.HexColor("#8a9bb0")
    TEXT_DARK  = colors.HexColor("#1a2e44")
    RED        = colors.HexColor("#c0392b")
    GREEN      = colors.HexColor("#1a7a4a")

    @classmethod
    def _qr_image(cls, data: str) -> ImageReader:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0d2b4e", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return ImageReader(buf)

    @classmethod
    def generate(cls, timbre) -> str:
        W, H = A4
        MARGIN = 30 * mm
        INNER_W = W - 2 * MARGIN
        c_obj = canvas

        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)

        # ── Background ───────────────────────────────────────────────────────
        c.setFillColor(cls.CREAM)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor("#e8e0d0"))
        c.setLineWidth(0.3)
        for i in range(-20, 60):
            offset = i * 25
            c.line(offset, 0, offset + H, H)

        # ── Header band ──────────────────────────────────────────────────────
        HEADER_H = 110
        c.setFillColor(cls.NAVY)
        c.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)
        c.setFillColor(cls.GOLD)
        c.rect(0, H - 6, W, 6, fill=1, stroke=0)          # top stripe
        c.rect(0, H - HEADER_H, W, 3, fill=1, stroke=0)   # bottom stripe

        c.setFillColor(cls.LIGHT_GOLD)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(W / 2, H - 22, "RÉPUBLIQUE DE GUINÉE")
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(W / 2, H - 48, "TIMBRE Numerique")
        c.setFillColor(cls.GOLD)
        c.setFont("Helvetica", 10)
        c.drawCentredString(W / 2, H - 66, "Document Officiel — Valeur Légale")

        # Reference badge
        badge_w, badge_h = 160, 28
        badge_x = (W - badge_w) / 2
        badge_y = H - HEADER_H + 8
        c.setFillColor(cls.GOLD)
        c.roundRect(badge_x, badge_y, badge_w, badge_h, 14, fill=1, stroke=0)
        c.setFillColor(cls.NAVY)
        # afficher la referenc e 3 par 3 caracteres en majuscules
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(badge_x + badge_w / 2, badge_y, f"REF: {timbre.reference[:3].upper()} {timbre.reference[3:6].upper()} {timbre.reference[6:].upper()}")
     
        # ── Two-column layout ────────────────────────────────────────────────
        content_top = H - HEADER_H - 18
        col_gap = 14
        col1_w = INNER_W * 0.62
        col2_w = INNER_W * 0.38 - col_gap
        col1_x = MARGIN
        col2_x = MARGIN + col1_w + col_gap
        card_h = 370
        card_y = content_top - card_h

        # Left card
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.HexColor("#d4c9b0"))
        c.setLineWidth(0.8)
        c.roundRect(col1_x, card_y, col1_w, card_h, 8, fill=1, stroke=1)
        c.setFillColor(cls.NAVY)
        c.roundRect(col1_x, card_y + card_h - 32, col1_w, 32, 8, fill=1, stroke=0)
        c.rect(col1_x, card_y + card_h - 32, col1_w, 16, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(col1_x + 14, card_y + card_h - 20, "INFORMATIONS DU TIMBRE")

        def info_row(label, value, y, accent=False):
            row_h = 30
            if accent:
                c.setFillColor(colors.HexColor("#f5f0e8"))
                c.rect(col1_x + 1, y - row_h + 5, col1_w - 2, row_h - 2, fill=1, stroke=0)
            c.setFillColor(cls.MID_GRAY)
            c.setFont("Helvetica", 8)
            c.drawString(col1_x + 14, y - 2, label.upper())
            c.setFillColor(cls.TEXT_DARK)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(col1_x + 14, y - 16, str(value))
            c.setStrokeColor(colors.HexColor("#ece6da"))
            c.setLineWidth(0.5)
            c.line(col1_x + 10, y - row_h + 5, col1_x + col1_w - 10, y - row_h + 5)

        row_y = card_y + card_h - 48
        row_step = 44
        session = timbre.price.session

        info_row("Type de timbre",   timbre.type.name,                                     row_y,         accent=True)
        row_y -= row_step
        info_row("Session",          session.name,                                          row_y)
        row_y -= row_step
        info_row("Montant",          f"{timbre.price.price:,.0f} GNF",                     row_y,         accent=True)
        row_y -= row_step
        if(timbre.owned_by.first_name or timbre.owned_by.last_name):
            info_row("Propriétaire",     f"{timbre.owned_by.first_name} {timbre.owned_by.last_name}", row_y)
        else:
            info_row("Propriétaire",     f"{timbre.owned_by.username}", row_y)
        row_y -= row_step
        info_row("Nom d'utilisateur", timbre.owned_by.username,                            row_y,         accent=True)
        row_y -= row_step
        info_row("Email",            timbre.owned_by.email,                                row_y)
        row_y -= row_step
        info_row("Date d'émission",  timbre.created_at.strftime("%d/%m/%Y à %H:%M"),       row_y,         accent=True)
        row_y -= row_step
        info_row("Code",  timbre.qrCode,       row_y,         accent=True)
        
        # Status badge
        # sx, sy = col1_x + 14, card_y + 18
        # c.setFillColor(cls.RED if timbre.used else cls.GREEN)
        # c.roundRect(sx, sy, 80, 22, 11, fill=1, stroke=0)
        # c.setFillColor(colors.white)
        # c.setFont("Helvetica-Bold", 9)
        # c.drawCentredString(sx + 40, sy + 7, "UTILISÉ" if timbre.used else "VALIDE")

        # Right card (QR)
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.HexColor("#d4c9b0"))
        c.roundRect(col2_x, card_y, col2_w, card_h, 8, fill=1, stroke=1)
        c.setFillColor(cls.GOLD)
        c.roundRect(col2_x, card_y + card_h - 32, col2_w, 32, 8, fill=1, stroke=0)
        c.rect(col2_x, card_y + card_h - 32, col2_w, 16, fill=1, stroke=0)
        c.setFillColor(cls.NAVY)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(col2_x + col2_w / 2, card_y + card_h - 20, "QR CODE DE VÉRIFICATION")

        qr_url = {
            "proprietary": timbre.owned_by.username,
            "type": timbre.type.name,
            "montant": f"{timbre.price.price:,.0f} GNF",
            "reference": timbre.reference,
            "secret": timbre.secret,
            "url": f"{settings.FRONTEND_URL}/scan/{timbre.reference}"
        }
        qr_img = cls._qr_image(qr_url)
        qr_size = col2_w - 24
        qr_img_y = card_y + card_h - 48 - qr_size
        c.drawImage(qr_img, col2_x + 12, qr_img_y, width=qr_size, height=qr_size)

        c.setFillColor(cls.MID_GRAY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(col2_x + col2_w / 2, qr_img_y - 14, "Scannez pour consommer ou vérifier")
        c.drawCentredString(col2_x + col2_w / 2, qr_img_y - 25, "l'authenticité du timbre")

        # Secret code box
        sb_y = qr_img_y - 80
        c.setFillColor(cls.NAVY)
        c.roundRect(col2_x + 8, sb_y, col2_w - 16, 55, 6, fill=1, stroke=0)
        c.setFillColor(cls.LIGHT_GOLD)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(col2_x + col2_w / 2, sb_y + 41, "CODE SECRET")
        c.setFillColor(cls.GOLD)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(col2_x + col2_w / 2, sb_y + 12, str(timbre.secret))

        # ── Session band ─────────────────────────────────────────────────────
        band_y = card_y - 78
        band_h = 60
        c.setFillColor(cls.LIGHT_GRAY)
        c.setStrokeColor(colors.HexColor("#d4c9b0"))
        c.roundRect(MARGIN, band_y, INNER_W, band_h, 8, fill=1, stroke=1)
        cell_w = INNER_W / 3
        items = [
            ("PÉRIODE DE VALIDITÉ", f"{session.start_date} → {session.end_date}"),
            ("SESSION", session.name),
            ("VALEUR NOMINALE", f"{timbre.price.price:,.0f} GNF"),
        ]
        for i, (lbl, val) in enumerate(items):
            cx = MARGIN + cell_w * i + cell_w / 2
            if i > 0:
                c.setStrokeColor(colors.HexColor("#d4c9b0"))
                c.setLineWidth(0.5)
                c.line(MARGIN + cell_w * i, band_y + 10, MARGIN + cell_w * i, band_y + band_h - 10)
            c.setFillColor(cls.MID_GRAY)
            c.setFont("Helvetica", 7)
            c.drawCentredString(cx, band_y + band_h - 18, lbl)
            c.setFillColor(cls.TEXT_DARK)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(cx, band_y + 18, val)

        # ── Instructions box ─────────────────────────────────────────────────
        notice_y = band_y - 89
        notice_h = 75
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.HexColor("#d4c9b0"))
        c.roundRect(MARGIN, notice_y, INNER_W, notice_h, 6, fill=1, stroke=1)
        c.setFillColor(cls.GOLD)
        c.rect(MARGIN, notice_y, 4, notice_h, fill=1, stroke=0)
        c.setFillColor(cls.NAVY)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN + 14, notice_y + notice_h - 16, "INSTRUCTIONS D'UTILISATION")
        instructions = [
            "1. Ce timbre fiscal est à usage unique et strictement personnel. Toute reproduction est interdite.",
            "2. Présentez ce document (imprimé ou numérique) à l'agent vérificateur lors de votre démarche.",
            "3. L'agent scannera le QR Code ou saisira la reference et pour consommer le timbre.",
            "4. En cas de problème, contactez le service compétent en fournissant la référence du timbre.",
        ]
        c.setFillColor(cls.TEXT_DARK)
        c.setFont("Helvetica", 7.5)
        for j, line in enumerate(instructions):
            c.drawString(MARGIN + 14, notice_y + notice_h - 32 - j * 12, line)

        # ── Footer ───────────────────────────────────────────────────────────
        # FOOTER_H = 42
        # c.setFillColor(cls.NAVY)
        # c.rect(0, 0, W, FOOTER_H, fill=1, stroke=0)
        # c.setFillColor(cls.GOLD)
        # c.rect(0, FOOTER_H, W, 2, fill=1, stroke=0)
        # c.setFillColor(colors.white)
        # c.setFont("Helvetica", 7)
        # c.drawCentredString(W / 2, FOOTER_H - 14,
        #     f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')} | Réf: {timbre.reference}")
        # c.setFillColor(cls.MID_GRAY)
        # c.setFont("Helvetica", 6.5)
        # c.drawCentredString(W / 2, FOOTER_H - 26,
        #     "Ce document a valeur légale. Toute falsification est passible de poursuites judiciaires.")
        # c.setFillColor(cls.GOLD)
        # c.setFont("Helvetica-Bold", 7)
        # c.drawString(MARGIN, FOOTER_H - 14, "TIMBRE.GOV.GN")
        # c.drawRightString(W - MARGIN, FOOTER_H - 14, "Système de Gestion des Timbres numeriques")
        FOOTER_H = 55  # un peu plus haut pour avoir 3 lignes bien espacées

        c.setFillColor(cls.NAVY)
        c.rect(0, 0, W, FOOTER_H, fill=1, stroke=0)
        c.setFillColor(cls.GOLD)
        c.rect(0, FOOTER_H, W, 2, fill=1, stroke=0)

        # Ligne 1 (haute) : TIMBRE.GOV.GN  ←→  Système de Gestion...
        c.setFillColor(cls.GOLD)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(MARGIN, FOOTER_H - 14, "TIMBRE.GOV.GN")
        c.drawRightString(W - MARGIN, FOOTER_H - 14, "Système de Gestion des Timbres Numériques")

        # Ligne 2 (milieu) : référence centrée
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 7)
        c.drawCentredString(
        W / 2, FOOTER_H - 28,
        f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')} | Réf: {timbre.reference}"
        )

        # Ligne 3 (basse) : mention légale
        c.setFillColor(cls.MID_GRAY)
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(
        W / 2, FOOTER_H - 42,
        "Ce document a valeur légale. Toute falsification est passible de poursuites judiciaires."
        )

        # ── Perforated edge effect ────────────────────────────────────────────
        c.setFillColor(cls.CREAM)
        for dy in range(0, int(H), 22):
            c.circle(5, dy, 5, fill=1, stroke=0)
            c.circle(W - 5, dy, 5, fill=1, stroke=0)

        c.save()
        buf.seek(0)

        filename = f"timbre_{timbre.reference}.pdf"
        timbre.pdf_file.save(filename, ContentFile(buf.read()), save=True)
        buf.close()

        return timbre.pdf_file.url