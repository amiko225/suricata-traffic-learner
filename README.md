# Co to jest?
Skrypt uczący się reguł pass.rules, na podstawie podanych argumentów.

-  Na początku pobiera istniejące reguły z pliku pass.rules
-  Kolejno pobiera argumenty o zakresach IP
-  Na ich podstawie tworzy reguły typu alert, które zapisuje w learn.rules
-  Przeładowuje reguły bez konieczności restartowania całej usługi suricaty
-  Alerty spowodowane regułami z learn.rules lądują w folderze /var/log/suricata/learn_alerts.json
-  Skrypt interwałami po 60 sekund zbiera powiadomienia o alertach do kolejki z powyższego pliku
>  Jeśli jakieś znajdzie to:
-  Parsuje je i tworzy na ich podstawie nowe reguły, które dopisuje do pass.rules
-  Następnie przeładowuje reguły suricaty, które można uznać za wyuczone

# Ważne informacje

-  zakres uczących się adresów IP edytuje się w (**suricata/main.py**)
-  logi będą pojawiać się obok katalogu suricata ("**/logs**")
-  feature autostartu uruchamia się (sudo systemctl **enable suricata_traffic_learner.service**), a wyłącza poprzez (sudo systemctl **disable suricata_traffic_learner.service**)
-  obsługiwane przez Suricate pliki reguł: (**pre.rules, pass.rules, learn.rules, alert.rules**)
-  należy upewnić się, czy w pliku konfiguracyjnym Suricaty są odpowiednio dostrojone opcje: (**outputs:**), (**default-rule**) oraz (**af-packet:**)
-  na hoście z Wazuh Managerem znajduje się plik konfiguracyjny reguł **suricata_rules.xml**, są tam dopisane dwie reguły parsujące alerty uczące, oraz alerty z customową formułką msg
-  plik usługi systemd jest pod ścieżką: (**/etc/systemd/system/suricata_traffic_learner.service**)
-  należy pamiętać o tym by dostosować zawartość pliku usługi systemd pod nasze wymagania
-  skrypt upewnia się by nie tworzyć duplikatów
-  skrypt pamięta wyuczone reguły, co zmniejsza ilość cykli procesora

# Wymagania 

-  Python 3.9+

# Uruchomienie programu

Upewnij się czy istnieje i czy jest zaktualizowany:
-  python --version
-  python3 --version

Następnie:

-  sudo python3 /ścieżka/main.py

>  Albo: 

-  sudo systemctl daemon-reload
-  sudo systemctl start/restart suricata_traffic_learner.service


Żeby zakończyć:

-  sudo systemctl stop suricata_traffic_learner.service

