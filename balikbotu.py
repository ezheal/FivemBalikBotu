import cv2
import numpy as np
import pyautogui
import time
from PIL import ImageGrab

def color_change_detector():
    print("Düşük eşikli renk değişimi tespit sistemi başlatılıyor...")
    print("Programı durdurmak için 'q' tuşuna basın.")
    print("Referans görüntüyü güncellemek için 'r' tuşuna basın.")
    print("Hassasiyeti azaltmak için '-' tuşuna, artırmak için '+' tuşuna basın.")
    print("Algılama eşiğini artırmak için 'a' tuşuna, azaltmak için 'z' tuşuna basın.")
    
    # Ekran genişliği ve yüksekliği
    screen_width, screen_height = pyautogui.size()
    
    # Tarama bölgesi - 350x250 piksel (genişlik x yükseklik)
    width = 450
    height = 150
    
    center_x = screen_width // 2
    center_y = screen_height // 2
    
    region_x = center_x - (width // 2)
    region_y = center_y - (height // 2)
    
    search_region = (region_x, region_y, region_x + width, region_y + height)
    print(f"Tarama bölgesi: Ekranın ortasında {width}x{height} piksellik alan")
    
    # Çok düşük değişim algılama eşiği
    change_threshold = 50  # Piksel değerlerindeki değişim (0-255 arası)
    pixel_percent_threshold = 1.0  # Değişen piksellerin yüzdesi - %1
    
    # Tuş basma ayarları
    last_press_time = 0
    press_cooldown = 0.4  # saniye
    
    # Kararlılık için algılama sayacı
    consecutive_frames = 0  # Arka arkaya değişim tespit edilen kare sayısı
    required_detections = 3  # Tuşa basmak için arka arkaya kaç algılama gerekli
    
    # Referans kare oluştur (başlangıç için)
    print("Referans görüntü alınıyor...")
    ref_screenshot = ImageGrab.grab(bbox=search_region)
    reference_frame = np.array(ref_screenshot)
    reference_frame_bgr = cv2.cvtColor(reference_frame, cv2.COLOR_RGB2BGR)
    
    # Başlangıç gecikmesi
    print("Sistem hazır. Renk değişimi izleniyor...")
    time.sleep(1)
    
    try:
        while True:
            loop_start = time.time()
            
            # Ekran görüntüsü al
            screenshot = ImageGrab.grab(bbox=search_region)
            current_frame = np.array(screenshot)
            
            # RGB'den BGR'ye dönüştür (OpenCV için)
            current_frame_bgr = cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR)
            
            # Orijinal görüntü üzerinde çalışmak için bir kopya oluştur
            display_frame = current_frame_bgr.copy()
            
            # İki kare arasındaki farkı hesapla
            frame_diff = cv2.absdiff(reference_frame_bgr, current_frame_bgr)
            
            # Gürültü azaltma için blur uygula
            frame_diff = cv2.GaussianBlur(frame_diff, (5, 5), 0)
            
            # Farkı gri tonlamaya dönüştür
            gray_diff = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2GRAY)
            
            # Eşikleme işlemi - belirli bir değerden büyük farkları belirle
            _, thresh_diff = cv2.threshold(gray_diff, change_threshold, 255, cv2.THRESH_BINARY)
            
            # Küçük gürültüleri temizle
            kernel = np.ones((7, 7), np.uint8)
            thresh_diff = cv2.morphologyEx(thresh_diff, cv2.MORPH_OPEN, kernel)
            
            # Değişen piksel yüzdesi hesapla
            change_pixel_count = cv2.countNonZero(thresh_diff)
            total_pixels = thresh_diff.shape[0] * thresh_diff.shape[1]
            change_percentage = (change_pixel_count / total_pixels) * 100
            
            # Değişim maskesini görsel hale getir
            change_visual = cv2.cvtColor(thresh_diff, cv2.COLOR_GRAY2BGR)
            
            # Vurgulu fark görüntüsü oluştur
            change_highlight = cv2.bitwise_and(current_frame_bgr, current_frame_bgr, mask=thresh_diff)
            
            # Değişim algılandı mı?
            is_change_detected = change_percentage > pixel_percent_threshold
            
            # Ardışık kare sayacını güncelle
            if is_change_detected:
                consecutive_frames += 1
            else:
                consecutive_frames = 0
            
            # Kararlı değişim algılaması - yeterli sayıda ardışık kare değişiklik gösteriyor mu?
            stable_change_detected = consecutive_frames >= required_detections
            
            # Ekrana bilgi yazdır
            cv2.putText(display_frame, f"Degisen piksel: {change_percentage:.2f}%", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.putText(display_frame, f"Piksel esigi: {change_threshold}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                        
            cv2.putText(display_frame, f"Yuzde esigi: {pixel_percent_threshold:.1f}%", (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Ardışık kare bilgisi
            cv2.putText(display_frame, f"Ardisik kareler: {consecutive_frames}/{required_detections}", (10, 120), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Durum bilgisi
            if stable_change_detected:
                state_text = "KARARLI DEGISIM ALGILANDI!"
                state_color = (0, 0, 255)  # Kırmızı
            elif is_change_detected:
                state_text = "Onaylaniyor..."
                state_color = (0, 165, 255)  # Turuncu
            else:
                state_text = "Bekleniyor..."
                state_color = (0, 255, 0)  # Yeşil
                
            cv2.putText(display_frame, state_text, (10, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color, 2)
            
            # Görsel monitörü oluştur
            top_row = np.hstack((display_frame, change_visual))
            bottom_row = np.hstack((change_highlight, reference_frame_bgr))
            
            # Görüntüleri birleştir
            monitor_view = np.vstack((top_row, bottom_row))
            
            # Görüntüyü yeniden boyutlandır
            scale_percent = 70
            width_display = int(monitor_view.shape[1] * scale_percent / 100)
            height_display = int(monitor_view.shape[0] * scale_percent / 100)
            resized_view = cv2.resize(monitor_view, (width_display, height_display))
            
            # Görüntüyü göster
            cv2.imshow('Renk Degisimi Algilayici', resized_view)
            
            # Değişim algılama ve tuşa basma mantığı
            current_time = time.time()
            if stable_change_detected and (current_time - last_press_time) > press_cooldown:
                # E tuşuna bas!
                print("\nKararlı renk değişimi algılandı! 'e' tuşuna basılıyor...")
                pyautogui.press('e')
                
                # Referans kareyi güncelle
                reference_frame_bgr = current_frame_bgr.copy()
                
                # Zaman ve sayaç güncelleme
                last_press_time = current_time
                consecutive_frames = 0
            
            # Tuş basma kontrolleri
            key = cv2.waitKey(1) & 0xFF
            
            # 'q' tuşuna basılırsa çık
            if key == ord('q'):
                break
            
            # 'r' tuşuna basılırsa referans kareyi güncelle
            elif key == ord('r'):
                print("\nReferans kare güncellendi!")
                reference_frame_bgr = current_frame_bgr.copy()
                consecutive_frames = 0
            
            # '-' tuşuna basılırsa hassasiyeti azalt
            elif key == ord('-'):
                change_threshold = min(change_threshold + 5, 255)
                print(f"\nHassasiyet azaltıldı: Piksel eşiği = {change_threshold}")
            
            # '+' tuşuna basılırsa hassasiyeti artır
            elif key == ord('+') or key == ord('='):
                change_threshold = max(change_threshold - 5, 10)
                print(f"\nHassasiyet artırıldı: Piksel eşiği = {change_threshold}")
            
            # 'a' tuşuna basılırsa ardışık kare eşiğini artır
            elif key == ord('a'):
                required_detections = min(required_detections + 1, 10)
                print(f"\nArdışık kare sayısı artırıldı: {required_detections}")
            
            # 'z' tuşuna basılırsa ardışık kare eşiğini azalt
            elif key == ord('z'):
                required_detections = max(required_detections - 1, 1)
                print(f"\nArdışık kare sayısı azaltıldı: {required_detections}")
            
            # Döngü hızını düzenle
            loop_time = time.time() - loop_start
            if loop_time < 0.01:
                time.sleep(0.01 - loop_time)
    
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\nHata oluştu: {e}")
    finally:
        # Tüm pencereleri kapat
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Başlangıç gecikmesi
    print("Program 2 saniye içinde başlayacak...")
    print("Lütfen oyun ekranına dönün...")
    time.sleep(2)
    
    # Görsel değişim tespit sistemini başlat
    color_change_detector()