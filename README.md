# Shabakah (شبكة)

Interactive network security lab you SSH into to learn by doing.

Shabakah is a single self contained Docker container. You start it, SSH in, and
a guide greets you and walks you through hands on lessons in network security.
Every lesson comes with a real practice target running inside the box, a
challenge, and a checker that verifies your answer live. Nothing here reaches the
outside world, so you can practise scanning, capture, and enumeration safely.

Built and maintained by Ali AlEnezi (SiteQ8). Available in English and Arabic.

## Quick start

With Docker Compose:

```
git clone https://github.com/SiteQ8/Shabakah.git
cd Shabakah
docker compose up -d --build
ssh -p 2222 learner@localhost
```

The default password is `shabakah`. Change it with the `LEARNER_PASSWORD`
environment variable before using this anywhere shared.

Or pull the prebuilt image from the GitHub Container Registry:

```
docker run -d --name shabakah --cap-add NET_ADMIN -p 2222:22 ghcr.io/siteq8/shabakah:latest
ssh -p 2222 learner@localhost
```

`NET_ADMIN` is only needed for the firewall lesson. Everything else works
without it.

## What you get when you log in

The guide opens automatically. From it you can:

- Browse the ten lessons and read them in the terminal.
- Run the suggested commands against the practice targets.
- Check your challenge answer with `netsec check <lesson> <answer>`.
- Switch language between English and Arabic at any time.
- See lab target status and a command cheat sheet.

You can leave the guide and drop to a normal shell. Type `netsec` any time to
reopen it.

## The lessons

1. The network stack and sockets
2. Reading the wire with tcpdump
3. Port scanning with nmap
4. Service enumeration and banners
5. HTTP recon and cleartext exposure
6. DNS reconnaissance
7. TLS and certificates
8. Host firewalling
9. Traffic analysis and spotting attacks
10. Detection and hardening

## The practice targets

All bind to loopback inside the container.

- HTTP on port 8080, a deliberately careless web service for header, banner and
  cleartext analysis.
- HTTPS on port 8443, a TLS service with a self signed certificate to inspect.
- A raw TCP service on port 9000 for banner grabbing and enumeration.
- A small DNS resolver on port 5353 serving a practice zone.

## Tools inside

nmap, tcpdump, ngrep, netcat, socat, curl, dig and the dnsutils family, whois,
ss and the iproute2 family, netstat, ping, traceroute, mtr, openssl, nftables,
iptables, hping3, jq, and the manual pages, all on Debian.

## Safety and scope

This lab exists for learning on systems you own or are authorised to test. Only
scan the local practice targets. The container does not attack anything outside
itself, and you should not point its tools at hosts you do not have permission to
test.

## Build from source

```
docker build -t shabakah:latest .
docker run -d --name shabakah --cap-add NET_ADMIN -p 2222:22 shabakah:latest
```

## Run the smoke test

```
sh tests/smoke.sh
```

## License

MIT. See LICENSE.

---

# شبكة

مختبر تفاعلي لأمن الشبكات تدخل إليه عبر SSH وتتعلمه بالممارسة.

شبكة حاوية Docker واحدة ومكتفية بذاتها، فأنت تشغّلها ثم تدخل عبر SSH فيرحّب بك مرشد ويأخذك عبر دروس عملية في أمن الشبكات، ويأتي كل درس بهدف تدريب حقيقي يعمل داخل الحاوية وتحدٍّ ومدقّق يتحقق من إجابتك حيّا، ولا شيء هنا يصل إلى الخارج لذا تستطيع التدرب على الفحص والالتقاط والتعداد بأمان.

بناه ويعتني به علي العنزي أي SiteQ8، وهو متاح بالإنجليزية والعربية.

## البدء السريع

باستخدام Docker Compose:

```
git clone https://github.com/SiteQ8/Shabakah.git
cd Shabakah
docker compose up -d --build
ssh -p 2222 learner@localhost
```

كلمة المرور الافتراضية هي `shabakah` فغيّرها عبر متغير البيئة `LEARNER_PASSWORD` قبل استخدام هذا في أي مكان مشترك.

أو اسحب الصورة الجاهزة من سجل حاويات GitHub:

```
docker run -d --name shabakah --cap-add NET_ADMIN -p 2222:22 ghcr.io/siteq8/shabakah:latest
ssh -p 2222 learner@localhost
```

الصلاحية `NET_ADMIN` مطلوبة لدرس الجدار الناري فقط وكل ما عداه يعمل بدونها.

## ماذا تجد حين تدخل

يفتح المرشد تلقائيا، ومنه تستطيع:

- تصفح الدروس العشرة وقراءتها في الطرفية.
- تشغيل الأوامر المقترحة على أهداف التدريب.
- التحقق من إجابة تحديك بالأمر `netsec check <رقم الدرس> <الإجابة>`.
- تبديل اللغة بين الإنجليزية والعربية في أي وقت.
- رؤية حالة أهداف المختبر وورقة أوامر سريعة.

وتستطيع مغادرة المرشد والانتقال إلى طرفية عادية، ثم اكتب `netsec` في أي وقت لإعادة فتحه.

## الدروس

1. طبقات الشبكة والمقابس
2. قراءة حركة الشبكة باستخدام tcpdump
3. فحص المنافذ باستخدام nmap
4. تعداد الخدمات والترويسات الافتتاحية
5. استطلاع HTTP وخطر النص الصريح
6. استطلاع نظام أسماء النطاقات
7. بروتوكول TLS والشهادات
8. الجدار الناري على المضيف
9. تحليل الحركة واكتشاف الهجمات
10. الكشف والتحصين

## أهداف التدريب

كلها ترتبط بالاسترجاع داخل الحاوية.

- خدمة HTTP على المنفذ 8080 وهي خدمة ويب مهمِلة عن قصد لتحليل الترويسات واللافتات والنص الصريح.
- خدمة HTTPS على المنفذ 8443 وهي خدمة TLS بشهادة موقّعة ذاتيا لفحصها.
- خدمة TCP خام على المنفذ 9000 لالتقاط اللافتات والتعداد.
- خادم DNS صغير على المنفذ 5353 يخدم نطاقا تدريبيا.

## الأدوات في الداخل

nmap وtcpdump وngrep وnetcat وsocat وcurl وdig وعائلة dnsutils وwhois وss وعائلة iproute2 وnetstat وping وtraceroute وmtr وopenssl وnftables وiptables وhping3 وjq وصفحات الدليل، وكلها على Debian.

## الأمان والنطاق

وُجد هذا المختبر للتعلم على أنظمة تملكها أو مصرّح لك باختبارها، فافحص أهداف التدريب المحلية فقط، فالحاوية لا تهاجم شيئا خارج نفسها وينبغي ألا توجّه أدواتها إلى مضيفين لا تملك إذنا باختبارهم.

## البناء من المصدر

```
docker build -t shabakah:latest .
docker run -d --name shabakah --cap-add NET_ADMIN -p 2222:22 shabakah:latest
```

## تشغيل اختبار التحقق

```
sh tests/smoke.sh
```

## الرخصة

MIT فانظر ملف LICENSE.
