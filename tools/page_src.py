#!/usr/bin/env python3
"""Writes docs/index.html from the copy below.

The page keeps the markers that tools/build_site.py fills in (lesson list,
counts, Arabic number agreement), so run build_site.py after this script.
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "index.html")

# Ports of the lab, what runs there, which lessons touch it, which flags hide there.
PORTS = [
    {"port": "8080", "proto": "tcp", "lessons": ["02", "03", "04", "05", "12", "16", "17"],
     "flags": ["recon", "html", "backup"],
     "en": ("Cleartext web", "An HTTP service with a telling banner, hidden paths, and a page it should never expose."),
     "ar": ("ويب بنص صريح", "خدمة HTTP بلافتة تفضح نفسها، ومسارات مخفية، وصفحة ما كان ينبغي أن تظهر أبدا.")},
    {"port": "8443", "proto": "tcp", "lessons": ["02", "03", "07", "16", "17"],
     "flags": ["cert"],
     "en": ("TLS web", "The same service over TLS, with a self signed certificate to inspect and reason about."),
     "ar": ("ويب عبر TLS", "الخدمة نفسها لكن عبر TLS، بشهادة موقّعة ذاتيا تفحصها وتحلّل محتواها.")},
    {"port": "9000", "proto": "tcp", "lessons": ["03", "04", "09", "17"],
     "flags": ["debug"],
     "en": ("Enumeration service", "A raw TCP service with a chatty banner and an undocumented command to uncover."),
     "ar": ("خدمة تعداد", "خدمة TCP بسيطة بلافتة ثرثارة، وفيها أمر غير موثّق عليك أن تكتشفه.")},
    {"port": "2323", "proto": "tcp", "lessons": ["03", "12", "17"],
     "flags": ["reuse"],
     "en": ("Cleartext console", "A forgotten admin console that reuses a password, the kind that turns one leak into three."),
     "ar": ("وحدة تحكم بنص صريح", "وحدة تحكّم إدارية منسيّة تُعيد استخدام كلمة مرور، من النوع الذي يحوّل تسريبا واحدا إلى ثلاثة أبواب مفتوحة.")},
    {"port": "5353", "proto": "udp", "lessons": ["06"],
     "flags": [],
     "en": ("Lab DNS resolver", "An offline resolver for the shabakah.lab zone, with A, MX, and TXT records to query."),
     "ar": ("خادم DNS للمختبر", "خادم أسماء محلّي لنطاق shabakah.lab، فيه سجلات A وMX وTXT تستعلم عنها.")},
    {"port": "9001", "proto": "udp", "lessons": ["09", "11"],
     "flags": [],
     "en": ("UDP banner service", "A UDP service that stays silent until you speak its protocol, which is the point."),
     "ar": ("خدمة لافتة UDP", "خدمة UDP تلزم الصمت حتى تخاطبها باللغة التي تفهمها، وذلك هو التحدي.")},
]

FLAGS = {
    "recon":  (10, "8080", "Recon rookie", "The web service has a page it should not. A first curl finds it.",
               "مستكشف مبتدئ", "خدمة الويب تُخفي صفحة ما كان ينبغي أن تظهر، يكشفها أول طلب بـ curl."),
    "html":   (10, "8080", "Source reader", "The home page hides a note in its HTML source, not in the text you see.",
               "قارئ المصدر", "الصفحة الرئيسة تُخفي ملاحظة في مصدر HTML لا في النص الذي أمامك."),
    "backup": (20, "8080", "Left the door open", "robots.txt points at paths that were never meant to be public. One holds a config backup.",
               "باب مفتوح", "يدلّك ملف robots.txt على مسارات ما كان يُفترض أن تُنشر، وفي أحدها نسخة احتياطية من ملف الإعداد."),
    "debug":  (20, "9000", "Undocumented", "A service answers more commands than it admits to. Enumeration finds the one it hides.",
               "غير موثّق", "إحدى الخدمات تنفّذ أوامر أكثر مما تُعلن عنه، والتعداد الجيّد يكشف الأمر الخفيّ."),
    "reuse":  (30, "2323", "One leak, three doors", "A cleartext console reuses a password you already saw cross the wire.",
               "تسريب واحد وثلاثة أبواب", "وحدة تحكّم بنص صريح تستخدم كلمة مرور سبق أن رأيتها تمرّ على الشبكة."),
    "cert":   (20, "8443", "Hidden in plain sight", "The TLS certificate carries a field it never should. Read the whole subject.",
               "مخبأ على مرأى", "شهادة TLS تحمل حقلا زائدا ما كان ينبغي وجوده، فاقرأ حقل الموضوع كاملا."),
}
FLAG_ORDER = ["recon", "html", "backup", "debug", "reuse", "cert"]


def ar_points(n):
    return "%d %s" % (n, "نقاط" if 3 <= n <= 10 else "نقطة")


def e(s):
    return html.escape(s, quote=False)


def port_map(lang):
    ar = lang == "ar"
    sfx = "-ar" if ar else ""
    t = {
        "you": "جهازك" if ar else "Your computer",
        "wire": "SSH عبر المنفذ 22" if ar else "SSH on port 22",
        "box": "مختبر شبكة" if ar else "Shabakah lab",
        "guide": "ومعه المرشد netsec" if ar else "with the netsec guide",
        "ports": "خدمات التدريب" if ar else "Practice services",
        "lessons": "الدروس التي تستخدمه" if ar else "Lessons that use it",
        "flags": "التحديات المخبأة فيه" if ar else "Flags hidden here",
        "none": "لا تحدي هنا، لكن الدروس تعتمد عليه" if ar else "No flag here, but lessons depend on it",
        "cap": ("اختر منفذا لترى الخدمة التي تعمل خلفه، والدروس التي تستخدمه، والتحدي المخبأ فيه."
                if ar else "Pick a port to see the service behind it, the lessons that use it, and the flag hidden there."),
    }
    out = []
    out.append('<figure class="map" data-map>')
    out.append('  <div class="map-row">')
    out.append('    <div class="node-you"><svg viewBox="0 0 48 36" aria-hidden="true"><rect x="7" y="3" width="34" height="23" rx="3"/><path d="M2 31h44"/></svg>'
               '<b>%s</b><code>ssh -p 2222</code></div>' % t["you"])
    out.append('    <div class="wire" aria-hidden="true"><span>%s</span><i class="packet"></i></div>' % t["wire"])
    out.append('    <div class="box">')
    out.append('      <div class="box-head"><b>%s</b><span>%s</span></div>' % (t["box"], t["guide"]))
    out.append('      <div class="ports" role="tablist" aria-label="%s">' % t["ports"])
    for i, p in enumerate(PORTS):
        out.append('        <button type="button" class="port" role="tab" id="t%s-%s" aria-controls="p%s-%s" aria-selected="%s" style="--i:%d">'
                   '<i class="led"></i><span class="pn">%s</span><span class="pp">%s</span><span class="pname">%s</span></button>'
                   % (sfx, p["port"], sfx, p["port"], "true" if i == 0 else "false", i, p["port"], p["proto"], e(p[lang][0])))
    out.append('      </div>')
    for i, p in enumerate(PORTS):
        name, desc = p[lang]
        lessons = "".join('<a href="#l%s-%s">%s</a>' % (sfx, lid, lid) for lid in p["lessons"])
        if p["flags"]:
            items = []
            for fid in p["flags"]:
                pts, _, ten, _, tar, _ = FLAGS[fid]
                items.append("<li>%s<span>%s</span></li>" % (e(tar if ar else ten), ar_points(pts) if ar else "%d pt" % pts))
            flags = "<ul>%s</ul>" % "".join(items)
        else:
            flags = '<p class="muted">%s</p>' % t["none"]
        out.append('      <div class="pdetail" role="tabpanel" id="p%s-%s" aria-labelledby="t%s-%s">'
                   '<h3>%s <code>%s %s</code></h3><p>%s</p>'
                   '<div class="pmeta"><div><h4>%s</h4><div class="lchips">%s</div></div><div><h4>%s</h4>%s</div></div></div>'
                   % (sfx, p["port"], sfx, p["port"], e(name), p["proto"], p["port"], e(desc),
                      t["lessons"], lessons, t["flags"], flags))
    out.append('    </div>')
    out.append('  </div>')
    out.append('  <figcaption>%s</figcaption>' % t["cap"])
    out.append('</figure>')
    return "\n".join(out)


def scoreboard(lang):
    ar = lang == "ar"
    head = ("<tr><th>التحدي</th><th>أين تبحث</th><th>النقاط</th></tr>" if ar
            else "<tr><th>Flag</th><th>Where to look</th><th>Points</th></tr>")
    rows = []
    for fid in FLAG_ORDER:
        pts, port, ten, den, tar, dar = FLAGS[fid]
        rows.append('<tr><td><b>%s</b><span>%s</span></td><td><code>%s</code></td><td class="num">%s</td></tr>'
                    % (e(tar if ar else ten), e(dar if ar else den), port, ar_points(pts) if ar else str(pts)))
    total = ('<tr class="total"><td colspan="2">المجموع، ومعه شارة الأستاذ</td><td class="num"><!--ar:point:points-->110 نقاط<!--/ar--></td></tr>'
             if ar else
             '<tr class="total"><td colspan="2">Total, and the master badge with it</td><td class="num"><!--n:points-->110<!--/n--></td></tr>')
    return '<table class="board"><thead>%s</thead><tbody>%s%s</tbody></table>' % (head, "".join(rows), total)


TOOLS = "nmap tcpdump ngrep openssl dig whois netcat socat curl wget hping3 nftables iptables mtr traceroute".split()

CMDS = {
    "en": [("netsec", "open the interactive guide"), ("netsec next", "jump to your next lesson"),
           ("netsec lesson 05", "read one lesson"), ("netsec check 05 &lt;answer&gt;", "check a challenge answer"),
           ("netsec ctf", "show the flag board"), ("netsec submit flag{...}", "submit a flag you found"),
           ("netsec targets", "see which services are up"), ("netsec cert", "print your certificate when you finish"),
           ("netsec lang ar", "switch to Arabic")],
    "ar": [("netsec", "افتح المرشد التفاعلي"), ("netsec next", "انتقل إلى درسك التالي"),
           ("netsec lesson 05", "اقرأ درسا محدّدا"), ("netsec check 05 &lt;answer&gt;", "تحقّق من حلّ تمرين"),
           ("netsec ctf", "اعرض لوحة التحديات"), ("netsec submit flag{...}", "سلّم رمزا كشفته"),
           ("netsec targets", "اعرض حالة الخدمات"), ("netsec cert", "اطبع شهادتك حين تُنهي"),
           ("netsec lang en", "بدّل إلى الإنجليزية")],
}


def tools_block(lang):
    ar = lang == "ar"
    chips = "".join("<li>%s</li>" % t for t in TOOLS)
    cmds = "".join("<tr><td><code>%s</code></td><td>%s</td></tr>" % c for c in CMDS[lang])
    return ('<div class="tools"><div><h3>%s</h3><ul class="toollist">%s</ul></div>'
            '<div><h3>%s</h3><table class="cmds">%s</table></div></div>'
            % ("داخل المختبر" if ar else "Inside the lab", chips,
               "تحكّم بها عبر netsec" if ar else "Drive it with netsec", cmds))


EN = {
    "h1": "A network security lab you SSH into.",
    "lead": ("Shabakah runs on your own machine as one isolated Docker image. You start it, you SSH in, and a bilingual guide "
             "walks you through <!--n:lessons-->17<!--/n--> hands on lessons against real services running inside it. "
             "Every challenge is checked live, so you learn by doing, not by reading."),
    "cta1": "Get started", "cta2": "Source on GitHub",
    "facts": [("<!--n:lessons-->17<!--/n-->", "hands on lessons"), ("<!--n:targets-->6<!--/n-->", "practice services"),
              ("<!--n:flags-->6<!--/n-->", "hidden flags"), ("<!--n:points-->110<!--/n-->", "points to win"), ("2", "languages")],
}

AR = {
    "h1": "مختبر لأمن الشبكات في&nbsp;جهازك!",
    "lead": ("شبكة مختبرٌ متكامل لأمن الشبكات يعمل في بيئة Docker معزولة على جهازك وحده، تشغّله وتدخل إليه عبر SSH "
             "فيستقبلك مرشد بالعربية والإنجليزية ويسير بك في <!--ar:lesson_applied:lessons-->17 درسا تطبيقيا<!--/ar--> "
             "على خدمات حقيقية تعمل داخله، ويصحّح لك كل تمرين لحظة تنفيذه فتتعلّم بيدك لا بعينك."),
    "cta1": "ابدأ الآن", "cta2": "المصدر على GitHub",
    "facts": [("<!--n:lessons-->17<!--/n-->", "<!--arnoun:lesson_applied:lessons-->درسا تطبيقيا<!--/arnoun-->"),
              ("<!--n:targets-->6<!--/n-->", "<!--arnoun:service_train:targets-->خدمات للتدريب<!--/arnoun-->"),
              ("<!--n:flags-->6<!--/n-->", "<!--arnoun:code_hidden:flags-->تحديات مخفية<!--/arnoun-->"),
              ("<!--n:points-->110<!--/n-->", "<!--arnoun:point:points-->نقاط<!--/arnoun-->"), ("2", "لغتان")],
}


def main_block(lang):
    ar = lang == "ar"
    c = AR if ar else EN
    s = "-ar" if ar else ""
    facts = "".join('<div><b>%s</b><span>%s</span></div>' % f for f in c["facts"])
    if ar:
        steps = [("شغّل المختبر", "نزّل الصورة الجاهزة أو ابنها بنفسك ثم شغّلها، فهي تعمل أينما توفّر Docker.", "docker compose up -d --build"),
                 ("ادخل عبر SSH", "ادخل بحساب المتعلّم فيستقبلك المرشد من حيث توقّفت آخر مرة.", "ssh -p 2222 learner@localhost"),
                 ("تعلّم بالتجربة", "اقرأ الدرس ثم جرّب الأدوات على خدمات التدريب، ودع المرشد يصحّح إجابتك.", "netsec check 03 2323,8080,8443,9000")]
    else:
        steps = [("Run the lab", "Pull the image or build it, then bring it up. It runs anywhere Docker runs.", "docker compose up -d --build"),
                 ("SSH in", "Log in as the learner. The guide greets you and remembers where you left off.", "ssh -p 2222 learner@localhost"),
                 ("Learn by doing", "Read a lesson, run the tools on the live services, then let the guide check your answer.", "netsec check 03 2323,8080,8443,9000")]
    steps_html = "".join('<li><h3>%s</h3><p>%s</p><pre>%s</pre></li>' % st for st in steps)

    if ar:
        features = [
            ("مرشد يصحّح إجابتك", "برنامج netsec هو معلّمك داخل الطرفية، يعرض لك هدف كل درس وتمرينه ثم يتأكد من حلّك باختباره مباشرة على الخدمات العاملة، فيُحفظ تقدّمك مع كل إجابة صحيحة ويبقى معك بين الجلسات."),
            ("معزول وآمن", "كل الخدمات محبوسة داخل البيئة المعزولة ولا تستقبل إلا اتصالات من داخلها، فتستخدم الأدوات الهجومية بحرّية دون أن تؤذي أحدا، وهذه هي الطريقة الصحيحة لإتقانها."),
            ("أدوات حقيقية", "تجد nmap وtcpdump وopenssl وdig وnetcat وhping3 وغيرها جاهزة للعمل، وهي الأدوات ذاتها التي يعتمدها المحترفون في الميدان."),
            ("عربية وإنجليزية", "كل درس وتمرين وتلميح متوفّر باللغتين، تنتقل بينهما وقتما تشاء دون أن تفقد تقدّمك."),
            ("شارات وشهادة", "سبع شارات تكسبها تباعا مع كل درس تُنهيه وكل رمز تكشفه، ثم شهادة إتمام تطبعها حين تُنهي الدروس والتحديات كلها."),
            ("من الاستطلاع إلى التحصين", "تمرّ على التقاط الحزم وفحص المنافذ وتعداد الخدمات، وHTTP وTLS وDNS وUDP، ثم قراءة السجلات وتحصين SSH، فتخرج بجولة أولى شاملة في أمن الشبكات."),
        ]
    else:
        features = [
            ("A guide that checks your work", "The netsec program is your instructor in the terminal. It shows the objective and the challenge, then verifies your answer against the running services in real time. Right answers stick between sessions."),
            ("Safe by design", "Every practice service listens only inside the lab and runs without privileges. You practise the aggressive tools with no risk to anyone, which is the honest way to learn them."),
            ("Real tools", "nmap, tcpdump, openssl, dig, netcat, hping3 and more are installed. The same tools you use on the job."),
            ("English and Arabic", "Every lesson, prompt, and hint is written in both languages. Switch any time and your progress follows."),
            ("Badges and a certificate", "Seven badges unlock as you clear lessons and capture flags, and a certificate prints once you finish everything."),
            ("The whole surface", "Packet capture, port scanning, service enumeration, HTTP, TLS, DNS, UDP, log reading and SSH hardening. A full first pass over network security."),
        ]
    feats = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % f for f in features)

    shots = [("menu", "المرشد", "The guide"), ("lesson", "درس", "A lesson"), ("ctf", "التحديات", "Flags"),
             ("achievements", "الإنجازات", "Achievements"), ("targets", "الخدمات", "Services"), ("cheat", "الأوامر السريعة", "Cheat sheet")]
    tabs = "".join('<button type="button" role="tab" aria-selected="%s" data-shot="%s">%s</button>'
                   % ("true" if i == 0 else "false", k, a if ar else en) for i, (k, a, en) in enumerate(shots))

    T = (lambda a, b: a) if ar else (lambda a, b: b)
    faq = [
        (T("هل تشغيله خطر على جهازي؟", "Is any of this dangerous to run?"),
         T("لا، فكل شيء محبوس داخل البيئة المعزولة ولا شيء يخرج إلى شبكتك، فتشغّل nmap وtcpdump وhping3 بأقوى صورها دون أن تُلحق ضررا بأحد، ولهذا فالمختبر المعزول هو المكان الصحيح لتعلّم هذه الأدوات.",
           "No. Every practice service listens only inside the lab and nothing reaches the outside world. You get to run nmap, tcpdump, and hping3 the aggressive way with no risk to anyone.")),
        (T("هل أحتاج إلى خبرة بسطر الأوامر مسبقا؟", "Do I need to know the command line already?"),
         T("تكفي معرفة بسيطة بالطرفية، فالمرشد يعرض لك الأوامر الدقيقة في كل درس، وورقة الأوامر السريعة على بُعد ضغطة، والتكرار كفيل بترسيخ المهارة.",
           "A little comfort with a terminal helps, but the guide shows the exact commands for each lesson and the cheat sheet is one keypress away.")),
        (T("هل يحتاج إلى اتصال بالإنترنت؟", "Does it need an internet connection?"),
         T("يحتاجه مرة واحدة فقط لتنزيل الصورة أو بنائها، ثم يعمل كل شيء بعد ذلك دون إنترنت، حتى خادم الأسماء الخاص بالمختبر.",
           "Only to pull or build the image the first time. After that everything runs offline, including the lab DNS resolver.")),
        (T("هل يصلح لتدريس صف أو تنظيم ورشة؟", "Can I use it to teach a class or run a workshop?"),
         T("نعم، فهو مفتوح المصدر برخصة MIT وبلغتين، ويكفي كل متعلّم أن يشغّل نسخته الخاصة، فتقدّم كل واحد ونقاطه مستقلّة عن غيره.",
           "Yes. It is MIT licensed and bilingual, and each learner runs their own copy, so progress and flags stay per learner.")),
        (T("أين أُبلّغ عن مشكلة أو أقترح درسا جديدا؟", "Where do I report a problem or suggest a lesson?"),
         T("افتح مسألة (Issue) في مستودع المشروع على GitHub، ونرحّب بكل مساهمة بدروس أو خدمات جديدة.",
           "Open an issue on the GitHub repository. New lessons and services are welcome.")),
    ]
    faq_html = "".join("<details><summary>%s</summary><p>%s</p></details>" % q for q in faq)

    parts = []
    parts.append('<main lang="%s" dir="%s"%s>' % (lang, "rtl" if ar else "ltr", " hidden" if ar else ""))
    parts.append('''
<section class="hero"><div class="wrap hero-grid">
  <div class="hero-copy">
    <h1>%s</h1>
    <p class="lead">%s</p>
    <div class="cta"><a class="btn btn-primary" href="#start%s">%s</a><a class="btn btn-quiet" href="https://github.com/SiteQ8/Shabakah">%s</a></div>
  </div>
  %s
</div>
<div class="wrap"><div class="plate">%s</div></div>
</section>''' % (c["h1"], c["lead"], s, c["cta1"], c["cta2"], port_map(lang), facts))

    parts.append('''
<section id="how%s"><div class="wrap">
  <h2>%s</h2>
  <p class="lead">%s</p>
  <ol class="steps">%s</ol>
</div></section>''' % (s, T("ثلاثة أوامر وتدخل المختبر.", "Three commands and you are inside."),
                       T("لا إعدادات معقّدة ولا خوادم سحابية بمقابل، فكل شيء يعمل داخل بيئة معزولة على جهازك وحده.",
                         "No lab to wire up, no cloud to pay for, nothing that reaches the outside world."), steps_html))

    parts.append('''
<section class="tint" id="screens%s"><div class="wrap">
  <h2>%s</h2>
  <p class="lead">%s</p>
  <div class="shots">
    <div class="shot-tabs" role="tablist">%s</div>
    <div class="shot-stage"><img src="screenshots/%smenu.png" width="1564" height="1100" alt="%s"></div>
    <p class="shot-cap">%s</p>
  </div>
</div></section>''' % (s, T("شاهد المرشد قبل أن تبدأ.", "See the guide before you start."),
                       T("لقطات حقيقية من المرشد كما ستظهر في طرفيتك تماما.", "Real screens from the guide, straight out of the terminal."),
                       tabs, "ar/" if ar else "", T("مرشد شبكة كما يظهر بعد تسجيل الدخول", "The Shabakah guide as seen after logging in"),
                       T("يستقبلك المرشد فور دخولك ويتذكّر أين وصلت.", "The guide greets you when you SSH in and remembers your progress.")))

    parts.append('''
<section id="lessons%s"><div class="wrap split">
  <div class="split-head">
    <h2>%s</h2>
    <p class="lead">%s</p>
  </div>
  <div class="lessons"><!--lessons:%s-->
    <!--/lessons-->
  </div>
</div></section>''' % (s, T("<!--ar:lesson:lessons-->17 درسا<!--/ar-->، ولكل درس تمرين يُختبر مباشرة.",
                             "<!--n:lessons-->17<!--/n--> lessons, each with a live challenge."),
                       T("ينتهي كل درس بتطبيق عملي على خدمات التدريب يتحقق منه المرشد بنفسه، والدروس مرتّبة من التقاط الحزم إلى التحصين.",
                         "Every lesson ends with something to prove on the running services, checked by the guide. They run in order, from reading packets to hardening the door you came in through."),
                       lang))

    parts.append('''
<section class="tint" id="ctf%s"><div class="wrap split">
  <div class="split-head">
    <h2>%s</h2>
    <p class="lead">%s</p>
  </div>
  <div>%s</div>
</div></section>''' % (s, T("ابحث عن <!--ar:code:flags-->6 رموز سرية<!--/ar--> واجمع <!--ar:point:points-->110 نقاط<!--/ar-->.",
                             "<!--n:flags-->6<!--/n--> flags, <!--n:points-->110<!--/n--> points."),
                       T("التقاط الأعلام أسلوب تدريب معروف في الأمن السيبراني، خبّأنا فيه رموزا سرية داخل المختبر في أماكن يتركها فيها مشرف مهمل، فتكشف كل رمز بأدواتك ثم تسلّمه بالأمر <code>netsec submit flag{...}</code> لتكسب نقاطه، ويأخذك الدرس الثاني عشر في السلسلة كلها خطوة بخطوة.",
                         "Each flag sits where a careless operator would leave it, and each is reachable with a tool you already have. Find one, then run <code>netsec submit flag{...}</code>. Lesson 12 walks the whole chain."),
                       scoreboard(lang)))

    parts.append('''
<section id="features%s"><div class="wrap split">
  <div class="split-head">
    <h2>%s</h2>
    <p class="lead">%s</p>
  </div>
  <dl class="feats">%s</dl>
</div></section>''' % (s, T("أكثر من دروس تقرؤها.", "More than a set of notes."),
                       T("مرشد يعلّمك، وخدمات حقيقية تتدرّب عليها، وتحديات تتنافس فيها، كلها في مكان واحد.",
                         "A guide, live services, and a game, in one image so nothing gets in your way."), feats))

    parts.append('''
<section class="tint" id="tools%s"><div class="wrap">
  <h2>%s</h2>
  <p class="lead">%s</p>
  %s
</div></section>''' % (s, T("الأدوات جاهزة من البداية.", "The tools are already installed."),
                       T("لن تحتاج إلى تثبيت أي شيء أثناء الدرس، فالمختبر يأتي بعُدّة أمن شبكات كاملة ومعها المرشد الذي يوجّهك.",
                         "Nothing to install mid lesson. The lab ships with a working network security kit and the guide to drive it."),
                       tools_block(lang)))

    qa = "qs-ar" if ar else "qs-en"
    parts.append('''
<section id="start%s"><div class="wrap split">
  <div class="split-head">
    <h2>%s</h2>
    <p class="lead">%s</p>
  </div>
  <div class="starts">
    <h3>%s</h3>
    <div class="copywrap"><button type="button" class="copybtn" data-copy="%s">%s</button><pre id="%s">git clone https://github.com/SiteQ8/Shabakah.git
cd Shabakah
docker compose up -d --build
ssh -p 2222 learner@localhost</pre></div>
    <h3>%s</h3>
    <div class="copywrap"><button type="button" class="copybtn" data-copy="%s2">%s</button><pre id="%s2">docker run -d --name shabakah --cap-add NET_ADMIN -p 2222:22 ghcr.io/siteq8/shabakah:latest
ssh -p 2222 learner@localhost</pre></div>
    <p class="muted">%s</p>
  </div>
</div></section>''' % (s, T("جاهز في دقيقة.", "Up and running in a minute."),
                       T("كل ما تحتاجه هو Docker، والباقي موجود داخل الصورة.", "You need Docker. Everything else is in the image."),
                       T("من المصدر", "From source"), qa, T("نسخ", "Copy"), qa,
                       T("أو بالصورة الجاهزة من سجل GitHub", "Or with the prebuilt image"), qa, T("نسخ", "Copy"), qa,
                       T("كلمة المرور محدّدة في docker-compose.yml، وقيمتها الافتراضية shabakah.",
                         "The password is set in docker-compose.yml. The default is shabakah.")))

    parts.append('''
<section class="tint" id="faq%s"><div class="wrap split">
  <div class="split-head"><h2>%s</h2></div>
  <div class="faq">%s</div>
</div></section>''' % (s, T("أسئلة شائعة.", "Good to know."), faq_html))

    parts.append('''
<footer><div class="wrap foot">
  <span>%s</span>
  <a href="https://github.com/SiteQ8/Shabakah">github.com/SiteQ8/Shabakah</a>
</div></footer>
</main>''' % T("من تطوير علي العنزي، ومفتوح المصدر برخصة MIT.", "Built by Ali AlEnezi. Open source under the MIT license."))
    return "\n".join(parts)


def build():
    old = open(OUT, encoding="utf-8").read()
    head = old.split("<style>", 1)[0]
    head = head.replace('<meta name="theme-color" content="#0A0E1A">', '<meta name="theme-color" content="#EEF2F8">')
    head = re.sub(r'<link href="https://fonts.googleapis.com/css2\?[^"]*" rel="stylesheet">',
                  '<link href="https://fonts.googleapis.com/css2?family=Readex+Pro:wght@300..700&display=swap" rel="stylesheet">', head)
    head = re.sub(r'<link rel="icon"[^>]*>', '<link rel="icon" href="favicon.svg" type="image/svg+xml">', head)
    css = open(os.path.join(ROOT, "tools", "page.css"), encoding="utf-8").read()
    js = open(os.path.join(ROOT, "tools", "page.js"), encoding="utf-8").read()
    header = '''<header><div class="wrap bar">
  <a class="brand" href="#" aria-label="Shabakah">
    <svg viewBox="0 0 32 32" aria-hidden="true"><path d="M6 24 16 8 26 24Z"/><circle cx="6" cy="24" r="3.4"/><circle cx="16" cy="8" r="3.4"/><circle cx="26" cy="24" r="3.4"/></svg>
    <b>Shabakah</b><span lang="ar">شبكة</span>
  </a>
  <nav>
    <a class="navlink" href="#lessons" data-nav="lessons" data-en="Lessons" data-ar="الدروس">Lessons</a>
    <a class="navlink" href="#ctf" data-nav="ctf" data-en="Flags" data-ar="التحديات">Flags</a>
    <a class="navlink" href="#screens" data-nav="screens" data-en="Screens" data-ar="معاينة">Screens</a>
    <a class="navlink" href="#start" data-nav="start" data-en="Get started" data-ar="ابدأ">Get started</a>
    <div class="lang" role="group" aria-label="Language"><button type="button" data-lang="en" aria-pressed="true">EN</button><button type="button" data-lang="ar" aria-pressed="false">عربي</button></div>
  </nav>
</div></header>'''
    page = (head + "<style>\n" + css + "</style>\n<script>document.documentElement.classList.add('js');</script>\n</head>\n<body>\n"
            + header + "\n\n" + main_block("en") + "\n\n" + main_block("ar") + "\n\n<script>\n" + js + "</script>\n</body>\n</html>\n")
    open(OUT, "w", encoding="utf-8").write(page)


if __name__ == "__main__":
    build()
    print("wrote", OUT)
