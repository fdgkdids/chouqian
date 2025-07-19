import random
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于支持 flash 消息和 session

# 数据库文件路径,1324562976@qq.com|442202aa|zhangrx59@mail2.sysu.edu.cn|442202aa

DATABASE = 'users.db'

# 初始化数据库
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

# 初始化数据库
init_db()

# 定义64卦的信息
gua_list = [
    {"number": 1, "name": "乾卦", "sign": "上上", "text": "困龙得水好运交，不由喜气上眉梢，一切谋望皆如意，向后时运渐渐高。", "explanation": "此卦象征天，喻龙（德才的君子），表示好运来临，一切顺利。"},
    {"number": 2, "name": "坤卦", "sign": "上上", "text": "肥羊失群入山岗，饿虎逢之把口张，适口充肠心欢喜，卦若占之大吉昌。", "explanation": "此卦象征地，表示柔顺伸展，大吉大利。"},
    {"number": 3, "name": "屯卦", "sign": "下下", "text": "风刮乱丝不见头，颠三倒四犯忧愁，慢从款来左顺遂，急促反惹不自由。", "explanation": "此卦表示起始艰难，需谨慎行事。"},
    {"number": 4, "name": "蒙卦", "sign": "中下", "text": "卦中爻象犯小耗，君子占之运不高，婚姻合伙有琐碎，做事必然受苦劳。", "explanation": "此卦表示启蒙奋发，但过程可能有小挫折。"},
    {"number": 5, "name": "需卦", "sign": "中上", "text": "明珠土埋日久深，无光无亮到如今，忽然大风吹土去，自然显露有重新。", "explanation": "此卦表示守正待机，耐心等待时机。"},
    {"number": 6, "name": "讼卦", "sign": "中下", "text": "二人争路未肯降，彼此相持无赢状，若占此卦莫举事，到头多有是非妨。", "explanation": "此卦表示争讼，建议避免冲突，耐心等待。"},
    {"number": 7, "name": "师卦", "sign": "中上", "text": "将帅领兵去出征，骑着烈马拉硬弓，百步穿杨去得准，箭中金钱喜气生。", "explanation": "此卦表示军队出征，有成功之象。"},
    {"number": 8, "name": "比卦", "sign": "上上", "text": "顺风行船撒起帆，上岸才知路不平，好事临头宜谨慎，谋望求财百事宜。", "explanation": "此卦表示团结合作，大吉大利。"},
    {"number": 9, "name": "小畜卦", "sign": "中上", "text": "苗逢旱天尽焦梢，水想云浓雨不浇，农人仰面长吁气，是从款来莫心焦。", "explanation": "此卦表示小有积蓄，但需耐心等待。"},
    {"number": 10, "name": "履卦", "sign": "中上", "text": "凤凰落在西歧山，去鸣几声出圣贤，天降文王开基业，富贵荣华八百年。", "explanation": "此卦表示履道坦坦，有成功之象。"},
    {"number": 11, "name": "泰卦", "sign": "上上", "text": "学文满腹入场闱，三元及第得意回，从今解去愁和闷，喜庆平地一声雷。", "explanation": "此卦表示通泰，大吉大利。"},
    {"number": 12, "name": "否卦", "sign": "下下", "text": "虎落陷坑不堪言，进前容易退后难，谋望不遂自己便，疾病口舌事牵连。", "explanation": "此卦表示闭塞，需谨慎行事。"},
    {"number": 13, "name": "同人卦", "sign": "中上", "text": "心中有事犯猜疑，谋望从前不着实，幸遇明人来指引，至终好好成事业。", "explanation": "此卦表示团结合作，有成功之象。"},
    {"number": 14, "name": "大有卦", "sign": "上上", "text": "砍树摸巢喜气生，是非远去事皆成，婚姻合伙来费力，若问走失必来寻。", "explanation": "此卦表示大有收获，大吉大利。"},
    {"number": 15, "name": "谦卦", "sign": "上上", "text": "古镜昏暗好几年，一朝磨明似月圆，君子谋事逢此卦，运转时来事自新。", "explanation": "此卦表示谦虚有礼，大吉大利。"},
    {"number": 16, "name": "豫卦", "sign": "中上", "text": "太公插竿钓鱼溪，手拿丝线望溪垂，几回抛下无鱼走，一旦举竿双鱼归。", "explanation": "此卦表示豫悦，有成功之象。"},
    {"number": 17, "name": "随卦", "sign": "中上", "text": "泥中走路甚艰难，路上行人莫要闲，运去时来逢此卦，事须谨慎不迟延。", "explanation": "此卦表示随顺，有成功之象。"},
    {"number": 18, "name": "蛊卦", "sign": "中下", "text": "卦中爻象如推车，顺风而行两轮快，后人小心勤修德，前人修德无灾害。", "explanation": "此卦表示蛊惑，需谨慎行事。"},
    {"number": 19, "name": "临卦", "sign": "中上", "text": "君王无道民倒悬，常想拨云见青天，幸逢明主施仁政，重见太平重有年。", "explanation": "此卦表示临视，有成功之象。"},
    {"number": 20, "name": "观卦", "sign": "中上", "text": "卦中爻象如推车，顺风而行两轮快，后人小心勤修德，前人修德无灾害。", "explanation": "此卦表示观照，有成功之象。"},
    {"number": 21, "name": "噬嗑卦", "sign": "中上", "text": "运去时逢太岁星，若占此卦有灾危，夜梦蛟龙神鬼附，静心祈祷得安宁。", "explanation": "此卦表示噬嗑，需谨慎行事。"},
    {"number": 22, "name": "贲卦", "sign": "中上", "text": "近来行藏事难成，六月枯苗复发生，且宜静守无远去，免得鱼入别网惊。", "explanation": "此卦表示贲饰，有成功之象。"},
    {"number": 23, "name": "剥卦", "sign": "下下", "text": "花逢晚照已残枝，人到老年运渐衰，幸遇明人来指引，可能脱旧换新衣。", "explanation": "此卦表示剥落，需谨慎行事。"},
    {"number": 24, "name": "复卦", "sign": "中上", "text": "古镜昏暗好几年，一朝磨明似月圆，君子谋事逢此卦，运转时来事自新。", "explanation": "此卦表示复返，有成功之象。"},
    {"number": 25, "name": "无妄卦", "sign": "中上", "text": "飞鸟失机落笼中，纵然飞去也能擒，谋望未遂勿行动，静守时来显威风。", "explanation": "此卦表示无妄，需谨慎行事。"},
    {"number": 26, "name": "大畜卦", "sign": "中上", "text": "忧愁常锁两眉头，千头万绪挂心间，从今以后防开阵，任意行而不相干。", "explanation": "此卦表示大畜，有成功之象。"},
    {"number": 27, "name": "颐卦", "sign": "中上", "text": "太公独钓渭水河，手执丝杆忧愁多，时来又遇文王访，自此永不受折磨。", "explanation": "此卦表示颐养，有成功之象。"},
    {"number": 28, "name": "大过卦", "sign": "中下", "text": "夜晚行船雾里迷，明月出时难辨溪，幸得樵夫高指路，从今行去勿疑迟。", "explanation": "此卦表示大过，需谨慎行事。"},
    {"number": 29, "name": "坎卦", "sign": "下下", "text": "一轮明月照水中，只见影儿不见踪，愚夫当财下去取，摸来摸去一场空。", "explanation": "此卦表示险陷，需谨慎行事。"},
    {"number": 30, "name": "离卦", "sign": "中上", "text": "二人相争路不通，互相夺路无赢状，谋事不遂费心力，是非口舌可预防。", "explanation": "此卦表示附丽，有成功之象。"},
    {"number": 31, "name": "咸卦", "sign": "中上", "text": "运去黄金失色，时来铁也生光，福神福力支持，凡事自有安康。", "explanation": "此卦表示感应，有成功之象。"},
    {"number": 32, "name": "恒卦", "sign": "中上", "text": "风雷时雨夜行艰，拔尽蒿莱始见天，出得云来重见日，此时谋望遂心怀。", "explanation": "此卦表示恒久，有成功之象。"},
    {"number": 33, "name": "遁卦", "sign": "中下", "text": "浓云荫蔽月不明，果逢露出吐光明，谋望从今须努力，却如渔人下网时。", "explanation": "此卦表示退避，需谨慎行事。"},
    {"number": 34, "name": "大壮卦", "sign": "中上", "text": "卦中爻象犯小耗，君子占之运不高，婚姻合伙有琐碎，做事必然受苦劳。", "explanation": "此卦表示大壮，有成功之象。"},
    {"number": 35, "name": "晋卦", "sign": "中上", "text": "锄地锄去苗里草，谁想财帛将人找，一锄锄出银子来，这个运气也算好。", "explanation": "此卦表示进锐，有成功之象。"},
    {"number": 36, "name": "明夷卦", "sign": "中下", "text": "时乖运拙走不畅，愁云怨气上眉梢，幸逢明主来开导，从此青云步步高。", "explanation": "此卦表示明夷，需谨慎行事。"},
    {"number": 37, "name": "家人卦", "sign": "中上", "text": "一朵鲜花镜中开，虽美不能手中栽，求谋望事不遂意，劳碌奔波枉费财。", "explanation": "此卦表示家人，有成功之象。"},
    {"number": 38, "name": "睽卦", "sign": "中下", "text": "此卦占来运气低，如同太公遇文王，口是心非无好事，求望求财枉费力。", "explanation": "此卦表示睽违，需谨慎行事。"},
    {"number": 39, "name": "蹇卦", "sign": "下下", "text": "大雨倾盆落地，冲去路上行商，后来自有云开，一切皆得顺当。", "explanation": "此卦表示蹇难，需谨慎行事。"},
    {"number": 40, "name": "解卦", "sign": "中上", "text": "目下月令如过关，千辛万苦受熬煎，时来恰是中秋日，喜遇恩人得团圆。", "explanation": "此卦表示解脱，有成功之象。"},
    {"number": 41, "name": "损卦", "sign": "中下", "text": "时运不来好伤怀，忧心烦恼闷沉沉，幸逢明主来提携，从今必遇福星临。", "explanation": "此卦表示损减，需谨慎行事。"},
    {"number": 42, "name": "益卦", "sign": "中上", "text": "时运来时始遂心，真金出入不愁贫，可喜此卦无凶祸，牢把后头福命新。", "explanation": "此卦表示增益，有成功之象。"},
    {"number": 43, "name": "夬卦", "sign": "中上", "text": "时来运转喜气生，登台封神姜太公，到此诸神皆退位，纵然有祸不成凶。", "explanation": "此卦表示决断，有成功之象。"},
    {"number": 44, "name": "姤卦", "sign": "中下", "text": "他乡遇友喜气欢，须知运气福重添，自今交了顺遂运，向后自有升迁时。", "explanation": "此卦表示相遇，需谨慎行事。"},
    {"number": 45, "name": "萃卦", "sign": "中上", "text": "游鱼戏水被网惊，跳过龙门身化龙，三尺杨柳垂金钱，万朵桃花显芳容。", "explanation": "此卦表示萃聚，有成功之象。"},
    {"number": 46, "name": "升卦", "sign": "中上", "text": "士人来占必得名，生意买卖也兴隆，匠艺逢之交易好，农间庄稼亦收成。", "explanation": "此卦表示上升，有成功之象。"},
    {"number": 47, "name": "困卦", "sign": "下下", "text": "时运不来好伤怀，忧心烦恼闷沉沉，幸逢明主来提携，从今必遇福星临。", "explanation": "此卦表示困顿，需谨慎行事。"},
    {"number": 48, "name": "井卦", "sign": "中上", "text": "枯井破费已多年，一朝流泉出来鲜，资生济渴人称羡，时来运转喜自然。", "explanation": "此卦表示井养，有成功之象。"},
    {"number": 49, "name": "革卦", "sign": "中上", "text": "大人虎变美常多，占此占之喜气和，君自小心行好事，无非君子有庆贺。", "explanation": "此卦表示变革，有成功之象。"},
    {"number": 50, "name": "鼎卦", "sign": "中上", "text": "香炉焚起紫烟长，上祝三光照玉堂，若问前程事如意，从今诸事百成当。", "explanation": "此卦表示鼎新，有成功之象。"},
    {"number": 51, "name": "震卦", "sign": "中上", "text": "一鸟落树众鸟惊，上飞下跳乱纷纷，谁想此鸟身无伤，太岁当头福力增。", "explanation": "此卦表示震动，有成功之象。"},
    {"number": 52, "name": "艮卦", "sign": "中上", "text": "太公独钓渭水边，手执丝杆忧愁缠，时来又遇文王访，自此永不受孤单。", "explanation": "此卦表示静止，有成功之象。"},
    {"number": 53, "name": "渐卦", "sign": "中上", "text": "白鹤来占雪里梅，傲霜枝上一花开，幸逢太岁亲临此，调和鼎鼐大有权。", "explanation": "此卦表示渐进，有成功之象。"},
    {"number": 54, "name": "归妹卦", "sign": "中下", "text": "古镜昏暗好几年，一朝磨明似月圆，君子谋事逢此卦，运转时来事自新。", "explanation": "此卦表示归妹，需谨慎行事。"},
    {"number": 55, "name": "丰卦", "sign": "中上", "text": "古镜昏暗好多年，一朝磨明似月圆，出门见喜交大运，从今诸事百成全。", "explanation": "此卦表示丰大，有成功之象。"},
    {"number": 56, "name": "旅卦", "sign": "中下", "text": "飞鸟树上垒窝巢，小人使计用火烧，占此卦者逢此日，一切谋望枉徒劳。", "explanation": "此卦表示旅居，需谨慎行事。"},
    {"number": 57, "name": "巽卦", "sign": "中上", "text": "一叶孤舟落晚霞，得脱险难泛中流，时来风送滕王阁，莫愁无岸可停舟。", "explanation": "此卦表示巽顺，有成功之象。"},
    {"number": 58, "name": "兑卦", "sign": "中上", "text": "此卦占来运气平，多因疾病乱心神，时来运转吉无凶，谋望求财百事宜。", "explanation": "此卦表示喜悦，有成功之象。"},
    {"number": 59, "name": "涣卦", "sign": "中上", "text": "隔河望见一锭金，欲取岸宽水又深，利市有些终莫遂，疾病口舌事忧惊。", "explanation": "此卦表示涣散，需谨慎行事。"},
    {"number": 60, "name": "节卦", "sign": "中上", "text": "时来运转喜气生，登台封神姜太公，到此诸神皆退位，纵然有祸不成凶。", "explanation": "此卦表示节制，有成功之象。"},
    {"number": 61, "name": "中孚卦", "sign": "中上", "text": "路上行人色匆匆，急忙过桥步难停，忽地脚下逢一钉，立教醉汉睡途中。", "explanation": "此卦表示中孚，需谨慎行事。"},
    {"number": 62, "name": "小过卦", "sign": "中下", "text": "行人路过独木桥，心内惶恐眼里瞧，爽利保保过得去，慢行一步水中漂。", "explanation": "此卦表示小过，需谨慎行事。"},
    {"number": 63, "name": "既济卦", "sign": "中上", "text": "金榜以上题名时，壮元已占鳌头立，自今名望传千里，百事亨通威势大。", "explanation": "此卦表示既济，有成功之象。"},
    {"number": 64, "name": "未济卦", "sign": "中下", "text": "离地着人几丈深，是防偷营劫寨人，后封太岁为凶煞，时加谨慎祸不侵。", "explanation": "此卦表示未济，需谨慎行事。"}
]

