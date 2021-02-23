import cv2   #Görüntüyü işlemek için openCv kütüphanesi eklendi.
import numpy as np   #Görüntü işleme sırasında, dizilerin daha aktif kullanılabilmesi için eklendi.
import math  #Matematiksel bazı işemler için eklendi.
import time  #sleep komutu için eklendi.
import subprocess  #Kod geliştirilmeye çalışılırken eklendi.Başka bir modül import edilmek için kullanılır fakat, kodda şimdilik işlevi bulunmamaktadır. 


def nothing(x): #Trackbar oluşturmak için gerekli fakat görevi olmayan fonksiyon tanımlandı.
    pass

cv2.namedWindow("HSV ayarlama") #Bu kısım pencereyi oluşturuyor çok önemli kızakları eklemek için
cv2.resizeWindow("HSV ayarlama",340,205)
cv2.createTrackbar("Lower_H","HSV ayarlama",0,179,nothing) #Kızak ismi,pencere ismi,başl değeri,bitiş değ, öylesine fonks
cv2.setTrackbarPos("Lower_H","HSV ayarlama",0) #Başlangıç positionu ten rengine göre ayarladık
cv2.createTrackbar("Lower_S","HSV ayarlama",0,255,nothing)
cv2.setTrackbarPos("Lower_S","HSV ayarlama",20) #Başlangıç positionu ten rengine göre ayarladık
cv2.createTrackbar("Lower_V","HSV ayarlama",0,255,nothing)
cv2.setTrackbarPos("Lower_V","HSV ayarlama",70) #Başlangıç positionu ten rengine göre ayarladık
cv2.createTrackbar("Upper_H","HSV ayarlama",0,179,nothing)
cv2.setTrackbarPos("Upper_H","HSV ayarlama",20) #Başlangıç positionu ten rengine göre ayarladık
cv2.createTrackbar("Upper_S","HSV ayarlama",0,255,nothing)
cv2.setTrackbarPos("Upper_S","HSV ayarlama",255) #Başlangıç positionu ten rengine göre ayarladık
cv2.createTrackbar("Upper_V","HSV ayarlama",0,255,nothing)
cv2.setTrackbarPos("Upper_V","HSV ayarlama",255) #Başlangıç positionu ten rengine göre ayarladık



cap = cv2.VideoCapture(0)
#0 görüntü webcamden okunacak demektir.

zaman0 = 0
zaman2 = 0
zaman3 = 0
zaman4 = 0
zaman5 = 0
zaman6 = 0

döngü_ms = 100
songonderilen = ""
font_songonderilen=2


