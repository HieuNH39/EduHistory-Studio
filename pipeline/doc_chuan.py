"""Chuẩn hoá lời đọc trước khi đưa vào VieNeu-TTS (phụ đề KHÔNG đổi, vẫn ghi theo SGK).

1. Tên riêng nước ngoài: SGK ghi theo phiên âm tiếng Việt (Cô-lôm-bô, Mát-xcơ-va…). Bộ đọc VieNeu v3 Turbo
   tự nhận ra chữ tiếng Anh / chữ gốc Latinh và đọc bằng âm vị tiếng Anh, nên đổi phiên âm về tên gốc
   (Columbus, Moscow…) để giọng đọc phát âm theo tiếng nước ngoài – yêu cầu GVHD 15/11/2026.
   Giữ cách đọc Việt cho tên đã Việt hoá hoặc tên khu vực mà cách đọc Việt vốn sát âm gốc
   (Chăm-pa, Cam-pu-chia, Khơ-me, Luông Pha-bang, ki-lô-mét…).
2. Số La Mã trong ngữ cảnh (thế kỉ, niên kỉ, khoá, Đại hội, tên vua…) đổi sang số Ả Rập để bộ đọc đọc
   "thế kỉ năm" chứ không đánh vần "vê"; cả dãy "thế kỉ X – XV", "thế kỉ XVI đến XVIII".
3. Khoảng năm / ngày có gạch nối có dấu cách ("1929 – 1933") đọc là "1929 đến 1933".
"""
import re

# cụm nhiều từ (xét trước), kể cả viết tắt tên riêng "C. Cô-lôm-bô"
CUM = [
    ("C. Cô-lôm-bô", "Christopher Columbus"), ("Ph. Ma-gien-lăng", "Ferdinand Magellan"), ("C. Mác", "Karl Marx"),
    ("Các Mác", "Karl Marx"), ("B. Đi-a-xơ", "Bartolomeu Dias"), ("V. Ga-ma", "Vasco da Gama"),
    ("Va-xcô đơ Ga-ma", "Vasco da Gama"), ("Ph. Ăng-ghen", "Friedrich Engels"), ("Ph. Gác-ni-ê", "Francis Garnier"),
    ("H. Ri-vi-e", "Henri Riviere"), ("V. I. Lê-nin", "Lenin"), ("V.I. Lê-nin", "Lenin"), ("S. Ê-ca-nô", "Sebastian Elcano"),
    ("R. Ác-rai", "Richard Arkwright"), ("I. Niu-tơn", "Isaac Newton"), ("M. Goóc-ba-chốp", "Mikhail Gorbachev"),
    ("B. Clin-tơn", "Bill Clinton"), ("M. Lô-mô-nô-xốp", "Mikhail Lomonosov"), ("S. Đác-uyn", "Charles Darwin"),
    ("E. Các-rai", "Edmund Cartwright"), ("M. Xéc-van-tét", "Miguel de Cervantes"), ("W. Sếch-xpia", "William Shakespeare"),
    ("N. Cô-péc-ních", "Nicolaus Copernicus"), ("G. Ga-li-lê", "Galileo Galilei"), ("G. Bru-nô", "Giordano Bruno"),
    ("Lê-ô-na đơ Vanh-xi", "Leonardo da Vinci"), ("Đờ Ca-xtơ-ri", "de Castries"), ("Mô-hen-giô Đa-rô", "Mohenjo daro"),
    ("Tơ-ru-nô Giê-giô", "Trunojoyo"), ("Hô-xê Ri-dan", "Jose Rizal"), ("Tô-mát Mo-rơ", "Thomas More"),
    ("I-u-ri Ga-ga-rin", "Yuri Gagarin"), ("Rây-mân A-ron", "Raymond Aron"), ("Mác-cô Pô-lô", "Marco Polo"),
    ("Xan Phran-xi-xcô", "San Francisco"), ("Xanh Pê-téc-bua", "Saint Petersburg"), ("Ăng-glô Xắc-xông", "Anglo Saxon"),
    ("Đôn Ki-hô-tê", "Don Quixote"), ("La-ra Giong-grang", "Lara Jonggrang"), ("Chao Phray-a", "Chao Phraya"),
    ("Sri Kse-tra", "Sri Ksetra"), ("Pôn Đu-me", "Paul Doumer"), ("Pôn Pốt", "Pol Pot"), ("San-đra Gúp-ta", "Chandragupta"),
    ("A-cha Hem-chiêu", "Achar Hem Chieu"), ("A-cha Xoa", "Achar Sva"), ("Pô Klong Ga-rai", "Po Klong Garai"),
    ("Ăng-co Bo-rây", "Angkor Borei"), ("Ăng-co Thom", "Angkor Thom"), ("Ăng-co Vát", "Angkor Wat"),
    ("Mô-hen-giô", "Mohenjo"), ("Ha-ráp-pa", "Harappa"),
]