guan_yin_signs = [
    {"number": 1, "name": "钟离成道", "attribute": "上上", "text": "开天辟地作良缘 吉日良时万物全 若得此签非小可 人行忠正帝王宣", "explanation": "此卦盘古初开天地之象，诸事皆吉。"},
    {"number": 2, "name": "苏秦不第", "attribute": "中下", "text": "临风冒雨去还乡 正是其身似燕儿 衔得坭来欲作垒 到头垒坏复须坭", "explanation": "此卦燕子衔坭之象，凡事劳心费力。"},
    {"number": 3, "name": "董永卖身葬父", "attribute": "中", "text": "临风冒雨去还乡 正是其身似燕儿 衔得坭来欲作垒 到头垒坏复须坭", "explanation": "此卦燕子衔坭之象，凡事劳心费力。"},
    {"number": 4, "name": "玉莲会十朋", "attribute": "上", "text": "千年古镜复重圆 女再求夫男再婚 自此门庭重改换 更添福禄在儿孙", "explanation": "此卦串镜重圆之象，凡事劳心有贵。"},
    {"number": 5, "name": "刘晨遇仙", "attribute": "中", "text": "临风冒雨去还乡 正是其身似燕儿 衔得坭来欲作垒 到头垒坏复须坭", "explanation": "此卦燕子衔坭之象，凡事劳心费力。"},
    {"number": 6, "name": "吕洞宾度何仙姑", "attribute": "上上", "text": "一帆风顺水长流 两岸芦花风正秋 但见渔翁垂钓处 满身明月泛归舟", "explanation": "此卦一帆风顺之象，诸事皆吉。"},
    {"number": 7, "name": "铁拐李度曹国舅", "attribute": "上", "text": "一帆风顺水长流 两岸芦花风正秋 但见渔翁垂钓处 满身明月泛归舟", "explanation": "此卦一帆风顺之象，诸事皆吉。"},
    {"number": 8, "name": "蓝采和度韩湘子", "attribute": "中", "text": "一帆风顺水长流 两岸芦花风正秋 但见渔翁垂钓处 满身明月泛归舟", "explanation": "此卦一帆风顺之象，诸事皆吉。"},
    {"number": 9, "name": "张果老度何仙姑", "attribute": "上", "text": "一帆风顺水长流 两岸芦花风正秋 但见渔翁垂钓处 满身明月泛归舟", "explanation": "此卦一帆风顺之象，诸事皆吉。"},
    {"number": 10, "name": "汉钟离度吕洞宾", "attribute": "上上", "text": "一帆风顺水长流 两岸芦花风正秋 但见渔翁垂钓处 满身明月泛归舟", "explanation": "此卦一帆风顺之象，诸事皆吉。"},
    # ... 添加其他签的信息
{"number": 11, "name": "书荐姜维", "attribute": "上", "text": "欲求胜事可非常，争奈亲姻日暂忙。到头竟必成鹿箭，贵人指引贵人乡。", "explanation": "此卦贵人指引之象，诸事有成。"},
    {"number": 12, "name": "武吉遇师", "attribute": "上", "text": "否去泰来咫尺间，暂交君子出于山。若逢虎兔佳音信，立志忙中事即间。", "explanation": "此卦否去泰来之象，诸事有成。"},
{"number": 13, "name": "姜太公钓鱼", "attribute": "中", "text": "君今庚甲未亨通，且向江头作钓翁。玉兔重生应发迹，万人头上逞英雄。", "explanation": "此卦玉兔重生之象，凡事待时。"},
    {"number": 14, "name": "子牙弃官", "attribute": "中", "text": "宛如仙鹤出樊笼，脱却羁縻处处通。南北东西无障碍，任君直上九霄中。", "explanation": "此卦仙鹤出笼之象，凡事大吉。"},
    {"number": 15, "name": "张君瑞求官", "attribute": "上", "text": "触人口气最难吞，忽有灾危祸到门。燕子垒巢终有成，方知此理是乾坤。", "explanation": "此卦燕子垒巢之象，凡事忍耐终成。"},
    {"number": 16, "name": "叶梦熊朝帝", "attribute": "上", "text": "愁眉思虑暂时开，启出云霄喜自来。宛如粪土中藏玉，良工一举出尘埃。", "explanation": "此卦粪土藏玉之象，凡事终吉。"},
    {"number": 17, "name": "石崇被难", "attribute": "中下", "text": "莫听闲言说是非，晨昏只好念阿弥。若将狂话为真实，书饼如何止得饥。", "explanation": "此卦书饼止饥之象，凡事虚妄。"},
    {"number": 18, "name": "曹国舅求仙", "attribute": "中", "text": "金乌西坠兔东升，日夜循环至古今。僧道得知无不利，士农工商各从心。", "explanation": "此卦日月循环之象，凡事和合大吉。"},
    {"number": 19, "name": "子仪封王", "attribute": "上", "text": "急水滩头放船归，风波作浪欲何为。若要安然求稳静，等待浪静过此危。", "explanation": "此卦船过急滩之象，凡事守旧待时。"},
    {"number": 20, "name": "姜女寻夫", "attribute": "中", "text": "当春久雨喜初晴，玉兔金乌渐渐明。旧事已成新事遂，看看一跳入蓬瀛。", "explanation": "此卦久雨初晴之象，凡事遂意。"},
    {"number": 21, "name": "李旦龙凤配合", "attribute": "上", "text": "阴阳道合总由天，女嫁男婚岂偶然。但看龙蛇堪运动，熊罴叶梦喜团圆。", "explanation": "此卦阴阳道合之象，凡事和合大吉。"},
    {"number": 22, "name": "六郎逢救", "attribute": "中", "text": "旱时田里皆枯槁，谢天甘雨落淋淋。花果草木皆润泽，始知一雨值千金。", "explanation": "此卦旱逢甘雨之象，凡事难中有救。"},
    {"number": 23, "name": "王翦灭楚", "attribute": "上", "text": "欲攀仙桂蟾宫去，岂虑天门不放开。谋望一般音信好，高人自送岭头来。", "explanation": "此卦蟾宫折桂之象，凡事必成。"},
    {"number": 24, "name": "文王遇姜尚", "attribute": "上", "text": "一番桃李一番新，谁识阳和气象明。林下水边多活计，见山了了称心情。", "explanation": "此卦阳和气象之象，凡事顺遂。"},
    {"number": 25, "name": "刘小姐爱蒙正", "attribute": "中", "text": "过了忧危事几重，从今再立永无空。宽心自有宽心计，得遇高人立大功。", "explanation": "此卦忧危已过之象，凡事有成。"},
    {"number": 26, "name": "桓侯得病", "attribute": "中下", "text": "上下传来事总虚，天边接得一封书。书中许我功名遂，直到终时亦是虚。", "explanation": "此卦虚传消息之象，凡事虚妄。"},
    {"number": 27, "name": "李邺侯救孤", "attribute": "上", "text": "一谋一用一番书，虑后思前不敢为。时到贵人相助力，如山墙立可安居。", "explanation": "此卦贵人相助之象，凡事终吉。"},
    {"number": 28, "name": "相如完璧归赵", "attribute": "上", "text": "东方月上正婵娟，顷刻云遮月半边。莫道圆时还又缺，须教缺处复重圆。", "explanation": "此卦月缺重圆之象，凡事终吉。"},
    {"number": 29, "name": "张骞误入斗牛宫", "attribute": "中", "text": "宝剑出匣耀光明，在匣全然不惹尘。今得贵人携出现，有威有势众人钦。", "explanation": "此卦宝剑出匣之象，凡事有威有势。"},
    {"number": 30, "name": "柳毅传书", "attribute": "上", "text": "劝君切莫向他求，似鹤飞来暗箭投。若去采薪蛇在草，恐遭毒口也忧愁。", "explanation": "此卦暗箭难防之象，凡事谨慎。"},
{"number": 31, "name": "苏武牧羊", "attribute": "中", "text": "清闲无忧静处坐，饱后吃茶时坐卧。放下身心不用忙，必定不招冤与祸。", "explanation": "此卦清闲无忧之象，凡事守旧安常。"},
    {"number": 32, "name": "周公解梦", "attribute": "上", "text": "前程杳杳定无疑，石中藏玉有谁知。一朝良匠分明剖，始觉安然碧玉期。", "explanation": "此卦石中藏玉之象，凡事终吉。"},
    {"number": 33, "name": "庄子鼓盆歌", "attribute": "中", "text": "石藏无价玉和珍，只管他乡外处寻。宛如持灯更觅火，不如收拾枉劳心。", "explanation": "此卦持灯觅火之象，凡事守旧待时。"},
    {"number": 34, "name": "萧何追韩信", "attribute": "上", "text": "行藏出入礼义恭，言必忠良信必从。心不了然且静澈，光明红日正当空。", "explanation": "此卦红日当空之象，凡事顺遂。"},
    {"number": 35, "name": "王勃滕王阁序", "attribute": "上", "text": "衣冠重整旧家风，道是无功却有功。扫却当途荆棘刺，三人共议事和同。", "explanation": "此卦重整家风之象，凡事和合大吉。"},
    {"number": 36, "name": "谢安石东山高卧", "attribute": "上", "text": "目前虽遇困，后福自然来。高山人仰止，有日庆云开。", "explanation": "此卦后福自然之象，凡事终吉。"},
    {"number": 37, "name": "李靖归山", "attribute": "中", "text": "欲待身安动泰时，风中灯烛不相宜。不如收拾深堂坐，庶免光摇静处期。", "explanation": "此卦风中灯烛之象，凡事守旧待时。"},
    {"number": 38, "name": "何文秀玉钗记", "attribute": "上", "text": "镜月当空出匣时，刹那云雾又昏迷。宽心守待浮云散，更改相宜可为期。", "explanation": "此卦浮云遮月之象，凡事守旧待时。"},
    {"number": 39, "name": "吕蒙正守困", "attribute": "中", "text": "天边消息应难思，切莫牵罡妄求之。若把石头磨作镜，精神枉费也难施。", "explanation": "此卦石头磨镜之象，凡事虚妄。"},
    {"number": 40, "name": "马援女献铜柱", "attribute": "上", "text": "红轮西坠兔东升，阴长阳消百事亨。若是女人宜望用，增添财禄福其增。", "explanation": "此卦阴长阳消之象，女人大吉。"},
    {"number": 41, "name": "董永遇仙", "attribute": "上", "text": "无限好语君须记，却为认贼将作子。莫贪眼下有些甜，可虑他时还受苦。", "explanation": "此卦认贼作子之象，凡事谨慎。"},
    {"number": 42, "name": "韩信功劳不久", "attribute": "中", "text": "君垂恩泽润无边，覆祷祈穰没党偏。一切有情皆受用，均沾乐利得周全。", "explanation": "此卦恩泽无边之象，凡事大吉。"},
    {"number": 43, "name": "玄德入赘孙权妹", "attribute": "上", "text": "一纸官书火急催，扁舟东下浪如雷。虽然目下多惊险，保汝平安去复回。", "explanation": "此卦惊险平安之象，凡事终吉。"},
    {"number": 44, "name": "姜维邓艾斗阵", "attribute": "中", "text": "棋逢敌手要藏机，黑白盘中未决时。到底欲知谁胜负，须教先着相机宜。", "explanation": "此卦棋逢敌手之象，凡事谨慎。"},
    {"number": 45, "name": "张良隐山", "attribute": "上", "text": "温柔自古胜刚强，积善之门大吉昌。若是有人占此卦，宛如正渴遇琼浆。", "explanation": "此卦积善之门之象，凡事大吉。"},
    {"number": 46, "name": "赵子龙救阿斗", "attribute": "上", "text": "劝君耐守旧生涯，把定身心莫听邪。直待有人轻着力，枯枝老树再生花。", "explanation": "此卦枯木逢春之象，凡事终吉。"},
    {"number": 47, "name": "梁灏夺魁", "attribute": "上", "text": "锦上添花色愈鲜，运来禄马喜双全。时人莫讶功名晚，一举登科四海传。", "explanation": "此卦锦上添花之象，凡事大吉。"},
    {"number": 48, "name": "赵五娘寻夫", "attribute": "中", "text": "鹍鸟秋来化作鹏，好游快乐喜飞腾。翱翔万里云霄去，余外诸禽总不能。", "explanation": "此卦鹍鸟化鹏之象，凡事终吉。"},
    {"number": 49, "name": "张翼德义释严颜", "attribute": "上", "text": "营图万事若冰消，何必悭贪苦自劳。试向天台高处望，南柯梦断不堪招。", "explanation": "此卦万事冰消之象，凡事大吉。"},
    {"number": 50, "name": "陶渊明归隐", "attribute": "中", "text": "五湖四海任君行，高挂帆蓬自在撑。若得顺风随即至，满船宝贝喜层层。", "explanation": "此卦顺风得宝之象，凡事顺遂。"},
{"number": 51, "name": "孔明求寿", "attribute": "中", "text": "夏日初临日正长，人皆愁恼热非常。天公也解诸人意，故遣薰风特送凉。", "explanation": "此卦夏日送凉之象，凡事终吉。"},
    {"number": 52, "name": "太白醉捞明月", "attribute": "上", "text": "水中捉月费工夫，费尽工夫却又无。莫信闲言并浪语，枉劳心力独身孤。", "explanation": "此卦水中捉月之象，凡事虚妄。"},
    {"number": 53, "name": "刘先主入赘孙权妹", "attribute": "上", "text": "失意翻成得意时，龙吟虎啸两相宜。青天自有通宵路，许我功名再有期。", "explanation": "此卦失意得意之象，凡事终吉。"},
    {"number": 54, "name": "苏秦背剑", "attribute": "中", "text": "梦中得宝醒来无，应说巫山只是虚。苦问婚姻并病讼，别寻生路得相宜。", "explanation": "此卦梦中得宝之象，凡事虚妄。"},
    {"number": 55, "name": "周武王登位", "attribute": "上", "text": "父贤传子子传孙，衣食丰隆只靠天。堂上椿萱人快乐，饥饭渴饮困时眠。", "explanation": "此卦衣食丰隆之象，凡事大吉。"},
    {"number": 56, "name": "王昭君和番", "attribute": "中", "text": "涧小石粗流水响，力劳撑驾恐损伤。路须指出前江去，风静潮平尽不妨。", "explanation": "此卦涧小石粗之象，凡事谨慎。"},
    {"number": 57, "name": "董仲寻亲", "attribute": "上", "text": "说是说非风过耳，好衣好禄自然来。君须记取他年事，汝意还同我意谐。", "explanation": "此卦好衣好禄之象，凡事大吉。"},
    {"number": 58, "name": "苏东坡劝民", "attribute": "上", "text": "忠言善语君须记，莫向他方求别艺。劝君安守旧生涯，除却有余都不是。", "explanation": "此卦安守旧业之象，凡事守旧待时。"},
    {"number": 59, "name": "张骞误入斗牛宫", "attribute": "中", "text": "直上高山去学仙，岂知一旦帝王宣。青天白日常明照，志在声名四海传。", "explanation": "此卦直上高山之象，凡事终吉。"},
    {"number": 60, "name": "赤壁鏖兵", "attribute": "上", "text": "抱薪救火火增烟，烧却三千及大千。若问营谋并出入，不如收拾莫忧煎。", "explanation": "此卦抱薪救火之象，凡事谨慎。"},
    {"number": 61, "name": "苏小妹难夫", "attribute": "中", "text": "日上吟诗月下歌，逢场作戏笑呵呵。相逢会遇难藏避，喝彩齐声嗹哩啰。", "explanation": "此卦逢场作戏之象，凡事虚妄。"},
    {"number": 62, "name": "宋太祖陈桥即位", "attribute": "上", "text": "晨昏全赖佛扶持，虽是逢危不见危。若得贵人来接引，此时福禄自相随。", "explanation": "此卦逢危不见危之象，凡事终吉。"},
    {"number": 63, "name": "杨令公撞李陵碑", "attribute": "中", "text": "昔日行船失了针，今朝依旧海中寻。若还寻得原针在，也费功夫也费心。", "explanation": "此卦寻针之象，凡事劳心费力。"},
    {"number": 64, "name": "管鲍分金", "attribute": "上", "text": "譬若初三四五蟾，半无半有未完全。须教十五良宵夜，到处清光到处圆。", "explanation": "此卦月缺重圆之象，凡事终吉。"},
    {"number": 65, "name": "蒙正木兰和诗", "attribute": "中", "text": "苦问荣华何日成，此心常向静中行。如今得遇高人力，好把蟠桃会上名。", "explanation": "此卦贵人相助之象，凡事终吉。"},
    {"number": 66, "name": "江遗嘱儿", "attribute": "上", "text": "路险马行人去远，失群羊困虎相当。危滩船过风翻浪，春暮花残天降霜。", "explanation": "此卦路险马行之象，凡事谨慎。"},
    {"number": 67, "name": "金星试窦儿", "attribute": "中", "text": "一条金线秤君心，无减无增无重轻。为人平生心正直，文章全具艺光明。", "explanation": "此卦心正直之象，凡事大吉。"},
    {"number": 68, "name": "钱玉莲投江", "attribute": "中", "text": "南贩珍珠北贩盐，年来几倍货财添。劝君积此修功德，作福时来命运甜。", "explanation": "此卦积善修德之象，凡事大吉。"},
    {"number": 69, "name": "孙庞斗智", "attribute": "中", "text": "冬来岭上一枝梅，叶落枝枯总不摧。但得阳春消息至，依然还我作花魁。", "explanation": "此卦梅花报春之象，凡事终吉。"},
    {"number": 70, "name": "李密反唐", "attribute": "中", "text": "朝朝役役恰如蜂，飞来飞去西复东。春暮花残无觅处，此身不恋旧丛中。", "explanation": "此卦劳碌之象，凡事谨慎。"},
{"number": 71, "name": "庄子扇坟", "attribute": "中", "text": "谁知爱宠遇强徒，女子当年嫁二夫。自是一弓施两箭，骑龙跨凤上江湖。", "explanation": "此卦一弓两箭之象，凡事谨慎。"},
    {"number": 72, "name": "高文举追姑", "attribute": "上", "text": "河渠傍路有高低，可叹长途日已西。纵有荣华好时节，直须猴犬换金鸡。", "explanation": "此卦长途跋涉之象，凡事谨慎。"},
    {"number": 73, "name": "王勃题滕王阁", "attribute": "上", "text": "忆昔兰房分半钗，而今忽把信音乖。痴心指望成连理，到底谁知事不谐。", "explanation": "此卦事不谐之象，凡事谨慎。"},
    {"number": 74, "name": "崔武求官", "attribute": "中", "text": "崔巍崔巍复崔巍，履险如夷去复来。身似菩提心似镜，长江一道放春回。", "explanation": "此卦履险如夷之象，凡事终吉。"},
    {"number": 75, "name": "刘小姐爱蒙正", "attribute": "中", "text": "宛如仙鹤出樊笼，脱却羁縻处处通。南北东西无障碍，任君直上九霄中。", "explanation": "此卦仙鹤出笼之象，凡事大吉。"},
    {"number": 76, "name": "萧何月下追韩信", "attribute": "上", "text": "鱼龙混杂意和同，耐守寒潭未济中。不觉一朝头角耸，禹门一跃到天宫。", "explanation": "此卦鱼跃龙门之象，凡事终吉。"},
    {"number": 77, "name": "吕后害韩信", "attribute": "中", "text": "梦中说梦获多财，身外浮名总莫猜。水远山遥难信定，贵人一指笑颜开。", "explanation": "此卦梦中说梦之象，凡事虚妄。"},
    {"number": 78, "name": "袁安守困", "attribute": "中", "text": "冷水来浇白雪洋，不寒不热自温凉。要行天下无他事，惟有中藏一艺强。", "explanation": "此卦温水之象，凡事守旧待时。"},
    {"number": 79, "name": "宋仁宗认母", "attribute": "上", "text": "虚空结愿结人缘，保得人安愿未还。得兔忘蹄真绝迹，敢将初誓谩轻瞒。", "explanation": "此卦结愿之象，凡事终吉。"},
    {"number": 80, "name": "郭璞为母下葬", "attribute": "上", "text": "直上高山去学仙，岂知一旦帝王宣。青天白日常明照，志在声名四海传。", "explanation": "此卦直上高山之象，凡事终吉。"},
    {"number": 81, "name": "风送滕王阁", "attribute": "上", "text": "梧桐叶落秋将暮，行客归程去似云。谢得天公高著力，顺风相送宝舟轻。", "explanation": "此卦顺风相送之象，凡事大吉。"},
    {"number": 82, "name": "宋仁宗认母", "attribute": "上", "text": "时融时泰不须疑，指日新君坐帝畿。丹凤来仪天下治，四方黎庶尽皈依。", "explanation": "此卦时融时泰之象，凡事大吉。"},
    {"number": 83, "name": "诸葛孔明学道", "attribute": "上", "text": "譬若初三四五蟾，半无半有未完全。须教十五良宵夜，到处清光到处圆。", "explanation": "此卦月缺重圆之象，凡事终吉。"},
    {"number": 84, "name": "庄子试妻", "attribute": "中", "text": "因名丧德不和同，切莫贪图造化工。凡事只宜随分过，免教烦恼日添浓。", "explanation": "此卦随分守己之象，凡事谨慎。"},
    {"number": 85, "name": "韩文公祭鳄鱼", "attribute": "上", "text": "重开山后藏前事，万宝园中可再逢。蛇兔逢牛三合会，到处游鱼化真龙。", "explanation": "此卦鱼化真龙之象，凡事终吉。"},
    {"number": 86, "name": "商辂中三元", "attribute": "上", "text": "一舟行货好招邀，积少成多自富饶。常把他人比自己，管须日后胜今朝。", "explanation": "此卦积少成多之象，凡事大吉。"},
    {"number": 87, "name": "武侯七擒孟获", "attribute": "上", "text": "人行半岭日衔山，峻岭崖岩未可攀。仰望上天垂护佑，此身犹在太虚间。", "explanation": "此卦上天护佑之象，凡事终吉。"},
    {"number": 88, "name": "高文举追姑", "attribute": "上", "text": "木有根荄水有源，君当自此究其原。莫随道路人闲话，讼到终凶是至言。", "explanation": "此卦究其根源之象，凡事谨慎。"},
    {"number": 89, "name": "大舜耕历山", "attribute": "上", "text": "樽前无事且高歌，时未来时奈若何。白马渡江嘶日暮，虎头城里看巍峨。", "explanation": "此卦时来运转之象，凡事终吉。"},
    {"number": 90, "name": "杨文广陷柳州", "attribute": "中", "text": "崆峒城里事如麻，无事如君有几家。劝汝不须勤致祷，徒劳心力走天涯。", "explanation": "此卦徒劳心力之象，凡事谨慎。"},
     {"number": 91, "name": "赵子龙救阿斗", "attribute": "上", "text": "好把愁眉须展开，大才大用荐将来。一条大路平如掌，凡有施为总称怀。", "explanation": "此卦大才大用之象，凡事大吉。"},
    {"number": 92, "name": "蔡卿报恩", "attribute": "上", "text": "自幼为旅任施为，财禄丰盈不用求。若问进身谋望事，秀才出去状元回。", "explanation": "此卦财禄丰盈之象，凡事大吉。"},
    {"number": 93, "name": "邵康节定阴阳", "attribute": "上", "text": "鸾凤翔毛雨淋漓，当时却被雀儿欺。终教一日云开散，依旧还君整羽衣。", "explanation": "此卦云开见日之象，凡事终吉。"},
    {"number": 94, "name": "提结过长者", "attribute": "中", "text": "小人君子别贤愚，事有差讹合是非。琴遇知音当鼓操，争如定静得便宜。", "explanation": "此卦定静得宜之象，凡事谨慎。"},
    {"number": 95, "name": "张文远求官", "attribute": "上", "text": "事业功勤苦力求，光明红日正当头。若逢牛鼠交承日，那日成名万事休。", "explanation": "此卦红日当空之象，凡事大吉。"},
    {"number": 96, "name": "山涛见王衍", "attribute": "上", "text": "巍巍宝塔不寻常，八面玲珑尽放光。劝汝志心勤顶礼，天龙拥护降千祥。", "explanation": "此卦宝塔放光之象，凡事大吉。"},
    {"number": 97, "name": "买臣五十富贵", "attribute": "上", "text": "五十功名心已灰，那知富贵逼人来。更行好事存方寸，寿比冈陵位鼎台。", "explanation": "此卦富贵逼人之象，凡事大吉。"},
    {"number": 98, "name": "薛仁贵投军", "attribute": "上", "text": "经商得利称心怀，福禄荣华倍获财。若问进身谋望事，秀才出去状元回。", "explanation": "此卦福禄荣华之象，凡事大吉。"},
    {"number": 99, "name": "陶渊明赏菊", "attribute": "上", "text": "贵人遭遇水云乡，冷淡交情滋味长。黄阁开时延故旧，正如锦上再添花。", "explanation": "此卦锦上添花之象，凡事大吉。"},
    {"number": 100, "name": "三教谈道", "attribute": "上", "text": "佛神灵变与君知，痴人说事转昏迷。老人求得灵签去，不如守旧待来时。", "explanation": "此卦守旧待时之象，凡事终吉。"},
]
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html')
    else:
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user[0] == password:
            session['username'] = username
            flash('登录成功！', 'success')
            return redirect(url_for('home'))
        else:
            flash('用户名或密码错误！', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
            flash('密码必须不少于8位，且包含数字和字母！', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('密码和确认密码不一致！', 'error')
            return redirect(url_for('register'))

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('注册成功！', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('用户名已存在！', 'error')
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('您已成功登出！', 'success')
    return redirect(url_for('home'))

@app.route('/draw_gua')
def draw_gua():
    if 'username' not in session:
        flash('请先登录！', 'error')
        return redirect(url_for('login'))

    random_number = random.randint(1, 64)
    selected_gua = next(gua for gua in gua_list if gua["number"] == random_number)

    return render_template('draw_gua.html', sign=selected_gua)

@app.route('/draw_guanyin')
def draw_guanyin():
    if 'username' not in session:
        flash('请先登录！', 'error')
        return redirect(url_for('login'))

    random_number = random.randint(1, 100)
    selected_sign = next(sign for sign in guan_yin_signs if sign["number"] == random_number)

    return render_template('draw_guanyin.html', sign=selected_sign)


