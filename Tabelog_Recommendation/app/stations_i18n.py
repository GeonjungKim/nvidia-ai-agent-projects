"""역명 ko/en 라벨 v3 (2026-07-08, 3-리뷰어 유니온 기준 재생성). 키=원문.
ko: 국립국어원 가나-한글 대조표 결정론 변환 + 기존 수동검증 오버라이드 전량 보존.
en: 헵번 로마자 + 표지판 관행 장음 축약. 신규 자동 변환분은 stations_review.csv로 검수."""

STATION_LABELS = {
 "六本木": {
  "ko": "롯폰기",
  "en": "Roppongi"
 },
 "銀座": {
  "ko": "긴자",
  "en": "Ginza"
 },
 "赤坂": {
  "ko": "아카사카",
  "en": "Akasaka"
 },
 "新橋": {
  "ko": "신바시",
  "en": "Shimbashi"
 },
 "代官山": {
  "ko": "다이칸야마",
  "en": "Daikanyama"
 },
 "乃木坂": {
  "ko": "노기자카",
  "en": "Nogizaka"
 },
 "内幸町": {
  "ko": "우치사이와이초",
  "en": "Uchisaiwaicho"
 },
 "渋谷": {
  "ko": "시부야",
  "en": "Shibuya"
 },
 "麻布十番": {
  "ko": "아자부주반",
  "en": "Azabujuban"
 },
 "恵比寿": {
  "ko": "에비스",
  "en": "Ebisu"
 },
 "新宿西口": {
  "ko": "신주쿠니시구치",
  "en": "Shinjukunishiguchi"
 },
 "東銀座": {
  "ko": "히가시긴자",
  "en": "Higashiginza"
 },
 "櫛田神社前": {
  "ko": "구시다진자마에",
  "en": "Kushida-jinja-mae"
 },
 "有楽町": {
  "ko": "유라쿠초",
  "en": "Yurakucho"
 },
 "池袋": {
  "ko": "이케부쿠로",
  "en": "Ikebukuro"
 },
 "神泉": {
  "ko": "신센",
  "en": "Shinsen"
 },
 "西武新宿": {
  "ko": "세이부신주쿠",
  "en": "Seibushinjuku"
 },
 "六本木一丁目": {
  "ko": "롯폰기잇초메",
  "en": "Roppongiitchome"
 },
 "田町": {
  "ko": "다마치",
  "en": "Tamachi"
 },
 "西鉄福岡（天神）": {
  "ko": "니시테쓰후쿠오카(덴진)",
  "en": "Nishitetsu-Fukuoka (Tenjin)"
 },
 "三田": {
  "ko": "미타",
  "en": "Mita"
 },
 "新宿三丁目": {
  "ko": "신주쿠산초메",
  "en": "Shinjukusanchome"
 },
 "神保町": {
  "ko": "진보초",
  "en": "Jinbocho"
 },
 "中目黒": {
  "ko": "나카메구로",
  "en": "Naka-meguro"
 },
 "広尾": {
  "ko": "히로오",
  "en": "Hiro"
 },
 "中洲川端": {
  "ko": "나카스카와바타",
  "en": "Nakasukawabata"
 },
 "新御茶ノ水": {
  "ko": "신오차노미즈",
  "en": "Shinochanomizu"
 },
 "浅草（つくばＥＸＰ）": {
  "ko": "아사쿠사쓰쿠바",
  "en": "Asakusa(Tsukubaexp)"
 },
 "祇園": {
  "ko": "기온",
  "en": "Gion"
 },
 "淡路町": {
  "ko": "아와지초",
  "en": "Awajicho"
 },
 "九段下": {
  "ko": "구단시타",
  "en": "Kudanshita"
 },
 "水道橋": {
  "ko": "스이도바시",
  "en": "Suidobashi"
 },
 "東京": {
  "ko": "도쿄",
  "en": "Tokyo"
 },
 "表参道": {
  "ko": "오모테산도",
  "en": "Omotesando"
 },
 "浅草（東武・都営・メトロ）": {
  "ko": "아사쿠사토부토에이메토로",
  "en": "Asakusa(Tobu・Toei・Metoro)"
 },
 "小川町": {
  "ko": "오가와초",
  "en": "Ogawacho"
 },
 "日本橋": {
  "ko": "니혼바시",
  "en": "Nihombashi"
 },
 "天神南": {
  "ko": "덴진미나미",
  "en": "Tenjinminami"
 },
 "田原町": {
  "ko": "다와라마치",
  "en": "Tawaramachi"
 },
 "赤羽橋": {
  "ko": "아카바네하시",
  "en": "Akabanehashi"
 },
 "京橋": {
  "ko": "교바시",
  "en": "Kyobashi"
 },
 "明治神宮前": {
  "ko": "메이지진구마에",
  "en": "Meiji-jingumae"
 },
 "赤坂見附": {
  "ko": "아카사카미쓰케",
  "en": "Akasakamitsuke"
 },
 "東池袋": {
  "ko": "히가시이케부쿠로",
  "en": "Higashiikebukuro"
 },
 "博多": {
  "ko": "하카타",
  "en": "Hakata"
 },
 "四谷三丁目": {
  "ko": "요쓰야산초메",
  "en": "Yotsuyasanchome"
 },
 "蒲田": {
  "ko": "가마타",
  "en": "Kamata"
 },
 "大崎広小路": {
  "ko": "오사키히로코지",
  "en": "Osakihirokoji"
 },
 "五反田": {
  "ko": "고탄다",
  "en": "Gotanda"
 },
 "京急蒲田": {
  "ko": "게이큐카마타",
  "en": "Keikyu Kamata"
 },
 "飯田橋": {
  "ko": "이다바시",
  "en": "Iidabashi"
 },
 "三越前": {
  "ko": "미쓰코시마에",
  "en": "Mitsukoshimae"
 },
 "日比谷": {
  "ko": "히비야",
  "en": "Hibiya"
 },
 "蓮沼": {
  "ko": "하스누마",
  "en": "Hasunuma"
 },
 "築地": {
  "ko": "쓰키지",
  "en": "Tsukiji"
 },
 "上野広小路": {
  "ko": "우에노히로코지",
  "en": "Uenohirokoji"
 },
 "錦糸町": {
  "ko": "긴시초",
  "en": "Kinshicho"
 },
 "上野御徒町": {
  "ko": "우에노오카치마치",
  "en": "Uenokachimachi"
 },
 "新富町": {
  "ko": "신토미마치",
  "en": "Shintomimachi"
 },
 "牛込神楽坂": {
  "ko": "우시고메카구라자카",
  "en": "Ushigomekagurazaka"
 },
 "人形町": {
  "ko": "닌교초",
  "en": "Ningyocho"
 },
 "秋葉原": {
  "ko": "아키하바라",
  "en": "Akihabara"
 },
 "虎ノ門": {
  "ko": "도라노몬",
  "en": "Toranomon"
 },
 "薬院大通": {
  "ko": "야쿠인오도오리",
  "en": "Yakuinodori"
 },
 "不動前": {
  "ko": "후도마에",
  "en": "Fudomae"
 },
 "二重橋前": {
  "ko": "니주바시마에",
  "en": "Nijubashimae"
 },
 "浜松町": {
  "ko": "하마마쓰초",
  "en": "Hamamatsucho"
 },
 "水天宮前": {
  "ko": "스이텐구우마에",
  "en": "Suitengumae"
 },
 "新宿御苑前": {
  "ko": "신주쿠교엔마에",
  "en": "Shinjukugyoenmae"
 },
 "大門": {
  "ko": "다이몬",
  "en": "Daimon"
 },
 "目黒": {
  "ko": "메구로",
  "en": "Meguro"
 },
 "要町": {
  "ko": "가나메초",
  "en": "Kanamecho"
 },
 "呉服町": {
  "ko": "고후쿠초",
  "en": "Gofukucho"
 },
 "岩本町": {
  "ko": "이와모토마치",
  "en": "Iwamotomachi"
 },
 "中野": {
  "ko": "나카노",
  "en": "Nakano"
 },
 "曙橋": {
  "ko": "아케보노바시",
  "en": "Akebonobashi"
 },
 "虎ノ門ヒルズ": {
  "ko": "도라노몬히루즈",
  "en": "Toranomonhiruzu"
 },
 "西早稲田": {
  "ko": "니시와세다",
  "en": "Nishiwaseda"
 },
 "祐天寺": {
  "ko": "유텐지",
  "en": "Yutenji"
 },
 "高田馬場": {
  "ko": "다카다노바바",
  "en": "Takadanobaba"
 },
 "麹町": {
  "ko": "고지마치",
  "en": "Kojimachi"
 },
 "吉祥寺": {
  "ko": "기치조지",
  "en": "Kichijoji"
 },
 "四ツ谷": {
  "ko": "요쓰야",
  "en": "Yotsuya"
 },
 "高円寺": {
  "ko": "고엔지",
  "en": "Koenji"
 },
 "外苑前": {
  "ko": "가이엔마에",
  "en": "Gaienmae"
 },
 "白金高輪": {
  "ko": "시로가네타카나와",
  "en": "Shiroganetakanawa"
 },
 "立川": {
  "ko": "다치카와",
  "en": "Tachikawa"
 },
 "新大久保": {
  "ko": "신오쿠보",
  "en": "Shin'Okubo"
 },
 "三軒茶屋": {
  "ko": "산겐자야",
  "en": "Sangen-jaya"
 },
 "北品川": {
  "ko": "기타시나가와",
  "en": "Kitashinagawa"
 },
 "新高円寺": {
  "ko": "니이타카엔테라",
  "en": "Niitakaentera"
 },
 "面影橋": {
  "ko": "오모카게하시",
  "en": "Omokagehashi"
 },
 "井の頭公園": {
  "ko": "이노카시라코엔",
  "en": "Inokashira-koen"
 },
 "立川南": {
  "ko": "다치카와미나미",
  "en": "Tachikawaminami"
 },
 "茅場町": {
  "ko": "가야바초",
  "en": "Kayabacho"
 },
 "京王八王子": {
  "ko": "게이오하치오지",
  "en": "Keiohachioji"
 },
 "荻窪": {
  "ko": "오기쿠보",
  "en": "Ogikubo"
 },
 "八王子": {
  "ko": "하치오지",
  "en": "Hachioji"
 },
 "白金台": {
  "ko": "시로가네다이",
  "en": "Shiroganedai"
 },
 "八丁堀": {
  "ko": "핫초보리",
  "en": "Hatchobori"
 },
 "菊川": {
  "ko": "기쿠가와",
  "en": "Kikugawa"
 },
 "品川": {
  "ko": "시나가와",
  "en": "Shinagawa"
 },
 "亀戸": {
  "ko": "가메이도",
  "en": "Kameido"
 },
 "大久保": {
  "ko": "오쿠보",
  "en": "Okubo"
 },
 "浅草橋": {
  "ko": "아사쿠사바시",
  "en": "Asakusabashi"
 },
 "代々木上原": {
  "ko": "요요기우에하라",
  "en": "Yoyogiuehara"
 },
 "西太子堂": {
  "ko": "니시타이시도",
  "en": "Nishitaishido"
 },
 "原宿": {
  "ko": "하라주쿠",
  "en": "Harajuku"
 },
 "南新宿": {
  "ko": "미나미신주쿠",
  "en": "Minamishinjuku"
 },
 "下北沢": {
  "ko": "시모키타자와",
  "en": "Shimokitazawa"
 },
 "代々木": {
  "ko": "요요기",
  "en": "Yoyogi"
 },
 "阿佐ケ谷": {
  "ko": "아사케타니",
  "en": "Asaketani"
 },
 "大崎": {
  "ko": "오사키",
  "en": "Osaki"
 },
 "新井薬師前": {
  "ko": "아라이쿠스리시마에",
  "en": "Araikusurishimae"
 },
 "幡ケ谷": {
  "ko": "하타케타니",
  "en": "Hataketani"
 },
 "神谷町": {
  "ko": "가미야초",
  "en": "Kamiyacho"
 },
 "南阿佐ケ谷": {
  "ko": "미나미아사케타니",
  "en": "Minamiasaketani"
 },
 "武蔵小山": {
  "ko": "무사시코야마",
  "en": "Musashikoyama"
 },
 "入谷": {
  "ko": "이리야",
  "en": "Iriya"
 },
 "代々木公園": {
  "ko": "요요기코엔",
  "en": "Yoyogikoen"
 },
 "本郷三丁目": {
  "ko": "혼고산초메",
  "en": "Hongosanchome"
 },
 "学芸大学": {
  "ko": "가쿠게이다이가쿠",
  "en": "Gakugeidaigaku"
 },
 "池尻大橋": {
  "ko": "이케지리오하시",
  "en": "Ikejiriohashi"
 },
 "平和通": {
  "ko": "헤이와토오리",
  "en": "Heiwatori"
 },
 "春日": {
  "ko": "가스가",
  "en": "Kasuga"
 },
 "旦過": {
  "ko": "단카",
  "en": "Tanka"
 },
 "池ノ上": {
  "ko": "이케노에",
  "en": "Ikenoe"
 },
 "木場": {
  "ko": "기바",
  "en": "Kiba"
 },
 "町田": {
  "ko": "마치다",
  "en": "Machida"
 },
 "福岡空港": {
  "ko": "후쿠오카쿠우코",
  "en": "Fukuokakuko"
 },
 "桜台": {
  "ko": "사쿠라다이",
  "en": "Sakuradai"
 },
 "赤羽岩淵": {
  "ko": "아카바네이와부치",
  "en": "Akabaneiwabuchi"
 },
 "半蔵門": {
  "ko": "한조몬",
  "en": "Hanzomon"
 },
 "練馬": {
  "ko": "네리마",
  "en": "Nerima"
 },
 "亀戸水神": {
  "ko": "가메이도스이진",
  "en": "Kameidosuijin"
 },
 "北千住": {
  "ko": "기타센주",
  "en": "Kita-senju"
 },
 "赤羽": {
  "ko": "아카바네",
  "en": "Akabane"
 },
 "稲荷町": {
  "ko": "이나리초",
  "en": "Inaricho"
 },
 "駒込": {
  "ko": "고마고메",
  "en": "Komagome"
 },
 "代々木八幡": {
  "ko": "요요기하치만",
  "en": "Yoyogihachiman"
 },
 "青山一丁目": {
  "ko": "아오야마잇초메",
  "en": "Aoyamaitchome"
 },
 "日暮里": {
  "ko": "닛포리",
  "en": "Nippori"
 },
 "大森海岸": {
  "ko": "오모리카이간",
  "en": "Omorikaigan"
 },
 "大森": {
  "ko": "오모리",
  "en": "Omori"
 },
 "小倉": {
  "ko": "오구라",
  "en": "Ogura"
 },
 "初台": {
  "ko": "쇼다이",
  "en": "Shodai"
 },
 "西小山": {
  "ko": "니시오야마",
  "en": "Nishioyama"
 },
 "早稲田（都電）": {
  "ko": "와세다토덴",
  "en": "Waseda(Toden)"
 },
 "東比恵": {
  "ko": "히가시히메구미",
  "en": "Higashihimegumi"
 },
 "西荻窪": {
  "ko": "니시오기쿠보",
  "en": "Nishiogikubo"
 },
 "三鷹": {
  "ko": "미타카",
  "en": "Mitaka"
 },
 "市ケ谷": {
  "ko": "이치가야",
  "en": "Ichigaya"
 },
 "鮫洲": {
  "ko": "사메즈",
  "en": "Samezu"
 },
 "笹塚": {
  "ko": "사사즈카",
  "en": "Sasazuka"
 },
 "門前仲町": {
  "ko": "몬젠나카마치",
  "en": "Monzennakamachi"
 },
 "市役所前": {
  "ko": "시야쿠쇼마에",
  "en": "Shiyakushomae"
 },
 "千駄木": {
  "ko": "센다기",
  "en": "Sendagi"
 },
 "桜坂": {
  "ko": "사쿠라자카",
  "en": "Sakurazaka"
 },
 "大井町": {
  "ko": "오이초",
  "en": "Oicho"
 },
 "亀有": {
  "ko": "가메아리",
  "en": "Kameari"
 },
 "関内": {
  "ko": "세키우치",
  "en": "Sekiuchi"
 },
 "馬車道": {
  "ko": "바샤미치",
  "en": "Bashamichi"
 },
 "蔵前": {
  "ko": "구라마에",
  "en": "Kuramae"
 },
 "国分寺": {
  "ko": "고쿠분지",
  "en": "Kokubunji"
 },
 "自由が丘": {
  "ko": "지유가오카",
  "en": "Jiyugaoka"
 },
 "駒場東大前": {
  "ko": "고마바토다이마에",
  "en": "Komabatodaimae"
 },
 "巣鴨": {
  "ko": "스가모",
  "en": "Sugamo"
 },
 "豊島園": {
  "ko": "도요시마소노",
  "en": "Toyoshimasono"
 },
 "下板橋": {
  "ko": "시타이타하시",
  "en": "Shitaitahashi"
 },
 "北新地": {
  "ko": "기타신치",
  "en": "Kitashinchi"
 },
 "大塚駅前": {
  "ko": "오쓰카에키마에",
  "en": "Otsukaekimae"
 },
 "西日暮里": {
  "ko": "니시닛포리",
  "en": "Nishinippori"
 },
 "奥沢": {
  "ko": "오쿠사와",
  "en": "Okusawa"
 },
 "芦花公園": {
  "ko": "로카코엔",
  "en": "Rokakoen"
 },
 "秋田": {
  "ko": "아키타",
  "en": "Akita"
 },
 "箱崎": {
  "ko": "하코자키",
  "en": "Hakozaki"
 },
 "椎名町": {
  "ko": "시이나마치",
  "en": "Shiinamachi"
 },
 "鶯谷": {
  "ko": "우구이스다니",
  "en": "Uguisudani"
 },
 "東十条": {
  "ko": "히가시주조",
  "en": "Higashijujo"
 },
 "江古田": {
  "ko": "에코다",
  "en": "Ekoda"
 },
 "祇園四条": {
  "ko": "기온시조",
  "en": "Gionshijo"
 },
 "新桜台": {
  "ko": "신사쿠라다이",
  "en": "Shinsakuradai"
 },
 "大塚": {
  "ko": "오쓰카",
  "en": "Otsuka"
 },
 "大山": {
  "ko": "오야마",
  "en": "Oyama"
 },
 "十条": {
  "ko": "주조",
  "en": "Jujo"
 },
 "牛田": {
  "ko": "우시타",
  "en": "Ushita"
 },
 "中野坂上": {
  "ko": "나카노사카우에",
  "en": "Nakanosakaue"
 },
 "中野新橋": {
  "ko": "나카노신바시",
  "en": "Nakanoshinbashi"
 },
 "千代県庁口": {
  "ko": "지요켄초쿠치",
  "en": "Chiyokenchokuchi"
 },
 "駒沢大学": {
  "ko": "고마자와다이가쿠",
  "en": "Komazawadaigaku"
 },
 "日ノ出町": {
  "ko": "니치노데마치",
  "en": "Nichinodemachi"
 },
 "天満": {
  "ko": "덴마",
  "en": "Tenma"
 },
 "西新": {
  "ko": "니시신",
  "en": "Nishishin"
 },
 "目白": {
  "ko": "메지로",
  "en": "Mejiro"
 },
 "箱崎宮前": {
  "ko": "하코자키미야마에",
  "en": "Hakozakimiyamae"
 },
 "板橋区役所前": {
  "ko": "이타바시쿠야쿠쇼마에",
  "en": "Itabashikuyakushomae"
 },
 "別府": {
  "ko": "벳푸",
  "en": "Beppu"
 },
 "大橋": {
  "ko": "오하시",
  "en": "Ohashi"
 },
 "松本": {
  "ko": "마쓰모토",
  "en": "Matsumoto"
 },
 "沼袋": {
  "ko": "누마부쿠로",
  "en": "Numabukuro"
 },
 "東梅田": {
  "ko": "히가시우메다",
  "en": "Higashiumeda"
 },
 "小岩": {
  "ko": "고이와",
  "en": "Koiwa"
 },
 "白山": {
  "ko": "하쿠산",
  "en": "Hakusan"
 },
 "新飯塚": {
  "ko": "신이이즈카",
  "en": "Shiniizuka"
 },
 "新代田": {
  "ko": "신시로타",
  "en": "Shinshirota"
 },
 "石川町": {
  "ko": "이시카와초",
  "en": "Ishikawacho"
 },
 "天神橋筋六丁目": {
  "ko": "덴진바시스지로쿠초메",
  "en": "Tenjinbashisujirokuchome"
 },
 "なんば（大阪メトロ）": {
  "ko": "난바오사카메토로",
  "en": "Nanba(Osakametoro)"
 },
 "七隈": {
  "ko": "나나쿠마",
  "en": "Nanakuma"
 },
 "勝どき": {
  "ko": "가치도키",
  "en": "Kachidoki"
 },
 "東中野": {
  "ko": "히가시나카노",
  "en": "Higashinakano"
 },
 "東京テレポート": {
  "ko": "도쿄테레포토",
  "en": "Tokyoterepoto"
 },
 "西鉄久留米": {
  "ko": "니시테쓰쿠루메",
  "en": "Nishitetsukurume"
 },
 "八幡山": {
  "ko": "야하타야마",
  "en": "Yahatayama"
 },
 "新小岩": {
  "ko": "신코이와",
  "en": "Shinkoiwa"
 },
 "六本松": {
  "ko": "롯폰마쓰",
  "en": "Ropponmatsu"
 },
 "長野（長野電鉄）": {
  "ko": "나가노나가노덴테쓰",
  "en": "Nagano(Naganodentetsu)"
 },
 "武蔵小金井": {
  "ko": "무사시코가네이",
  "en": "Musashikoganei"
 },
 "経堂": {
  "ko": "교도",
  "en": "Kyodo"
 },
 "山下": {
  "ko": "야마시타",
  "en": "Yamashita"
 },
 "落合": {
  "ko": "오치아이",
  "en": "Ochiai"
 },
 "台場": {
  "ko": "다이바",
  "en": "Daiba"
 },
 "桜木町": {
  "ko": "사쿠라기초",
  "en": "Sakuragicho"
 },
 "北松本": {
  "ko": "기타마쓰혼",
  "en": "Kitamatsuhon"
 },
 "藤崎": {
  "ko": "후지사키",
  "en": "Fujisaki"
 },
 "横浜": {
  "ko": "요코하마",
  "en": "Yokohama"
 },
 "押上": {
  "ko": "오시아게",
  "en": "Oshiage"
 },
 "竹下": {
  "ko": "다케시타",
  "en": "Takeshita"
 },
 "元町・中華街": {
  "ko": "모토마치추카가이",
  "en": "Motomachi・Chukagai"
 },
 "三条京阪": {
  "ko": "산조케이한",
  "en": "Sanjokeihan"
 },
 "栄町": {
  "ko": "사카에마치",
  "en": "Sakaemachi"
 },
 "府中本町": {
  "ko": "후추혼마치",
  "en": "Fuchuhonmachi"
 },
 "宮の坂": {
  "ko": "미야노사카",
  "en": "Miyanosaka"
 },
 "新潟": {
  "ko": "니이가타",
  "en": "Niigata"
 },
 "新横浜": {
  "ko": "신요코하마",
  "en": "Shinyokohama"
 },
 "野方": {
  "ko": "노가타",
  "en": "Nogata"
 },
 "戸越公園": {
  "ko": "도코시코엔",
  "en": "Tokoshikoen"
 },
 "千駄ケ谷": {
  "ko": "센다케타니",
  "en": "Sendaketani"
 },
 "荏原中延": {
  "ko": "에하라나카노베",
  "en": "Eharanakanobe"
 },
 "博多南": {
  "ko": "하카타미나미",
  "en": "Hakataminami"
 },
 "京成金町": {
  "ko": "게이세이카네마치",
  "en": "Keiseikanemachi"
 },
 "代田橋": {
  "ko": "시로타하시",
  "en": "Shirotahashi"
 },
 "福島（阪神）": {
  "ko": "후쿠시마한신",
  "en": "Fukushima(Hanshin)"
 },
 "月島": {
  "ko": "가쓰시마",
  "en": "Gatsushima"
 },
 "とうきょうスカイツリー": {
  "ko": "도쿄스카이쓰리",
  "en": "Tokyosukaitsurii"
 },
 "布田": {
  "ko": "후다",
  "en": "Fuda"
 },
 "祖師ケ谷大蔵": {
  "ko": "소시가야오쿠라",
  "en": "Soshigaya-okura"
 },
 "葛西": {
  "ko": "가사이",
  "en": "Kasai"
 },
 "国立競技場": {
  "ko": "고쿠리쓰쿄기조",
  "en": "Kokuritsukyogijo"
 },
 "金沢": {
  "ko": "가나자와",
  "en": "Kanazawa"
 },
 "京急川崎": {
  "ko": "게이큐카와사키",
  "en": "Keikyukawasaki"
 },
 "新板橋": {
  "ko": "신이타바시",
  "en": "Shin'Itabashi"
 },
 "川崎": {
  "ko": "가와사키",
  "en": "Kawasaki"
 },
 "三ノ輪": {
  "ko": "산노와",
  "en": "Sannowa"
 },
 "根津": {
  "ko": "네즈",
  "en": "Nezu"
 },
 "新馬場": {
  "ko": "신바바",
  "en": "Shinbaba"
 },
 "北鉄金沢": {
  "ko": "호쿠테쓰카나자와",
  "en": "Hokutetsukanazawa"
 },
 "新福島": {
  "ko": "신후쿠시마",
  "en": "Shinfukushima"
 },
 "中板橋": {
  "ko": "나카이타바시",
  "en": "Nakaitabashi"
 },
 "名鉄名古屋": {
  "ko": "메이테쓰나고야",
  "en": "Meitetsunagoya"
 },
 "花畑": {
  "ko": "하나하타",
  "en": "Hanahata"
 },
 "広瀬通": {
  "ko": "히로세토오리",
  "en": "Hirosetori"
 },
 "武蔵新田": {
  "ko": "무사시닛타",
  "en": "Musashinitta"
 },
 "新小金井": {
  "ko": "신코가네이",
  "en": "Shinkoganei"
 },
 "成城学園前": {
  "ko": "세이조가쿠엔마에",
  "en": "Seijogakuen-mae"
 },
 "北千束": {
  "ko": "기타센조쿠",
  "en": "Kitasenzoku"
 },
 "新豊洲": {
  "ko": "신토요스",
  "en": "Shintoyosu"
 },
 "明大前": {
  "ko": "메이다이마에",
  "en": "Meidaimae"
 },
 "近鉄名古屋": {
  "ko": "긴테쓰나고야",
  "en": "Kintetsunagoya"
 },
 "大宮": {
  "ko": "오미야",
  "en": "Omiya"
 },
 "栄（名古屋）": {
  "ko": "사카에나고야",
  "en": "Sakae(Nagoya)"
 },
 "心斎橋": {
  "ko": "신사이바시",
  "en": "Shinsaibashi"
 },
 "三ノ輪橋": {
  "ko": "산노와하시",
  "en": "Sannowahashi"
 },
 "大岡山": {
  "ko": "오카야마",
  "en": "Ookayama"
 },
 "桜新町": {
  "ko": "사쿠라신마치",
  "en": "Sakurashinmachi"
 },
 "高山": {
  "ko": "고잔",
  "en": "Kozan"
 },
 "二子玉川": {
  "ko": "후타코타마가와",
  "en": "Futako-tamagawa"
 },
 "田無": {
  "ko": "다나시",
  "en": "Tanashi"
 },
 "柴崎": {
  "ko": "시바사키",
  "en": "Shibasaki"
 },
 "府中": {
  "ko": "후추",
  "en": "Fuchu"
 },
 "西新井": {
  "ko": "니시아라이",
  "en": "Nishiarai"
 },
 "東松原": {
  "ko": "히가시마쓰바라",
  "en": "Higashimatsubara"
 },
 "大泉学園": {
  "ko": "오이즈미가쿠엔",
  "en": "Oizumigakuen"
 },
 "天王洲アイル": {
  "ko": "덴노즈아이루",
  "en": "Tennozuairu"
 },
 "静岡": {
  "ko": "시즈오카",
  "en": "Shizuoka"
 },
 "武蔵境": {
  "ko": "무사시사카이",
  "en": "Musashisakai"
 },
 "新静岡": {
  "ko": "신시즈오카",
  "en": "Shinshizuoka"
 },
 "武蔵小杉": {
  "ko": "무사시코스기",
  "en": "Musashikosugi"
 },
 "板橋本町": {
  "ko": "이타바시혼초",
  "en": "Itabashihoncho"
 },
 "飯塚": {
  "ko": "이이즈카",
  "en": "Iizuka"
 },
 "黒崎駅前": {
  "ko": "구로사키에키마에",
  "en": "Kurosakiekimae"
 },
 "東小金井": {
  "ko": "히가시코가네이",
  "en": "Higashikoganei"
 },
 "黒崎": {
  "ko": "구로사키",
  "en": "Kurosaki"
 },
 "羽田空港第１・第２ターミナル（京急）": {
  "ko": "하네다쿠우코다이이치다이니타미나루케이큐",
  "en": "Hanedakukodaiichi・Dainitaaminaru(Keikyu)"
 },
 "本川越": {
  "ko": "혼카와에쓰",
  "en": "Honkawaetsu"
 },
 "烏丸": {
  "ko": "가라스마",
  "en": "Karasuma"
 },
 "平沼橋": {
  "ko": "히라누마바시",
  "en": "Hiranumabashi"
 },
 "新丸子": {
  "ko": "신마루코",
  "en": "Shinmaruko"
 },
 "四ツ橋": {
  "ko": "시쓰하시",
  "en": "Shitsuhashi"
 },
 "二子新地": {
  "ko": "후타코신치",
  "en": "Futakoshinchi"
 },
 "世田谷": {
  "ko": "세타가야",
  "en": "Setagaya"
 },
 "原町": {
  "ko": "하라마치",
  "en": "Haramachi"
 },
 "下丸子": {
  "ko": "시모마루코",
  "en": "Shimomaruko"
 },
 "勾当台公園": {
  "ko": "고토다이코엔",
  "en": "Kotodaikoen"
 },
 "大師前": {
  "ko": "다이시마에",
  "en": "Daishimae"
 },
 "黄金町": {
  "ko": "고가네초",
  "en": "Koganecho"
 },
 "川越市": {
  "ko": "가와고에시",
  "en": "Kawagoeshi"
 },
 "三宮（神戸市営）": {
  "ko": "산노미야코베시에이",
  "en": "Sannomiya(Kobeshiei)"
 },
 "松陰神社前": {
  "ko": "쇼인진자마에",
  "en": "Shoinjinjamae"
 },
 "西川緑道公園": {
  "ko": "니시카와료쿠도코엔",
  "en": "Nishikawaryokudokoen"
 },
 "京都市役所前": {
  "ko": "교토시야쿠쇼마에",
  "en": "Kyotoshiyakushomae"
 },
 "酒殿": {
  "ko": "사케도노",
  "en": "Sakedono"
 },
 "成増": {
  "ko": "나리마스",
  "en": "Narimasu"
 },
 "王子駅前": {
  "ko": "오지에키마에",
  "en": "Ojiekimae"
 },
 "渡辺橋": {
  "ko": "와타나베하시",
  "en": "Watanabehashi"
 },
 "大鳥居": {
  "ko": "오토리이",
  "en": "Otorii"
 },
 "船橋": {
  "ko": "후나바시",
  "en": "Funabashi"
 },
 "河辺": {
  "ko": "가와베",
  "en": "Kawabe"
 },
 "軽井沢": {
  "ko": "가루이자와",
  "en": "Karuizawa"
 },
 "王子": {
  "ko": "오지",
  "en": "Oji"
 },
 "一乗寺": {
  "ko": "이치조지",
  "en": "Ichijoji"
 },
 "西葛西": {
  "ko": "니시카사이",
  "en": "Nishikasai"
 },
 "佐野市": {
  "ko": "사노시",
  "en": "Sanoshi"
 },
 "等々力": {
  "ko": "도도로키",
  "en": "Todoroki"
 },
 "本町": {
  "ko": "혼초",
  "en": "Honcho"
 },
 "国立": {
  "ko": "고쿠리쓰",
  "en": "Kokuritsu"
 },
 "伏見": {
  "ko": "후시미",
  "en": "Fushimi"
 },
 "一橋学園": {
  "ko": "히토쓰바시가쿠엔",
  "en": "Hitotsubashigakuen"
 },
 "熊本城・市役所前": {
  "ko": "구마모토조시야쿠쇼마에",
  "en": "Kumamotojo・Shiyakushomae"
 },
 "岡山駅前": {
  "ko": "오카야마에키마에",
  "en": "Okayamaekimae"
 },
 "小作": {
  "ko": "오자쿠",
  "en": "Ozaku"
 },
 "鬼子母神前": {
  "ko": "기시모진마에",
  "en": "Kishimojinmae"
 },
 "福生": {
  "ko": "훗사",
  "en": "Fussa"
 },
 "東中神": {
  "ko": "히가시나카카미",
  "en": "Higashinakakami"
 },
 "四条（京都市営）": {
  "ko": "시조쿄토시에이",
  "en": "Shijo(Kyotoshiei)"
 },
 "新栄町": {
  "ko": "신에이마치",
  "en": "Shin'Eimachi"
 },
 "肥後橋": {
  "ko": "히고바시",
  "en": "Higobashi"
 },
 "中神": {
  "ko": "나카가미",
  "en": "Nakagami"
 },
 "石神井公園": {
  "ko": "샤쿠지이코엔",
  "en": "Shakujiikoen"
 },
 "松戸": {
  "ko": "마쓰도",
  "en": "Matsudo"
 },
 "柏": {
  "ko": "가시와",
  "en": "Kashiwa"
 },
 "泉外旭川": {
  "ko": "이즈미소토아사히카와",
  "en": "Izumisotoasahikawa"
 },
 "上北台": {
  "ko": "가미키타다이",
  "en": "Kamikitadai"
 },
 "阪東橋": {
  "ko": "반도하시",
  "en": "Bandohashi"
 },
 "横川": {
  "ko": "요코카와",
  "en": "Yokokawa"
 },
 "東神奈川": {
  "ko": "히가시카나가와",
  "en": "Higashikanagawa"
 },
 "狛江": {
  "ko": "고마에",
  "en": "Komae"
 },
 "東武宇都宮": {
  "ko": "도부우쓰노미야",
  "en": "Tobutsunomiya"
 },
 "西永福": {
  "ko": "니시나가후쿠",
  "en": "Nishinagafuku"
 },
 "豊洲": {
  "ko": "도요스",
  "en": "Toyosu"
 },
 "水戸": {
  "ko": "미토",
  "en": "Mito"
 },
 "西武柳沢": {
  "ko": "세이부야나기사와",
  "en": "Seibuyanagisawa"
 },
 "上石神井": {
  "ko": "가미이시카미이",
  "en": "Kamiishikamii"
 },
 "上井草": {
  "ko": "가미이구사",
  "en": "Kamiigusa"
 },
 "戸畑": {
  "ko": "고하타",
  "en": "Kohata"
 },
 "京成船橋": {
  "ko": "게이세이후나바시",
  "en": "Keiseifunabashi"
 },
 "下赤塚": {
  "ko": "시타아카쓰카",
  "en": "Shitaakatsuka"
 },
 "花小金井": {
  "ko": "하나코가네이",
  "en": "Hanakoganei"
 },
 "神戸三宮（阪急）": {
  "ko": "고베산노미야한큐",
  "en": "Kobesannomiya(Hankyu)"
 },
 "池上": {
  "ko": "이케가미",
  "en": "Ikegami"
 },
 "山形": {
  "ko": "야마가타",
  "en": "Yamagata"
 },
 "修学院": {
  "ko": "슈가쿠인",
  "en": "Shugakuin"
 },
 "浦和": {
  "ko": "우라와",
  "en": "Urawa"
 },
 "白楽": {
  "ko": "하쿠라쿠",
  "en": "Hakuraku"
 },
 "永福町": {
  "ko": "에이후쿠마치",
  "en": "Eifukumachi"
 },
 "今池": {
  "ko": "이마이케",
  "en": "Imaike"
 },
 "八坂": {
  "ko": "야사카",
  "en": "Yasaka"
 },
 "梅ケ丘": {
  "ko": "우메케오카",
  "en": "Umekeoka"
 },
 "三ノ宮（ＪＲ）": {
  "ko": "산노미야",
  "en": "Sannomiya(Jr)"
 },
 "花畑町": {
  "ko": "하나바타초",
  "en": "Hanabatacho"
 },
 "烏丸御池": {
  "ko": "가라스마오이케",
  "en": "Karasumaoike"
 },
 "尾山台": {
  "ko": "오야마다이",
  "en": "Oyamadai"
 },
 "堺筋本町": {
  "ko": "사카이스지혼초",
  "en": "Sakaisujihoncho"
 },
 "東白楽": {
  "ko": "도하쿠라쿠",
  "en": "Tohakuraku"
 },
 "東大和市": {
  "ko": "히가시야마토시",
  "en": "Higashiyamatoshi"
 },
 "丸の内": {
  "ko": "마루노치",
  "en": "Marunochi"
 },
 "日吉": {
  "ko": "히요시",
  "en": "Hiyoshi"
 },
 "湯河原": {
  "ko": "유가와라",
  "en": "Yugawara"
 },
 "福間": {
  "ko": "후쿠마",
  "en": "Fukuma"
 },
 "九州工大前": {
  "ko": "규슈코다이마에",
  "en": "Kyushukodaimae"
 },
 "中軽井沢": {
  "ko": "나카카루이자와",
  "en": "Nakakaruizawa"
 },
 "大須観音": {
  "ko": "오스칸논",
  "en": "Osukannon"
 },
 "青葉台": {
  "ko": "아오바다이",
  "en": "Aobadai"
 },
 "本八幡": {
  "ko": "혼하치만",
  "en": "Honhachiman"
 },
 "鎌倉": {
  "ko": "가마쿠라",
  "en": "Kamakura"
 },
 "折尾": {
  "ko": "세쓰비",
  "en": "Setsubi"
 },
 "雑餉隈": {
  "ko": "잣쇼쿠마",
  "en": "Zasshokuma"
 },
 "県庁前": {
  "ko": "겐초마에",
  "en": "Kenchomae"
 },
 "千葉中央": {
  "ko": "지바추오",
  "en": "Chibachuo"
 },
 "成瀬": {
  "ko": "나루세",
  "en": "Naruse"
 },
 "戸塚": {
  "ko": "도쓰카",
  "en": "Totsuka"
 },
 "胡町": {
  "ko": "에비스초",
  "en": "Ebisucho"
 },
 "葭川公園": {
  "ko": "요시카와코엔",
  "en": "Yoshikawakoen"
 },
 "清瀬": {
  "ko": "기요세",
  "en": "Kiyose"
 },
 "矢部": {
  "ko": "야베",
  "en": "Yabe"
 },
 "高崎（ＪＲ）": {
  "ko": "다카사키",
  "en": "Takasaki(Jr)"
 },
 "谷町四丁目": {
  "ko": "다니마치시테이메",
  "en": "Tanimachishiteime"
 },
 "京成八幡": {
  "ko": "게이세이하치만",
  "en": "Keiseihachiman"
 },
 "阿波座": {
  "ko": "아와자",
  "en": "Awaza"
 },
 "久米川": {
  "ko": "구메가와",
  "en": "Kumegawa"
 },
 "谷町六丁目": {
  "ko": "다니마치로쿠초메",
  "en": "Tanimachirokuchome"
 },
 "和田塚": {
  "ko": "와다쓰카",
  "en": "Wadatsuka"
 },
 "和泉多摩川": {
  "ko": "이즈미타마가와",
  "en": "Izumitamagawa"
 },
 "新大阪": {
  "ko": "신오사카",
  "en": "Shin'Osaka"
 },
 "聖蹟桜ケ丘": {
  "ko": "세이세키사쿠라가오카",
  "en": "Seisekisakuragaoka"
 },
 "城下": {
  "ko": "조카",
  "en": "Joka"
 },
 "思案橋": {
  "ko": "시안하시",
  "en": "Shianhashi"
 },
 "相模原": {
  "ko": "사가미하라",
  "en": "Sagamihara"
 },
 "熱海": {
  "ko": "아타미",
  "en": "Atami"
 },
 "船堀": {
  "ko": "후나보리",
  "en": "Funabori"
 },
 "宇都宮": {
  "ko": "우쓰노미야",
  "en": "Utsunomiya"
 },
 "本城": {
  "ko": "혼조",
  "en": "Honjo"
 },
 "あおば通": {
  "ko": "아오바토오리",
  "en": "Aobatori"
 },
 "松屋町": {
  "ko": "마쓰야마치",
  "en": "Matsuyamachi"
 },
 "本厚木": {
  "ko": "혼아쓰기",
  "en": "Hon'Atsugi"
 },
 "佐野": {
  "ko": "사노",
  "en": "Sano"
 },
 "観光通": {
  "ko": "간코토오리",
  "en": "Kankotori"
 },
 "京都": {
  "ko": "교토",
  "en": "Kyoto"
 },
 "八幡": {
  "ko": "하치만",
  "en": "Hachiman"
 },
 "下曽根": {
  "ko": "시모소네",
  "en": "Shimosone"
 },
 "酒田": {
  "ko": "사카타",
  "en": "Sakata"
 },
 "来宮": {
  "ko": "기노미야",
  "en": "Kinomiya"
 },
 "北山形": {
  "ko": "기타야마카타치",
  "en": "Kitayamakatachi"
 },
 "高幡不動": {
  "ko": "다카하타후도",
  "en": "Takahatafudo"
 },
 "たまプラーザ": {
  "ko": "다마푸라자",
  "en": "Tamapuraaza"
 },
 "京急鶴見": {
  "ko": "게이큐쓰루미",
  "en": "Keikyutsurumi"
 },
 "元町（ＪＲ）": {
  "ko": "모토마치",
  "en": "Motomachi(Jr)"
 },
 "筑前前原": {
  "ko": "지쿠젠마에하라",
  "en": "Chikuzenmaehara"
 },
 "西中島南方": {
  "ko": "니시나카시마난포",
  "en": "Nishinakashimananpo"
 },
 "矢加部": {
  "ko": "야카베",
  "en": "Yakabe"
 },
 "茅野": {
  "ko": "지노",
  "en": "Chino"
 },
 "高崎（上信）": {
  "ko": "다카사키우에신",
  "en": "Takasaki(Ueshin)"
 },
 "名鉄岐阜": {
  "ko": "메이테쓰기후",
  "en": "Meitetsugifu"
 },
 "鶴見": {
  "ko": "쓰루미",
  "en": "Tsurumi"
 },
 "鶴橋": {
  "ko": "쓰루하시",
  "en": "Tsuruhashi"
 },
 "片原町（高松）": {
  "ko": "가타하라마치타카마쓰",
  "en": "Kataharamachi(Takamatsu)"
 },
 "下関": {
  "ko": "시모노세키",
  "en": "Shimonoseki"
 },
 "川口": {
  "ko": "가와구치",
  "en": "Kawaguchi"
 },
 "上田": {
  "ko": "우에다",
  "en": "Ueda"
 },
 "蕨": {
  "ko": "와라비",
  "en": "Warabi"
 },
 "辻堂": {
  "ko": "쓰지도",
  "en": "Tsujido"
 },
 "競馬場前": {
  "ko": "게이바조마에",
  "en": "Keibajomae"
 },
 "西鉄柳川": {
  "ko": "니시테쓰야나가와",
  "en": "Nishitetsuyanagawa"
 },
 "千種": {
  "ko": "지구사",
  "en": "Chigusa"
 },
 "新綱島": {
  "ko": "신쓰나시마",
  "en": "Shintsunashima"
 },
 "つくば": {
  "ko": "쓰쿠바",
  "en": "Tsukuba"
 },
 "塚口（阪急）": {
  "ko": "쓰카구치한큐",
  "en": "Tsukaguchi(Hankyu)"
 },
 "元町（阪神）": {
  "ko": "모토마치한신",
  "en": "Motomachi(Hanshin)"
 },
 "富山": {
  "ko": "도야마",
  "en": "Toyama"
 },
 "多摩川": {
  "ko": "다마가와",
  "en": "Tamagawa"
 },
 "高槻": {
  "ko": "다카쓰키",
  "en": "Takatsuki"
 },
 "上前津": {
  "ko": "가미마에즈",
  "en": "Kamimaezu"
 },
 "上大岡": {
  "ko": "가미오카",
  "en": "Kamiooka"
 },
 "西北見": {
  "ko": "세이호쿠켄",
  "en": "Seihokuken"
 },
 "東久留米": {
  "ko": "히가시쿠루메",
  "en": "Higashikurume"
 },
 "厚木": {
  "ko": "아쓰기",
  "en": "Atsugi"
 },
 "長岡": {
  "ko": "나가오카",
  "en": "Nagaoka"
 },
 "一之江": {
  "ko": "이치노에",
  "en": "Ichinoe"
 },
 "喜多方": {
  "ko": "기타카타",
  "en": "Kitakata"
 },
 "電鉄富山": {
  "ko": "덴테쓰토야마",
  "en": "Dentetsutoyama"
 },
 "獨協大学前": {
  "ko": "돗쿄다이가쿠마에",
  "en": "Dokkyodaigakumae"
 },
 "佐世保中央": {
  "ko": "사세보추오",
  "en": "Sasebochuo"
 },
 "京王多摩センター": {
  "ko": "게이오타마센타",
  "en": "Keiotamasentaa"
 },
 "藤が丘": {
  "ko": "후지가오카",
  "en": "Fujigaoka"
 },
 "天文館通": {
  "ko": "덴몬칸토오리",
  "en": "Tenmonkantori"
 },
 "東秋留": {
  "ko": "히가시아키류",
  "en": "Higashiakiryu"
 },
 "西川口": {
  "ko": "니시카와쿠치",
  "en": "Nishikawakuchi"
 },
 "伊勢市": {
  "ko": "이세시",
  "en": "Iseshi"
 },
 "宇治山田": {
  "ko": "우지야마다",
  "en": "Ujiyamada"
 },
 "程久保": {
  "ko": "호도쿠보",
  "en": "Hodokubo"
 },
 "曽根田": {
  "ko": "소네다",
  "en": "Soneda"
 },
 "京成成田": {
  "ko": "게이세이나리타",
  "en": "Keiseinarita"
 },
 "瓦町": {
  "ko": "가와라초",
  "en": "Kawaracho"
 },
 "スペースワールド": {
  "ko": "스페스와루도",
  "en": "Supeesuwaarudo"
 },
 "岐阜": {
  "ko": "기후",
  "en": "Gifu"
 },
 "新浜松": {
  "ko": "니이하마마쓰",
  "en": "Niihamamatsu"
 },
 "港南中央": {
  "ko": "고난추오",
  "en": "Konanchuo"
 },
 "鳥取": {
  "ko": "돗토리",
  "en": "Tottori"
 },
 "西長堀": {
  "ko": "니시나가호리",
  "en": "Nishinagahori"
 },
 "溝の口": {
  "ko": "미조노쿠치",
  "en": "Mizonokuchi"
 },
 "上溝": {
  "ko": "우와미조",
  "en": "Uwamizo"
 },
 "今宮戎": {
  "ko": "이마미야주",
  "en": "Imamiyaju"
 },
 "鶴岡": {
  "ko": "쓰루오카",
  "en": "Tsuruoka"
 },
 "富士見ケ丘": {
  "ko": "후지미케오카",
  "en": "Fujimikeoka"
 },
 "北見": {
  "ko": "기타미",
  "en": "Kitami"
 },
 "成田": {
  "ko": "나리타",
  "en": "Narita"
 },
 "高見馬場": {
  "ko": "다카미바바",
  "en": "Takamibaba"
 },
 "天王町": {
  "ko": "덴노초",
  "en": "Tennocho"
 },
 "十三": {
  "ko": "주산",
  "en": "Jusan"
 },
 "小路（大阪メトロ）": {
  "ko": "고지오사카메토로",
  "en": "Koji(Osakametoro)"
 },
 "八女市その他": {
  "ko": "야메시소노호카",
  "en": "Yameshisonohoka"
 },
 "石上": {
  "ko": "이시가미",
  "en": "Ishigami"
 },
 "平塚": {
  "ko": "히라쓰카",
  "en": "Hiratsuka"
 },
 "広島": {
  "ko": "히로시마",
  "en": "Hiroshima"
 },
 "田園調布": {
  "ko": "덴엔초후",
  "en": "Den'Enchofu"
 },
 "三鷹台": {
  "ko": "미타카다이",
  "en": "Mitakadai"
 },
 "高槻市": {
  "ko": "다카쓰키시",
  "en": "Takatsukishi"
 },
 "大牟田": {
  "ko": "오무타",
  "en": "Omuta"
 },
 "中佐世保": {
  "ko": "주사요호",
  "en": "Chusayoho"
 },
 "福島": {
  "ko": "후쿠시마",
  "en": "Fukushima"
 },
 "草加": {
  "ko": "소카",
  "en": "Soka"
 },
 "御花畑": {
  "ko": "오하나하타",
  "en": "Ohanahata"
 },
 "高岳": {
  "ko": "다카오카",
  "en": "Takaoka"
 },
 "北浦和": {
  "ko": "기타우라와",
  "en": "Kitaurawa"
 },
 "九条": {
  "ko": "규조",
  "en": "Kyujo"
 },
 "武蔵溝ノ口": {
  "ko": "무사시미조노쿠치",
  "en": "Musashimizonokuchi"
 },
 "第一通り": {
  "ko": "다이이치토리",
  "en": "Daiichitori"
 },
 "大阪上本町": {
  "ko": "오사카우에혼마치",
  "en": "Osakauehonmachi"
 },
 "狭間": {
  "ko": "하자마",
  "en": "Hazama"
 },
 "筑後吉井": {
  "ko": "지쿠고요시이",
  "en": "Chikugoyoshii"
 },
 "遠賀川": {
  "ko": "온가카와",
  "en": "Ongakawa"
 },
 "秋川": {
  "ko": "아키가와",
  "en": "Akigawa"
 },
 "御器所": {
  "ko": "고키소",
  "en": "Gokiso"
 },
 "大阪ビジネスパーク": {
  "ko": "오사카비지네스파쿠",
  "en": "Osakabijinesupaaku"
 },
 "苅田": {
  "ko": "가리다",
  "en": "Karida"
 },
 "登戸": {
  "ko": "노보리토",
  "en": "Noborito"
 },
 "幸手": {
  "ko": "삿테",
  "en": "Satte"
 },
 "小田急相模原": {
  "ko": "오다큐사가미하라",
  "en": "Odakyusagamihara"
 },
 "天王台": {
  "ko": "덴노다이",
  "en": "Tennodai"
 },
 "桜山": {
  "ko": "사쿠라야마",
  "en": "Sakurayama"
 },
 "京急東神奈川": {
  "ko": "게이큐히가시카나가와",
  "en": "Keikyuhigashikanagawa"
 },
 "鶴間": {
  "ko": "쓰루마",
  "en": "Tsuruma"
 },
 "東郷": {
  "ko": "도고",
  "en": "Togo"
 },
 "所沢": {
  "ko": "도코로자와",
  "en": "Tokorozawa"
 },
 "吹上": {
  "ko": "후키아게",
  "en": "Fukiage"
 },
 "五橋": {
  "ko": "이쓰쓰바시",
  "en": "Itsutsubashi"
 },
 "西国分寺": {
  "ko": "니시코쿠분지",
  "en": "Nishikokubunji"
 },
 "愛宕橋": {
  "ko": "아타고바시",
  "en": "Atagobashi"
 },
 "上諏訪": {
  "ko": "가미스와",
  "en": "Kamisuwa"
 },
 "さいたま新都心": {
  "ko": "사이타마신토신",
  "en": "Saitamashintoshin"
 },
 "出光美術館": {
  "ko": "이데미쓰비주쓰칸",
  "en": "Idemitsubijutsukan"
 },
 "西馬込": {
  "ko": "니시마고메",
  "en": "Nishimagome"
 },
 "赤塚": {
  "ko": "아카쓰카",
  "en": "Akatsuka"
 },
 "三滝": {
  "ko": "미타키",
  "en": "Mitaki"
 },
 "長岡市その他": {
  "ko": "나가오카시소노호카",
  "en": "Nagaokashisonohoka"
 },
 "帯広": {
  "ko": "오비히로",
  "en": "Obihiro"
 },
 "九州鉄道記念館": {
  "ko": "규슈테쓰도키넨칸",
  "en": "Kyushutetsudokinenkan"
 },
 "宮古島市": {
  "ko": "미야코시마시",
  "en": "Miyakoshimashi"
 },
 "小山": {
  "ko": "오야마",
  "en": "Oyama"
 },
 "七条": {
  "ko": "나나조",
  "en": "Nanajo"
 },
 "相川": {
  "ko": "아이카와",
  "en": "Aikawa"
 },
 "仙台": {
  "ko": "센다이",
  "en": "Sendai"
 },
 "行橋": {
  "ko": "유쿠하시",
  "en": "Yukuhashi"
 },
 "松阪": {
  "ko": "마쓰사카",
  "en": "Matsusaka"
 },
 "高尾": {
  "ko": "다카오",
  "en": "Takao"
 },
 "小手指": {
  "ko": "고테사시",
  "en": "Kotesashi"
 },
 "鶴瀬": {
  "ko": "쓰루세",
  "en": "Tsuruse"
 },
 "布施": {
  "ko": "후세",
  "en": "Fuse"
 },
 "海老名": {
  "ko": "에비나",
  "en": "Ebina"
 },
 "浦安": {
  "ko": "우라야스",
  "en": "Urayasu"
 },
 "羽犬塚": {
  "ko": "하이누즈카",
  "en": "Hainuzuka"
 },
 "岡谷": {
  "ko": "오카야",
  "en": "Okaya"
 },
 "あざみ野": {
  "ko": "아자미노",
  "en": "Azamino"
 },
 "燕三条": {
  "ko": "쓰바메산조",
  "en": "Tsubamesanjo"
 },
 "糸島高校前": {
  "ko": "이토시마코코마에",
  "en": "Itoshimakokomae"
 },
 "丹波口": {
  "ko": "단바구치",
  "en": "Tanbaguchi"
 },
 "志木": {
  "ko": "시키",
  "en": "Shiki"
 },
 "西武秩父": {
  "ko": "세이부치치부",
  "en": "Seibuchichibu"
 },
 "鷺沼": {
  "ko": "사기누마",
  "en": "Saginuma"
 },
 "館山": {
  "ko": "다테야마",
  "en": "Tateyama"
 },
 "水海道": {
  "ko": "미쓰카이도",
  "en": "Mitsukaido"
 },
 "一ノ割": {
  "ko": "이치노와리",
  "en": "Ichinowari"
 },
 "草津町その他": {
  "ko": "구사쓰마치소노호카",
  "en": "Kusatsumachisonohoka"
 },
 "日田": {
  "ko": "히타",
  "en": "Hita"
 },
 "逗子・葉山": {
  "ko": "즈시하야마",
  "en": "Zushi・Hayama"
 },
 "下新庄": {
  "ko": "시모신조",
  "en": "Shimoshinjo"
 },
 "向ケ丘遊園": {
  "ko": "고케오카유우엔",
  "en": "Kokeokayuen"
 },
 "日生": {
  "ko": "닛세이",
  "en": "Nissei"
 },
 "柏の葉キャンパス": {
  "ko": "가시와노하캰파스",
  "en": "Kashiwanohakyanpasu"
 },
 "馬替": {
  "ko": "우마카에",
  "en": "Umakae"
 },
 "一本松": {
  "ko": "잇폰마쓰",
  "en": "Ipponmatsu"
 },
 "萩原": {
  "ko": "하기와라",
  "en": "Hagiwara"
 },
 "大分": {
  "ko": "오이타",
  "en": "Oita"
 },
 "飯能": {
  "ko": "한노",
  "en": "Hanno"
 },
 "上新庄": {
  "ko": "조신쇼",
  "en": "Joshinsho"
 },
 "武蔵藤沢": {
  "ko": "무사시후지사와",
  "en": "Musashifujisawa"
 },
 "新千葉": {
  "ko": "신치바",
  "en": "Shinchiba"
 },
 "熊谷": {
  "ko": "구마가야",
  "en": "Kumagaya"
 },
 "みのり台": {
  "ko": "미노리다이",
  "en": "Minoridai"
 },
 "元田中": {
  "ko": "모토타나카",
  "en": "Mototanaka"
 },
 "高坂": {
  "ko": "다카사카",
  "en": "Takasaka"
 },
 "桂川": {
  "ko": "가쓰라가와",
  "en": "Katsuragawa"
 },
 "西横浜": {
  "ko": "니시요코하마",
  "en": "Nishiyokohama"
 },
 "南林間": {
  "ko": "미나미린칸",
  "en": "Minamirinkan"
 },
 "幡生": {
  "ko": "하타나마",
  "en": "Hatanama"
 },
 "安房鴨川": {
  "ko": "아와카모가와",
  "en": "Awakamogawa"
 },
 "逗子": {
  "ko": "즈시",
  "en": "Zushi"
 },
 "玉出": {
  "ko": "다마슈쓰",
  "en": "Tamashutsu"
 },
 "大阪阿部野橋": {
  "ko": "오사카아베노하시",
  "en": "Osakaabenohashi"
 },
 "荒川沖": {
  "ko": "아라카와오키",
  "en": "Arakawaoki"
 },
 "甘木（西鉄）": {
  "ko": "아마기니시테쓰",
  "en": "Amagi(Nishitetsu)"
 },
 "海老津": {
  "ko": "에비쓰",
  "en": "Ebitsu"
 },
 "熱田神宮伝馬町": {
  "ko": "아쓰타진구우덴마초",
  "en": "Atsutajingudenmacho"
 },
 "城東": {
  "ko": "조토",
  "en": "Joto"
 },
 "甘木（甘木鉄道）": {
  "ko": "아마기아마기테쓰도",
  "en": "Amagi(Amagitetsudo)"
 },
 "東門前": {
  "ko": "히가시몬마에",
  "en": "Higashimonmae"
 },
 "大船": {
  "ko": "오후나",
  "en": "Ofuna"
 },
 "富士見町": {
  "ko": "후지미초",
  "en": "Fujimicho"
 },
 "北野白梅町": {
  "ko": "기타노시라우메마치",
  "en": "Kitanoshiraumemachi"
 },
 "立町": {
  "ko": "다치마치",
  "en": "Tachimachi"
 },
 "筑豊直方": {
  "ko": "지쿠호노오가타",
  "en": "Chikuhonogata"
 },
 "菊名": {
  "ko": "기쿠나",
  "en": "Kikuna"
 },
 "中央前橋": {
  "ko": "주오마에바시",
  "en": "Chuomaebashi"
 },
 "小布施": {
  "ko": "오부세",
  "en": "Obuse"
 },
 "松江しんじ湖温泉": {
  "ko": "마쓰에신지미즈우미온센",
  "en": "Matsueshinjimizumionsen"
 },
 "ドーム前千代崎": {
  "ko": "도무마에치요자키",
  "en": "Domumaechiyozaki"
 },
 "玉名": {
  "ko": "다마나",
  "en": "Tamana"
 },
 "南守谷": {
  "ko": "미나미모리야",
  "en": "Minamimoriya"
 },
 "子安": {
  "ko": "고야스",
  "en": "Koyasu"
 },
 "千林": {
  "ko": "센바야시",
  "en": "Senbayashi"
 },
 "入生田": {
  "ko": "이리우다",
  "en": "Iriuda"
 },
 "新倉敷": {
  "ko": "니이쿠라시키",
  "en": "Niikurashiki"
 },
 "塚口（ＪＲ）": {
  "ko": "쓰카구치",
  "en": "Tsukaguchi(Jr)"
 },
 "谷保": {
  "ko": "야호",
  "en": "Yaho"
 },
 "都住": {
  "ko": "미야코주",
  "en": "Miyakoju"
 },
 "宮前平": {
  "ko": "미야마에다이라",
  "en": "Miyamaedaira"
 },
 "国母": {
  "ko": "고쿠보",
  "en": "Kokubo"
 },
 "小淵沢": {
  "ko": "오부치자와",
  "en": "Obuchizawa"
 },
 "桃山御陵前": {
  "ko": "모모야마고료마에",
  "en": "Momoyamagoryomae"
 },
 "新子安": {
  "ko": "신코야스",
  "en": "Shinkoyasu"
 },
 "天童": {
  "ko": "덴도",
  "en": "Tendo"
 },
 "古国府": {
  "ko": "후루고",
  "en": "Furugo"
 },
 "戸田": {
  "ko": "도다",
  "en": "Toda"
 },
 "伊勢田": {
  "ko": "이세다",
  "en": "Iseda"
 },
 "三郷": {
  "ko": "미사토",
  "en": "Misato"
 },
 "センター南": {
  "ko": "센타미나미",
  "en": "Sentaaminami"
 },
 "西宮（ＪＲ）": {
  "ko": "니시노미야",
  "en": "Nishinomiya(Jr)"
 },
 "北水海道": {
  "ko": "호쿠스이카이도",
  "en": "Hokusuikaido"
 },
 "吹田（ＪＲ）": {
  "ko": "스이타",
  "en": "Suita(Jr)"
 },
 "京成大久保": {
  "ko": "게이세이오쿠보",
  "en": "Keiseiokubo"
 },
 "荒子": {
  "ko": "아라코",
  "en": "Arako"
 },
 "守谷": {
  "ko": "모리야",
  "en": "Moriya"
 },
 "風祭": {
  "ko": "가자마쓰리",
  "en": "Kazamatsuri"
 },
 "福井": {
  "ko": "후쿠이",
  "en": "Fukui"
 },
 "北朝霞": {
  "ko": "호쿠초카스미",
  "en": "Hokuchokasumi"
 },
 "蒲生四丁目": {
  "ko": "가모시테이메",
  "en": "Gamoshiteime"
 },
 "すすきの（市営）": {
  "ko": "스스키노시에이",
  "en": "Susukino(Shiei)"
 },
 "くぬぎ山": {
  "ko": "구누기야마",
  "en": "Kunugiyama"
 },
 "二条": {
  "ko": "니조",
  "en": "Nijo"
 },
 "さっぽろ（札幌市営）": {
  "ko": "삿포로삿포로시에이",
  "en": "Sapporo(Sapporoshiei)"
 },
 "伏見桃山": {
  "ko": "후시미모모야마",
  "en": "Fushimimomoyama"
 },
 "踊場": {
  "ko": "오도리바",
  "en": "Odoriba"
 },
 "西院（阪急）": {
  "ko": "사이인한큐",
  "en": "Saiin(Hankyu)"
 },
 "上栄町": {
  "ko": "우에사카에마치",
  "en": "Uesakaemachi"
 },
 "京成津田沼": {
  "ko": "게이세이쓰다누마",
  "en": "Keiseitsudanuma"
 },
 "五井": {
  "ko": "고이",
  "en": "Goi"
 },
 "栃木": {
  "ko": "도치기",
  "en": "Tochigi"
 },
 "俊徳道": {
  "ko": "도시노리미치",
  "en": "Toshinorimichi"
 },
 "西宮（阪神）": {
  "ko": "니시노미야한신",
  "en": "Nishinomiya(Hanshin)"
 },
 "名古屋城": {
  "ko": "나고야조",
  "en": "Nagoyajo"
 },
 "天王寺": {
  "ko": "덴노지",
  "en": "Tennoji"
 },
 "岩村田": {
  "ko": "이와무라다",
  "en": "Iwamurada"
 },
 "北新井": {
  "ko": "기타신이",
  "en": "Kitashini"
 },
 "加納": {
  "ko": "가노",
  "en": "Kano"
 },
 "西焼津": {
  "ko": "니시야이즈",
  "en": "Nishiyaizu"
 },
 "浜金谷": {
  "ko": "하마킨타니",
  "en": "Hamakintani"
 },
 "北茅ケ崎": {
  "ko": "기타메케사키",
  "en": "Kitamekesaki"
 },
 "小田原": {
  "ko": "오다와라",
  "en": "Odawara"
 },
 "稲城長沼": {
  "ko": "이나기나가누마",
  "en": "Inaginaganuma"
 },
 "塚西": {
  "ko": "쓰카니시",
  "en": "Tsukanishi"
 },
 "紀伊勝浦": {
  "ko": "기이카쓰우라",
  "en": "Kiikatsura"
 },
 "八潮": {
  "ko": "야시오",
  "en": "Yashio"
 },
 "茅ケ崎": {
  "ko": "메케사키",
  "en": "Mekesaki"
 },
 "朝霞台": {
  "ko": "아사카다이",
  "en": "Asakadai"
 },
 "塚本": {
  "ko": "쓰카모토",
  "en": "Tsukamoto"
 },
 "東酒田": {
  "ko": "히가시사카타",
  "en": "Higashisakata"
 },
 "甲府": {
  "ko": "고후",
  "en": "Kofu"
 },
 "富谷町その他": {
  "ko": "도미야초소노호카",
  "en": "Tomiyachosonohoka"
 },
 "高雄": {
  "ko": "다카오",
  "en": "Takao"
 },
 "新川崎": {
  "ko": "신카와사키",
  "en": "Shinkawasaki"
 },
 "焼津": {
  "ko": "야이즈",
  "en": "Yaizu"
 },
 "我孫子": {
  "ko": "아비코",
  "en": "Abiko"
 },
 "霊丘公園体育館": {
  "ko": "레이오카코엔타이이쿠칸",
  "en": "Reiokakoentaiikukan"
 },
 "新玉名": {
  "ko": "신타마메이",
  "en": "Shintamamei"
 },
 "中村日赤": {
  "ko": "나카무라닛세키",
  "en": "Nakamuranisseki"
 },
 "直方": {
  "ko": "노오가타",
  "en": "Nogata"
 },
 "東岩槻": {
  "ko": "히가시이와쓰키",
  "en": "Higashiiwatsuki"
 },
 "大師橋": {
  "ko": "다이시하시",
  "en": "Taishihashi"
 },
 "横須賀中央": {
  "ko": "요코스카추오",
  "en": "Yokosukachuo"
 },
 "四方津": {
  "ko": "시호쓰",
  "en": "Shihotsu"
 },
 "上熊谷": {
  "ko": "우에쿠마가야",
  "en": "Uekumagaya"
 },
 "西院（京福）": {
  "ko": "사이인케이후쿠",
  "en": "Saiin(Keifuku)"
 },
 "本諫早": {
  "ko": "혼이사하야",
  "en": "Honisahaya"
 },
 "みつわ台": {
  "ko": "미쓰와다이",
  "en": "Mitsuwadai"
 },
 "野々市工大前": {
  "ko": "노노이치코다이마에",
  "en": "Nonoichikodaimae"
 },
 "土浦": {
  "ko": "쓰치우라",
  "en": "Tsuchiura"
 },
 "佐原": {
  "ko": "사와라",
  "en": "Sawara"
 },
 "上星川": {
  "ko": "조세이카와",
  "en": "Joseikawa"
 },
 "鹿島田": {
  "ko": "가시마타",
  "en": "Kashimata"
 },
 "松江": {
  "ko": "마쓰에",
  "en": "Matsue"
 },
 "すすきの（市電）": {
  "ko": "스스키노시덴",
  "en": "Susukino(Shiden)"
 },
 "春日部": {
  "ko": "가스카베",
  "en": "Kasukabe"
 },
 "長町": {
  "ko": "나가마치",
  "en": "Nagamachi"
 },
 "六甲道": {
  "ko": "롯코미치",
  "en": "Rokkomichi"
 },
 "北上尾": {
  "ko": "기타카미오",
  "en": "Kitakamio"
 },
 "南多摩": {
  "ko": "미나미타마",
  "en": "Minamitama"
 },
 "南草津": {
  "ko": "미나미소쓰",
  "en": "Minamisotsu"
 },
 "下呂": {
  "ko": "게로",
  "en": "Gero"
 },
 "六番町": {
  "ko": "로쿠반초",
  "en": "Rokubancho"
 },
 "天満橋": {
  "ko": "덴마바시",
  "en": "Tenmabashi"
 },
 "今里（近鉄）": {
  "ko": "이마사토킨테쓰",
  "en": "Imasato(Kintetsu)"
 },
 "西４丁目": {
  "ko": "니시초메",
  "en": "Nishi4Chome"
 },
 "新在家": {
  "ko": "신자이케",
  "en": "Shinzaike"
 },
 "佐久平": {
  "ko": "사쿠다이라",
  "en": "Sakudaira"
 },
 "動物公園": {
  "ko": "도부쓰코엔",
  "en": "Dobutsukoen"
 },
 "湯浅": {
  "ko": "유아사",
  "en": "Yuasa"
 },
 "伊豆市その他": {
  "ko": "이즈시소노호카",
  "en": "Izushisonohoka"
 },
 "仏子": {
  "ko": "붓시",
  "en": "Busshi"
 },
 "徳和": {
  "ko": "노리카즈",
  "en": "Norikazu"
 },
 "東飯能": {
  "ko": "히가시한노",
  "en": "Higashihanno"
 },
 "新白河": {
  "ko": "신시라카와",
  "en": "Shinshirakawa"
 },
 "庄内": {
  "ko": "쇼나이",
  "en": "Shonai"
 },
 "梁川": {
  "ko": "야나가와",
  "en": "Yanagawa"
 },
 "会津豊川": {
  "ko": "아이즈토요카와",
  "en": "Aizutoyokawa"
 },
 "初石": {
  "ko": "하쓰이시",
  "en": "Hatsuishi"
 },
 "鶴ケ峰": {
  "ko": "쓰루케미네",
  "en": "Tsurukemine"
 },
 "土居": {
  "ko": "쓰치이",
  "en": "Tsuchii"
 },
 "福井城址大名町": {
  "ko": "후쿠이조시다이묘마치",
  "en": "Fukuijoshidaimyomachi"
 },
 "茂原": {
  "ko": "모바라",
  "en": "Mobara"
 },
 "円町": {
  "ko": "엔마치",
  "en": "Enmachi"
 },
 "田奈": {
  "ko": "다나",
  "en": "Tana"
 },
 "松崎町その他": {
  "ko": "마쓰자키마치소노호카",
  "en": "Matsuzakimachisonohoka"
 },
 "長津田": {
  "ko": "나가쓰다",
  "en": "Nagatsuda"
 },
 "我孫子町": {
  "ko": "아비코마치",
  "en": "Abikomachi"
 },
 "二宮": {
  "ko": "니노미야",
  "en": "Ninomiya"
 },
 "福山": {
  "ko": "후쿠야마",
  "en": "Fukuyama"
 },
 "屏風浦": {
  "ko": "뵤부우라",
  "en": "Byobura"
 },
 "三津浜": {
  "ko": "미쓰하마",
  "en": "Mitsuhama"
 },
 "嵐電嵯峨": {
  "ko": "란덴사가",
  "en": "Randensaga"
 },
 "ひたち野うしく": {
  "ko": "히타치노시쿠",
  "en": "Hitachinoshiku"
 },
 "直江津": {
  "ko": "나오에쓰",
  "en": "Naoetsu"
 },
 "岩沼": {
  "ko": "이와누마",
  "en": "Iwanuma"
 },
 "トロッコ嵯峨": {
  "ko": "도롯코사가",
  "en": "Torokkosaga"
 },
 "南栗橋": {
  "ko": "미나미쿠리하시",
  "en": "Minamikurihashi"
 },
 "日光": {
  "ko": "닛코",
  "en": "Nikko"
 },
 "天満町": {
  "ko": "덴마마치",
  "en": "Tenmamachi"
 },
 "久宝寺口": {
  "ko": "규호지쿠치",
  "en": "Kyuhojikuchi"
 },
 "塩釜口": {
  "ko": "시오가마쿠치",
  "en": "Shiogamakuchi"
 },
 "寒河": {
  "ko": "소고",
  "en": "Sogo"
 },
 "松山市": {
  "ko": "마쓰야마시",
  "en": "Matsuyamashi"
 },
 "黒磯": {
  "ko": "구로이소",
  "en": "Kuroiso"
 },
 "平岸（札幌市営）": {
  "ko": "히라기시삿포로시에이",
  "en": "Hiragishi(Sapporoshiei)"
 },
 "和歌山市": {
  "ko": "와카야마시",
  "en": "Wakayamashi"
 },
 "高岡": {
  "ko": "다카오카",
  "en": "Takaoka"
 },
 "船尾": {
  "ko": "센비",
  "en": "Senbi"
 },
 "木更津": {
  "ko": "기사라즈",
  "en": "Kisarazu"
 },
 "尼ケ坂": {
  "ko": "아마케사카",
  "en": "Amakesaka"
 },
 "はなみずき通": {
  "ko": "하나미즈키토오리",
  "en": "Hanamizukitori"
 },
 "美祢市その他": {
  "ko": "미네시소노호카",
  "en": "Mineshisonohoka"
 },
 "氷見": {
  "ko": "히미",
  "en": "Himi"
 },
 "岩切": {
  "ko": "이와키리",
  "en": "Iwakiri"
 },
 "笠岡": {
  "ko": "가사오카",
  "en": "Kasaoka"
 },
 "西大宮": {
  "ko": "니시오미야",
  "en": "Nishiomiya"
 },
 "倉敷": {
  "ko": "구라시키",
  "en": "Kurashiki"
 },
 "祇園新橋北": {
  "ko": "기온신바시키타",
  "en": "Gionshinbashikita"
 },
 "勝浦市その他": {
  "ko": "가쓰우라시소노호카",
  "en": "Katsurashisonohoka"
 },
 "上尾": {
  "ko": "아게오",
  "en": "Ageo"
 },
 "白河": {
  "ko": "시라카와",
  "en": "Shirakawa"
 },
 "南平岸": {
  "ko": "미나미히라기시",
  "en": "Minamihiragishi"
 },
 "ドーム前": {
  "ko": "도무마에",
  "en": "Domumae"
 },
 "東野": {
  "ko": "히가시노",
  "en": "Higashino"
 },
 "渋沢": {
  "ko": "시부사와",
  "en": "Shibusawa"
 },
 "堺東": {
  "ko": "사카이히가시",
  "en": "Sakaihigashi"
 },
 "茂林寺前": {
  "ko": "모린테라마에",
  "en": "Morinteramae"
 },
 "杉田": {
  "ko": "스기타",
  "en": "Sugita"
 },
 "薬師堂": {
  "ko": "야쿠시도",
  "en": "Yakushido"
 },
 "せきてらす前": {
  "ko": "세키테라스마에",
  "en": "Sekiterasumae"
 },
 "細谷": {
  "ko": "호소야",
  "en": "Hosoya"
 },
 "伊東": {
  "ko": "이토",
  "en": "Ito"
 },
 "島原船津": {
  "ko": "시마바라후나쓰",
  "en": "Shimabarafunatsu"
 },
 "那須町その他": {
  "ko": "나스마치소노호카",
  "en": "Nasumachisonohoka"
 },
 "北久里浜": {
  "ko": "기타쿠리하마",
  "en": "Kitakurihama"
 },
 "百合ケ丘": {
  "ko": "유리케오카",
  "en": "Yurikeoka"
 },
 "大津": {
  "ko": "오쓰",
  "en": "Otsu"
 },
 "近鉄四日市": {
  "ko": "긴테쓰욧카이치",
  "en": "Kintetsuyokkaichi"
 },
 "富雄": {
  "ko": "도미오",
  "en": "Tomio"
 },
 "蓮田": {
  "ko": "하스다",
  "en": "Hasuda"
 },
 "苅藻": {
  "ko": "가리모",
  "en": "Karimo"
 },
 "志賀本通": {
  "ko": "시가혼도오리",
  "en": "Shigahondori"
 },
 "千林大宮": {
  "ko": "센바야시오미야",
  "en": "Senbayashiomiya"
 },
 "奥多摩": {
  "ko": "오쿠타마",
  "en": "Okutama"
 },
 "平和": {
  "ko": "헤이와",
  "en": "Heiwa"
 },
 "北鴻巣": {
  "ko": "기타코노스",
  "en": "Kitakonosu"
 },
 "宮崎": {
  "ko": "미야자키",
  "en": "Miyazaki"
 },
 "川島町その他": {
  "ko": "가와시마마치소노호카",
  "en": "Kawashimamachisonohoka"
 },
 "宮前": {
  "ko": "미야마에",
  "en": "Miyamae"
 },
 "あびこ": {
  "ko": "아비코",
  "en": "Abiko"
 },
 "台中": {
  "ko": "다이추",
  "en": "Taichu"
 },
 "植田（名古屋市営）": {
  "ko": "우에다나고야시에이",
  "en": "Ueda(Nagoyashiei)"
 },
 "大通": {
  "ko": "오도오리",
  "en": "Odori"
 },
 "本郷台": {
  "ko": "혼고다이",
  "en": "Hongodai"
 },
 "西大路": {
  "ko": "니시오지",
  "en": "Nishioji"
 },
 "東津山": {
  "ko": "히가시쓰야마",
  "en": "Higashitsuyama"
 },
 "関": {
  "ko": "간",
  "en": "Kan"
 },
 "戸倉": {
  "ko": "도쿠라",
  "en": "Tokura"
 },
 "十文字": {
  "ko": "주몬지",
  "en": "Jumonji"
 },
 "松川町": {
  "ko": "마쓰카와초",
  "en": "Matsukawacho"
 },
 "郡山富田": {
  "ko": "고리야마토미타",
  "en": "Koriyamatomita"
 },
 "多治見": {
  "ko": "다지미",
  "en": "Tajimi"
 },
 "唐津": {
  "ko": "가라쓰",
  "en": "Karatsu"
 },
 "まんのう町その他": {
  "ko": "만노마치소노호카",
  "en": "Mannomachisonohoka"
 },
 "太田": {
  "ko": "오타",
  "en": "Ota"
 },
 "伊那北": {
  "ko": "이나키타",
  "en": "Inakita"
 },
 "島田": {
  "ko": "시마다",
  "en": "Shimada"
 },
 "新百合ケ丘": {
  "ko": "신유리케오카",
  "en": "Shinyurikeoka"
 },
 "沼津": {
  "ko": "누마즈",
  "en": "Numazu"
 },
 "西千葉": {
  "ko": "니시치바",
  "en": "Nishichiba"
 },
 "南行徳": {
  "ko": "미나미유키토쿠",
  "en": "Minamiyukitoku"
 },
 "中山": {
  "ko": "나카야마",
  "en": "Nakayama"
 },
 "金沢八景": {
  "ko": "가나자와핫케이",
  "en": "Kanazawahakkei"
 },
 "館林": {
  "ko": "다테바야시",
  "en": "Tatebayashi"
 },
 "箱根板橋": {
  "ko": "하코네이타바시",
  "en": "Hakoneitabashi"
 },
 "長池": {
  "ko": "나가이케",
  "en": "Nagaike"
 },
 "大曲": {
  "ko": "오마가리",
  "en": "Omagari"
 },
 "三条市その他": {
  "ko": "산조시소노호카",
  "en": "Sanjoshisonohoka"
 },
 "東別府": {
  "ko": "히가시벳푸",
  "en": "Higashibeppu"
 },
 "肥後大津": {
  "ko": "히고오쓰",
  "en": "Higootsu"
 },
 "山手": {
  "ko": "야마테",
  "en": "Yamate"
 },
 "南宮崎": {
  "ko": "미나미미야자키",
  "en": "Minamimiyazaki"
 },
 "山中湖村その他": {
  "ko": "야마나카코무라소노호카",
  "en": "Yamanakakomurasonohoka"
 },
 "入地": {
  "ko": "뉴치",
  "en": "Nyuchi"
 },
 "河口湖": {
  "ko": "가와구치코",
  "en": "Kawaguchiko"
 },
 "盛岡": {
  "ko": "모리오카",
  "en": "Morioka"
 },
 "三崎口": {
  "ko": "미사키구치",
  "en": "Misakiguchi"
 },
 "三ツ境": {
  "ko": "산쓰사카이",
  "en": "Santsusakai"
 },
 "撫牛子": {
  "ko": "부우시코",
  "en": "Bushiko"
 },
 "東諫早": {
  "ko": "히가시이사하야",
  "en": "Higashiisahaya"
 },
 "筑後大石": {
  "ko": "지쿠고오이시",
  "en": "Chikugooishi"
 },
 "牧志": {
  "ko": "마키시",
  "en": "Makishi"
 },
 "あすなろう四日市": {
  "ko": "아스나로욧카이치",
  "en": "Asunaroyokkaichi"
 },
 "浜田": {
  "ko": "하마다",
  "en": "Hamada"
 },
 "神保原": {
  "ko": "진보하라",
  "en": "Jinbohara"
 },
 "今福鶴見": {
  "ko": "이마후쿠쓰루미",
  "en": "Imafukutsurumi"
 },
 "飯山": {
  "ko": "이이야마",
  "en": "Iiyama"
 },
 "奈良": {
  "ko": "나라",
  "en": "Nara"
 },
 "八幡宿": {
  "ko": "하치만야도",
  "en": "Hachimanyado"
 },
 "大小路": {
  "ko": "다이쇼미치",
  "en": "Daishomichi"
 },
 "潮見": {
  "ko": "시오미",
  "en": "Shiomi"
 },
 "白石（ＪＲ北海道）": {
  "ko": "시로이시홋카이도",
  "en": "Shiroishi(Jrhokkaido)"
 },
 "京終": {
  "ko": "교바테",
  "en": "Kyobate"
 },
 "清水": {
  "ko": "시미즈",
  "en": "Shimizu"
 },
 "湘南台": {
  "ko": "쇼난다이",
  "en": "Shonandai"
 },
 "大磯": {
  "ko": "오이소",
  "en": "Oiso"
 },
 "岡町": {
  "ko": "오카초",
  "en": "Okacho"
 },
 "富浦": {
  "ko": "도미우라",
  "en": "Tomiura"
 },
 "センター北": {
  "ko": "센타키타",
  "en": "Sentaakita"
 },
 "東武日光": {
  "ko": "도부닛코",
  "en": "Tobunikko"
 },
 "敦賀": {
  "ko": "쓰루가",
  "en": "Tsuruga"
 },
 "壺川": {
  "ko": "쓰보가와",
  "en": "Tsubogawa"
 },
 "大国町": {
  "ko": "다이코쿠초",
  "en": "Daikokucho"
 },
 "西帯広": {
  "ko": "니시오비히로",
  "en": "Nishiobihiro"
 },
 "鴨居": {
  "ko": "가모이",
  "en": "Kamoi"
 },
 "新長田": {
  "ko": "신나가타",
  "en": "Shinnagata"
 },
 "六浦": {
  "ko": "무쓰우라",
  "en": "Mutsura"
 },
 "袖ケ浦": {
  "ko": "소데케우라",
  "en": "Sodekeura"
 },
 "二俣川": {
  "ko": "후타마타가와",
  "en": "Futamatagawa"
 },
 "法隆寺": {
  "ko": "호류지",
  "en": "Horyuji"
 },
 "伊丹（ＪＲ）": {
  "ko": "이타미",
  "en": "Itami(Jr)"
 },
 "伊豆急下田": {
  "ko": "이즈큐시모다",
  "en": "Izukyushimoda"
 },
 "大麻": {
  "ko": "다이마",
  "en": "Taima"
 },
 "住吉（ＪＲ・六甲ライナー）": {
  "ko": "스미요시롯코라이나",
  "en": "Sumiyoshi(Jr・Rokkorainaa)"
 },
 "石橋阪大前": {
  "ko": "이시바시한다이마에",
  "en": "Ishibashihandaimae"
 },
 "榎町": {
  "ko": "에노마치",
  "en": "Enomachi"
 },
 "北１２条": {
  "ko": "기타조",
  "en": "Kita12Jo"
 },
 "紀伊天満": {
  "ko": "기이텐마",
  "en": "Kiitenma"
 },
 "湘南江の島": {
  "ko": "쇼난코노시마",
  "en": "Shonankonoshima"
 },
 "七日町": {
  "ko": "나누카마치",
  "en": "Nanukamachi"
 },
 "赤磐市その他": {
  "ko": "아카이와시소노호카",
  "en": "Akaiwashisonohoka"
 },
 "六会日大前": {
  "ko": "무쓰아이니치다이마에",
  "en": "Mutsuainichidaimae"
 },
 "南陽市役所": {
  "ko": "난요시야쿠쇼",
  "en": "Nanyoshiyakusho"
 },
 "東大垣": {
  "ko": "도다이카키",
  "en": "Todaikaki"
 },
 "小町屋": {
  "ko": "고마치야",
  "en": "Komachiya"
 },
 "大和小泉": {
  "ko": "야마토코이즈미",
  "en": "Yamatokoizumi"
 },
 "平城山": {
  "ko": "나라야마",
  "en": "Narayama"
 },
 "常陸太田": {
  "ko": "히타치오타",
  "en": "Hitachiota"
 },
 "下松": {
  "ko": "구다마쓰",
  "en": "Kudamatsu"
 },
 "行天宮周辺": {
  "ko": "교텐미야슈헨",
  "en": "Gyotenmiyashuhen"
 },
 "美江寺": {
  "ko": "미에테라",
  "en": "Mietera"
 },
 "上枝": {
  "ko": "우에에다",
  "en": "Ueeda"
 },
 "新神戸": {
  "ko": "신코베",
  "en": "Shinkobe"
 },
 "リゾートゲートウェイ・ステーション": {
  "ko": "리조토게토이스테숀",
  "en": "Rizotogeetoei・Suteeshon"
 },
 "佐和": {
  "ko": "사와",
  "en": "Sawa"
 },
 "安曇追分": {
  "ko": "아즈미오이와케",
  "en": "Azumioiwake"
 },
 "上狛": {
  "ko": "우에코마",
  "en": "Uekoma"
 },
 "民権西路駅周辺": {
  "ko": "민켄니시미치에키슈헨",
  "en": "Minkennishimichiekishuhen"
 },
 "上ゲ": {
  "ko": "우에게",
  "en": "Uege"
 },
 "能代": {
  "ko": "노시로",
  "en": "Noshiro"
 },
 "勝浦": {
  "ko": "가쓰우라",
  "en": "Katsura"
 },
 "牛久": {
  "ko": "우시쿠",
  "en": "Ushiku"
 },
 "新三田": {
  "ko": "신미타",
  "en": "Shinmita"
 },
 "忠孝新生駅周辺": {
  "ko": "주코신세이에키슈헨",
  "en": "Chukoshinseiekishuhen"
 },
 "羽鳥": {
  "ko": "하토리",
  "en": "Hatori"
 },
 "箕島": {
  "ko": "미노시마",
  "en": "Minoshima"
 },
 "旭川": {
  "ko": "아사히카와",
  "en": "Asahikawa"
 },
 "西二見": {
  "ko": "니시후타미",
  "en": "Nishifutami"
 },
 "金蔵寺": {
  "ko": "긴조테라",
  "en": "Kinzotera"
 },
 "隼人": {
  "ko": "하야토",
  "en": "Hayato"
 },
 "阿蘇下田城": {
  "ko": "아소시모다시로",
  "en": "Asoshimodashiro"
 },
 "たけふ新": {
  "ko": "다케후신",
  "en": "Takefushin"
 },
 "南気仙沼": {
  "ko": "미나미케센누마",
  "en": "Minamikesennuma"
 },
 "生駒": {
  "ko": "이코마",
  "en": "Ikoma"
 },
 "西小坂井": {
  "ko": "니시코자카이",
  "en": "Nishikozakai"
 },
 "北坂戸": {
  "ko": "기타사카코",
  "en": "Kitasakako"
 },
 "中田": {
  "ko": "나카다",
  "en": "Nakada"
 },
 "神俣": {
  "ko": "간마타",
  "en": "Kanmata"
 },
 "三浦半島その他": {
  "ko": "미우라한시마소노호카",
  "en": "Miurahanshimasonohoka"
 },
 "河内松原": {
  "ko": "가와우치마쓰바라",
  "en": "Kawauchimatsubara"
 },
 "串木野": {
  "ko": "구시키노",
  "en": "Kushikino"
 },
 "東金": {
  "ko": "도가네",
  "en": "Togane"
 },
 "代官町": {
  "ko": "다이칸마치",
  "en": "Daikanmachi"
 },
 "八木原": {
  "ko": "야기하라",
  "en": "Yagihara"
 },
 "嬬恋村その他": {
  "ko": "쓰마고이무라소노호카",
  "en": "Tsumagoimurasonohoka"
 },
 "高山村その他": {
  "ko": "고잔무라소노호카",
  "en": "Kozanmurasonohoka"
 },
 "下新田": {
  "ko": "시모신덴",
  "en": "Shimoshinden"
 },
 "草津": {
  "ko": "구사쓰",
  "en": "Kusatsu"
 },
 "旭": {
  "ko": "아사히",
  "en": "Asahi"
 },
 "市田": {
  "ko": "이치다",
  "en": "Ichida"
 },
 "能生": {
  "ko": "노",
  "en": "No"
 },
 "人吉": {
  "ko": "히토요시",
  "en": "Hitoyoshi"
 },
 "八尾": {
  "ko": "야오",
  "en": "Yao"
 },
 "手稲": {
  "ko": "데이네",
  "en": "Teine"
 },
 "山城多賀": {
  "ko": "야마시로타가",
  "en": "Yamashirotaga"
 },
 "三島": {
  "ko": "미시마",
  "en": "Mishima"
 },
 "由布院": {
  "ko": "유후인",
  "en": "Yufuin"
 },
 "親鼻": {
  "ko": "오야하나",
  "en": "Oyahana"
 },
 "常陸太田市その他": {
  "ko": "히타치오타시소노호카",
  "en": "Hitachiotashisonohoka"
 },
 "伊勢崎": {
  "ko": "이세사키",
  "en": "Isesaki"
 },
 "武生": {
  "ko": "다케후",
  "en": "Takefu"
 },
 "すずらんの里": {
  "ko": "스즈란노사토",
  "en": "Suzurannosato"
 },
 "丸森": {
  "ko": "마루모리",
  "en": "Marumori"
 },
 "七光台": {
  "ko": "나나히카리다이",
  "en": "Nanahikaridai"
 },
 "南仙台": {
  "ko": "미나미센다이",
  "en": "Minamisendai"
 },
 "伊奈": {
  "ko": "이나",
  "en": "Ina"
 },
 "湯沢": {
  "ko": "유자와",
  "en": "Yuzawa"
 },
 "魚沼田中": {
  "ko": "우오누마타나카",
  "en": "Uonumatanaka"
 },
 "掛川": {
  "ko": "가케가와",
  "en": "Kakegawa"
 },
 "鴨川": {
  "ko": "가모가와",
  "en": "Kamogawa"
 },
 "鞍馬": {
  "ko": "구라마",
  "en": "Kurama"
 },
 "手力": {
  "ko": "데치카라",
  "en": "Techikara"
 },
 "羽後本荘": {
  "ko": "우고혼조",
  "en": "Ugohonjo"
 },
 "京阪山科": {
  "ko": "게이한야마시나",
  "en": "Keihanyamashina"
 },
 "石動": {
  "ko": "이스루기",
  "en": "Isurugi"
 },
 "御門台": {
  "ko": "미카도다이",
  "en": "Mikadodai"
 },
 "美濃高田": {
  "ko": "미노타카다",
  "en": "Minotakada"
 },
 "大阪空港": {
  "ko": "오사카쿠우코",
  "en": "Osakakuko"
 },
 "朝来": {
  "ko": "아사고",
  "en": "Asago"
 },
 "京成稲毛": {
  "ko": "게이세이이나게",
  "en": "Keiseiinage"
 },
 "船戸": {
  "ko": "후나도",
  "en": "Funado"
 },
 "伊豆長岡": {
  "ko": "이즈나가오카",
  "en": "Izunagaoka"
 },
 "北広島": {
  "ko": "기타히로시마",
  "en": "Kitahiroshima"
 },
 "中島公園": {
  "ko": "나카지마코엔",
  "en": "Nakajimakoen"
 },
 "会津若松": {
  "ko": "아이즈와카마쓰",
  "en": "Aizuwakamatsu"
 },
 "尾道": {
  "ko": "오노미치",
  "en": "Onomichi"
 },
 "大垣": {
  "ko": "오가키",
  "en": "Ogaki"
 },
 "伊丹（阪急）": {
  "ko": "이타미한큐",
  "en": "Itami(Hankyu)"
 },
 "倉吉": {
  "ko": "구라요시",
  "en": "Kurayoshi"
 },
 "印旛日本医大": {
  "ko": "인바닛폰이다이",
  "en": "Inbanipponidai"
 },
 "幕張本郷": {
  "ko": "마쿠하리혼고",
  "en": "Makuharihongo"
 },
 "余呉": {
  "ko": "요고",
  "en": "Yogo"
 },
 "南区役所前": {
  "ko": "미나미쿠야쿠쇼마에",
  "en": "Minamikuyakushomae"
 },
 "中電前": {
  "ko": "주덴마에",
  "en": "Chudenmae"
 },
 "中島公園通": {
  "ko": "나카지마코엔토오리",
  "en": "Nakajimakoentori"
 },
 "井原": {
  "ko": "이하라",
  "en": "Ihara"
 },
 "南高田": {
  "ko": "미나미다카타",
  "en": "Minamidakata"
 },
 "佐賀": {
  "ko": "사가",
  "en": "Saga"
 },
 "吉成": {
  "ko": "요시나리",
  "en": "Yoshinari"
 },
 "新千歳空港": {
  "ko": "신치토세쿠우코",
  "en": "Shinchitosekuko"
 },
 "岩出": {
  "ko": "이와데",
  "en": "Iwade"
 },
 "城端": {
  "ko": "조하나",
  "en": "Johana"
 },
 "下野宮": {
  "ko": "시모쓰케미야",
  "en": "Shimotsukemiya"
 },
 "十日市町": {
  "ko": "도오카이치마치",
  "en": "Tokaichimachi"
 },
 "新宮": {
  "ko": "신구우",
  "en": "Shingu"
 },
 "宇島": {
  "ko": "우시마",
  "en": "Ushima"
 },
 "本竜野": {
  "ko": "혼류노",
  "en": "Honryuno"
 },
 "物井": {
  "ko": "모노이",
  "en": "Monoi"
 },
 "新庄": {
  "ko": "신조",
  "en": "Shinjo"
 },
 "はりま勝原": {
  "ko": "하리마카쓰하라",
  "en": "Harimakatsuhara"
 },
 "勝川（東海交通）": {
  "ko": "가쓰카와토카이코쓰우",
  "en": "Katsukawa(Tokaikotsu)"
 },
 "星ケ丘": {
  "ko": "호시케오카",
  "en": "Hoshikeoka"
 },
 "千歳": {
  "ko": "지토세",
  "en": "Chitose"
 },
 "都留文科大学前": {
  "ko": "쓰루분카다이가쿠마에",
  "en": "Tsurubunkadaigakumae"
 },
 "名護市": {
  "ko": "나고시",
  "en": "Nagoshi"
 },
 "貴船口": {
  "ko": "기후네쿠치",
  "en": "Kifunekuchi"
 },
 "三瀬": {
  "ko": "미쓰세",
  "en": "Mitsuse"
 },
 "小田林": {
  "ko": "오다하야시",
  "en": "Odahayashi"
 },
 "中萱": {
  "ko": "나카카야",
  "en": "Nakakaya"
 },
 "住道": {
  "ko": "스미노도",
  "en": "Suminodo"
 },
 "河瀬": {
  "ko": "가와세",
  "en": "Kawase"
 },
 "光岡": {
  "ko": "미쓰오카",
  "en": "Mitsuoka"
 },
 "番田": {
  "ko": "반타",
  "en": "Banta"
 },
 "藤阪": {
  "ko": "후지사카",
  "en": "Fujisaka"
 },
 "下祇園": {
  "ko": "시타기온",
  "en": "Shitagion"
 },
 "嘉義": {
  "ko": "가기",
  "en": "Kagi"
 },
 "那賀町その他": {
  "ko": "나카마치소노호카",
  "en": "Nakamachisonohoka"
 },
 "南由布": {
  "ko": "미나미유후",
  "en": "Minamiyufu"
 },
 "電鉄魚津": {
  "ko": "덴테쓰우오즈",
  "en": "Dentetsuozu"
 },
 "津和野": {
  "ko": "쓰와노",
  "en": "Tsuwano"
 },
 "帯解": {
  "ko": "오비카이",
  "en": "Obikai"
 },
 "新ノ口": {
  "ko": "신노쿠치",
  "en": "Shinnokuchi"
 },
 "加勢": {
  "ko": "가세이",
  "en": "Kasei"
 },
 "上挙母": {
  "ko": "우에코로모",
  "en": "Uekoromo"
 },
 "八橋": {
  "ko": "야쓰하시",
  "en": "Yatsuhashi"
 },
 "市政府駅周辺": {
  "ko": "시세이후에키슈헨",
  "en": "Shiseifuekishuhen"
 },
 "桔梗": {
  "ko": "기쿄",
  "en": "Kikyo"
 },
 "藤並": {
  "ko": "후지나미",
  "en": "Fujinami"
 },
 "島尾": {
  "ko": "시마오",
  "en": "Shimao"
 },
 "剛志": {
  "ko": "다케시",
  "en": "Takeshi"
 },
 "上総松丘": {
  "ko": "가즈사마쓰오카",
  "en": "Kazusamatsuoka"
 },
 "荘原": {
  "ko": "쇼바라",
  "en": "Shobara"
 },
 "内牧": {
  "ko": "우치마키",
  "en": "Uchimaki"
 },
 "京成幕張本郷": {
  "ko": "게이세이마쿠하리혼고",
  "en": "Keiseimakuharihongo"
 },
 "玉淀": {
  "ko": "다마요도",
  "en": "Tamayodo"
 },
 "桂台": {
  "ko": "가쓰라다이",
  "en": "Katsuradai"
 },
 "二和向台": {
  "ko": "후타와무카에다이",
  "en": "Futawamukaedai"
 },
 "越後湯沢": {
  "ko": "에치고유자와",
  "en": "Echigoyuzawa"
 },
 "富士川": {
  "ko": "후지가와",
  "en": "Fujigawa"
 },
 "象潟": {
  "ko": "기사카타",
  "en": "Kisakata"
 },
 "二月田": {
  "ko": "니가쓰덴",
  "en": "Nigatsuden"
 },
 "下妻": {
  "ko": "시모즈마",
  "en": "Shimozuma"
 },
 "白浜": {
  "ko": "시라하마",
  "en": "Shirahama"
 },
 "岩国": {
  "ko": "이와쿠니",
  "en": "Iwakuni"
 },
 "谷村町": {
  "ko": "다니무라마치",
  "en": "Tanimuramachi"
 },
 "津軽新城": {
  "ko": "쓰가루신조",
  "en": "Tsugarushinjo"
 },
 "西桑名": {
  "ko": "니시쿠와나",
  "en": "Nishikuwana"
 },
 "芦屋（阪神）": {
  "ko": "아시야한신",
  "en": "Ashiya(Hanshin)"
 },
 "平原": {
  "ko": "헤이겐",
  "en": "Heigen"
 },
 "三原": {
  "ko": "미하라",
  "en": "Mihara"
 },
 "三野瀬": {
  "ko": "미노세",
  "en": "Minose"
 },
 "豊頃": {
  "ko": "도요코로",
  "en": "Toyokoro"
 },
 "椎田": {
  "ko": "시이다",
  "en": "Shiida"
 },
 "黒石": {
  "ko": "구로이시",
  "en": "Kuroishi"
 },
 "瑞浪市その他": {
  "ko": "미즈나미시소노호카",
  "en": "Mizunamishisonohoka"
 },
 "土橋": {
  "ko": "도바시",
  "en": "Dobashi"
 },
 "舟入川口町": {
  "ko": "후나이리카와구치마치",
  "en": "Funairikawaguchimachi"
 },
 "北山": {
  "ko": "기타야마",
  "en": "Kitayama"
 },
 "学園前": {
  "ko": "가쿠엔마에",
  "en": "Gakuenmae"
 },
 "七尾": {
  "ko": "나나오",
  "en": "Nanao"
 },
 "さくら市その他": {
  "ko": "사쿠라시소노호카",
  "en": "Sakurashisonohoka"
 },
 "三岡": {
  "ko": "미쓰오카",
  "en": "Mitsuoka"
 },
 "下今市": {
  "ko": "시타이마이치",
  "en": "Shitaimaichi"
 },
 "新青森": {
  "ko": "신아오모리",
  "en": "Shinaomori"
 },
 "松尾": {
  "ko": "마쓰오",
  "en": "Matsuo"
 },
 "津山": {
  "ko": "쓰야마",
  "en": "Tsuyama"
 },
 "中之条町その他": {
  "ko": "나카노조마치소노호카",
  "en": "Nakanojomachisonohoka"
 },
 "名古屋大学": {
  "ko": "나고야다이가쿠",
  "en": "Nagoyadaigaku"
 },
 "田辺市その他": {
  "ko": "다나베시소노호카",
  "en": "Tanabeshisonohoka"
 },
 "栗橋": {
  "ko": "구리하시",
  "en": "Kurihashi"
 },
 "打出": {
  "ko": "우치이데",
  "en": "Uchiide"
 },
 "不動の沢": {
  "ko": "후도노사와",
  "en": "Fudonosawa"
 },
 "南中郷": {
  "ko": "난추사토",
  "en": "Nanchusato"
 },
 "国府多賀城": {
  "ko": "고타가조",
  "en": "Kotagajo"
 },
 "東觜崎": {
  "ko": "히가시하시사키",
  "en": "Higashihashisaki"
 },
 "大網": {
  "ko": "오아미",
  "en": "Oami"
 },
 "呼人": {
  "ko": "요비토",
  "en": "Yobito"
 },
 "桜町": {
  "ko": "사쿠라마치",
  "en": "Sakuramachi"
 },
 "村野": {
  "ko": "무라노",
  "en": "Murano"
 },
 "小見川": {
  "ko": "오미가와",
  "en": "Omigawa"
 },
 "広大附属学校前": {
  "ko": "고다이후조쿠갓코마에",
  "en": "Kodaifuzokugakkomae"
 },
 "東福寺": {
  "ko": "도후쿠지",
  "en": "Tofukuji"
 },
 "潮来": {
  "ko": "이타코",
  "en": "Itako"
 },
 "楽々園": {
  "ko": "라쿠라쿠소노",
  "en": "Rakurakusono"
 },
 "新尾道": {
  "ko": "신오노미치",
  "en": "Shin'Onomichi"
 },
 "常陸大子": {
  "ko": "히타치오고",
  "en": "Hitachiogo"
 },
 "大和高田": {
  "ko": "야마토타카다",
  "en": "Yamatotakada"
 },
 "松井山手": {
  "ko": "마쓰이야마테",
  "en": "Matsuiyamate"
 },
 "雙連駅周辺": {
  "ko": "소렌에키슈헨",
  "en": "Sorenekishuhen"
 },
 "原水": {
  "ko": "하라미즈",
  "en": "Haramizu"
 },
 "江ノ島": {
  "ko": "고노시마",
  "en": "Konoshima"
 },
 "ひばりが丘": {
  "ko": "히바리가오카",
  "en": "Hibarigaoka"
 },
 "南郷１８丁目": {
  "ko": "난고초메",
  "en": "Nango18Chome"
 },
 "二本松市その他": {
  "ko": "니혼마쓰시소노호카",
  "en": "Nihonmatsushisonohoka"
 },
 "桑名": {
  "ko": "구와나",
  "en": "Kuwana"
 },
 "津久田": {
  "ko": "쓰쿠타",
  "en": "Tsukuta"
 },
 "住吉（阪神）": {
  "ko": "스미요시한신",
  "en": "Sumiyoshi(Hanshin)"
 },
 "日原": {
  "ko": "히하라",
  "en": "Hihara"
 },
 "東生駒": {
  "ko": "하루오코마",
  "en": "Haruokoma"
 },
 "安積永盛": {
  "ko": "아사카에이조",
  "en": "Asakaeijo"
 },
 "忠孝復興駅周辺": {
  "ko": "주코훗코에키슈헨",
  "en": "Chukofukkoekishuhen"
 },
 "西川町その他": {
  "ko": "니시가와초소노호카",
  "en": "Nishigawachosonohoka"
 },
 "伊那市": {
  "ko": "이나시",
  "en": "Inashi"
 },
 "境松": {
  "ko": "사카이마쓰",
  "en": "Sakaimatsu"
 },
 "りんくう常滑": {
  "ko": "린쿠우토코나메",
  "en": "Rinkutokoname"
 },
 "みの": {
  "ko": "미노",
  "en": "Mino"
 },
 "信濃平": {
  "ko": "시나노타이라",
  "en": "Shinanotaira"
 },
 "富士宮": {
  "ko": "후지노미야",
  "en": "Fujinomiya"
 },
 "舟入幸町": {
  "ko": "후나이리사이와이초",
  "en": "Funairisaiwaicho"
 },
 "新町": {
  "ko": "신마치",
  "en": "Shinmachi"
 },
 "行方市その他": {
  "ko": "나메가타시소노호카",
  "en": "Namegatashisonohoka"
 },
 "丸亀": {
  "ko": "마루가메",
  "en": "Marugame"
 },
 "ウッディタウン中央": {
  "ko": "웃데타운추오",
  "en": "Uddeitaunchuo"
 },
 "本通": {
  "ko": "혼도오리",
  "en": "Hondori"
 },
 "赤湯": {
  "ko": "아카유",
  "en": "Akayu"
 },
 "天童南": {
  "ko": "덴도미나미",
  "en": "Tendominami"
 },
 "岩屋": {
  "ko": "이와야",
  "en": "Iwaya"
 },
 "上今市": {
  "ko": "우에이마이치",
  "en": "Ueimaichi"
 },
 "駒ケ根": {
  "ko": "고마케네",
  "en": "Komakene"
 },
 "岩本": {
  "ko": "이와모토",
  "en": "Iwamoto"
 },
 "後藤": {
  "ko": "고토",
  "en": "Goto"
 },
 "中新湊": {
  "ko": "주신미나토",
  "en": "Chushinminato"
 },
 "向島": {
  "ko": "고시마",
  "en": "Koshima"
 },
 "新井": {
  "ko": "아라이",
  "en": "Arai"
 },
 "新魚津": {
  "ko": "신우오즈",
  "en": "Shinuozu"
 },
 "粟津": {
  "ko": "아와즈",
  "en": "Awazu"
 },
 "大橋通": {
  "ko": "오하시토오리",
  "en": "Ohashitori"
 },
 "二本松": {
  "ko": "니혼마쓰",
  "en": "Nihonmatsu"
 },
 "烏山": {
  "ko": "가라스야마",
  "en": "Karasuyama"
 },
 "大宝": {
  "ko": "다이호",
  "en": "Taiho"
 },
 "須坂": {
  "ko": "스자카",
  "en": "Suzaka"
 },
 "角館": {
  "ko": "가쿠노다테",
  "en": "Kakunodate"
 },
 "津ノ井": {
  "ko": "쓰노이",
  "en": "Tsunoi"
 },
 "北１３条東": {
  "ko": "기타조히가시",
  "en": "Kita13Johigashi"
 },
 "紙屋町東": {
  "ko": "가미야초히가시",
  "en": "Kamiyachohigashi"
 },
 "信濃松川": {
  "ko": "시나노마쓰카와",
  "en": "Shinanomatsukawa"
 },
 "中津": {
  "ko": "나카쓰",
  "en": "Nakatsu"
 },
 "佐賀市その他": {
  "ko": "사가시소노호카",
  "en": "Sagashisonohoka"
 },
 "勝田": {
  "ko": "가쓰타",
  "en": "Katsuta"
 },
 "西門町": {
  "ko": "니시카도마치",
  "en": "Nishikadomachi"
 },
 "五百石": {
  "ko": "고햐쿠이시",
  "en": "Gohyakuishi"
 },
 "堀詰": {
  "ko": "호리즈메",
  "en": "Horizume"
 },
 "鉢形": {
  "ko": "하치가타",
  "en": "Hachigata"
 },
 "壬生": {
  "ko": "미부",
  "en": "Mibu"
 },
 "上盛岡": {
  "ko": "우에모리오카",
  "en": "Uemorioka"
 },
 "泉中央": {
  "ko": "이즈미추오",
  "en": "Izumichuo"
 },
 "笠田": {
  "ko": "가사다",
  "en": "Kasada"
 },
 "三河豊田": {
  "ko": "미카와토요다",
  "en": "Mikawatoyoda"
 },
 "光": {
  "ko": "히카리",
  "en": "Hikari"
 },
 "南アルプス市その他": {
  "ko": "미나미아루푸스시소노호카",
  "en": "Minamiarupusushisonohoka"
 },
 "味岡": {
  "ko": "아지오카",
  "en": "Ajioka"
 },
 "奥武山公園": {
  "ko": "오산코소노",
  "en": "Osankosono"
 },
 "人吉温泉": {
  "ko": "히토요시온센",
  "en": "Hitoyoshionsen"
 },
 "勝瑞": {
  "ko": "쇼즈이",
  "en": "Shozui"
 },
 "上長瀞": {
  "ko": "조초토로",
  "en": "Jochotoro"
 },
 "本部町": {
  "ko": "혼부마치",
  "en": "Honbumachi"
 },
 "北大路": {
  "ko": "기타오지",
  "en": "Kitaoji"
 },
 "切通": {
  "ko": "셋쓰우",
  "en": "Settsu"
 },
 "市役所": {
  "ko": "시야쿠쇼",
  "en": "Shiyakusho"
 },
 "東福山": {
  "ko": "도후쿠야마",
  "en": "Tofukuyama"
 },
 "佐伯区役所前": {
  "ko": "사에키쿠야쿠쇼마에",
  "en": "Saekikuyakushomae"
 },
 "津田": {
  "ko": "쓰다",
  "en": "Tsuda"
 },
 "北谷町": {
  "ko": "기타타니마치",
  "en": "Kitatanimachi"
 },
 "樟葉": {
  "ko": "구스노하",
  "en": "Kusunoha"
 },
 "忠孝敦化駅周辺": {
  "ko": "주코톤카에키슈헨",
  "en": "Chukotonkaekishuhen"
 },
 "新宿": {
  "ko": "신주쿠",
  "en": "Shinjuku"
 },
 "つつじケ丘": {
  "ko": "쓰쓰지케오카",
  "en": "Tsutsujikeoka"
 },
 "池下": {
  "ko": "이케시타",
  "en": "Ikeshita"
 },
 "大阪梅田（阪神）": {
  "ko": "오사카우메다（한신）",
  "en": "Osakaumeda(Hanshin)"
 },
 "覚王山": {
  "ko": "가쿠오잔",
  "en": "Kakuozan"
 },
 "千歳烏山": {
  "ko": "지토세카라스야마",
  "en": "Chitosekarasuyama"
 },
 "梅田": {
  "ko": "우메다",
  "en": "Umeda"
 },
 "ひばりケ丘": {
  "ko": "히바리케오카",
  "en": "Hibarikeoka"
 },
 "小田急多摩センター": {
  "ko": "오다큐타마센타",
  "en": "Odakyutamasentaa"
 },
 "千歳船橋": {
  "ko": "지토세후나바시",
  "en": "Chitosefunabashi"
 },
 "住吉": {
  "ko": "스미요시",
  "en": "Sumiyoshi"
 },
 "都立家政": {
  "ko": "도리쓰카세이",
  "en": "Toritsukasei"
 },
 "用賀": {
  "ko": "요가",
  "en": "Yoga"
 },
 "日本大通り": {
  "ko": "니혼다이토리",
  "en": "Nihondaitori"
 },
 "戸越銀座": {
  "ko": "도코시긴자",
  "en": "Tokoshiginza"
 },
 "中野富士見町": {
  "ko": "나카노후지미초",
  "en": "Nakanofujimicho"
 },
 "ナゴヤドーム前矢田": {
  "ko": "나고야도무마에야다",
  "en": "Nagoyadomumaeyada"
 },
 "新高島": {
  "ko": "니이타카시마",
  "en": "Niitakashima"
 },
 "難波（南海）": {
  "ko": "난바（난카이）",
  "en": "Nanba(Nankai)"
 },
 "美栄橋": {
  "ko": "요시에하시",
  "en": "Yoshiehashi"
 },
 "札幌（ＪＲ）": {
  "ko": "삿포로（ＪＲ）",
  "en": "Sapporo(Jr)"
 },
 "久我山": {
  "ko": "구가야마",
  "en": "Kugayama"
 },
 "京都河原町": {
  "ko": "교토카와라마치",
  "en": "Kyotokawaramachi"
 },
 "矢田": {
  "ko": "야다",
  "en": "Yada"
 },
 "都立大学": {
  "ko": "도리쓰다이가쿠",
  "en": "Toritsudaigaku"
 },
 "緑が丘": {
  "ko": "미도리가오카",
  "en": "Midorigaoka"
 },
 "浜田山": {
  "ko": "하마다야마",
  "en": "Hamadayama"
 },
 "武蔵関": {
  "ko": "무사시세키",
  "en": "Musashiseki"
 },
 "昭島": {
  "ko": "아키라시마",
  "en": "Akirashima"
 },
 "戸越": {
  "ko": "도코시",
  "en": "Tokoshi"
 },
 "豪徳寺": {
  "ko": "고토쿠지",
  "en": "Gotokuji"
 },
 "緑町": {
  "ko": "미도리마치",
  "en": "Midorimachi"
 },
 "地下鉄成増": {
  "ko": "지카테쓰나리마스",
  "en": "Chikatetsunarimasu"
 },
 "東武練馬": {
  "ko": "도부네리마",
  "en": "Tobunerima"
 },
 "亀島": {
  "ko": "가메시마",
  "en": "Kameshima"
 },
 "東村山": {
  "ko": "히가시무라야마",
  "en": "Higashimurayama"
 },
 "羽田空港第１ターミナル（東京モノレール）": {
  "ko": "하네다쿠우코다이이치타미나루（토쿄모노레루）",
  "en": "Hanedakukodaiichitaaminaru(Tokyomonoreeru)"
 },
 "市場前": {
  "ko": "시조마에",
  "en": "Shijomae"
 },
 "東京ディズニーランド・ステーション": {
  "ko": "도쿄데ぃ즈니란도・스테숀",
  "en": "Tokyodizuniirando・Suteeshon"
 },
 "綱島": {
  "ko": "쓰나시마",
  "en": "Tsunashima"
 },
 "御殿場": {
  "ko": "고텐바",
  "en": "Gotenba"
 },
 "京王よみうりランド": {
  "ko": "게이오요미우리란도",
  "en": "Keioyomiurirando"
 },
 "東淀川": {
  "ko": "히가시요도가와",
  "en": "Higashiyodogawa"
 },
 "長久手古戦場": {
  "ko": "나가쿠테코센조",
  "en": "Nagakutekosenjo"
 },
 "矢野口": {
  "ko": "야노구치",
  "en": "Yanoguchi"
 },
 "中部国際空港": {
  "ko": "주부코쿠사이쿠우코",
  "en": "Chubukokusaikuko"
 },
 "新所沢": {
  "ko": "신토코로자와",
  "en": "Shintokorozawa"
 },
 "栄生": {
  "ko": "사카에나마",
  "en": "Sakaenama"
 },
 "みなとみらい": {
  "ko": "미나토미라이",
  "en": "Minatomirai"
 },
 "浅間町": {
  "ko": "아사마마치",
  "en": "Asamamachi"
 },
 "豊田": {
  "ko": "도요다",
  "en": "Toyoda"
 },
 "相模大野": {
  "ko": "사가미오노",
  "en": "Sagamiono"
 },
 "西高蔵": {
  "ko": "니시코쿠라",
  "en": "Nishikokura"
 },
 "小幡": {
  "ko": "오바타",
  "en": "Obata"
 },
 "一社": {
  "ko": "잇샤",
  "en": "Issha"
 },
 "小樽": {
  "ko": "오타루",
  "en": "Otaru"
 },
 "那覇空港": {
  "ko": "나하쿠우코",
  "en": "Nahakuko"
 },
 "鶴川": {
  "ko": "쓰루카와",
  "en": "Tsurukawa"
 },
 "近鉄奈良": {
  "ko": "긴테쓰나라",
  "en": "Kintetsunara"
 },
 "板橋": {
  "ko": "이타바시",
  "en": "Itabashi"
 },
 "おもろまち": {
  "ko": "오모로마치",
  "en": "Omoromachi"
 },
 "箱根湯本": {
  "ko": "하코네유모토",
  "en": "Hakoneyumoto"
 },
 "小竹向原": {
  "ko": "고타케무카이하라",
  "en": "Kotakemukaihara"
 },
 "鵜の木": {
  "ko": "우노키",
  "en": "Unoki"
 },
 "塔ノ沢": {
  "ko": "도노사와",
  "en": "Tonosawa"
 },
 "いりなか": {
  "ko": "이리나카",
  "en": "Irinaka"
 },
 "港町": {
  "ko": "미나토마치",
  "en": "Minatomachi"
 },
 "足柄": {
  "ko": "아시가라",
  "en": "Ashigara"
 },
 "越谷レイクタウン": {
  "ko": "고시가야레이쿠타운",
  "en": "Koshigayareikutaun"
 },
 "桜街道": {
  "ko": "사쿠라카이도",
  "en": "Sakurakaido"
 },
 "蓮根": {
  "ko": "렌콘",
  "en": "Renkon"
 },
 "芸大通": {
  "ko": "게이다이토오리",
  "en": "Geidaitori"
 },
 "秩父": {
  "ko": "지치부",
  "en": "Chichibu"
 },
 "箱根ケ崎": {
  "ko": "하코네케사키",
  "en": "Hakonekesaki"
 },
 "姪浜": {
  "ko": "메이노하마",
  "en": "Meinohama"
 },
 "豊橋": {
  "ko": "도요하시",
  "en": "Toyohashi"
 },
 "駅前": {
  "ko": "에키마에",
  "en": "Ekimae"
 },
 "竹ノ塚": {
  "ko": "다케노쓰카",
  "en": "Takenotsuka"
 },
 "藤沢": {
  "ko": "후지사와",
  "en": "Fujisawa"
 },
 "佐渡市その他": {
  "ko": "사도시소노호카",
  "en": "Sadoshisonohoka"
 },
 "熱田": {
  "ko": "아쓰타",
  "en": "Atsuta"
 },
 "淀屋橋": {
  "ko": "요도야바시",
  "en": "Yodoyabashi"
 },
 "喜多山": {
  "ko": "기타야마",
  "en": "Kitayama"
 },
 "天王寺駅前": {
  "ko": "덴노지에키마에",
  "en": "Tennojiekimae"
 },
 "武蔵五日市": {
  "ko": "무사시이쓰카이치",
  "en": "Musashiitsukaichi"
 },
 "長崎": {
  "ko": "나가사키",
  "en": "Nagasaki"
 },
 "倉敷市": {
  "ko": "구라시키시",
  "en": "Kurashikishi"
 },
 "青梅": {
  "ko": "오메",
  "en": "Ome"
 },
 "長崎駅前": {
  "ko": "나가사키에키마에",
  "en": "Nagasakiekimae"
 },
 "新津田沼": {
  "ko": "신쓰다누마",
  "en": "Shintsudanuma"
 },
 "鳩ケ谷": {
  "ko": "하토케타니",
  "en": "Hatoketani"
 },
 "松島海岸": {
  "ko": "마쓰시마카이간",
  "en": "Matsushimakaigan"
 },
 "南小樽": {
  "ko": "미나미오타루",
  "en": "Minamiotaru"
 },
 "茨木": {
  "ko": "이바라키",
  "en": "Ibaraki"
 },
 "尾張一宮": {
  "ko": "오와리이치노미야",
  "en": "Owariichinomiya"
 },
 "宮の沢": {
  "ko": "미야노사와",
  "en": "Miyanosawa"
 },
 "名鉄一宮": {
  "ko": "메이테쓰이치노미야",
  "en": "Meitetsuichinomiya"
 },
 "鴻巣": {
  "ko": "고노스",
  "en": "Konosu"
 },
 "太宰府": {
  "ko": "다자이후",
  "en": "Dazaifu"
 },
 "羽後牛島": {
  "ko": "우고시지마",
  "en": "Ugoshijima"
 },
 "鈴木町": {
  "ko": "스즈키초",
  "en": "Suzukicho"
 },
 "宮内": {
  "ko": "미야우치",
  "en": "Miyauchi"
 },
 "米沢": {
  "ko": "요네자와",
  "en": "Yonezawa"
 },
 "金手": {
  "ko": "긴테",
  "en": "Kinte"
 },
 "桶川": {
  "ko": "오케가와",
  "en": "Okegawa"
 },
 "いづろ通": {
  "ko": "이즈로토오리",
  "en": "Izurotori"
 },
 "笹原": {
  "ko": "사사하라",
  "en": "Sasahara"
 },
 "幸谷": {
  "ko": "고타니",
  "en": "Kotani"
 },
 "相武台前": {
  "ko": "소부다이마에",
  "en": "Sobudaimae"
 },
 "長浜": {
  "ko": "나가하마",
  "en": "Nagahama"
 },
 "新大村": {
  "ko": "신다이무라",
  "en": "Shindaimura"
 },
 "伊豆大島": {
  "ko": "이즈오시마",
  "en": "Izuoshima"
 },
 "新三郷": {
  "ko": "신조사토",
  "en": "Shinzosato"
 },
 "八街": {
  "ko": "야치마타",
  "en": "Yachimata"
 },
 "菖蒲町その他": {
  "ko": "쇼부마치소노호카",
  "en": "Shobumachisonohoka"
 },
 "恵美須町": {
  "ko": "에비스마치",
  "en": "Ebisumachi"
 },
 "富士山": {
  "ko": "후지산",
  "en": "Fujisan"
 },
 "郡山": {
  "ko": "고리야마",
  "en": "Koriyama"
 },
 "谷町九丁目": {
  "ko": "다니마치큐초메",
  "en": "Tanimachikyuchome"
 },
 "諏訪": {
  "ko": "스와",
  "en": "Suwa"
 },
 "十字街": {
  "ko": "주지마치",
  "en": "Jujimachi"
 },
 "福住": {
  "ko": "후쿠즈미",
  "en": "Fukuzumi"
 },
 "山陽姫路": {
  "ko": "산요히메지",
  "en": "Sanyohimeji"
 },
 "中津川": {
  "ko": "나카쓰가와",
  "en": "Nakatsugawa"
 },
 "春日井（ＪＲ）": {
  "ko": "가스가이（ＪＲ）",
  "en": "Kasugai(Jr)"
 },
 "姫路": {
  "ko": "히메지",
  "en": "Himeji"
 },
 "浄心": {
  "ko": "조신",
  "en": "Joshin"
 },
 "三島広小路": {
  "ko": "미시마히로코지",
  "en": "Mishimahirokoji"
 },
 "豊田市": {
  "ko": "도요타시",
  "en": "Toyotashi"
 },
 "函館駅前": {
  "ko": "하코다테에키마에",
  "en": "Hakodateekimae"
 },
 "竜舞": {
  "ko": "류마이",
  "en": "Ryumai"
 },
 "北中城村": {
  "ko": "기타나카구스쿠무라",
  "en": "Kitanakagusukumura"
 },
 "二十四軒": {
  "ko": "니주시켄",
  "en": "Nijushiken"
 },
 "読谷村": {
  "ko": "요미탄무라",
  "en": "Yomitanmura"
 },
 "高松築港": {
  "ko": "다카마쓰칫코",
  "en": "Takamatsuchikko"
 },
 "長後": {
  "ko": "조고",
  "en": "Chogo"
 },
 "新今宮駅前": {
  "ko": "신이마미야에키마에",
  "en": "Shin'Imamiyaekimae"
 },
 "琴似（札幌市営）": {
  "ko": "고토니（삿포로시에이）",
  "en": "Kotoni(Sapporoshiei)"
 },
 "鳥羽": {
  "ko": "도바",
  "en": "Toba"
 },
 "榎戸": {
  "ko": "에노토",
  "en": "Enoto"
 },
 "糸満市": {
  "ko": "이토만시",
  "en": "Itomanshi"
 },
 "南知多町その他": {
  "ko": "미나미치타마치소노호카",
  "en": "Minamichitamachisonohoka"
 },
 "江南": {
  "ko": "고난",
  "en": "Konan"
 },
 "宮山": {
  "ko": "미야야마",
  "en": "Miyayama"
 },
 "入間市": {
  "ko": "이루마시",
  "en": "Irumashi"
 },
 "上大月": {
  "ko": "우에오쓰키",
  "en": "Ueotsuki"
 },
 "中之郷": {
  "ko": "나카유키사토",
  "en": "Nakayukisato"
 },
 "長瀞": {
  "ko": "나가토로",
  "en": "Nagatoro"
 },
 "北新横浜": {
  "ko": "기타신요코하마",
  "en": "Kitashinyokohama"
 },
 "富士急ハイランド": {
  "ko": "후지큐하이란도",
  "en": "Fujikyuhairando"
 },
 "東区役所前": {
  "ko": "히가시쿠야쿠쇼마에",
  "en": "Higashikuyakushomae"
 },
 "中福良": {
  "ko": "나카후쿠료",
  "en": "Nakafukuryo"
 },
 "本塩釜": {
  "ko": "혼시오가마",
  "en": "Honshiogama"
 },
 "南酒々井": {
  "ko": "미나미사케々이",
  "en": "Minamisake(Kurikaesi)I"
 },
 "南あわじ市その他": {
  "ko": "미나미아와지시소노호카",
  "en": "Minamiawajishisonohoka"
 },
 "東大宮": {
  "ko": "도다이미야",
  "en": "Todaimiya"
 },
 "木更津市その他": {
  "ko": "기사라즈시소노호카",
  "en": "Kisarazushisonohoka"
 },
 "西富士宮": {
  "ko": "니시후지노미야",
  "en": "Nishifujinomiya"
 },
 "秦野": {
  "ko": "하다노",
  "en": "Hadano"
 },
 "中央弘前": {
  "ko": "주오히로사키",
  "en": "Chuohirosaki"
 },
 "女川": {
  "ko": "메가와",
  "en": "Megawa"
 },
 "儀保": {
  "ko": "기호",
  "en": "Giho"
 },
 "倉見": {
  "ko": "구라미",
  "en": "Kurami"
 },
 "彦根": {
  "ko": "히코네",
  "en": "Hikone"
 },
 "志津": {
  "ko": "시즈",
  "en": "Shizu"
 },
 "阪神国道": {
  "ko": "한신코쿠도",
  "en": "Hanshinkokudo"
 },
 "余市": {
  "ko": "요이치",
  "en": "Yoichi"
 },
 "てだこ浦西": {
  "ko": "데다코라니시",
  "en": "Tedakoranishi"
 },
 "環状通東": {
  "ko": "간조토오리히가시",
  "en": "Kanjotorihigashi"
 },
 "勝山町": {
  "ko": "가쓰야마마치",
  "en": "Katsuyamamachi"
 },
 "千葉ニュータウン中央": {
  "ko": "지바뉴타운추오",
  "en": "Chibanyutaunchuo"
 },
 "三河安城": {
  "ko": "미카와안조",
  "en": "Mikawaanjo"
 },
 "野島公園": {
  "ko": "노지마코엔",
  "en": "Nojimakoen"
 },
 "淡路市その他": {
  "ko": "아와지시소노호카",
  "en": "Awajishisonohoka"
 },
 "研究学園": {
  "ko": "겐큐가쿠엔",
  "en": "Kenkyugakuen"
 },
 "出町柳": {
  "ko": "데마치야나기",
  "en": "Demachiyanagi"
 },
 "石和温泉": {
  "ko": "이시와온센",
  "en": "Ishiwaonsen"
 },
 "安部山公園": {
  "ko": "아베야마코엔",
  "en": "Abeyamakoen"
 },
 "首里": {
  "ko": "슈리",
  "en": "Shuri"
 },
 "蟹江": {
  "ko": "가니에",
  "en": "Kanie"
 },
 "草薙（静岡鉄道）": {
  "ko": "구사나기（시즈오카테쓰도）",
  "en": "Kusanagi(Shizuokatetsudo)"
 },
 "等持院・立命館大学衣笠キャンパス前": {
  "ko": "도지인・리쓰메이칸다이가쿠키누가사캰파스마에",
  "en": "Tojiin・Ritsumeikandaigakukinugasakyanpasumae"
 },
 "草薙（ＪＲ）": {
  "ko": "구사나기（ＪＲ）",
  "en": "Kusanagi(Jr)"
 },
 "愛川町その他": {
  "ko": "아이카와마치소노호카",
  "en": "Aikawamachisonohoka"
 },
 "辰巳": {
  "ko": "다쓰미",
  "en": "Tatsumi"
 },
 "北３４条": {
  "ko": "기타３４조",
  "en": "Kita34Jo"
 },
 "嵐山（京福）": {
  "ko": "아라시야마（케이후쿠）",
  "en": "Arashiyama(Keifuku)"
 },
 "渋川市その他": {
  "ko": "시부카와시소노호카",
  "en": "Shibukawashisonohoka"
 },
 "片瀬江ノ島": {
  "ko": "가타세코노시마",
  "en": "Katasekonoshima"
 },
 "新豊田": {
  "ko": "신토요다",
  "en": "Shintoyoda"
 },
 "吉田町その他": {
  "ko": "요시다초소노호카",
  "en": "Yoshidachosonohoka"
 },
 "津": {
  "ko": "쓰",
  "en": "Tsu"
 },
 "飯田": {
  "ko": "이이다",
  "en": "Iida"
 },
 "おもちゃのまち": {
  "ko": "오모차노마치",
  "en": "Omochanomachi"
 },
 "亀川": {
  "ko": "가메카와",
  "en": "Kamekawa"
 },
 "円山公園": {
  "ko": "마루야마코엔",
  "en": "Maruyamakoen"
 },
 "宇治（ＪＲ）": {
  "ko": "우지（ＪＲ）",
  "en": "Uji(Jr)"
 },
 "尼崎（ＪＲ）": {
  "ko": "아마가사키（ＪＲ）",
  "en": "Amagasaki(Jr)"
 },
 "広電宮島口": {
  "ko": "히로덴미야지마쿠치",
  "en": "Hirodenmiyajimakuchi"
 },
 "東海大学前": {
  "ko": "도카이다이가쿠마에",
  "en": "Tokaidaigakumae"
 },
 "石垣市": {
  "ko": "이시가키시",
  "en": "Ishigakishi"
 },
 "西尾口": {
  "ko": "니시오쿠치",
  "en": "Nishiokuchi"
 },
 "近江八幡": {
  "ko": "오미하치만",
  "en": "Omihachiman"
 },
 "三原市": {
  "ko": "미하라시",
  "en": "Miharashi"
 },
 "広丘": {
  "ko": "고오카",
  "en": "Koka"
 },
 "磯部": {
  "ko": "이소베",
  "en": "Isobe"
 },
 "五日町": {
  "ko": "이쓰카마치",
  "en": "Itsukamachi"
 },
 "八木崎": {
  "ko": "야기사키",
  "en": "Yagisaki"
 },
 "堅田": {
  "ko": "가타타",
  "en": "Katata"
 },
 "共和": {
  "ko": "교와",
  "en": "Kyowa"
 },
 "印西牧の原": {
  "ko": "인자이마키노하라",
  "en": "Inzaimakinohara"
 },
 "石打": {
  "ko": "이시우치",
  "en": "Ishiuchi"
 },
 "東松山": {
  "ko": "히가시마쓰야마",
  "en": "Higashimatsuyama"
 },
 "中之条": {
  "ko": "나카노조",
  "en": "Nakanojo"
 },
 "西宮北口": {
  "ko": "니시노미야키타구치",
  "en": "Nishinomiyakitaguchi"
 },
 "藤枝": {
  "ko": "후지에다",
  "en": "Fujieda"
 },
 "ＪＲ河内永和": {
  "ko": "ＪＲ카와우치히사카즈",
  "en": "Jrkawauchihisakazu"
 },
 "海津市その他": {
  "ko": "가이즈시소노호카",
  "en": "Kaizushisonohoka"
 },
 "花田口": {
  "ko": "하나다쿠치",
  "en": "Hanadakuchi"
 },
 "山北": {
  "ko": "산포쿠",
  "en": "Sanpoku"
 },
 "浦添前田": {
  "ko": "우라소에마에다",
  "en": "Urasoemaeda"
 },
 "旭川四条": {
  "ko": "아사히카와시조",
  "en": "Asahikawashijo"
 },
 "甚目寺": {
  "ko": "지모쿠지",
  "en": "Jimokuji"
 },
 "柏崎": {
  "ko": "가시와자키",
  "en": "Kashiwazaki"
 },
 "粟野": {
  "ko": "아와노",
  "en": "Awano"
 },
 "芦屋（ＪＲ）": {
  "ko": "아시야（ＪＲ）",
  "en": "Ashiya(Jr)"
 },
 "江坂": {
  "ko": "에사카",
  "en": "Esaka"
 },
 "宇治（京阪）": {
  "ko": "우지（케이한）",
  "en": "Uji(Keihan)"
 },
 "月江寺": {
  "ko": "겟코테라",
  "en": "Gekkotera"
 },
 "岩槻": {
  "ko": "이와쓰키",
  "en": "Iwatsuki"
 },
 "古河": {
  "ko": "고가",
  "en": "Koga"
 },
 "桜町前": {
  "ko": "사쿠라마치마에",
  "en": "Sakuramachimae"
 },
 "デンテツターミナルビル前": {
  "ko": "덴테쓰타미나루비루마에",
  "en": "Dentetsutaaminarubirumae"
 },
 "はりまや橋": {
  "ko": "하리마야하시",
  "en": "Harimayahashi"
 },
 "箕面萱野": {
  "ko": "미노오카야노",
  "en": "Minokayano"
 },
 "水上": {
  "ko": "스이조",
  "en": "Suijo"
 },
 "六名": {
  "ko": "로쿠메이",
  "en": "Rokumei"
 },
 "袋井": {
  "ko": "후쿠로이",
  "en": "Fukuroi"
 },
 "大谷地": {
  "ko": "오야치",
  "en": "Oyachi"
 },
 "弘高下": {
  "ko": "히로타카시타",
  "en": "Hirotakashita"
 },
 "東岡崎": {
  "ko": "히가시오카자키",
  "en": "Higashiokazaki"
 },
 "桜島": {
  "ko": "사쿠라시마",
  "en": "Sakurashima"
 },
 "六丁の目": {
  "ko": "로쿠초노메",
  "en": "Rokuchonome"
 },
 "上州福島": {
  "ko": "조슈후쿠시마",
  "en": "Joshufukushima"
 },
 "干潟": {
  "ko": "히가타",
  "en": "Higata"
 },
 "青森": {
  "ko": "아오모리",
  "en": "Aomori"
 },
 "青堀": {
  "ko": "아오호리",
  "en": "Aohori"
 },
 "和歌山": {
  "ko": "와카야마",
  "en": "Wakayama"
 },
 "牧之原市その他": {
  "ko": "마키노하라시소노호카",
  "en": "Makinoharashisonohoka"
 },
 "寄居": {
  "ko": "요리이",
  "en": "Yorii"
 },
 "平戸市その他": {
  "ko": "히라도시소노호카",
  "en": "Hiradoshisonohoka"
 },
 "吉野ケ里公園": {
  "ko": "요시노케사토코엔",
  "en": "Yoshinokesatokoen"
 },
 "砂川": {
  "ko": "스나가와",
  "en": "Sunagawa"
 },
 "野洲": {
  "ko": "야스",
  "en": "Yasu"
 },
 "御室仁和寺": {
  "ko": "오무로니와테라",
  "en": "Omuroniwatera"
 },
 "釧路": {
  "ko": "구시로",
  "en": "Kushiro"
 },
 "思川": {
  "ko": "오모이가와",
  "en": "Omoigawa"
 },
 "箕面": {
  "ko": "미노오",
  "en": "Mino"
 },
 "柏矢町": {
  "ko": "가시와야마치",
  "en": "Kashiwayamachi"
 },
 "島原": {
  "ko": "시마바라",
  "en": "Shimabara"
 },
 "八幡浜": {
  "ko": "야와타하마",
  "en": "Yawatahama"
 },
 "播州赤穂": {
  "ko": "반슈아코",
  "en": "Banshuako"
 },
 "坂出市その他": {
  "ko": "사카이데시소노호카",
  "en": "Sakaideshisonohoka"
 },
 "御影（阪神）": {
  "ko": "미카게（한신）",
  "en": "Mikage(Hanshin)"
 },
 "三本松口": {
  "ko": "산본마쓰쿠치",
  "en": "Sanbonmatsukuchi"
 },
 "亀山": {
  "ko": "가메야마",
  "en": "Kameyama"
 },
 "大河原": {
  "ko": "오가와라",
  "en": "Ogawara"
 },
 "高山市その他": {
  "ko": "고잔시소노호카",
  "en": "Kozanshisonohoka"
 },
 "出雲市": {
  "ko": "이즈모시",
  "en": "Izumoshi"
 },
 "大口": {
  "ko": "오구치",
  "en": "Oguchi"
 },
 "八尾南": {
  "ko": "야오미나미",
  "en": "Yaominami"
 },
 "室": {
  "ko": "시쓰",
  "en": "Shitsu"
 },
 "恵那": {
  "ko": "에나",
  "en": "Ena"
 },
 "穂高": {
  "ko": "호다카",
  "en": "Hodaka"
 },
 "希望ケ丘": {
  "ko": "기보케오카",
  "en": "Kibokeoka"
 },
 "ユニバーサルシティ": {
  "ko": "유니바사루시테ぃ",
  "en": "Yunibaasarushitei"
 },
 "小松": {
  "ko": "고마쓰",
  "en": "Komatsu"
 },
 "電鉄出雲市": {
  "ko": "덴테쓰이즈모시",
  "en": "Dentetsuizumoshi"
 },
 "多賀大社前": {
  "ko": "다가타이샤마에",
  "en": "Tagataishamae"
 },
 "ひこね芹川": {
  "ko": "히코네세리카와",
  "en": "Hikoneserikawa"
 },
 "沼田": {
  "ko": "누마타",
  "en": "Numata"
 },
 "妙心寺": {
  "ko": "묘신테라",
  "en": "Myoshintera"
 },
 "芦屋川": {
  "ko": "아시야카와",
  "en": "Ashiyakawa"
 },
 "春日居町": {
  "ko": "가스가이초",
  "en": "Kasugaicho"
 },
 "永田": {
  "ko": "나가타",
  "en": "Nagata"
 },
 "船岡": {
  "ko": "후나오카",
  "en": "Funaoka"
 },
 "富良野": {
  "ko": "후라노",
  "en": "Furano"
 },
 "石巻": {
  "ko": "이시노마키",
  "en": "Ishinomaki"
 },
 "大船渡": {
  "ko": "오후나토",
  "en": "Ofunato"
 },
 "登別市その他": {
  "ko": "노보리베쓰시소노호카",
  "en": "Noboribetsushisonohoka"
 },
 "南魚崎": {
  "ko": "미나미우오사키",
  "en": "Minamiuosaki"
 },
 "小豆島町その他": {
  "ko": "쇼즈시마마치소노호카",
  "en": "Shozushimamachisonohoka"
 },
 "けやき台": {
  "ko": "게야키다이",
  "en": "Keyakidai"
 },
 "岡本": {
  "ko": "오카모토",
  "en": "Okamoto"
 },
 "新伊勢崎": {
  "ko": "신이세사키",
  "en": "Shinisesaki"
 },
 "真駒内": {
  "ko": "마코마나이",
  "en": "Makomanai"
 },
 "今治": {
  "ko": "이마바리",
  "en": "Imabari"
 },
 "垂水市その他": {
  "ko": "다루미즈시소노호카",
  "en": "Tarumizushisonohoka"
 },
 "北広島市その他": {
  "ko": "기타히로시마시소노호카",
  "en": "Kitahiroshimashisonohoka"
 },
 "有馬温泉": {
  "ko": "아리마온센",
  "en": "Arimaonsen"
 },
 "加木屋中ノ池": {
  "ko": "가키야나카노이케",
  "en": "Kakiyanakanoike"
 },
 "近鉄郡山": {
  "ko": "긴테쓰코리야마",
  "en": "Kintetsukoriyama"
 },
 "太子堂": {
  "ko": "다이시도",
  "en": "Taishido"
 },
 "田京": {
  "ko": "다쿄",
  "en": "Takyo"
 },
 "三里木": {
  "ko": "산리키",
  "en": "Sanriki"
 },
 "ワイキキ": {
  "ko": "와이키키",
  "en": "Waikiki"
 },
 "守山": {
  "ko": "모리야마",
  "en": "Moriyama"
 },
 "横河原": {
  "ko": "요코가와하라",
  "en": "Yokogawahara"
 },
 "南米沢": {
  "ko": "난베이사와",
  "en": "Nanbeisawa"
 },
 "十条（近鉄）": {
  "ko": "주조（킨테쓰）",
  "en": "Jujo(Kintetsu)"
 },
 "札幌市南区その他": {
  "ko": "삿포로시미나미쿠소노호카",
  "en": "Sapporoshiminamikusonohoka"
 },
 "石狩市その他": {
  "ko": "이시카리시소노호카",
  "en": "Ishikarishisonohoka"
 },
 "岡部": {
  "ko": "오카베",
  "en": "Okabe"
 },
 "指宿": {
  "ko": "이부스키",
  "en": "Ibusuki"
 },
 "阿波池田": {
  "ko": "아와이케다",
  "en": "Awaikeda"
 },
 "木ノ本": {
  "ko": "기노혼",
  "en": "Kinohon"
 },
 "三沢": {
  "ko": "미사와",
  "en": "Misawa"
 },
 "野江": {
  "ko": "노에",
  "en": "Noe"
 },
 "柳井": {
  "ko": "야나이",
  "en": "Yanai"
 },
 "滝川": {
  "ko": "다키카와",
  "en": "Takikawa"
 },
 "美濃太田": {
  "ko": "미노오타",
  "en": "Minoota"
 },
 "河和": {
  "ko": "고와",
  "en": "Kowa"
 },
 "三日市": {
  "ko": "밋카이치",
  "en": "Mikkaichi"
 },
 "椥辻": {
  "ko": "나기쓰지",
  "en": "Nagitsuji"
 },
 "たびら平戸口": {
  "ko": "다비라히라도쿠치",
  "en": "Tabirahiradokuchi"
 },
 "針中野": {
  "ko": "하리나카노",
  "en": "Harinakano"
 },
 "多喜浜": {
  "ko": "다키하마",
  "en": "Takihama"
 },
 "汐入": {
  "ko": "시오이리",
  "en": "Shioiri"
 },
 "古里": {
  "ko": "후루사토",
  "en": "Furusato"
 },
 "東柏崎": {
  "ko": "히가시카시와자키",
  "en": "Higashikashiwazaki"
 },
 "弥彦": {
  "ko": "야히코",
  "en": "Yahiko"
 },
 "八百津町その他": {
  "ko": "야오쓰마치소노호카",
  "en": "Yaotsumachisonohoka"
 },
 "神戸": {
  "ko": "고베",
  "en": "Kobe"
 },
 "笠間市その他": {
  "ko": "가사마시소노호카",
  "en": "Kasamashisonohoka"
 },
 "東行田": {
  "ko": "도코타",
  "en": "Tokota"
 },
 "嬉野温泉": {
  "ko": "우레시노온센",
  "en": "Ureshinonsen"
 },
 "錦岡": {
  "ko": "니시키오카",
  "en": "Nishikioka"
 },
 "北藤岡": {
  "ko": "기타후지오카",
  "en": "Kitafujioka"
 },
 "シンガポール・チャンギ国際空港 (SIN) 周辺": {
  "ko": "신가포루・찬기코쿠사이쿠우코 (SIN) 슈헨",
  "en": "Shingaporu・Changikokusaikuko (Sin) Shuhen"
 },
 "沖縄市": {
  "ko": "오키나와시",
  "en": "Okinawashi"
 },
 "洞爺湖町その他": {
  "ko": "도야코마치소노호카",
  "en": "Toyakomachisonohoka"
 },
 "新さっぽろ": {
  "ko": "아타라삿포로",
  "en": "Atarasapporo"
 },
 "鎌ケ谷大仏": {
  "ko": "가마케타니다이부쓰",
  "en": "Kamaketanidaibutsu"
 },
 "春江": {
  "ko": "하루에",
  "en": "Harue"
 },
 "かみのやま温泉": {
  "ko": "가미노야마온센",
  "en": "Kaminoyamaonsen"
 },
 "中札内村その他": {
  "ko": "나카사쓰나이무라소노호카",
  "en": "Nakasatsunaimurasonohoka"
 },
 "大和八木": {
  "ko": "야마토야기",
  "en": "Yamatoyagi"
 },
 "京都市左京区その他": {
  "ko": "교토시사쿄쿠소노호카",
  "en": "Kyotoshisakyokusonohoka"
 },
 "相生": {
  "ko": "아이오이",
  "en": "Aioi"
 },
 "波止浜": {
  "ko": "하시하마",
  "en": "Hashihama"
 },
 "陸奥湊": {
  "ko": "미치노쿠미나토",
  "en": "Michinokuminato"
 },
 "巌根": {
  "ko": "이와네",
  "en": "Iwane"
 },
 "田原": {
  "ko": "다하라",
  "en": "Tahara"
 },
 "南稚内": {
  "ko": "미나미왓카나이",
  "en": "Minamiwakkanai"
 },
 "撫養": {
  "ko": "무야",
  "en": "Muya"
 },
 "宿毛": {
  "ko": "스쿠모",
  "en": "Sukumo"
 },
 "水沢": {
  "ko": "미즈사와",
  "en": "Mizusawa"
 },
 "白石": {
  "ko": "시로이시",
  "en": "Shiroishi"
 },
 "枕崎": {
  "ko": "마쿠라자키",
  "en": "Makurazaki"
 },
 "安土": {
  "ko": "아즈치",
  "en": "Azuchi"
 },
 "本山町その他": {
  "ko": "모토야마초소노호카",
  "en": "Motoyamachosonohoka"
 },
 "礼文町その他": {
  "ko": "레분마치소노호카",
  "en": "Rebunmachisonohoka"
 },
 "十日町": {
  "ko": "도오카마치",
  "en": "Tokamachi"
 },
 "坂出": {
  "ko": "사카이데",
  "en": "Sakaide"
 },
 "ほしみ": {
  "ko": "호시미",
  "en": "Hoshimi"
 },
 "東宿毛": {
  "ko": "히가시슈쿠케",
  "en": "Higashishukuke"
 },
 "幕張豊砂": {
  "ko": "마쿠하리유타카스나",
  "en": "Makuhariyutakasuna"
 },
 "中津川市その他": {
  "ko": "나카쓰가와시소노호카",
  "en": "Nakatsugawashisonohoka"
 },
 "都農": {
  "ko": "쓰노",
  "en": "Tsuno"
 },
 "法華口": {
  "ko": "홋케쿠치",
  "en": "Hokkekuchi"
 },
 "中標津町その他": {
  "ko": "나카시베쓰마치소노호카",
  "en": "Nakashibetsumachisonohoka"
 },
 "別海町その他": {
  "ko": "벳카이마치소노호카",
  "en": "Bekkaimachisonohoka"
 },
 "川南": {
  "ko": "가와미나미",
  "en": "Kawaminami"
 },
 "似内": {
  "ko": "니타나이",
  "en": "Nitanai"
 },
 "あいの里教育大": {
  "ko": "아이노사토쿄이쿠다이",
  "en": "Ainosatokyoikudai"
 },
 "網野": {
  "ko": "아미노",
  "en": "Amino"
 },
 "南砺市その他": {
  "ko": "난토시소노호카",
  "en": "Nantoshisonohoka"
 },
 "大藪": {
  "ko": "오야부",
  "en": "Oyabu"
 },
 "新府": {
  "ko": "신푸",
  "en": "Shinpu"
 },
 "チャリング・クロス駅周辺": {
  "ko": "자린구・쿠로스에키슈헨",
  "en": "Charingu・Kurosuekishuhen"
 },
 "坂戸": {
  "ko": "사카토",
  "en": "Sakato"
 },
 "前平公園": {
  "ko": "마에히라코엔",
  "en": "Maehirakoen"
 },
 "柘植": {
  "ko": "쓰게",
  "en": "Tsuge"
 },
 "桜井": {
  "ko": "사쿠라이",
  "en": "Sakurai"
 },
 "五島市その他": {
  "ko": "고토시소노호카",
  "en": "Gotoshisonohoka"
 },
 "日下": {
  "ko": "구사카",
  "en": "Kusaka"
 },
 "大聖寺": {
  "ko": "다이쇼지",
  "en": "Daishoji"
 },
 "瑞浪": {
  "ko": "미즈나미",
  "en": "Mizunami"
 },
 "加賀温泉": {
  "ko": "가가온센",
  "en": "Kagaonsen"
 },
 "恵我ノ荘": {
  "ko": "에가노소",
  "en": "Eganoso"
 },
 "出戸浜": {
  "ko": "데토하마",
  "en": "Detohama"
 },
 "うるま市": {
  "ko": "우루마시",
  "en": "Urumashi"
 },
 "二軒屋": {
  "ko": "니켄야",
  "en": "Nikenya"
 },
 "土庄町その他": {
  "ko": "도노쇼마치소노호카",
  "en": "Tonoshomachisonohoka"
 },
 "利尻町その他": {
  "ko": "리시리마치소노호카",
  "en": "Rishirimachisonohoka"
 },
 "近鉄八尾": {
  "ko": "긴테쓰야오",
  "en": "Kintetsuyao"
 },
 "新山口": {
  "ko": "신야마구치",
  "en": "Shinyamaguchi"
 },
 "十川": {
  "ko": "소가와",
  "en": "Sogawa"
 },
 "富士見": {
  "ko": "후지미",
  "en": "Fujimi"
 },
 "大洗": {
  "ko": "오아라이",
  "en": "Oarai"
 },
 "厚岸": {
  "ko": "앗케시",
  "en": "Akkeshi"
 },
 "飛騨市その他": {
  "ko": "히다시소노호카",
  "en": "Hidashisonohoka"
 },
 "城陽": {
  "ko": "조요",
  "en": "Joyo"
 },
 "仁山": {
  "ko": "진센",
  "en": "Jinsen"
 },
 "忍ケ丘": {
  "ko": "닌케오카",
  "en": "Ninkeoka"
 },
 "上二田": {
  "ko": "우에후타다",
  "en": "Uefutada"
 },
 "岩国市その他": {
  "ko": "이와쿠니시소노호카",
  "en": "Iwakunishisonohoka"
 },
 "泉（ＪＲ）": {
  "ko": "이즈미（ＪＲ）",
  "en": "Izumi(Jr)"
 },
 "竜野": {
  "ko": "다쓰노",
  "en": "Tatsuno"
 },
 "住吉大社": {
  "ko": "스미요시타이샤",
  "en": "Sumiyoshitaisha"
 },
 "紀伊宮原": {
  "ko": "기이미야하라",
  "en": "Kiimiyahara"
 },
 "豊見城市": {
  "ko": "도미구스쿠시",
  "en": "Tomigusukushi"
 },
 "貝田": {
  "ko": "가이다",
  "en": "Kaida"
 },
 "アプトいちしろ": {
  "ko": "아푸토이치시로",
  "en": "Aputoichishiro"
 },
 "西向日": {
  "ko": "니시코히",
  "en": "Nishikohi"
 },
 "不破一色": {
  "ko": "후와잇쇼쿠",
  "en": "Fuwaisshoku"
 },
 "阿漕": {
  "ko": "아코기",
  "en": "Akogi"
 },
 "串間": {
  "ko": "구시마",
  "en": "Kushima"
 },
 "久田野": {
  "ko": "히사다노",
  "en": "Hisadano"
 },
 "三角": {
  "ko": "산카쿠",
  "en": "Sankaku"
 },
 "東大門市場 トンデムンシジャン": {
  "ko": "도다이몬시조 톤데문시잔",
  "en": "Todaimonshijo Tondemunshijan"
 },
 "轟": {
  "ko": "도도로키",
  "en": "Todoroki"
 },
 "郡上八幡": {
  "ko": "구조하치만",
  "en": "Gujohachiman"
 },
 "摂津本山": {
  "ko": "셋쓰혼잔",
  "en": "Settsuhonzan"
 },
 "甲賀市その他": {
  "ko": "고카시소노호카",
  "en": "Kokashisonohoka"
 },
 "板野": {
  "ko": "이타노",
  "en": "Itano"
 },
 "湯沢市その他": {
  "ko": "유자와시소노호카",
  "en": "Yuzawashisonohoka"
 },
 "岩原スキー場前": {
  "ko": "이와하라스키바마에",
  "en": "Iwaharasukiibamae"
 },
 "小杉（あいの風）": {
  "ko": "고스기（아이노카제）",
  "en": "Kosugi(Ainokaze)"
 },
 "パディントン": {
  "ko": "파데〴톤",
  "en": "Padinton"
 },
 "阿字ケ浦": {
  "ko": "아지케우라",
  "en": "Ajikeura"
 },
 "南羽生": {
  "ko": "미나미하뉴",
  "en": "Minamihanyu"
 },
 "苫小牧": {
  "ko": "도마코마이",
  "en": "Tomakomai"
 },
 "モレラ岐阜": {
  "ko": "모레라기후",
  "en": "Moreragifu"
 },
 "八木西口": {
  "ko": "야기니시구치",
  "en": "Yaginishiguchi"
 },
 "北殿": {
  "ko": "기타토노",
  "en": "Kitatono"
 },
 "東石黒": {
  "ko": "도세키쿠로",
  "en": "Tosekikuro"
 },
 "西明石": {
  "ko": "니시아카시",
  "en": "Nishiakashi"
 },
 "新上五島町その他": {
  "ko": "신우에고토마치소노호카",
  "en": "Shinuegotomachisonohoka"
 },
 "本宮": {
  "ko": "모토미야",
  "en": "Motomiya"
 },
 "天塩中川": {
  "ko": "데시오나카가와",
  "en": "Teshionakagawa"
 },
 "長岡天神": {
  "ko": "나가오카텐진",
  "en": "Nagaokatenjin"
 },
 "小平町その他": {
  "ko": "고다이라마치소노호카",
  "en": "Kodairamachisonohoka"
 },
 "金比羅前": {
  "ko": "곤피라마에",
  "en": "Konpiramae"
 },
 "上総三又": {
  "ko": "가즈사미쓰마타",
  "en": "Kazusamitsumata"
 },
 "男鹿市その他": {
  "ko": "오가시소노호카",
  "en": "Ogashisonohoka"
 },
 "宮島口": {
  "ko": "미야지마쿠치",
  "en": "Miyajimakuchi"
 },
 "幕別": {
  "ko": "마쿠베쓰",
  "en": "Makubetsu"
 },
 "安部": {
  "ko": "아베",
  "en": "Abe"
 },
 "松原湖": {
  "ko": "마쓰바라코",
  "en": "Matsubarako"
 },
 "一ツ木": {
  "ko": "이치쓰키",
  "en": "Ichitsuki"
 },
 "清川村その他": {
  "ko": "기요카와무라소노호카",
  "en": "Kiyokawamurasonohoka"
 },
 "宝塚南口": {
  "ko": "다카라즈카미나미구치",
  "en": "Takarazukaminamiguchi"
 },
 "おゆみ野": {
  "ko": "오유미노",
  "en": "Oyumino"
 },
 "国英": {
  "ko": "구니후사",
  "en": "Kunifusa"
 },
 "徳山": {
  "ko": "도쿠야마",
  "en": "Tokuyama"
 },
 "津軽五所川原": {
  "ko": "쓰가루고쇼가와라",
  "en": "Tsugarugoshogawara"
 },
 "益城町その他": {
  "ko": "마시키마치소노호카",
  "en": "Mashikimachisonohoka"
 },
 "鹿島神宮": {
  "ko": "가시마진구우",
  "en": "Kashimajingu"
 },
 "稲積公園": {
  "ko": "이즈미코엔",
  "en": "Izumikoen"
 },
 "小中野": {
  "ko": "고나카노",
  "en": "Konakano"
 },
 "小岩井": {
  "ko": "고이와이",
  "en": "Koiwai"
 },
 "大甕": {
  "ko": "오미카",
  "en": "Omika"
 },
 "伊予宮野下": {
  "ko": "이요미야노시타",
  "en": "Iyomiyanoshita"
 },
 "糸貫": {
  "ko": "이토누키",
  "en": "Itonuki"
 },
 "志文": {
  "ko": "고코로자시분",
  "en": "Kokorozashibun"
 },
 "田子町その他": {
  "ko": "다고마치소노호카",
  "en": "Tagomachisonohoka"
 },
 "宝塚": {
  "ko": "다카라즈카",
  "en": "Takarazuka"
 },
 "穴山": {
  "ko": "아나야마",
  "en": "Anayama"
 },
 "鑓見内": {
  "ko": "야리켄나이",
  "en": "Yarikennai"
 },
 "新松田": {
  "ko": "신마쓰다",
  "en": "Shinmatsuda"
 },
 "五所川原": {
  "ko": "고쇼가와라",
  "en": "Goshogawara"
 },
 "飛騨古川": {
  "ko": "히다후루카와",
  "en": "Hidafurukawa"
 },
 "新島": {
  "ko": "니이지마",
  "en": "Niijima"
 },
 "志布志": {
  "ko": "시부시",
  "en": "Shibushi"
 },
 "新居浜": {
  "ko": "니이하마",
  "en": "Niihama"
 },
 "知床斜里": {
  "ko": "시레토코샤리",
  "en": "Shiretokoshari"
 },
 "呉": {
  "ko": "구레",
  "en": "Kure"
 },
 "伊予吉田": {
  "ko": "이요요시다",
  "en": "Iyoyoshida"
 },
 "八日市": {
  "ko": "요카이치",
  "en": "Yokaichi"
 },
 "モン・デ・ザール": {
  "ko": "몬・데・자루",
  "en": "Mon・De・Zaaru"
 },
 "横手": {
  "ko": "요코테",
  "en": "Yokote"
 },
 "御嵩町その他": {
  "ko": "미타케마치소노호카",
  "en": "Mitakemachisonohoka"
 },
 "栃原": {
  "ko": "도치하라",
  "en": "Tochihara"
 },
 "瀬戸田町沢": {
  "ko": "세토다마치자와",
  "en": "Setodamachizawa"
 },
 "備中高梁": {
  "ko": "빗추타카하시",
  "en": "Bitchutakahashi"
 },
 "上戸手": {
  "ko": "조고테",
  "en": "Jogote"
 },
 "多田": {
  "ko": "다다",
  "en": "Tada"
 },
 "中飯降": {
  "ko": "나카메시코",
  "en": "Nakameshiko"
 },
 "学研北生駒": {
  "ko": "갓켄키타이코마",
  "en": "Gakkenkitaikoma"
 },
 "サン=マロ": {
  "ko": "산=마로",
  "en": "San=Maro"
 },
 "久慈": {
  "ko": "구지",
  "en": "Kuji"
 },
 "下志比": {
  "ko": "시타시히",
  "en": "Shitashihi"
 },
 "田沢湖": {
  "ko": "다자와코",
  "en": "Tazawako"
 },
 "留萌": {
  "ko": "루모이",
  "en": "Rumoi"
 },
 "草野": {
  "ko": "구사노",
  "en": "Kusano"
 },
 "和泊町その他": {
  "ko": "와도마리마치소노호카",
  "en": "Wadomarimachisonohoka"
 },
 "加治木": {
  "ko": "가지키",
  "en": "Kajiki"
 },
 "恩納村": {
  "ko": "온나무라",
  "en": "Onnamura"
 },
 "一ノ関": {
  "ko": "이치노세키",
  "en": "Ichinoseki"
 },
 "宇部新川": {
  "ko": "우베신카와",
  "en": "Ubeshinkawa"
 },
 "真鶴": {
  "ko": "마나쓰루",
  "en": "Manatsuru"
 },
 "土々呂": {
  "ko": "쓰치々로",
  "en": "Tsuchi(Kurikaesi)Ro"
 },
 "本川内": {
  "ko": "혼카와나이",
  "en": "Honkawanai"
 },
 "古部": {
  "ko": "고베",
  "en": "Kobe"
 },
 "金武町": {
  "ko": "가나타케마치",
  "en": "Kanatakemachi"
 },
 "対馬市その他": {
  "ko": "쓰시마시소노호카",
  "en": "Tsushimashisonohoka"
 },
 "目時": {
  "ko": "메토키",
  "en": "Metoki"
 },
 "中原": {
  "ko": "나카하라",
  "en": "Nakahara"
 },
 "郡上市その他": {
  "ko": "구조시소노호카",
  "en": "Gujoshisonohoka"
 },
 "深谷": {
  "ko": "후카야",
  "en": "Fukaya"
 },
 "日置市その他": {
  "ko": "히오키시소노호카",
  "en": "Hiokishisonohoka"
 },
 "兵庫": {
  "ko": "효고",
  "en": "Hyogo"
 },
 "防府": {
  "ko": "호후",
  "en": "Hofu"
 },
 "扇田": {
  "ko": "오기타",
  "en": "Ogita"
 },
 "洲本市その他": {
  "ko": "스모토시소노호카",
  "en": "Sumotoshisonohoka"
 },
 "丸亀市その他": {
  "ko": "마루가메시소노호카",
  "en": "Marugameshisonohoka"
 },
 "小浜": {
  "ko": "오바마",
  "en": "Obama"
 },
 "信濃境": {
  "ko": "시나노사카이",
  "en": "Shinanosakai"
 },
 "大洋": {
  "ko": "다이요",
  "en": "Taiyo"
 },
 "日登": {
  "ko": "니치토",
  "en": "Nichito"
 },
 "しんざ": {
  "ko": "신자",
  "en": "Shinza"
 },
 "宮古": {
  "ko": "미야코",
  "en": "Miyako"
 },
 "台湾桃園国際空港(TPE)周辺": {
  "ko": "다이완모모조노코쿠사이쿠우코(TPE)슈헨",
  "en": "Taiwanmomozonokokusaikuko(Tpe)Shuhen"
 },
 "上深川": {
  "ko": "우에후카가와",
  "en": "Uefukagawa"
 },
 "狩場沢": {
  "ko": "가리바사와",
  "en": "Karibasawa"
 },
 "五条": {
  "ko": "고조",
  "en": "Gojo"
 },
 "西都城": {
  "ko": "사이토시로",
  "en": "Saitoshiro"
 },
 "伊佐市その他": {
  "ko": "이사시소노호카",
  "en": "Isashisonohoka"
 },
 "吉浦": {
  "ko": "요시우라",
  "en": "Yoshiura"
 },
 "玖波": {
  "ko": "구나미",
  "en": "Kunami"
 },
 "鏡石": {
  "ko": "가가미이시",
  "en": "Kagamiishi"
 },
 "世羅町": {
  "ko": "세라마치",
  "en": "Seramachi"
 },
 "藪神": {
  "ko": "야부카미",
  "en": "Yabukami"
 },
 "ウィンザー": {
  "ko": "우〴자",
  "en": "Uinzaa"
 },
 "安来": {
  "ko": "야스기",
  "en": "Yasugi"
 },
 "上下": {
  "ko": "조게",
  "en": "Joge"
 },
 "東多久": {
  "ko": "히가시타쿠",
  "en": "Higashitaku"
 },
 "宮之阪": {
  "ko": "미야유키사카",
  "en": "Miyayukisaka"
 },
 "武雄温泉": {
  "ko": "다케온센",
  "en": "Takeonsen"
 },
 "七飯": {
  "ko": "나나에",
  "en": "Nanae"
 },
 "あわら湯のまち": {
  "ko": "아와라유노마치",
  "en": "Awarayunomachi"
 },
 "ピサ": {
  "ko": "피사",
  "en": "Pisa"
 },
 "カイルア(オアフ島)": {
  "ko": "가이루아(오아후시마)",
  "en": "Kairua(Oafushima)"
 },
 "白川村その他": {
  "ko": "시라카와무라소노호카",
  "en": "Shirakawamurasonohoka"
 },
 "貞光": {
  "ko": "사다미쓰",
  "en": "Sadamitsu"
 },
 "引田": {
  "ko": "히키타",
  "en": "Hikita"
 },
 "南さつま市その他": {
  "ko": "미나미사쓰마시소노호카",
  "en": "Minamisatsumashisonohoka"
 },
 "向井原": {
  "ko": "무카이바라",
  "en": "Mukaibara"
 },
 "中山駅周辺": {
  "ko": "나카야마에키슈헨",
  "en": "Nakayamaekishuhen"
 },
 "パリ": {
  "ko": "파리",
  "en": "Pari"
 },
 "与論町その他": {
  "ko": "요론마치소노호카",
  "en": "Yoronmachisonohoka"
 },
 "新西脇": {
  "ko": "신자이와키",
  "en": "Shinzaiwaki"
 },
 "リトル・インディア": {
  "ko": "리토루・인데ぃ아",
  "en": "Ritoru・India"
 },
 "乙供": {
  "ko": "오쓰토모",
  "en": "Otsutomo"
 },
 "横尾": {
  "ko": "요코오",
  "en": "Yoko"
 },
 "延方": {
  "ko": "엔호",
  "en": "Enho"
 },
 "斜里町その他": {
  "ko": "샤리마치소노호카",
  "en": "Sharimachisonohoka"
 },
 "猪苗代町その他": {
  "ko": "이나와시로마치소노호카",
  "en": "Inawashiromachisonohoka"
 },
 "岩泉町その他": {
  "ko": "이와이즈미마치소노호카",
  "en": "Iwaizumimachisonohoka"
 },
 "西御坊": {
  "ko": "니시고보",
  "en": "Nishigobo"
 },
 "能登中島": {
  "ko": "노토나카지마",
  "en": "Notonakajima"
 },
 "宇品五丁目": {
  "ko": "우지나고초메",
  "en": "Ujinagochome"
 },
 "西之表市その他": {
  "ko": "니시노오모테시소노호카",
  "en": "Nishinomoteshisonohoka"
 },
 "アントワープ": {
  "ko": "안토와푸",
  "en": "Antowaapu"
 },
 "新居町": {
  "ko": "신쿄마치",
  "en": "Shinkyomachi"
 },
 "東萩": {
  "ko": "히가시하기",
  "en": "Higashihagi"
 },
 "市川本町": {
  "ko": "이치카와혼초",
  "en": "Ichikawahoncho"
 },
 "相馬": {
  "ko": "소마",
  "en": "Soma"
 },
 "ジョグジャカルタ": {
  "ko": "조구자카루타",
  "en": "Jogujakaruta"
 },
 "金浦": {
  "ko": "긴포",
  "en": "Kinpo"
 },
 "仲ノ町": {
  "ko": "나카노마치",
  "en": "Nakanomachi"
 },
 "八重瀬町": {
  "ko": "야에세마치",
  "en": "Yaesemachi"
 },
 "中条": {
  "ko": "주조",
  "en": "Chujo"
 },
 "邑南町その他": {
  "ko": "오난마치소노호카",
  "en": "Onanmachisonohoka"
 },
 "関西空港": {
  "ko": "간사이쿠우코",
  "en": "Kansaikuko"
 },
 "小出": {
  "ko": "고이데",
  "en": "Koide"
 },
 "大道": {
  "ko": "다이도",
  "en": "Daido"
 },
 "神城": {
  "ko": "가미조",
  "en": "Kamijo"
 },
 "伊達市その他": {
  "ko": "다테시소노호카",
  "en": "Dateshisonohoka"
 },
 "下市口": {
  "ko": "시모이치쿠치",
  "en": "Shimoichikuchi"
 },
 "鳥栖": {
  "ko": "도스",
  "en": "Tosu"
 },
 "マルペンサ空港周辺": {
  "ko": "마루펜사쿠우코슈헨",
  "en": "Marupensakukoshuhen"
 },
 "讃岐相生": {
  "ko": "사누키아이오이",
  "en": "Sanukiaioi"
 },
 "桔梗が丘": {
  "ko": "기쿄가오카",
  "en": "Kikyogaoka"
 },
 "下北": {
  "ko": "시모키타",
  "en": "Shimokita"
 },
 "麻植塚": {
  "ko": "오에쓰카",
  "en": "Oetsuka"
 },
 "川東": {
  "ko": "가와토",
  "en": "Kawato"
 },
 "香登": {
  "ko": "가카토",
  "en": "Kakato"
 },
 "サブロン広場": {
  "ko": "사부론히로바",
  "en": "Saburonhiroba"
 },
 "窪川": {
  "ko": "구보카와",
  "en": "Kubokawa"
 },
 "日岡": {
  "ko": "히오카",
  "en": "Hioka"
 },
 "左沢": {
  "ko": "아테라자와",
  "en": "Aterazawa"
 },
 "周南市その他": {
  "ko": "슈난시소노호카",
  "en": "Shunanshisonohoka"
 },
 "能勢町その他": {
  "ko": "노세마치소노호카",
  "en": "Nosemachisonohoka"
 },
 "市川大門": {
  "ko": "이치카와다이몬",
  "en": "Ichikawadaimon"
 },
 "太海": {
  "ko": "다우미",
  "en": "Taumi"
 },
 "人丸前": {
  "ko": "히토마로마에",
  "en": "Hitomaromae"
 },
 "下立": {
  "ko": "시타리쓰",
  "en": "Shitaritsu"
 },
 "長万部": {
  "ko": "오샤만베",
  "en": "Oshamanbe"
 },
 "上牧": {
  "ko": "간마키",
  "en": "Kanmaki"
 },
 "駒鳴": {
  "ko": "고마메이",
  "en": "Komamei"
 },
 "中深川": {
  "ko": "주후카카와",
  "en": "Chufukakawa"
 },
 "小諸": {
  "ko": "고모로",
  "en": "Komoro"
 },
 "仁保": {
  "ko": "니이호",
  "en": "Niiho"
 },
 "東栄町その他": {
  "ko": "도에이마치소노호카",
  "en": "Toeimachisonohoka"
 },
 "宇品四丁目": {
  "ko": "우지나시테이메",
  "en": "Ujinashiteime"
 },
 "国東市その他": {
  "ko": "구니사키시소노호카",
  "en": "Kunisakishisonohoka"
 },
 "勝沼ぶどう郷": {
  "ko": "가쓰누마부도사토",
  "en": "Katsunumabudosato"
 },
 "佐々木": {
  "ko": "사사키",
  "en": "Sasaki"
 },
 "小林": {
  "ko": "고바야시",
  "en": "Kobayashi"
 },
 "唐津市その他": {
  "ko": "가라쓰시소노호카",
  "en": "Karatsushisonohoka"
 },
 "東白石": {
  "ko": "도하쿠이시",
  "en": "Tohakuishi"
 },
 "吉富": {
  "ko": "요시토미",
  "en": "Yoshitomi"
 },
 "里庄": {
  "ko": "사토쇼",
  "en": "Satosho"
 },
 "久米島町": {
  "ko": "구메시마마치",
  "en": "Kumeshimamachi"
 },
 "伏尾": {
  "ko": "후쿠오",
  "en": "Fukuo"
 },
 "南小国町その他": {
  "ko": "미나미오구니마치소노호카",
  "en": "Minamiogunimachisonohoka"
 },
 "枚方公園": {
  "ko": "히라카타코엔",
  "en": "Hirakatakoen"
 },
 "歌津": {
  "ko": "우타쓰",
  "en": "Utatsu"
 },
 "菊池市その他": {
  "ko": "기쿠치시소노호카",
  "en": "Kikuchishisonohoka"
 },
 "極楽橋": {
  "ko": "고쿠라쿠하시",
  "en": "Gokurakuhashi"
 },
 "中央市場前": {
  "ko": "주오시조마에",
  "en": "Chuoshijomae"
 },
 "布施屋": {
  "ko": "후세야",
  "en": "Fuseya"
 },
 "小城": {
  "ko": "오기",
  "en": "Ogi"
 },
 "ルクセンブルク": {
  "ko": "루쿠센부루쿠",
  "en": "Rukusenburuku"
 },
 "伊賀市その他": {
  "ko": "이가시소노호카",
  "en": "Igashisonohoka"
 },
 "積丹町その他": {
  "ko": "샤코탄마치소노호카",
  "en": "Shakotanmachisonohoka"
 },
 "瀬戸田町林": {
  "ko": "세토다마치하야시",
  "en": "Setodamachihayashi"
 },
 "キングズ・クロス": {
  "ko": "긴구즈・쿠로스",
  "en": "Kinguzu・Kurosu"
 },
 "六原": {
  "ko": "로쿠하라",
  "en": "Rokuhara"
 },
 "西勝間田": {
  "ko": "사이쇼마다",
  "en": "Saishomada"
 },
 "新冠": {
  "ko": "니이캇푸",
  "en": "Niikappu"
 },
 "三次": {
  "ko": "산지",
  "en": "Sanji"
 },
 "並河": {
  "ko": "나미카와",
  "en": "Namikawa"
 },
 "三河一宮": {
  "ko": "미카와이치노미야",
  "en": "Mikawaichinomiya"
 },
 "新里": {
  "ko": "니이사토",
  "en": "Niisato"
 },
 "南九州市その他": {
  "ko": "미나미큐슈시소노호카",
  "en": "Minamikyushushisonohoka"
 },
 "穴水": {
  "ko": "아나미즈",
  "en": "Anamizu"
 },
 "山陽明石": {
  "ko": "산요아카시",
  "en": "Sanyoakashi"
 },
 "崎守": {
  "ko": "사키슈",
  "en": "Sakishu"
 },
 "有家": {
  "ko": "아리이에",
  "en": "Ariie"
 },
 "勝間田": {
  "ko": "가쓰마타",
  "en": "Katsumata"
 },
 "多比良": {
  "ko": "다이라",
  "en": "Taira"
 },
 "伊賀神戸": {
  "ko": "이가코베",
  "en": "Igakobe"
 },
 "十和田南": {
  "ko": "도와다미나미",
  "en": "Towadaminami"
 },
 "三河大塚": {
  "ko": "미카와오쓰카",
  "en": "Mikawaotsuka"
 },
 "加古川": {
  "ko": "가코가와",
  "en": "Kakogawa"
 },
 "下立口": {
  "ko": "시타리쓰쿠치",
  "en": "Shitaritsukuchi"
 },
 "只見": {
  "ko": "다다미",
  "en": "Tadami"
 },
 "新高徳": {
  "ko": "니이타카토쿠",
  "en": "Niitakatoku"
 },
 "稚内": {
  "ko": "왓카나이",
  "en": "Wakkanai"
 },
 "三豊市その他": {
  "ko": "미토요시소노호카",
  "en": "Mitoyoshisonohoka"
 },
 "三河田原": {
  "ko": "미카와다하라",
  "en": "Mikawadahara"
 },
 "愛大医学部南口": {
  "ko": "아이다이이가쿠부미나미구치",
  "en": "Aidaiigakubuminamiguchi"
 },
 "掛川市役所前": {
  "ko": "가케가와시야쿠쇼마에",
  "en": "Kakegawashiyakushomae"
 },
 "ロンドン・ヒースロー空港 (LHR) 周辺": {
  "ko": "론돈・히스로쿠우코 (LHR) 슈헨",
  "en": "Rondon・Hiisurokuko (Lhr) Shuhen"
 },
 "岩木町その他": {
  "ko": "이와키마치소노호카",
  "en": "Iwakimachisonohoka"
 },
 "千厩": {
  "ko": "센마야",
  "en": "Senmaya"
 },
 "波多浦": {
  "ko": "하타우라",
  "en": "Hataura"
 },
 "肥前浜": {
  "ko": "히젠하마",
  "en": "Hizenhama"
 },
 "神戸空港": {
  "ko": "고베쿠우코",
  "en": "Kobekuko"
 },
 "本納": {
  "ko": "혼노",
  "en": "Honno"
 },
 "奥泉": {
  "ko": "오쿠이즈미",
  "en": "Okuizumi"
 },
 "種市": {
  "ko": "다네이치",
  "en": "Taneichi"
 },
 "鹿沼": {
  "ko": "가누마",
  "en": "Kanuma"
 },
 "駅家": {
  "ko": "우마야",
  "en": "Umaya"
 },
 "大崎町その他": {
  "ko": "오사키마치소노호카",
  "en": "Osakimachisonohoka"
 },
 "竹原": {
  "ko": "다케하라",
  "en": "Takehara"
 },
 "福知山": {
  "ko": "후쿠치야마",
  "en": "Fukuchiyama"
 },
 "和食": {
  "ko": "와쇼쿠",
  "en": "Washoku"
 },
 "塩山": {
  "ko": "엔잔",
  "en": "Enzan"
 },
 "志津川": {
  "ko": "시즈가와",
  "en": "Shizugawa"
 },
 "南部": {
  "ko": "난부",
  "en": "Nanbu"
 },
 "伊予市": {
  "ko": "이요시",
  "en": "Iyoshi"
 },
 "安芸津": {
  "ko": "아키쓰",
  "en": "Akitsu"
 },
 "柴平": {
  "ko": "시바타이라",
  "en": "Shibataira"
 },
 "袋": {
  "ko": "후쿠로",
  "en": "Fukuro"
 },
 "八甲田山": {
  "ko": "핫코다산",
  "en": "Hakkodasan"
 },
 "赤川": {
  "ko": "아카가와",
  "en": "Akagawa"
 },
 "花巻": {
  "ko": "하나마키",
  "en": "Hanamaki"
 },
 "屋久島町その他": {
  "ko": "야쿠시마마치소노호카",
  "en": "Yakushimamachisonohoka"
 },
 "剣淵": {
  "ko": "겐부치",
  "en": "Kenbuchi"
 },
 "湖西市その他": {
  "ko": "고사이시소노호카",
  "en": "Kosaishisonohoka"
 },
 "上富良野": {
  "ko": "가미후라노",
  "en": "Kamifurano"
 },
 "三河三谷": {
  "ko": "미카와미타니",
  "en": "Mikawamitani"
 },
 "佐川": {
  "ko": "사가와",
  "en": "Sagawa"
 },
 "水沢江刺": {
  "ko": "미즈사와에사시",
  "en": "Mizusawaesashi"
 },
 "山之口": {
  "ko": "야마노쿠치",
  "en": "Yamanokuchi"
 },
 "萩": {
  "ko": "하기",
  "en": "Hagi"
 },
 "ベルサイユ": {
  "ko": "베루사이유",
  "en": "Berusaiyu"
 },
 "南城市": {
  "ko": "난조시",
  "en": "Nanjoshi"
 },
 "紋別市その他": {
  "ko": "몬베쓰시소노호카",
  "en": "Monbetsushisonohoka"
 },
 "平野": {
  "ko": "헤이야",
  "en": "Heiya"
 },
 "上之郷": {
  "ko": "가미노고",
  "en": "Kaminogo"
 },
 "ほっとゆだ": {
  "ko": "홋토유다",
  "en": "Hottoyuda"
 },
 "三輪": {
  "ko": "미와",
  "en": "Miwa"
 },
 "磐田": {
  "ko": "이와타",
  "en": "Iwata"
 },
 "みどり湖": {
  "ko": "미도리미즈우미",
  "en": "Midorimizumi"
 },
 "新大楽毛": {
  "ko": "신다이라쿠케",
  "en": "Shindairakuke"
 },
 "二戸": {
  "ko": "니노헤",
  "en": "Ninohe"
 },
 "君ケ浜": {
  "ko": "군케하마",
  "en": "Kunkehama"
 },
 "東新川": {
  "ko": "히가시신카와",
  "en": "Higashishinkawa"
 },
 "原爆ドーム前": {
  "ko": "겐바쿠도무마에",
  "en": "Genbakudomumae"
 },
 "布津": {
  "ko": "후쓰",
  "en": "Futsu"
 },
 "アラモアナ": {
  "ko": "아라모아나",
  "en": "Aramoana"
 },
 "バッキンガム宮殿周辺": {
  "ko": "밧킨가무큐덴슈헨",
  "en": "Bakkingamukyudenshuhen"
 },
 "伊達": {
  "ko": "다테",
  "en": "Date"
 },
 "羽沢横浜国大": {
  "ko": "하자와요코하마코쿠다이",
  "en": "Hazawayokohamakokudai"
 },
 "伊万里": {
  "ko": "이마리",
  "en": "Imari"
 },
 "壱岐市その他": {
  "ko": "이치시시소노호카",
  "en": "Ichishishisonohoka"
 },
 "福知山市その他": {
  "ko": "후쿠치야마시소노호카",
  "en": "Fukuchiyamashisonohoka"
 },
 "嘉島町その他": {
  "ko": "가시마마치소노호카",
  "en": "Kashimamachisonohoka"
 },
 "紀伊富田": {
  "ko": "기이토미타",
  "en": "Kiitomita"
 },
 "土佐久礼": {
  "ko": "도사쿠레",
  "en": "Tosakure"
 },
 "八代": {
  "ko": "야쓰시로",
  "en": "Yatsushiro"
 },
 "御前崎市その他": {
  "ko": "오마에자키시소노호카",
  "en": "Omaezakishisonohoka"
 },
 "長与": {
  "ko": "나가요",
  "en": "Nagayo"
 },
 "三つ峠": {
  "ko": "밋쓰토게",
  "en": "Mittsutoge"
 },
 "綾町その他": {
  "ko": "아야마치소노호카",
  "en": "Ayamachisonohoka"
 },
 "横瀬": {
  "ko": "요코세",
  "en": "Yokose"
 },
 "下段": {
  "ko": "게단",
  "en": "Gedan"
 },
 "因島田熊町": {
  "ko": "인시마다쿠마마치",
  "en": "Inshimadakumamachi"
 },
 "塩之沢": {
  "ko": "시오유키사와",
  "en": "Shioyukisawa"
 },
 "三良坂": {
  "ko": "미라사카",
  "en": "Mirasaka"
 },
 "篠山口": {
  "ko": "시노야마쿠치",
  "en": "Shinoyamakuchi"
 },
 "志摩市その他": {
  "ko": "시마시소노호카",
  "en": "Shimashisonohoka"
 },
 "羽前中山": {
  "ko": "우젠나카야마",
  "en": "Uzennakayama"
 },
 "新涯町": {
  "ko": "신가이마치",
  "en": "Shingaimachi"
 },
 "地蔵橋": {
  "ko": "지조하시",
  "en": "Jizohashi"
 },
 "グランプラス周辺": {
  "ko": "구란푸라스슈헨",
  "en": "Guranpurasushuhen"
 },
 "会津坂下": {
  "ko": "아이즈반게",
  "en": "Aizubange"
 },
 "四国中央市その他": {
  "ko": "시코쿠추오시소노호카",
  "en": "Shikokuchuoshisonohoka"
 },
 "いの町その他": {
  "ko": "이노마치소노호카",
  "en": "Inomachisonohoka"
 },
 "東大館": {
  "ko": "도다이칸",
  "en": "Todaikan"
 },
 "芦別": {
  "ko": "아시베쓰",
  "en": "Ashibetsu"
 },
 "男鹿": {
  "ko": "오가",
  "en": "Oga"
 },
 "北上": {
  "ko": "기타카미",
  "en": "Kitakami"
 },
 "羽咋": {
  "ko": "하쿠이",
  "en": "Hakui"
 },
 "上高地その他": {
  "ko": "가미코치소노호카",
  "en": "Kamikochisonohoka"
 },
 "ナイツブリッジ": {
  "ko": "나이쓰부릿지",
  "en": "Naitsuburijji"
 },
 "大川野": {
  "ko": "오카와노",
  "en": "Okawano"
 },
 "土佐市その他": {
  "ko": "도사시소노호카",
  "en": "Tosashisonohoka"
 },
 "十勝清水": {
  "ko": "도카치시미즈",
  "en": "Tokachishimizu"
 },
 "近江今津": {
  "ko": "오미이마즈",
  "en": "Omiimazu"
 },
 "姶良": {
  "ko": "아이라",
  "en": "Aira"
 },
 "三ツ沢上町": {
  "ko": "산쓰사와카미마치",
  "en": "Santsusawakamimachi"
 }
}