# một từ có gạch nối (phiên âm SGK) → tên gốc
TU = {
    "In-đô-nê-xi-a": "Indonesia", "I-ta-li-a": "Italy", "Pa-ri": "Paris", "Ăng-co": "Angkor", "Cu-ba": "Cuba",
    "Phi-líp-pin": "Philippines", "A-ten": "Athens", "Vi-giay-a": "Vijaya", "Lê-nin": "Lenin", "Ma-lắc-ca": "Malacca",
    "Ma-gien-lăng": "Magellan", "Gia-va": "Java", "Xu-ma-tơ-ra": "Sumatra", "Cô-lôm-bô": "Columbus", "Đê-li": "Delhi",
    "Ăng-ghen": "Engels", "Bôn-sê-vích": "Bolshevik", "Gúp-ta": "Gupta", "Ma-lai-xi-a": "Malaysia", "Mát-xcơ-va": "Moscow",
    "Giay-a-vác-man": "Jayavarman", "A-cơ-ba": "Akbar", "Gác-ni-ê": "Garnier", "Hin-đu": "Hindu", "Ba-bi-lon": "Babylon",
    "Pi-rê": "Piraeus", "Phray-a": "Phraya", "Phi-đen": "Fidel", "Na-va": "Navarre", "Pa-tơ-nốt": "Patenotre",
    "Niu-tơn": "Newton", "Giéc-man": "German", "Phơ-răng": "Frank", "Man-ta": "Malta", "Su-khô-thay": "Sukhothai",
    "A-út-thay-a": "Ayutthaya", "Ba-ray": "Baray", "Mi-an-ma": "Myanmar", "Goóc-ba-chốp": "Gorbachev",
    "Mác-san": "Marshall", "Xta-lin-grát": "Stalingrad", "Ba-xti": "Bastille", "Hít-le": "Hitler", "Ri-vi-e": "Riviere",
    "Xin-ga-po": "Singapore", "Ba-li": "Bali", "Sác-lơ-ma-nhơ": "Charlemagne", "Đra-vi-đa": "Dravida",
    "Tơ-ru-man": "Truman", "Xu-me": "Sumer", "Ti-gơ-rơ": "Tigris", "Ơ-phơ-rát": "Euphrates", "La-pu-la-pu": "Lapulapu",
    "Ban-đu-la": "Bandula", "Mô-gôn": "Mughal", "I-an-ta": "Yalta", "Béc-lin": "Berlin", "Cát-xtơ-rô": "Castro",
    "Bô-rô-bu-đua": "Borobudur", "Man-che-xtơ": "Manchester", "Véc-xai": "Versailles", "Hác-măng": "Harmand",
    "Đác-uyn": "Darwin", "Bru-nây": "Brunei", "Su-đra": "Shudra", "Vác-na": "Varna", "Mô-giô-pa-hít": "Majapahit",
    "Hi-ma-lay-a": "Himalaya", "Mê-nét": "Menes", "pha-ra-ông": "pharaoh", "Pha-ra-ông": "Pharaoh", "Mem-phít": "Memphis",
    "Đa-rô": "daro", "I-oóc-tao": "Yorktown", "Bô-xtơn": "Boston", "Mác-tan": "Mactan", "Đi-a-xơ": "Dias",
    "Ga-ma": "Gama", "Sin-ha-pu-ra": "Singhapura", "In-đra-pu-ra": "Indrapura", "Tô-ky-ô": "Tokyo", "Tô-ki-ô": "Tokyo",
    "Sác-lơ": "Charles", "ơ-rô": "euro", "I-ra-oa-đi": "Irrawaddy", "Ka-lin-ga": "Kalinga", "Pê-tơ-rô-grát": "Petrograd",
    "Ba-ti-xta": "Batista", "Pa-gan": "Bagan", "Rơ-ve": "Revers", "Ni-a": "Niah", "Ê-ca-nô": "Elcano",
    "Bô-lô-na": "Bologna", "Lô-mô-nô-xốp": "Lomonosov", "Ha-oai": "Hawaii", "Ních-xơn": "Nixon", "Các-rai": "Cartwright",
    "A-ri-a": "Aryan", "Pa-ri-a": "Pariah", "Đê-can": "Deccan", "San-đra": "Chandra", "Nô-va-lét": "Novales",
    "Khơ-rút-xơ": "Cruz", "Đi-pô-nê-gô-rô": "Diponegoro", "Ca-li-cút": "Calicut", "Ta-be": "Taberd",
    "Vi-ra-pu-ra": "Virapura", "Ca-ra-ven": "caravel", "Oa-sinh-tơn": "Washington", "Hô-xê": "Jose", "Ri-dan": "Rizal",
    "Sa-min": "Samin", "Ra-ma-y-a-na": "Ramayana", "Áp-sa-ra": "Apsara", "Noóc-măng-đi": "Normandy",
    "Mi-ken-lăng-giơ": "Michelangelo", "Cô-péc-ních": "Copernicus", "Ga-li-lê": "Galileo", "Xê-nô": "Seno",
    "Boóc-nê-ô": "Borneo", "Bác-men": "Barmen", "Ác-rai": "Arkwright", "Đni-ép": "Dnieper", "Boóc-đô": "Bordeaux",
    "Mông-te-xki-ơ": "Montesquieu", "Vôn-te": "Voltaire", "Rút-xô": "Rousseau", "Phran-xi-xcô": "Francisco",
    "Giơ-ne-vơ": "Geneva", "Tha-kin": "Thakin", "Xti-phen-xơn": "Stephenson", "Li-vơ-pun": "Liverpool",
    "Gien-ni": "Jenny", "Bra-man": "Brahmin", "Ksa-tri-a": "Kshatriya", "Vai-si-a": "Vaishya", "Phơn-tơn": "Fulton",
    "Si-va-sa-xa-na": "Sivasasana", "Ta-na-ca": "Tanaka", "Na-pô-lê-ông": "Napoleon", "en-xi": "ensi",
    "Ha-mu-ra-bi": "Hammurabi", "Xa-ra-tô-ga": "Saratoga", "Su-ra-pa-tít": "Surapati", "Li-xbon": "Lisbon",
    "Ban-căng": "Balkan", "Song-kran": "Songkran", "Clin-tơn": "Clinton", "Méc-lanh": "Merlin", "Vác-sa-va": "Warsaw",
    "Kê-óp": "Cheops", "A-chê": "Aceh", "Bô-ni-pha-xi-ô": "Bonifacio", "Ni-ca-ra-goa": "Nicaragua", "Si-va": "Shiva",
    "Hê-rô-đốt": "Herodotus", "Giê-su": "Jesus", "Hin-du-xtan": "Hindustan", "Hin-du": "Hindu", "Ma-ta-ram": "Mataram",
    "Pa-lem-bang": "Palembang", "Ét-pê-răng": "Esperance", "Giô-công-đơ": "Gioconda", "Đan-tê": "Dante",
    "Xéc-van-tét": "Cervantes", "Ki-hô-tê": "Quixote", "Sếch-xpia": "Shakespeare", "Xích-xtin": "Sistine",
    "Bru-nô": "Bruno", "Pê-téc-bua": "Petersburg", "Ta-cô-la": "Takola", "Pông-túc": "Pong Tuk", "Xéc-bi": "Serbia",
    "Môn-ca-đa": "Moncada", "Mê-hi-cô": "Mexico", "Gran-ma": "Granma", "Đva-ra-va-ti": "Dvaravati",
    "Ha-ri-pun-giay-a": "Haripunjaya", "Gia-cô-banh": "Jacobin", "Ti-ri-ơ": "Trier", "Phi-ren-xê": "Florence",
    "Oét-min-tơ": "Westminster", "Hin-đen-bua": "Hindenburg", "U-crai-na": "Ukraine", "Bê-lô-rút-xi-a": "Belarus",
    "Cáp-ca-dơ": "Caucasus", "các-ten": "cartel", "xanh-đi-ca": "syndicate", "tơ-rớt": "trust", "Ba-danh": "Bazin",
    "Mác-xây": "Marseille", "Lu-i": "Louis", "Hăm-buốc": "Hamburg", "Top-ka-pi": "Topkapi", "Lê-nin-grát": "Leningrad",
    "Ki-ép": "Kiev", "Ma-lay-a": "Malaya", "Com-ma-đam": "Kommadam", "Xi-xê-rông": "Cicero", "Pác-tê-nông": "Parthenon",
    "Pê-ri-clét": "Pericles", "Ác-cát": "Akkad", "Át-xi-ri": "Assyria", "U-rúc": "Uruk", "E-ri-đu": "Eridu",
    "lin-ga": "linga", "Lin-ga": "Linga", "Mê-ru": "Meru", "An-giê-ri": "Algeria", "Ma-rốc": "Morocco", "Đu-me": "Doumer",
    "Mút-su-hi-tô": "Mutsuhito", "Kô-mây": "Komei", "Xít-ni": "Sydney", "Si-ca-gô": "Chicago", "Ca-ri-bê": "Caribbean",
    "Rốc-phe-lơ": "Rockefeller", "Moóc-gân": "Morgan", "Bô-inh": "Boeing", "Xcốt-len": "Scotland",
    "Vích-to-ri-a": "Victoria", "Xi-pay": "Sepoy", "Ma-ni-la": "Manila", "Ca-li-man-tan": "Kalimantan",
    "Ca-vi-tô": "Cavite", "Pu-côm-bô": "Pou Kombo", "Si-vô-tha": "Sivotha", "Bô-lô-ven": "Bolaven",
    "Ca-xtơ-ri": "Castries", "Bô-li-vi-a": "Bolivia", "Vê-nê-xu-ê-la": "Venezuela", "Cô-lôm-bi-a": "Colombia",
    "Xan-đi-nô": "Sandino", "A-vi-a": "Avia", "Ma-ha-bha-ra-ta": "Mahabharata", "I-rắc": "Iraq", "Sin-đu": "Sindhu",
    "Hi-rô-si-ma": "Hiroshima", "Na-ga-sa-ki": "Nagasaki", "Rô-mê-ô": "Romeo", "Giu-li-ét": "Juliet",
    "Hăm-lét": "Hamlet", "Ô-ten-lô": "Othello", "Đa-vít": "David", "Ha-ba-na": "Havana", "Hi-rô-hi-tô": "Hirohito",
    "Sam-sung": "Samsung", "Hyun-đai": "Hyundai", "Xơ-un": "Seoul", "Hung-ga-ri": "Hungary", "pô-li-me": "polymer",
    "com-pô-dít": "composite", "na-nô": "nano", "Cai-rô": "Cairo", "Bay-on": "Bayon", "check-in": "check in",
}
# một từ không gạch nối
TU_DON = [(r"\bMác\b(?!-)", "Marx")]

