# Be Right Back!

Bu program, League of Legends oyununda eşleşme bulunduğunda otomatik olarak kabul et butonuna tıklar. Hem Sihirdar Vadisi hem de TFT için çalışır.

![screen](https://github.com/draxya/lol-auto-accept/assets/68575901/8aa84c53-fce9-4218-bd6f-360a5cdcb034)

## Özellikler

- **Otomatik Kabul**: Eşleşme bulunduğunda otomatik olarak kabul et butonuna tıklar
- **Çoklu Dil Desteği**: Türkçe, İngilizce, Almanca, Fransızca, İspanyolca, Rusça, Korece, Japonca ve Çince
- **Görüntü Tanıma**: Kabul et butonunu hem Rift hem de TFT için otomatik olarak tanır
- **Metin Tanıma (OCR)**: Tesseract ile metin tanıma desteği
- **1080p Sabit Mod**: 1920x1080 çözünürlükte sabit koordinat kullanabilme
- **Düşük Sistem Gereksinimleri**: Minimum RAM ve CPU kullanımı

## Kurulum

### Hazır Kurulum (Önerilen)

1. [Buradan](https://github.com/draxya/BeRightBack/releases/download/v1.1.0/BeRightBack.exe) en son sürümü indirin
2. İndirilen EXE dosyasını çalıştırın
3. Oyun dilini seçin ve başlat butonuna tıklayın

### Manuel Kurulum (Geliştiriciler İçin)

1. Repo'yu klonlayın: `git clone https://github.com/kullanici-adi/repo-adi.git`
2. Uygun Python sürümünü indirin: Python 3.9.x
3. Gerekli kütüphaneleri yükleyin: `pip install -r requirements.txt`
4. `main.py` dosyasını çalıştırın: `python main.py`

## Kullanım

1. Aşağıda bulunan **OCR (Metin Tanıma) Özelliği İçin Tesseract Kurulumu** adımını takip edin.
2. Programı başlatın
3. League of Legends'ın dilini seçin
4. "Başlat (F6)" butonuna tıklayın veya F6 tuşuna basın
5. League of Legends'ı açın ve eşleşme aramaya başlayın
6. Program otomatik olarak kabul et butonuna tıklayacaktır
7. Programı durdurmak için "Durdur (F7)" butonuna tıklayın veya F7 tuşuna basın
8. Keyfini çıkarın!

## Algılama Yöntemleri

Program, kabul et butonunu bulmak için üç farklı yöntem kullanır:

1. **Görüntü Tanıma**: Kabul et butonunun görüntüsünü tanır
2. **Metin Tanıma (OCR)**: Ekrandaki "Kabul Et", "Accept" vb. metinleri tanır
3. **1080p Sabit Mod**: 1920x1080 çözünürlükte *penceresi yeniden konumlandırılmamış olan* LoL'ün sabit kabul et butonu koordinatlarını kullanır

## OCR (Metin Tanıma) Özelliği İçin Tesseract Kurulumu

OCR özelliğini kullanmak için Tesseract OCR kurmanız gerekir:

1. [Tesseract OCR indirme sayfasından](https://github.com/UB-Mannheim/tesseract/wiki) en son sürümü indirin
2. Kurulum sırasında "Additional language data" seçeneğinden LoL'de kullanmak istediğiniz dilleri seçin:
   - Türkçe için: Turkish
   - İngilizce için: English
   - Diğer dilleri de ekleyebilirsiniz (German (Almanca), French (Fransızca), Spanish (İspanyolca), Russian (Rusça), Korean (Korece), Japanese (Japonca) ve Simplified Chinese (Çince))
3. Varsayılan kurulum konumunu değiştirmeyin (`C:\Program Files\Tesseract-OCR\`)
4. Kurulum tamamlandıktan sonra programı başlatın, OCR özelliği otomatik olarak aktif olacaktır

## Sık Sorulan Sorular

### Antivirüs programım uyarı veriyor, bu normal mi?
Evet, PyInstaller ile derlenen uygulamalar bazen antivirüs programları tarafından yanlış pozitif olarak algılanabilir. Program tamamen güvenlidir ve kaynak kodu açıktır.

### Program açılmıyor, ne yapmalıyım?
Windows'un bilinmeyen yayıncıdan gelen uyarılarında "Yine de çalıştır" seçeneğini işaretleyin. Yine de sorun yaşıyorsanız, Python kurup manuel kurulum adımlarını takip edebilirsiniz.

### Metin tanıma (OCR) çalışmıyor, neden?
Tesseract OCR kurulu olmayabilir veya doğru şekilde yapılandırılmamış olabilir. Yukarıdaki "OCR Özelliği İçin Tesseract Kurulumu" adımlarını takip edin.

### Farklı çözünürlüklerde çalışıyor mu?
Evet, görüntü tanıma ve metin tanıma özellikleri tüm çözünürlüklerde çalışır. Sabit koordinat modu ise sadece 1920x1080 çözünürlükte çalışır.

## Sürüm Notları

### v1.1.0
- Yeni sürüm
- Görüntü tanıma özelliği
- Metin tanıma (OCR) desteği
- Çoklu dil desteği
- 1080p sabit mod

## Katkıda Bulunma

1. Bu repo'yu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: XYZ'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Bir Pull Request oluşturun

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
