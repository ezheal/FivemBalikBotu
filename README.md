# Renk Değişimi Algılayıcı

Bu program, ekranın belirli bir bölgesindeki renk değişimlerini algılayarak otomatik olarak 'e' tuşuna basar. Oyunlarda veya benzeri uygulamalardaki zamanlamalı olaylarda kullanılabilir.

## Gereksinimler

Programı çalıştırmak için aşağıdaki kütüphaneleri kurmanız gerekir:
pip install opencv-python numpy pyautogui pillow

## Kullanım

1. Programı çalıştırın: `python color_change_detector.py`
2. Program otomatik olarak ekranın ortasındaki alanı taramaya başlayacaktır
3. Renk değişimi algılandığında otomatik olarak 'e' tuşuna basılacaktır

## Kontroller

- 'q': Programdan çıkar
- 'r': Referans kareyi günceller
- '+/-': Hassasiyeti artırır/azaltır
- 'a/z': Ardışık kare sayısını artırır/azaltır