_LA_MA = r"(?:M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))"
_RM = re.compile(r"\b(" + _LA_MA + r")\b")
_GIA_TRI = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def la_ma(s):
    n, tr = 0, 0
    for ch in reversed(s):
        v = _GIA_TRI[ch]
        n += -v if v < tr else v
        tr = max(tr, v)
    return n


# từ dẫn trước số La Mã: thế kỉ, niên kỉ, khoá, Đại hội, lần thứ, khu, Chương, Phần, Quốc tế (Quốc tế III)…
_DAN = r"(?:[Tt]hế\s+k[ỉỷ]|[Nn]iên\s+k[ỉỷ]|[Tt]hiên\s+niên\s+k[ỉỷ]|[Kk]ho[áà]|Đại\s+hội|lần\s+thứ|[Kk]hu|Chương|Phần|Quốc\s+tế|Hội\s+nghị\s+Trung\s+ương)"
_NOI = r"(?:\s*[,–—-]\s*|\s+(?:đến|và|hoặc|tới|sang)\s+|\s+–\s+đầu\s+thế\s+k[ỉỷ]\s+|\s+đến\s+(?:đầu|giữa|cuối)\s+thế\s+k[ỉỷ]\s+)"
_DAY = re.compile(_DAN + r"\s+" + r"(" + _LA_MA + r")" + r"((?:" + _NOI + _LA_MA + r"\b)*)\b")
# tên vua / người có số thứ tự: Giay-a-vác-man VII, Lu-i XVI, Sác-lơ I, Na-pô-lê-ông III (đã đổi sang tên gốc hoặc chưa)
_TEN_SO = re.compile(r"(\b[A-ZÀ-ỸĐ][\wÀ-ỹ]*(?:-[\wÀ-ỹ]+)*\s+)(" + _LA_MA + r")\b(?![\wÀ-ỹ-])")


