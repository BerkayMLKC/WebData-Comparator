# WebData-Comparator

[![CI](https://github.com/BerkayMLKC/WebData-Comparator/actions/workflows/ci.yml/badge.svg)](https://github.com/BerkayMLKC/WebData-Comparator/actions)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Birden fazla web kaynağından ürün/fiyat verisi toplayıp **aynı ürünleri eşleştiren**, en ucuz kaynağı ve fiyat farkını gösteren **CSV ve Markdown rapor** üreten Python aracı.

Kaynaklar kodda değil, bir JSON dosyasında tanımlanır. Yeni bir siteyi eklemek için sadece CSS seçicilerini yazman yeterli.

## Özellikler

- **Config tabanlı scraping:** Her kaynak için `item`, `name`, `price`, `link` CSS seçicileri
- **Fiyat ayrıştırma:** `1.299,90 TL` (TR/EU) ve `$1,299.50` (US) formatlarını destekler
- **Akıllı eşleştirme:** Büyük/küçük harf, noktalama, Türkçe karakterler ve kelime sırası farklarını tolere eder (`difflib`, eşik değeri ayarlanabilir)
- **Birebir eşleşme:** Bir ürün başka bir ürünle iki kez eşleşmez
- **Raporlama:** `comparison.csv` (Excel uyumlu, UTF-8 BOM) ve `comparison.md`
- **Sorumlu scraping:** `robots.txt` kontrolü, `User-Agent`, zaman aşımı ve istekler arası bekleme
- **Dayanıklılık:** Bir kaynak hata verirse diğerleriyle devam eder
- **Test + CI:** pytest testleri ve GitHub Actions

## Kurulum

```bash
git clone https://github.com/BerkayMLKC/WebData-Comparator.git
cd WebData-Comparator
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Hızlı deneme

Repoda internet gerektirmeyen iki örnek mağaza sayfası var:

```bash
python -m webdata_comparator --config config.example.json
```

Çıktı:

```
[ok]   Store A: 4 items
[ok]   Store B: 4 items
[done] 5 products, reports written to reports/
```

`reports/comparison.md`:

| Product | Store A | Store B | Cheapest | Difference |
|---|---:|---:|---|---:|
| Logitech MX Master 3S Kablosuz Mouse | 1,299.90 | **1,249.00** | Store B | 50.90 |
| Keychron K2 Mekanik Klavye | **2,199.00** | 2,299.00 | Store A | 100.00 |
| Samsung 27 Odyssey Monitör | 7,499.00 | **7,399.00** | Store B | 100.00 |
| Anker 65W GaN Şarj Aleti | 899.00 | - | - | - |
| JBL Tune 510BT Kulaklık | - | 799.00 | - | - |

Üçüncü satırda iki mağazada kelime sırası farklı yazılmış ürün (`Odyssey 27` / `27 Odyssey`) doğru eşleşiyor.

## Kendi sitelerini ekleme

`config.example.json` dosyasını `config.json` olarak kopyala ve düzenle:

```json
{
  "threshold": 0.8,
  "delay_seconds": 2,
  "sources": [
    {
      "name": "Magaza A",
      "url": "https://ornek-magaza-a.com/kategori/mouse",
      "selectors": {
        "item": ".product-card",
        "name": ".product-title",
        "price": ".price",
        "link": "a"
      }
    }
  ]
}
```

| Alan | Açıklama |
|------|----------|
| `name` | Raporda görünecek kaynak adı |
| `url` / `path` | Canlı sayfa adresi veya yerel HTML dosyası (biri yeterli) |
| `base_url` | Göreli linkleri tam adrese çevirmek için (opsiyonel) |
| `selectors.item` | Her ürün kartını seçen CSS seçici |
| `selectors.name` / `price` / `link` | Kartın içindeki alanlar (`link` opsiyonel) |
| `threshold` | İsim benzerlik eşiği, 0 ile 1 arası (varsayılan 0.8) |
| `delay_seconds` | Canlı kaynaklar arası bekleme süresi |

Komut seçenekleri: `--out klasör`, `--threshold 0.75`, `--ignore-robots`.

## Nasıl çalışır?

```
config.json ──► scraper ──► matcher ──► report
              (HTML → Item)  (aynı ürünü grupla)  (CSV + Markdown)
```

1. **scraper.py:** HTML'i indirir/okur, seçicilerle `Item(source, name, price, url)` üretir.
2. **matcher.py:** İsimleri normalize eder, benzerlik skorunu hesaplar. İlk kaynak referanstır; sonraki kaynakların ürünleri en yüksek skorlu referans ürünle birebir eşleştirilir, eşleşmeyenler yeni satır olur.
3. **report.py:** Satırları CSV ve Markdown olarak yazar, her satır için en ucuz kaynağı ve fiyat farkını hesaplar.

## Testler

```bash
pip install -r requirements-dev.txt
python -m pytest -v
```

## Sorumlu kullanım

Bu araç eğitim ve portföy amaçlıdır. Bir siteyi taramadan önce kullanım şartlarına ve `robots.txt` dosyasına bakın, makul bekleme süreleri kullanın. `--ignore-robots` seçeneğini yalnızca izniniz olan sitelerde kullanın.

## Yol haritası

- [ ] Çoklu sayfa (pagination) desteği
- [ ] Fiyat geçmişi takibi (SQLite)
- [ ] JSON çıktısı
- [ ] Para birimi dönüşümü

## Lisans

MIT, bkz. [LICENSE](LICENSE).
