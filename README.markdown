# Veresiye Defteri

Python ve Tkinter kullanılarak geliştirilmiş basit bir **veresiye takip uygulaması**. SQLite veritabanı ile çalışır ve kullanıcı dostu bir arayüz sunar.  

---

## Özellikler

- **Müşteri Yönetimi**
  - Yeni müşteri ekleme
  - Mevcut müşteri adını değiştirme (yeniden adlandırma)
  - Müşteri listesi otomatik sıralanır

- **İşlem Yönetimi**
  - Borç ve tahsilat işlemleri ekleme
  - İşlem notu ekleyebilme
  - İşlem tarihi otomatik olarak kaydedilir
  - Son 20 işlem seçili müşteriye özel görüntülenir
  - Tüm müşterilerin son 100 işlemi görüntülenir

- **Borç Takibi**
  - Her müşteri için toplam borç hesaplanır
  - Tüm müşterilerin toplam borcu gösterilir
  - İşlem tablosu ve toplam borç bilgisi anlık güncellenir

- **Admin İşlemleri**
  - Seçili işlemi silme (şifre korumalı)
  - Tüm işlemleri CSV formatında indirme

- **Kullanıcı Arayüzü**
  - Tkinter ile responsive bir tasarım
  - Treeview ile tablolar ve sıralanabilir listeler
  - Scrollable frame sayesinde uzun liste desteği

---

## Gereksinimler

- Python 3.x
- Tkinter (Python ile birlikte gelir)
- SQLite3 (Python ile birlikte gelir)

---


