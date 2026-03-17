import json
from app import create_app
from models import db, Poem, LearningSession, InteractionEvent

def init_database():
    """初始化数据库并插入古诗数据"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表（包括新的追踪表）
        db.create_all()
        print("✅ Database tables created successfully!")
        print("📊 Tables: Poem, User, Exercise, LearningRecord, QARecord, AttentionTracking, LearningSession, InteractionEvent")
        
        # 检查是否已有数据
        if Poem.query.count() > 0:
            print("Database already contains poem data.")
            return
        
        # 插入古诗数据
        poems_data = [
            {
                "title": "静夜思",
                "author": "李白",
                "dynasty": "唐",
                "content": "床前明月光，疑是地上霜。\n举头望明月，低头思故乡。",
                "translation": "明亮的月光洒在床前的窗户纸上，好像地上泛起了一层白霜。我禁不住抬起头来，看那天窗外空中的一轮明月，不由得低头沉思，想起远方的家乡。",
                "background": "这首诗是李白在外地思念家乡时所作。诗人在寂静的夜晚，看到明月当空，触景生情，思念起远方的故乡和亲人。",
                "analysis": "全诗语言清新朴素，韵律和谐，意境深远。通过对月光的描写，表达了诗人深深的思乡之情。",
                "annotations": json.dumps({
                    "床": "这里指窗台或床榻",
                    "疑": "怀疑，以为",
                    "举头": "抬头",
                    "故乡": "家乡，故土"
                }),
                "difficulty_level": 1,
                "tags": "思乡,月亮,夜晚",
                "video_path": "/static/videos/jingyesi.mp4",
                "audio_path": "/static/audio/jingyesi.mp3"
            },
            {
                "title": "春晓",
                "author": "孟浩然",
                "dynasty": "唐",
                "content": "春眠不觉晓，处处闻啼鸟。\n夜来风雨声，花落知多少。",
                "translation": "春日里贪睡不知不觉天已破晓，搅醒我的是那啁啾的小鸟。昨天夜里风声雨声一直不断，那娇美的春花不知被吹落了多少？",
                "background": "这是孟浩然隐居在鹿门山时所作，诗人通过春晨的所见所闻，表现了对春天的喜爱和对自然的关注。",
                "analysis": "诗歌描绘了春天早晨的美好景象，表达了诗人对春天的喜爱之情。语言自然流畅，意境清新。",
                "annotations": json.dumps({
                    "春眠": "春天的睡眠",
                    "晓": "天亮，黎明",
                    "啼鸟": "鸟儿的叫声",
                    "夜来": "昨夜"
                }),
                "difficulty_level": 1,
                "tags": "春天,早晨,鸟鸣",
                "video_path": "/static/videos/chunxiao.mp4",
                "audio_path": "/static/audio/chunxiao.mp3"
            },
            {
                "title": "登鹳雀楼",
                "author": "王之涣",
                "dynasty": "唐",
                "content": "白日依山尽，黄河入海流。\n欲穷千里目，更上一层楼。",
                "translation": "夕阳依傍着西山慢慢地沉没，滔滔黄河朝着东海汹涌奔流。若想把千里的风光景物看够，那就要登上更高的一层城楼。",
                "background": "诗人登上鹳雀楼，眺望山河壮丽景色时所作。鹳雀楼位于山西永济，是古代著名的观景胜地。",
                "analysis": "前两句写景，描绘了壮阔的自然景象；后两句抒情，表达了积极向上的人生态度。蕴含着深刻的哲理。",
                "annotations": json.dumps({
                    "依": "靠着",
                    "尽": "消失",
                    "欲": "想要",
                    "穷": "穷尽，看完",
                    "更": "再"
                }),
                "difficulty_level": 2,
                "tags": "登高,哲理,黄河",
                "video_path": "/static/videos/dengguanquelou.mp4",
                "audio_path": "/static/audio/dengguanquelou.mp3"
            },
            {
                "title": "相思",
                "author": "王维",
                "dynasty": "唐",
                "content": "红豆生南国，春来发几枝。\n愿君多采撷，此物最相思。",
                "translation": "红豆生长在阳光明媚的南方，每逢春天不知长出多少新枝。希望思念的人儿多多采摘，因为它最能寄托相思之情。",
                "background": "这是王维怀念友人时所作的诗。红豆又名相思子，常用来象征爱情或友情。",
                "analysis": "诗歌借红豆寄托相思之情，语言朴素自然，情感真挚。全诗意境优美，寓意深刻。",
                "annotations": json.dumps({
                    "红豆": "相思子，一种植物",
                    "南国": "南方",
                    "君": "您，对朋友的尊称",
                    "采撷": "采摘",
                    "此物": "这东西，指红豆"
                }),
                "difficulty_level": 2,
                "tags": "相思,友情,红豆",
                "video_path": "/static/videos/xiangsi.mp4",
                "audio_path": "/static/audio/xiangsi.mp3"
            },
            {
                "title": "咏鹅",
                "author": "骆宾王",
                "dynasty": "唐",
                "content": "鹅，鹅，鹅，曲项向天歌。\n白毛浮绿水，红掌拨清波。",
                "translation": "鹅，鹅，鹅，弯着脖子朝天欢叫。洁白的羽毛漂浮在碧绿水面，红红的脚掌拨动着清清水波。",
                "background": "这是骆宾王七岁时所作的诗，是一首咏物诗，描写了鹅的形象和动态。",
                "analysis": "诗歌生动形象地描绘了鹅的外形特征和动作，语言简洁明快，充满童趣。",
                "annotations": json.dumps({
                    "咏": "用诗歌赞美",
                    "曲项": "弯着脖子",
                    "向天歌": "朝着天空鸣叫",
                    "浮": "漂浮",
                    "拨": "划动"
                }),
                "difficulty_level": 1,
                "tags": "咏物,动物,童趣",
                "video_path": "/static/videos/yonge.mp4",
                "audio_path": "/static/audio/yonge.mp3"
            },
            {
                "title": "悯农",
                "author": "李绅",
                "dynasty": "唐",
                "content": "锄禾日当午，汗滴禾下土。\n谁知盘中餐，粒粒皆辛苦。",
                "translation": "盛夏中午，烈日炎炎，农民还在劳作，汗珠滴入泥土。有谁想到，我们碗中的米饭，粒粒饱含着农民的血汗？",
                "background": "李绅目睹农民在烈日下辛勤劳作的情景，深受感动，写下这首诗来反映农民的辛苦。",
                "analysis": "诗歌通过对农民劳作场面的描写，表达了对农民辛勤劳动的赞美和对珍惜粮食的呼吁。",
                "annotations": json.dumps({
                    "悯": "怜悯，同情",
                    "锄禾": "用锄头松土除草",
                    "日当午": "正午时分",
                    "盘中餐": "碗里的饭",
                    "皆": "都是"
                }),
                "difficulty_level": 1,
                "tags": "农民,劳动,珍惜粮食",
                "video_path": "/static/videos/minnong.mp4",
                "audio_path": "/static/audio/minnong.mp3"
            },
            {
                "title": "江雪",
                "author": "柳宗元",
                "dynasty": "唐",
                "content": "千山鸟飞绝，万径人踪灭。\n孤舟蓑笠翁，独钓寒江雪。",
                "translation": "所有的山，飞鸟全都断绝；所有的路，不见人影踪迹。江上孤舟，渔翁披蓑戴笠；独自垂钓，不怕冰雪侵袭。",
                "background": "柳宗元被贬永州时所作，通过描写雪景中独钓的渔翁，表达了自己孤独而坚韧的心境。",
                "analysis": "诗歌通过对比手法，突出了渔翁的孤独和坚韧。意境深远，寓意深刻。",
                "annotations": json.dumps({
                    "绝": "断绝，没有",
                    "万径": "所有的小路",
                    "踪": "踪迹，脚印",
                    "蓑笠翁": "穿蓑衣戴斗笠的老翁",
                    "寒江": "寒冷的江面"
                }),
                "difficulty_level": 3,
                "tags": "雪景,孤独,坚韧",
                "video_path": "/static/videos/jiangxue.mp4",
                "audio_path": "/static/audio/jiangxue.mp3"
            },
            {
                "title": "赋得古原草送别",
                "author": "白居易",
                "dynasty": "唐",
                "content": "离离原上草，一岁一枯荣。\n野火烧不尽，春风吹又生。\n远芳侵古道，晴翠接荒城。\n又送王孙去，萋萋满别情。",
                "translation": "长长的原上草是多么茂盛，每年秋冬枯黄春来草色浓。无情的野火只能烧掉干叶，春风吹来大地又是绿茸茸。野草野花蔓延着淹没古道，艳阳下草地尽头是你征程。我又一次送走知心的好友，茂密的青草代表我的深情。",
                "background": "白居易十六岁时在长安应试所作，是一首送别诗，借草的生命力来表达离别之情。",
                "analysis": "诗歌前四句写草的顽强生命力，后四句点明送别主题。通过对草的描写，表达了对友人的深情厚谊。",
                "annotations": json.dumps({
                    "赋得": "按照规定的题目作诗",
                    "离离": "茂盛的样子",
                    "一岁": "一年",
                    "荣": "茂盛",
                    "远芳": "远处的香草",
                    "侵": "侵占，蔓延",
                    "王孙": "对友人的尊称",
                    "萋萋": "草茂盛的样子"
                }),
                "difficulty_level": 3,
                "tags": "送别,草原,生命力",
                "video_path": "/static/videos/fudeguyuancao.mp4",
                "audio_path": "/static/audio/fudeguyuancao.mp3"
            },
            {
                "title": "望庐山瀑布",
                "author": "李白",
                "dynasty": "唐",
                "content": "日照香炉生紫烟，遥看瀑布挂前川。\n飞流直下三千尺，疑是银河落九天。",
                "translation": "香炉峰在阳光的照射下生起紫色烟霞，远远望见瀑布似白色绢绸悬挂在山前。高崖上飞腾直落的瀑布好像有几千尺，让人恍惚以为银河从天上泻落到人间。",
                "background": "李白游览庐山时，被香炉峰瀑布的壮观景象所震撼，写下这首千古名篇。",
                "analysis": "诗歌运用夸张和比喻的手法，生动地描绘了庐山瀑布的壮观景象，表现了诗人豪迈的气概。",
                "annotations": json.dumps({
                    "香炉": "香炉峰，庐山的一座山峰",
                    "紫烟": "紫色的云雾",
                    "遥看": "远远地看",
                    "挂": "悬挂",
                    "前川": "前面的河流",
                    "银河": "天河，银河系",
                    "九天": "天空的最高处"
                }),
                "difficulty_level": 2,
                "tags": "瀑布,庐山,壮观",
                "video_path": "/static/videos/wanglushanpubu.mp4",
                "audio_path": "/static/audio/wanglushanpubu.mp3"
            },
            {
                "title": "早发白帝城",
                "author": "李白",
                "dynasty": "唐",
                "content": "朝辞白帝彩云间，千里江陵一日还。\n两岸猿声啼不住，轻舟已过万重山。",
                "translation": "清晨告别五彩云霞间的白帝城，千里之外的江陵一天就可以到达。两岸猿猴的啼声还在耳边不停地啼叫，轻快的小船已驶过连绵不绝的万重山峦。",
                "background": "李白因永王李璘案被流放夜郎，途中遇赦，心情愉快，在返回途中写下这首诗。",
                "analysis": "诗歌表现了诗人愉快的心情和对自由的向往。语言轻快流畅，节奏明快。",
                "annotations": json.dumps({
                    "朝": "早晨",
                    "辞": "告别",
                    "白帝": "白帝城，在今重庆奉节",
                    "彩云间": "彩云缭绕的地方",
                    "江陵": "今湖北荆州",
                    "还": "返回",
                    "轻舟": "轻快的小船"
                }),
                "difficulty_level": 2,
                "tags": "行舟,三峡,愉快",
                "video_path": "/static/videos/zaofabaidicheng.mp4",
                "audio_path": "/static/audio/zaofabaidicheng.mp3"
            }
        ]
        
        # 插入诗歌数据
        for poem_data in poems_data:
            poem = Poem(**poem_data)
            db.session.add(poem)
        
        db.session.commit()
        print(f"Successfully inserted {len(poems_data)} poems into the database!")

if __name__ == '__main__':
    init_database()
