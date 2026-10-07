import random
import hashlib
from typing import List, Dict, Any, Tuple
from llmforge.review.store import HumanReviewRecord, PassageAnnotation

class BenchmarkDatasetGenerator:
    """Reproducible generator for large-scale (1,000+ records) human review learning evaluation."""

    LABEL_TAXONOMY = [
        "ADVERTISEMENT",
        "SEO_SPAM",
        "BOILERPLATE",
        "EXCESSIVE_REPETITION",
        "PROPAGANDA_SUSPECTED",
        "SEXUAL_CONTENT",
        "WRONG_LANGUAGE",
        "PROMPT_INJECTION",
        "PII",
        "BENCHMARK_LEAKAGE"
    ]

    TEMPLATES = {
        "ADVERTISEMENT": {
            "positive": [
                "Aşağıdaki bağlantıya tıklayarak %50 indirimli satın almak için tıklayın kampanyasından faydalanın.",
                "En ucuz fiyat garantisiyle hemen sipariş verin, kaçırılmayacak fırsat!",
                "Özel ticari indirim koduyla ürünü hemen sepetinize ekleyin."
            ],
            "counter": [
                "Ürünü iki hafta boyunca tarafsız olarak inceledik; avantaj ve dezavantajları şunlardır.",
                "Tüketici hakları kapsamında firma hakkında yapılan şikayetler değerlendirildi.",
                "Şirket üçüncü çeyrek finansal raporunda yeni ürün lansman tarihlerini açıkladı."
            ]
        },
        "PROPAGANDA_SUSPECTED": {
            "positive": [
                "Doğruları yalnızca tarafımız söyler, diğer tüm yayın organları hain ve yalancıdır.",
                "Davamız uğruna herkes koşulsuz itaat etmeli ve tüm emirlere uymalıdır.",
                "Bizim grubumuz dışındaki herkes düşmandır ve yok edilmelidir."
            ],
            "counter": [
                "Tarihçi akademik makalesinde her iki siyasi grubun propaganda yöntemlerini incelemektedir.",
                "Mahkeme tutanağında sanığın propaganda beyanları delil olarak kaydedildi.",
                "Haber bülteni, örgütün yayınladığı propaganda bildirisini tarafsızca aktarmaktadır."
            ]
        },
        "PII": {
            "positive": [
                "Müşterimizin TC Kimlik Numarası 12345678901 ve telefon numarası 05551234567'dir.",
                "Gizli müşteri kredi kartı numarası 4543-1234-5678-9012 geçerlilik tarihi 12/26.",
                "Açık adres: Atatürk Mahallesi, Cumhuriyet Caddesi No:45 Daire:12 Kadıköy/İstanbul."
            ],
            "counter": [
                "Kişisel verilerin korunması kanunu kapsamında TC Kimlik No ve Telefon gibi veriler saklanır.",
                "Örnek adres formatı: Mahalle, Cadde, Bina No, İlçe/İl şeklinde olmalıdır.",
                "Kredi kartı güvenliği için CVV kodunu kimseyle paylaşmayınız."
            ]
        },
        "CLEAN_NEUTRAL": {
            "positive": [
                "Türkiye'nin coğrafi bölgeleri Marmara, Ege, Akdeniz, İç Anadolu, Karadeniz, Doğu ve Güneydoğu'dur.",
                "Kuantum fiziğinde ışık hem parçacık hem de dalga özelliği gösterir.",
                "Fotosentez bitkilerin güneş ışığını kullanarak organik besin üretme sürecidir."
            ]
        }
    }

    @classmethod
    def generate_benchmark_corpus(cls, count: int = 1000, seed: int = 42) -> Tuple[List[HumanReviewRecord], List[HumanReviewRecord]]:
        """Generate deterministic evaluation corpus split into 500 Training Evidence and 500 Unseen Holdout Validation records."""
        random.seed(seed)
        all_records = []

        categories = list(cls.TEMPLATES.keys())
        for i in range(count):
            cat = categories[i % len(categories)]
            tmpl_type = "positive" if (i % 2 == 0 or cat == "CLEAN_NEUTRAL") else "counter"
            phrases = cls.TEMPLATES[cat].get(tmpl_type, cls.TEMPLATES[cat]["positive"])
            base_text = phrases[i % len(phrases)]

            # Inject variation
            doc_text = f"Kayıt ID {i+1000}: {base_text} (Detay varyasyonu: {hashlib.md5(str(i).encode()).hexdigest()[:6]})"

            if cat == "CLEAN_NEUTRAL" or tmpl_type == "counter":
                decision = "ACCEPT"
                labels = ["ACCEPTABLE_CONTENT"]
                passages = []
            else:
                decision = "REJECT"
                labels = [cat]
                passages = [
                    PassageAnnotation(
                        passage_id=f"p_{i}",
                        start_offset=15,
                        end_offset=15 + len(base_text),
                        selected_text=base_text,
                        labels=[cat]
                    )
                ]

            rec = HumanReviewRecord(
                review_id=f"bm_rev_{i+1}",
                document_id=f"bm_doc_{i+1}",
                document_text=doc_text,
                decision=decision,
                labels=labels,
                passage_annotations=passages,
                is_correction=(i % 5 == 0)
            )
            all_records.append(rec)

        # Deterministic 50/50 split into Training Feedback and Unseen Holdout Validation
        training_feedback = [r for idx, r in enumerate(all_records) if idx % 2 == 0]
        unseen_validation = [r for idx, r in enumerate(all_records) if idx % 2 != 0]

        return training_feedback, unseen_validation