def _doi_day(m):
    goc = m.group(0)
    return re.sub(r"\b(" + _LA_MA + r")\b",
                  lambda k: str(la_ma(k.group(1))) if k.group(1) and k.group(1) not in ("C", "D", "L", "M") else k.group(0), goc)


def so_la_ma(t):
    t = _DAY.sub(_doi_day, t)

    def ten(m):
        so = m.group(2)
        if not so or so in ("I",) and m.group(1).strip() in ("Đức,", "Ở", "Còn"):
            return m.group(0)
        # chỉ đổi sau tên riêng (có gạch nối, hoặc tên gốc Latinh không dấu) để tránh chữ cái viết tắt (chiến khu D, độ C)
        ten_rieng = m.group(1).strip()
        if "-" in ten_rieng or re.fullmatch(r"[A-Z][a-z]+", ten_rieng):
            if len(so) == 1 and so in "CDLM":
                return m.group(0)
            return m.group(1) + str(la_ma(so))
        return m.group(0)
    return _TEN_SO.sub(ten, t)


def khoang(t):
    # "1929 – 1933", "13/3 – 7/5/1954", "thế kỉ 16 – 18" → "đến"
    return re.sub(r"(\d)\s+[–—-]\s+(\d)", r"\1 đến \2", t)


def ten_goc(t):
    for a, b in CUM:
        t = re.sub(r"(?<![\wÀ-ỹ-])" + re.escape(a) + r"(?![\wÀ-ỹ-])", b, t)
    t = re.sub(r"(?<![\wÀ-ỹ-])([\wÀ-ỹĐđ]+(?:-[\wÀ-ỹĐđ]+)+)(?![\wÀ-ỹ-])", lambda m: TU.get(m.group(1), m.group(1)), t)
    for a, b in TU_DON:
        t = re.sub(a, b, t)
    return t


def chuan(t):
    t = so_la_ma(t)          # trước khi đổi tên (để nhận "Giay-a-vác-man VII")
    t = ten_goc(t)
    t = khoang(t)
    return t


if __name__ == "__main__":
    import sys
    for s in sys.argv[1:] or ["Thế kỉ V trước Công nguyên, các thế kỉ XVI – XVIII, từ thế kỉ X đến XV.",
                              "Vua Giay-a-vác-man VII và Lu-i XVI; Sác-lơ I; Na-pô-lê-ông III; chiến khu D; 23,2 độ C.",
                              "Năm 1492, C. Cô-lôm-bô đến châu Mỹ; Mát-xcơ-va, Pa-ri, chủ nghĩa Mác – Lê-nin.",
                              "Khủng hoảng 1929 – 1933; Chiến dịch (13/3 – 7/5/1954); Đại hội III; Liên khu V."]:
        print(chuan(s))