while True:
#Sonsuz döngü içerisinde, 100 ms aralıklarla kameradan Frame alınarak çok hızlı bir şekilde gösterilmektedir.
#Bu şekilde insan gözü bunu video olarak algılamaktadır.
#try catch yapısının kullanılmasının sebebi;
#Frame webcamden çekildği sürece yeşil ile belirlenmiş kesit alanı içinde önceden HSV değeri ayarlanmış rengi
#aranmasıdır. Try kısmında eğer bu rengi yakalarsa, gerekli işlemler yapılır. Catch kısmında, eğer yakalayamazsa sadece
#frame, mask hsv gibi pencereler açık kalmaya devam eder, bir dahaki yakalama beklenir. Bu sonsuz föngü içinde tekrarlanır.
    try:

        _, frame = cap.read() #Kameradan kare(frame) okundu.
        simetri = 1  # y eksenine göre simetri alınacak
        frame = cv2.flip(frame, simetri)

        # Elimizin algılayacağı kesiti oluşturalım, yeşil dikdörtgeni çizelim.
          #            z   k    x   y
        kesit = frame[60:300, 20:360]  # once y, sonra x ekseni
                        #      x   z     y    k
        cv2.rectangle(frame, (20, 60), (360, 300), (0, 255, 0), 1)

        #Artık kameradan alınan görüntünün HSV karşılığını bulma zamanı geldi.
        hsv = cv2.cvtColor(kesit, cv2.COLOR_BGR2HSV)

        #HSV değelerinin, while üzerinde oluşturulan trackbardan alınması sağlanıyor.
        lh = cv2.getTrackbarPos("Lower_H", "HSV ayarlama")
        ls = cv2.getTrackbarPos("Lower_S", "HSV ayarlama")
        lv = cv2.getTrackbarPos("Lower_V", "HSV ayarlama")
        uh = cv2.getTrackbarPos("Upper_H", "HSV ayarlama")
        us = cv2.getTrackbarPos("Upper_S", "HSV ayarlama")
        uv = cv2.getTrackbarPos("Upper_V", "HSV ayarlama")

        lower_ten_rengi = np.array([lh,ls,lv], dtype=np.uint8)
        upper_ten_rengi = np.array([uh,us,uv], dtype=np.uint8)


        # kesitteki alanda elimizi ayıredelim;
        mask = cv2.inRange(hsv, lower_ten_rengi, upper_ten_rengi)
        # Karanlık noktaları beyazlarla dolduralım,karıncalanmalar azaltılmalı bu yüzden beyazlardan oluşan kernel
        # yaratılıyor.(Birlerden oluşturulması beyazlardan oluşması anlamına gelir.)
        kernel = np.ones((4, 4), dtype=np.uint8)
        # kernel 1'lerden oluştuğu için ele denk gelen yerdeki siyah noktaları da beyaz yapacak.
        mask = cv2.dilate(mask, kernel, iterations=5)
        # Oluşturulan kernel, maskeye 5 kere uygulandı.

        # Gaussianblur yerine başka bir blur yöntemi de kullanılabilir.(100 default değer)
        # Bu kısımda önemli olan görüntünün keskinliğinin yumuşatılması ve beyaz alanın daha soft bir yapı alması.
        # (7,7) değeri arttırılarak belki biraz daha blurlu bir görüntü elde edilebilirdi.
        # Not:(7,7) kısmında sadece tek sayılar kullanılabilir yoksa kod hata veriyor.
        mask = cv2.GaussianBlur(mask, (7, 7), 100)

        # Masklanan alanın konturlarını bulalım(Kontur, beyaz alanın çevresindeki çizgilere denk gelir diyebiliriz.)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Bu fonksiyon girdilere bakarak max olan konturun alanını döndürecek.(Konturun içine aldığı alan)
        max_cont = max(contours, key=lambda x: cv2.contourArea(x))

        # Gerçeğe daha yakın konturlar elde etmek için approx kullanıldı.
        # Bu yöntemin kullanılması zorunlu değil, fakat araştırmalar sonucunda kullanılmasının daha faydalı olduğu saptandı.
        # 0.0007 katsayısı değiştirilebilir.(Daha yakın konturlar için, fakat araştırmalara göre genelde 0.0007 tercih)
        approx = cv2.approxPolyDP(max_cont, 0.0007 * cv2.arcLength(max_cont, True), True)

        # Elimizin dışında dış bükey örtü oluşturup "ortu" içinde saklayacağız.
        ortu = cv2.convexHull(max_cont)  # Ortu için gerekli koordinatlar elde edildi
        # 'Ortu'nun tuttuğu koordinatların alanını ve elin alanını hesaplayacağız.
        area_ortu = cv2.contourArea(ortu)  # El üstündeki örtünün alanı
        area_hand = cv2.contourArea(max_cont)  # Elin alanı
        # Boşluğun, el alanına olan oranını bulduk(yüzde olarak)
        bosluk_el_orani = ((area_ortu - area_hand) / area_hand) * 100
        # Bosluk el oranı kodun devamında kullanılmadı, ama işimize yarayabilir.

        # Bu kısımda, konturlara bakılarak kusurlar tespit ediliyor.
        # Yaklaşım yaparak bulduğum elimin kontrularından dış bükey örtü oluşturuyorum.
        hull = cv2.convexHull(approx, returnPoints=False)  # True yazıldığında kontur değerleri, False'ta ise indisler döner.
        #Dış bükey örtü ve elimin konturlarına bakarak kusurları tespit ediyorum.
        kusurlar = cv2.convexityDefects(approx, hull)

        kusur = 0  # Şimdilik 0 olsun, şimdi kusur sayısını hesaplayacağız.

        for i in range(kusurlar.shape[0]):
            #Kusurun tüm koordinatları tek tek gezilerek start,end,far noktaları çizilecek
            s, e, f, d = kusurlar[i, 0]
            start = tuple(approx[s][0]) #Parmağım uç noktası
            end = tuple(approx[e][0])   #Bir ilerideki parmağın uç noktası
            far = tuple(approx[f][0])   #2 parmak arasindaki en uzak noktanın olduğu yer(kusur oluyor)

            #Bu işlemlerin neden yapıldığı raporda detaylı olarak anlatılmıştır. Bulunan 'd' ve 'angle' değerine göre
            #bazı kusurlar elenmektedir. Çünkü elin etrafında, parmakların arasındaki kusurlar dışında, farklı
            #kusurlar da bulunmuştur. Bu ekstra kusurlar sayının anlaşışmasını zorlaştırmaktadır.
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            s = (a + b + c) / 2
            area = math.sqrt(s * (s - a) * (s - b) * (s - c))
            # Noktalar ve dış bükey örtü arası dik mesafe=d
            d = (2 * area) / a

            # cos kuralı
            angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57
            # Açı değeri <= 90 ve d 30'dan büyükse kusur vardır diyebiliriz parmaklar için.
            # Açının max 90 olmasının sebebi; başparm-dirsek ve serçe p-dirsek arasını saymamak için.
            if angle <= 90 and d > 20: #d Sayısı 30'du fakat biraz daha azalttık.
                kusur += 1 #Eğer bu koşullar sağlanıyorsa, kusur +1 yap.
                cv2.circle(kesit, far, 3, [255, 0, 0], -1) # Kusurun yerini daire içine al.

            cv2.line(kesit, start, end, [0, 255, 0], 2) #Konveks Örtü, yeşil çizgi ile elin etrafına çizilir.

        kusur += 1  # 1 kusur, 2 sayısına denk gelir bu yüzden 1 arttırma ihtiyacı duyduk.

        # Eğer 10'dan büyükse fontu yeşil renk olsun, anlamlı sayıya geçiş yaptığı daha rahat görülsün.
        if zaman2 > 10:
            font2 = (0, 255, 0)
        else:
            font2 = (0, 0, 255)

        if zaman3 > 10:
            font3 = (0, 255, 0)
        else:
            font3 = (0, 0, 255)

        if zaman4 > 10:
            font4 = (0, 255, 0)
        else:
            font4 = (0, 0, 255)

        if zaman5 > 10:
            font5 = (0, 255, 0)
        else:
            font5 = (0, 0, 255)

        #"TV ON/OFF" ekrana sığmıyor eğer bu geliyorsa biraz daha küçük fontla yazsın.
        if songonderilen=="TV ON/OFF":
            font_songonderilen=1.2
        else:
            font_songonderilen=2



        if kusur == 1:  # Kusurun 0 olduğu durumlar(Hatırla: kusuru arttırmıştık)
            if area_hand < 2000:  # Elinin tamamının kutuda olmaması durumu, (beyaz alanların 2000'den küçük olması)
                cv2.putText(frame, 'Elinin tamamini kutuya koy!', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2,cv2.LINE_AA)
                # cv2.putText(frame, '0 -> ' + str(zaman0), (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 1,cv2.LINE_AA)
                cv2.putText(frame, '2 -> ' + str(zaman2), (110, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 1,cv2.LINE_AA)
                cv2.putText(frame, '3 -> ' + str(zaman3), (110, 380), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 1,cv2.LINE_AA)
                cv2.putText(frame, '4 -> ' + str(zaman4), (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 1,cv2.LINE_AA)
                cv2.putText(frame, '5 -> ' + str(zaman5), (110, 460), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 1,cv2.LINE_AA)
                # cv2.putText(frame, '6 -> ' + str(zaman6), (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 20, 180), 1,cv2.LINE_AA)
                cv2.putText(frame, 'Son Gonderilen:', (370, 200), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, songonderilen, (370, 250), cv2.FONT_HERSHEY_SIMPLEX, font_songonderilen, (0, 255, 0), 1, cv2.LINE_AA)
            else:
                # El 0 yapılıyor, elin tamamı kutuda-->Reset mi isteniyor, gönder mi isteniyor anla
                tespit = 0
                for kontrol in (zaman0, zaman2, zaman3, zaman4, zaman5, zaman6):
                    if kontrol > 10:  # Güncelleme: Eski 'Hali kontrol > 19' uzun sürüyordu bu sebeple azalttım.
                        tespit += 1
                    else:
                        continue
                # 20'den büyük olan zaman sayisi bulundu tespite koyuldu

                if tespit > 1:  # Demek ki 2 sayi bariz şekilde yapılmış ve tespit edilmiş,o zaman 'gönder'
                    # cv2.putText(frame, '0-->Tespit= '+ str(tespit), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3,cv2.LINE_AA)
                    # Evet 1'den fazla 10 birim zamanı geçen simge var o zaman bunları sayılar ile eşleştirelim

                    zamanlar = [
                        {'Name': 'zaman0', 'deger': int(zaman0)},
                        {'Name': 'zaman2', 'deger': int(zaman2)},
                        {'Name': 'zaman3', 'deger': int(zaman3)},
                        {'Name': 'zaman4', 'deger': int(zaman4)},
                        {'Name': 'zaman5', 'deger': int(zaman5)},
                        {'Name': 'zaman6', 'deger': int(zaman6)},
                    ]


                    def get_deger(zaman):
                        return zaman.get('deger')

                    #zaman değerleri büyükten küçüğe sıralandı.
                    zamanlar.sort(key=get_deger, reverse=True)

                    sirali_liste = []
                    for i in range(0, 5):
                        isim = zamanlar[i].get('Name')
                        sirali_liste.append(isim)
                    #sirali_liste--> büyükten küçüğe siralanmiş string listesi


                    onlar_str = str(sirali_liste[0])
                    birler_str = str(sirali_liste[1])

                    # Stringler gerçek int değerleri ile eşleştirilecek ve 2 basamaklı sayı oluşacak.
                    if onlar_str == "zaman2":
                        onlar = 2
                    if onlar_str == "zaman3":
                        onlar = 3
                    if onlar_str == "zaman4":
                        onlar = 4
                    if onlar_str == "zaman5":
                        onlar = 5

                    if birler_str == "zaman2":
                        birler = 2
                    if birler_str == "zaman3":
                        birler = 3
                    if birler_str == "zaman4":
                        birler = 4
                    if birler_str == "zaman5":
                        birler = 5

                    sayim = onlar * 10 + birler

                    print(str(sayim))
                    #Artık oluşan 2 basamaklı sayıya göre, komutlar belirlenir.
                    if sayim == 23:
                        songonderilen = "Kanal +"
                        print("Kanal +")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "KANAL_ILERI"])
                        #LIRC kütüphanesinden, bu komut ile tv_ELE495 dosyası içindeki KANAL_ILERI sinyali verici devre tarafından TV'ye gönederilir.
                    if sayim == 24:
                        songonderilen = "Kanal -"
                        print("Kanal -")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "KANAL_GERI"])
                    if sayim == 25:
                        songonderilen = "Ses +"
                        print("Ses +")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "SES_ARTTIR"])
                    if sayim == 32:
                        songonderilen = "Ses -"
                        print("Ses -")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "SES_AZALT"])
                    if sayim == 34:
                        songonderilen = "RETURN"
                        print("RETURN(back) ")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "RETURN"])
                    if sayim == 35:
                        songonderilen = "Home"
                        print("Home")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "HOME"])
                    if sayim == 42:
                        songonderilen = "SOURCE"
                        print("Ayarlar Menüsü(SOURCE) ")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "SOURCE"])
                    if sayim == 43:
                        songonderilen = "Netflix"
                        print("Netflix")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "NETFLIX"])
                    if sayim == 45:
                        songonderilen = "Amazon prime"
                        print("Amazon prime")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "AMAZON_PRIME"])
                    if sayim == 52:
                        songonderilen = "Mute"
                        print("Mute")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "MUTE"])
                    if sayim == 53:
                        songonderilen = "Exit"
                        print("Exit")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "EXIT"])
                    if sayim == 54:
                        songonderilen = "TV ON/OFF"
                        print("TV ON/OFF")
                        rtn = subprocess.call(["irsend", "SEND_ONCE", "tv_ELE495", "TV_ON_OFF"])

                    print("songonderilen=" + songonderilen)
                    time.sleep(1)  # Burada sinyali gönderme işlemi için zaman kazanılır. Bunu kaldırınca hata verdi.

                    #Gönderme yapıldı, sayaçlar 0'lansın. Yeni sayı girişi yapılacak.
                    zaman0 = 0
                    zaman2 = 0
                    zaman3 = 0
                    zaman4 = 0
                    zaman5 = 0
                    zaman6 = 0



                else:  # Resetle tespit edilen sayısı 2'den az(Yani 10 birim zamanı en az 2 sayı bile geçememiş.)
                    cv2.putText(frame, '0-->Reset ', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    zaman0 = 0
                    zaman2 = 0
                    zaman3 = 0
                    zaman4 = 0
                    zaman5 = 0
                    zaman6 = 0
                    # cv2.putText(frame, '0 -> ' + str(zaman0), (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 1,cv2.LINE_AA)
                    cv2.putText(frame, '2 -> ' + str(zaman2), (110, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font2, 1,cv2.LINE_AA)
                    cv2.putText(frame, '3 -> ' + str(zaman3), (110, 380), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font3, 1,cv2.LINE_AA)
                    cv2.putText(frame, '4 -> ' + str(zaman4), (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font4, 1,cv2.LINE_AA)
                    cv2.putText(frame, '5 -> ' + str(zaman5), (110, 460), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font5, 1, cv2.LINE_AA)
                    # cv2.putText(frame, '6 -> ' + str(zaman6), (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 20, 180), 1,cv2.LINE_AA)
                    cv2.putText(frame, 'Son Gonderilen:', (370, 200), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 255), 1, cv2.LINE_AA)
                    cv2.putText(frame, songonderilen, (370, 250), cv2.FONT_HERSHEY_SIMPLEX, font_songonderilen, (0, 255, 0), 1,cv2.LINE_AA)
                    # zaman0 += 1

        elif kusur == 2: #El 2 yapılıyor, 2'nin sayacı arttır.
            # cv2.putText(frame, '0 -> ' + str(zaman0), (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 1,cv2.LINE_AA)
            cv2.putText(frame, '2 -> ' + str(zaman2), (110, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font2, 1, cv2.LINE_AA)
            cv2.putText(frame, '3 -> ' + str(zaman3), (110, 380), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font3, 1, cv2.LINE_AA)
            cv2.putText(frame, '4 -> ' + str(zaman4), (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font4, 1, cv2.LINE_AA)
            cv2.putText(frame, '5 -> ' + str(zaman5), (110, 460), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font5, 1, cv2.LINE_AA)
            # cv2.putText(frame, '6 -> ' + str(zaman6), (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 20, 180), 1,cv2.LINE_AA)
            cv2.putText(frame, 'Son Gonderilen:', (370, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),1, cv2.LINE_AA)
            cv2.putText(frame, songonderilen, (370, 250), cv2.FONT_HERSHEY_SIMPLEX, font_songonderilen, (0, 255, 0),1, cv2.LINE_AA)
            zaman2 += 1

        elif kusur == 3: #El 3 yapılıyor, 3'ün sayacı arttır.
            # cv2.putText(frame, '0 -> ' + str(zaman0), (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 1,cv2.LINE_AA)
            cv2.putText(frame, '2 -> ' + str(zaman2), (110, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font2, 1, cv2.LINE_AA)
            cv2.putText(frame, '3 -> ' + str(zaman3), (110, 380), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font3, 1, cv2.LINE_AA)
            cv2.putText(frame, '4 -> ' + str(zaman4), (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font4, 1, cv2.LINE_AA)
            cv2.putText(frame, '5 -> ' + str(zaman5), (110, 460), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font5, 1, cv2.LINE_AA)
            # cv2.putText(frame, '6 -> ' + str(zaman6), (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 20, 180), 1,cv2.LINE_AA)
            cv2.putText(frame, 'Son Gonderilen:', (370, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),1, cv2.LINE_AA)
            cv2.putText(frame, songonderilen, (370, 250), cv2.FONT_HERSHEY_SIMPLEX, font_songonderilen, (0, 255, 0),1, cv2.LINE_AA)
            zaman3 += 1

        elif kusur == 4: #El 4 yapılıyor, 4'ün sayacı arttır.
            # cv2.putText(frame, '0 -> ' + str(zaman0), (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 1,cv2.LINE_AA)
            cv2.putText(frame, '2 -> ' + str(zaman2), (110, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font2, 1, cv2.LINE_AA)
            cv2.putText(frame, '3 -> ' + str(zaman3), (110, 380), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font3, 1, cv2.LINE_AA)
            cv2.putText(frame, '4 -> ' + str(zaman4), (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font4, 1, cv2.LINE_AA)
            cv2.putText(frame, '5 -> ' + str(zaman5), (110, 460), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font5, 1, cv2.LINE_AA)
            # cv2.putText(frame, '6 -> ' + str(zaman6), (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 20, 180), 1,cv2.LINE_AA)
            cv2.putText(frame, 'Son Gonderilen:', (370, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),1, cv2.LINE_AA)
            cv2.putText(frame, songonderilen, (370, 250), cv2.FONT_HERSHEY_SIMPLEX, font_songonderilen, (0, 255, 0),1, cv2.LINE_AA)
            zaman4 += 1

        elif kusur == 5: #El 5 yapılıyor, 5'in sayacı arttır.
            # cv2.putText(frame, '0 -> ' + str(zaman0), (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 1,cv2.LINE_AA)
            cv2.putText(frame, '2 -> ' + str(zaman2), (110, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font2, 1, cv2.LINE_AA)
            cv2.putText(frame, '3 -> ' + str(zaman3), (110, 380), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font3, 1, cv2.LINE_AA)
            cv2.putText(frame, '4 -> ' + str(zaman4), (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font4, 1, cv2.LINE_AA)
            cv2.putText(frame, '5 -> ' + str(zaman5), (110, 460), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font5, 1, cv2.LINE_AA)
            # cv2.putText(frame, '6 -> ' + str(zaman6), (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 20, 180), 1,cv2.LINE_AA)
            cv2.putText(frame, 'Son Gonderilen:', (370, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),1, cv2.LINE_AA)
            cv2.putText(frame, songonderilen, (370, 250), cv2.FONT_HERSHEY_SIMPLEX, font_songonderilen, (0, 255, 0),1, cv2.LINE_AA)
            zaman5 += 1


        else: #El 0,1,2,3,4,5 'ten farklı bir şey yapılıyor. İşime yarayacak bir şey yok, yine de sayaç5 saysın.(Önlem)
            # cv2.putText(frame, '0 -> ' + str(zaman0), (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 1,cv2.LINE_AA)
            cv2.putText(frame, '2 -> ' + str(zaman2), (110, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font2, 1, cv2.LINE_AA)
            cv2.putText(frame, '3 -> ' + str(zaman3), (110, 380), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font3, 1, cv2.LINE_AA)
            cv2.putText(frame, '4 -> ' + str(zaman4), (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font4, 1, cv2.LINE_AA)
            cv2.putText(frame, '5 -> ' + str(zaman5), (110, 460), cv2.FONT_HERSHEY_SIMPLEX, 1.2, font5, 1, cv2.LINE_AA)
            # cv2.putText(frame, '6 -> ' + str(zaman6), (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 20, 180), 1,cv2.LINE_AA)
            cv2.putText(frame, 'Son Gonderilen:', (370, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),1, cv2.LINE_AA)
            cv2.putText(frame, songonderilen, (370, 250), cv2.FONT_HERSHEY_SIMPLEX, font_songonderilen, (0, 255, 0),1, cv2.LINE_AA)
            zaman5 += 1  # Ocak 17 ile 'zaman6 += 1' komutu güncellendi,
            # Çünkü bazen 5 yaparken, ışıktan dolayı fazladan bir nokta
            # algılanabiliyor. Bu durumda da elin 5 yapıldığı varsayılıyor.

        cv2.imshow('mask', mask)
        cv2.imshow('frame', frame)

    # Hiçbir beyazlık yakalayamazsan sadece ekrandakileri göstermeye devam et.
    except:
        cv2.putText(frame, 'Elinin tamamini kutuya koy!', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,cv2.LINE_AA)
        # cv2.putText(frame, '0 -> ' + str(zaman0), (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 1,cv2.LINE_AA)
        cv2.putText(frame, '2 -> ' + str(zaman2), (110, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 1,cv2.LINE_AA)
        cv2.putText(frame, '3 -> ' + str(zaman3), (110, 380), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 1,cv2.LINE_AA)
        cv2.putText(frame, '4 -> ' + str(zaman4), (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 1,cv2.LINE_AA)
        cv2.putText(frame, '5 -> ' + str(zaman5), (110, 460), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 1,cv2.LINE_AA)
        # cv2.putText(frame, '6 -> ' + str(zaman6), (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 20, 180), 1,cv2.LINE_AA)
        cv2.putText(frame, 'Son Gonderilen:', (370, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, songonderilen, (370, 250), cv2.FONT_HERSHEY_SIMPLEX, font_songonderilen, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.imshow('frame', frame)
        pass

    #'q' ya basılarak video görünütüsü alma işi artık durdurulabilir. Basılmışsa sonsuz döngüden çıkılır.
    if cv2.waitKey(döngü_ms) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
cap.release()