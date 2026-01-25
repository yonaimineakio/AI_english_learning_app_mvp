"""
シャドーイング文のシードデータ

各シナリオのキーフレーズに対して3文ずつ、合計9文/シナリオを定義
"""

from typing import List, Dict, Any

# 各シナリオのシャドーイング文データ
# フォーマット: {scenario_id: [(key_phrase, sentence_en, sentence_ja, difficulty), ...]}

SHADOWING_SEED_DATA: Dict[int, List[tuple]] = {
    # === シナリオ1: 空港チェックイン ===
    1: [
        ("be about to board", "I'm about to board the flight to New York.", "ニューヨーク行きの便に搭乗するところです。", "beginner"),
        ("be about to board", "We're about to board, so please turn off your phone.", "まもなく搭乗ですので、電話の電源をお切りください。", "beginner"),
        ("be about to board", "The gate is closing. I'm about to board now.", "ゲートが閉まります。今搭乗するところです。", "beginner"),
        ("be supposed to check in", "I'm supposed to check in at counter 5.", "5番カウンターでチェックインすることになっています。", "beginner"),
        ("be supposed to check in", "What time am I supposed to check in?", "何時にチェックインすればいいですか？", "beginner"),
        ("be supposed to check in", "You're supposed to check in at least 2 hours before.", "少なくとも2時間前にチェックインすることになっています。", "beginner"),
        ("have to drop off my baggage", "I have to drop off my baggage before going to the gate.", "ゲートに行く前に荷物を預けなければなりません。", "beginner"),
        ("have to drop off my baggage", "Where do I have to drop off my baggage?", "荷物はどこで預ければいいですか？", "beginner"),
        ("have to drop off my baggage", "I have to drop off my baggage here, right?", "ここで荷物を預けるんですよね？", "beginner"),
    ],
    # === シナリオ2: ビジネスミーティング ===
    2: [
        ("want to bring up", "I want to bring up an important issue.", "重要な問題を提起したいと思います。", "intermediate"),
        ("want to bring up", "Before we move on, I want to bring up one more point.", "次に進む前に、もう一点提起したいことがあります。", "intermediate"),
        ("want to bring up", "I want to bring up the budget concerns.", "予算の懸念事項を提起したいと思います。", "intermediate"),
        ("need to follow up on", "I need to follow up on the action items from last week.", "先週のアクションアイテムをフォローアップする必要があります。", "intermediate"),
        ("need to follow up on", "We need to follow up on the client's feedback.", "クライアントのフィードバックをフォローアップする必要があります。", "intermediate"),
        ("need to follow up on", "Let me follow up on that point later.", "その点については後でフォローアップさせてください。", "intermediate"),
        ("be ready to move forward", "I think we're ready to move forward with the plan.", "計画を進める準備ができていると思います。", "intermediate"),
        ("be ready to move forward", "Are we ready to move forward to the next phase?", "次のフェーズに進む準備はできていますか？", "intermediate"),
        ("be ready to move forward", "Once approved, we'll be ready to move forward.", "承認されれば、前に進む準備ができます。", "intermediate"),
    ],
    # === シナリオ3: レストランでの注文 ===
    3: [
        ("would like to order", "I would like to order the grilled salmon, please.", "グリルサーモンをお願いします。", "beginner"),
        ("would like to order", "We would like to order some appetizers first.", "まず前菜をいくつか注文したいのですが。", "beginner"),
        ("would like to order", "I would like to order the chef's special.", "シェフのおすすめをお願いします。", "beginner"),
        ("be allergic to", "I'm allergic to shellfish.", "私は貝類にアレルギーがあります。", "beginner"),
        ("be allergic to", "Is there anything I should avoid if I'm allergic to nuts?", "ナッツアレルギーの場合、避けるべきものはありますか？", "beginner"),
        ("be allergic to", "My friend is allergic to dairy products.", "私の友人は乳製品にアレルギーがあります。", "beginner"),
        ("want to try", "I want to try something local.", "地元の料理を食べてみたいです。", "beginner"),
        ("want to try", "I want to try your most popular dish.", "一番人気の料理を食べてみたいです。", "beginner"),
        ("want to try", "I want to try the dessert menu.", "デザートメニューを試してみたいです。", "beginner"),
    ],
    # === シナリオ4: オンライン商談 ===
    4: [
        ("would like to walk you through", "I would like to walk you through our proposal.", "私たちの提案をご説明させていただきます。", "advanced"),
        ("would like to walk you through", "Let me walk you through the main features.", "主な機能についてご説明させてください。", "advanced"),
        ("would like to walk you through", "I would like to walk you through the timeline.", "スケジュールについてご説明させていただきます。", "advanced"),
        ("be willing to consider", "We're willing to consider your counteroffer.", "お客様の対案を検討する用意があります。", "advanced"),
        ("be willing to consider", "Are you willing to consider a longer contract?", "より長期の契約をご検討いただけますか？", "advanced"),
        ("be willing to consider", "I'm willing to consider alternative solutions.", "代替案を検討する用意があります。", "advanced"),
        ("plan to move forward", "We plan to move forward by the end of this month.", "今月末までに前進する予定です。", "advanced"),
        ("plan to move forward", "How do you plan to move forward with implementation?", "実装をどのように進める予定ですか？", "advanced"),
        ("plan to move forward", "We plan to move forward once we have approval.", "承認が得られ次第、前進する予定です。", "advanced"),
    ],
    # === シナリオ5: ホテルチェックイン ===
    5: [
        ("have a reservation under", "I have a reservation under the name Tanaka.", "田中という名前で予約しています。", "intermediate"),
        ("have a reservation under", "We have a reservation under my wife's name.", "妻の名前で予約しています。", "intermediate"),
        ("have a reservation under", "I have a reservation under my company's name.", "会社名で予約しています。", "intermediate"),
        ("would like to request", "I would like to request a room with a view.", "眺めの良い部屋をお願いしたいのですが。", "intermediate"),
        ("would like to request", "I would like to request extra towels.", "追加のタオルをお願いしたいのですが。", "intermediate"),
        ("would like to request", "I would like to request an early check-in.", "アーリーチェックインをお願いしたいのですが。", "intermediate"),
        ("need to check out", "I need to check out by noon tomorrow.", "明日の正午までにチェックアウトする必要があります。", "intermediate"),
        ("need to check out", "What time do I need to check out?", "何時にチェックアウトする必要がありますか？", "intermediate"),
        ("need to check out", "I need to check out a bit early for my flight.", "フライトのため少し早めにチェックアウトする必要があります。", "intermediate"),
    ],
    # === シナリオ6: 最高のバケーション ===
    6: [
        ("dream of going to", "I dream of going to the Maldives someday.", "いつかモルディブに行くのが夢です。", "beginner"),
        ("dream of going to", "I've always dreamed of going to Paris.", "ずっとパリに行くのが夢でした。", "beginner"),
        ("dream of going to", "We dream of going to a tropical island.", "熱帯の島に行くのが夢です。", "beginner"),
        ("would love to stay at", "I would love to stay at a beach resort.", "ビーチリゾートに泊まりたいです。", "beginner"),
        ("would love to stay at", "I would love to stay at a traditional Japanese inn.", "伝統的な日本旅館に泊まりたいです。", "beginner"),
        ("would love to stay at", "We would love to stay at a hotel with a pool.", "プール付きのホテルに泊まりたいです。", "beginner"),
        ("want to get away from", "I want to get away from the busy city life.", "忙しい都会の生活から離れたいです。", "beginner"),
        ("want to get away from", "I want to get away from work for a week.", "1週間仕事から離れたいです。", "beginner"),
        ("want to get away from", "We want to get away from the cold weather.", "寒い天気から逃れたいです。", "beginner"),
    ],
    # === シナリオ7: 日本を案内する ===
    7: [
        ("would like to show you around", "I would like to show you around Tokyo.", "東京をご案内したいと思います。", "intermediate"),
        ("would like to show you around", "I would like to show you around my hometown.", "私の故郷をご案内したいと思います。", "intermediate"),
        ("would like to show you around", "Let me show you around the temple.", "お寺をご案内させてください。", "intermediate"),
        ("plan to take you to", "I plan to take you to a famous sushi restaurant.", "有名な寿司屋にお連れする予定です。", "intermediate"),
        ("plan to take you to", "I plan to take you to see Mount Fuji.", "富士山を見にお連れする予定です。", "intermediate"),
        ("plan to take you to", "We plan to take you to a traditional tea ceremony.", "伝統的な茶道にお連れする予定です。", "intermediate"),
        ("want to introduce you to", "I want to introduce you to Japanese cuisine.", "日本料理をご紹介したいと思います。", "intermediate"),
        ("want to introduce you to", "I want to introduce you to my family.", "私の家族をご紹介したいと思います。", "intermediate"),
        ("want to introduce you to", "I want to introduce you to our local customs.", "私たちの地元の習慣をご紹介したいと思います。", "intermediate"),
    ],
    # === シナリオ8: 入国審査・税関で ===
    8: [
        ("be here on business", "I'm here on business for a conference.", "会議のためのビジネスで来ています。", "advanced"),
        ("be here on business", "I'm here on business to meet with clients.", "クライアントとの会議のためビジネスで来ています。", "advanced"),
        ("be here on business", "We're here on business for about a week.", "約1週間のビジネスで来ています。", "advanced"),
        ("plan to stay for", "I plan to stay for five days.", "5日間滞在する予定です。", "advanced"),
        ("plan to stay for", "I plan to stay for two weeks.", "2週間滞在する予定です。", "advanced"),
        ("plan to stay for", "We plan to stay for the entire month.", "丸1ヶ月滞在する予定です。", "advanced"),
        ("need to declare", "Do I need to declare these items?", "これらの品物を申告する必要がありますか？", "advanced"),
        ("need to declare", "I need to declare some souvenirs.", "いくつかのお土産を申告する必要があります。", "advanced"),
        ("need to declare", "I don't think I need to declare anything.", "申告するものはないと思います。", "advanced"),
    ],
    # === シナリオ9: 旅行計画を友達と相談 ===
    9: [
        ("be thinking of going to", "I'm thinking of going to Osaka next month.", "来月大阪に行こうと思っています。", "beginner"),
        ("be thinking of going to", "Are you thinking of going to the beach?", "ビーチに行こうと思っていますか？", "beginner"),
        ("be thinking of going to", "We're thinking of going to Europe this summer.", "今年の夏はヨーロッパに行こうと思っています。", "beginner"),
        ("want to spend time doing", "I want to spend time doing outdoor activities.", "アウトドアアクティビティをして過ごしたいです。", "beginner"),
        ("want to spend time doing", "I want to spend time doing sightseeing.", "観光をして過ごしたいです。", "beginner"),
        ("want to spend time doing", "We want to spend time doing nothing at the beach.", "ビーチで何もせずに過ごしたいです。", "beginner"),
        ("be flexible about", "I'm flexible about the dates.", "日程については融通が利きます。", "beginner"),
        ("be flexible about", "I'm flexible about the hotel.", "ホテルについては融通が利きます。", "beginner"),
        ("be flexible about", "We're flexible about the destination.", "目的地については融通が利きます。", "beginner"),
    ],
    # === シナリオ10: 財布を無くして警察に相談 ===
    10: [
        ("seem to have lost", "I seem to have lost my wallet on the train.", "電車の中で財布をなくしたようです。", "beginner"),
        ("seem to have lost", "I seem to have lost my phone somewhere.", "どこかで携帯をなくしたようです。", "beginner"),
        ("seem to have lost", "I seem to have lost my passport.", "パスポートをなくしたようです。", "beginner"),
        ("need to report", "I need to report a lost item.", "遺失物を届け出る必要があります。", "beginner"),
        ("need to report", "I need to report this to the police.", "これを警察に届け出る必要があります。", "beginner"),
        ("need to report", "Where do I need to report this?", "これをどこに届け出ればいいですか？", "beginner"),
        ("try to remember", "I'm trying to remember where I last saw it.", "最後に見た場所を思い出そうとしています。", "beginner"),
        ("try to remember", "Let me try to remember the exact time.", "正確な時間を思い出してみます。", "beginner"),
        ("try to remember", "I'm trying to remember what was inside.", "中に何が入っていたか思い出そうとしています。", "beginner"),
    ],
    # === シナリオ11: カスタマーサービスに相談 ===
    11: [
        ("would like to ask about", "I would like to ask about my order status.", "注文状況についてお聞きしたいのですが。", "beginner"),
        ("would like to ask about", "I would like to ask about your return policy.", "返品ポリシーについてお聞きしたいのですが。", "beginner"),
        ("would like to ask about", "I would like to ask about the warranty.", "保証についてお聞きしたいのですが。", "beginner"),
        ("need to complain about", "I need to complain about the service I received.", "受けたサービスについて苦情を言う必要があります。", "beginner"),
        ("need to complain about", "I need to complain about a damaged product.", "破損した商品について苦情を言う必要があります。", "beginner"),
        ("need to complain about", "I need to complain about the delivery delay.", "配送の遅延について苦情を言う必要があります。", "beginner"),
        ("hope to get replaced", "I hope to get this replaced with a new one.", "これを新しいものに交換してもらいたいです。", "beginner"),
        ("hope to get replaced", "I hope to get a refund or replacement.", "返金か交換をしてもらいたいです。", "beginner"),
        ("hope to get replaced", "I hope to get this issue resolved today.", "今日中にこの問題を解決してもらいたいです。", "beginner"),
    ],
    # === シナリオ12: おしゃれカフェで店員と雑談 ===
    12: [
        ("feel like trying", "I feel like trying something new today.", "今日は何か新しいものを試してみたい気分です。", "intermediate"),
        ("feel like trying", "I feel like trying your seasonal special.", "季節限定のスペシャルを試してみたい気分です。", "intermediate"),
        ("feel like trying", "I feel like trying a cold drink.", "冷たい飲み物を試してみたい気分です。", "intermediate"),
        ("be curious to know", "I'm curious to know what's in this drink.", "この飲み物に何が入っているか気になります。", "intermediate"),
        ("be curious to know", "I'm curious to know how you make this.", "これをどうやって作るのか気になります。", "intermediate"),
        ("be curious to know", "I'm curious to know where the beans are from.", "豆がどこから来ているのか気になります。", "intermediate"),
        ("keep coming back to", "I keep coming back to this cafe.", "このカフェに何度も来てしまいます。", "intermediate"),
        ("keep coming back to", "I keep coming back to this neighborhood.", "この界隈に何度も来てしまいます。", "intermediate"),
        ("keep coming back to", "I keep coming back to try different items.", "違うメニューを試しに何度も来てしまいます。", "intermediate"),
    ],
    # === シナリオ13: ショーチケットを入手 ===
    13: [
        ("be looking for", "I'm looking for two tickets for tonight's show.", "今夜のショーのチケットを2枚探しています。", "beginner"),
        ("be looking for", "I'm looking for seats near the front.", "前の方の席を探しています。", "beginner"),
        ("be looking for", "I'm looking for the cheapest available tickets.", "一番安いチケットを探しています。", "beginner"),
        ("hope to get seats near", "I hope to get seats near the stage.", "ステージの近くの席が取れるといいのですが。", "beginner"),
        ("hope to get seats near", "I hope to get seats near the aisle.", "通路側の席が取れるといいのですが。", "beginner"),
        ("hope to get seats near", "We hope to get seats near each other.", "隣同士の席が取れるといいのですが。", "beginner"),
        ("want to sit close to", "I want to sit close to the front.", "前の方に座りたいです。", "beginner"),
        ("want to sit close to", "I want to sit close to my friends.", "友達の近くに座りたいです。", "beginner"),
        ("want to sit close to", "We want to sit close to the exit.", "出口の近くに座りたいです。", "beginner"),
    ],
    # === シナリオ14: 公園で雑談 ===
    14: [
        ("just wanted to say", "I just wanted to say what a beautiful day it is.", "なんて素晴らしい日なんでしょうと言いたかっただけです。", "intermediate"),
        ("just wanted to say", "I just wanted to say hello.", "こんにちはと言いたかっただけです。", "intermediate"),
        ("just wanted to say", "I just wanted to say I love your dog.", "あなたの犬が素敵だと言いたかっただけです。", "intermediate"),
        ("enjoy spending time", "I enjoy spending time in nature.", "自然の中で過ごすのが好きです。", "intermediate"),
        ("enjoy spending time", "I enjoy spending time reading here.", "ここで読書をして過ごすのが好きです。", "intermediate"),
        ("enjoy spending time", "I enjoy spending time with my family here.", "ここで家族と過ごすのが好きです。", "intermediate"),
        ("like to come here to", "I like to come here to relax.", "リラックスするためにここに来るのが好きです。", "intermediate"),
        ("like to come here to", "I like to come here to exercise.", "運動するためにここに来るのが好きです。", "intermediate"),
        ("like to come here to", "I like to come here to watch the sunset.", "夕日を見るためにここに来るのが好きです。", "intermediate"),
    ],
    # === シナリオ15: ミーティングをリスケする ===
    15: [
        ("need to reschedule", "I need to reschedule our meeting.", "ミーティングをリスケする必要があります。", "beginner"),
        ("need to reschedule", "I'm sorry, but I need to reschedule.", "申し訳ありませんが、リスケする必要があります。", "beginner"),
        ("need to reschedule", "Can we reschedule to next week?", "来週にリスケできますか？", "beginner"),
        ("be able to move to", "Would you be able to move to Thursday?", "木曜日に変更できますか？", "beginner"),
        ("be able to move to", "I'd be able to move to any day next week.", "来週ならどの日でも変更できます。", "beginner"),
        ("be able to move to", "We might be able to move to the afternoon.", "午後に変更できるかもしれません。", "beginner"),
        ("appreciate it if we could", "I would appreciate it if we could reschedule.", "リスケしていただけるとありがたいです。", "beginner"),
        ("appreciate it if we could", "I would appreciate it if we could meet earlier.", "もっと早く会えるとありがたいです。", "beginner"),
        ("appreciate it if we could", "I would appreciate it if we could do a video call.", "ビデオ通話にしていただけるとありがたいです。", "beginner"),
    ],
    # === シナリオ16: ミーティングを立てる ===
    16: [
        ("want to set up", "I want to set up a meeting for next week.", "来週のミーティングを設定したいです。", "intermediate"),
        ("want to set up", "I want to set up a quick call to discuss this.", "これについて話すための簡単な電話を設定したいです。", "intermediate"),
        ("want to set up", "I want to set up a recurring weekly meeting.", "毎週の定例ミーティングを設定したいです。", "intermediate"),
        ("be available to meet", "Are you available to meet on Tuesday?", "火曜日にお会いできますか？", "intermediate"),
        ("be available to meet", "I'm available to meet anytime this week.", "今週ならいつでもお会いできます。", "intermediate"),
        ("be available to meet", "When would you be available to meet?", "いつお会いできますか？", "intermediate"),
        ("work around your schedule", "I can work around your schedule.", "あなたのスケジュールに合わせられます。", "intermediate"),
        ("work around your schedule", "Let me work around your schedule.", "あなたのスケジュールに合わせさせてください。", "intermediate"),
        ("work around your schedule", "We'll work around your schedule.", "あなたのスケジュールに合わせます。", "intermediate"),
    ],
    # === シナリオ17: 会議を進行する ===
    17: [
        ("would like to start with", "I would like to start with the agenda.", "アジェンダから始めたいと思います。", "advanced"),
        ("would like to start with", "I would like to start with a brief update.", "簡単なアップデートから始めたいと思います。", "advanced"),
        ("would like to start with", "I would like to start with introductions.", "自己紹介から始めたいと思います。", "advanced"),
        ("move on to", "Let's move on to the next topic.", "次のトピックに移りましょう。", "advanced"),
        ("move on to", "I think we can move on to the discussion.", "議論に移れると思います。", "advanced"),
        ("move on to", "Shall we move on to the Q&A session?", "質疑応答に移りましょうか？", "advanced"),
        ("come back to", "Let's come back to this point later.", "この点については後で戻りましょう。", "advanced"),
        ("come back to", "We can come back to this if time permits.", "時間があればこれに戻れます。", "advanced"),
        ("come back to", "I'd like to come back to what you said earlier.", "先ほどおっしゃったことに戻りたいと思います。", "advanced"),
    ],
    # === シナリオ18: 契約条件の交渉 ===
    18: [
        ("would like to focus on", "I would like to focus on the pricing.", "価格に焦点を当てたいと思います。", "advanced"),
        ("would like to focus on", "I would like to focus on the delivery terms.", "納期条件に焦点を当てたいと思います。", "advanced"),
        ("would like to focus on", "I would like to focus on the key issues.", "主要な問題に焦点を当てたいと思います。", "advanced"),
        ("be prepared to offer", "We're prepared to offer a 10% discount.", "10%の割引を提供する用意があります。", "advanced"),
        ("be prepared to offer", "We're prepared to offer extended support.", "延長サポートを提供する用意があります。", "advanced"),
        ("be prepared to offer", "I'm prepared to offer better payment terms.", "より良い支払い条件を提供する用意があります。", "advanced"),
        ("be willing to compromise", "We're willing to compromise on the deadline.", "締め切りについては妥協する用意があります。", "advanced"),
        ("be willing to compromise", "I'm willing to compromise on certain points.", "いくつかの点については妥協する用意があります。", "advanced"),
        ("be willing to compromise", "Are you willing to compromise on the price?", "価格について妥協する用意はありますか？", "advanced"),
    ],
    # === シナリオ19: 顧客満足度の調査結果をプレゼン ===
    19: [
        ("would like to share", "I would like to share the key findings.", "主要な調査結果を共有したいと思います。", "advanced"),
        ("would like to share", "I would like to share our recommendations.", "私たちの提言を共有したいと思います。", "advanced"),
        ("would like to share", "I would like to share some insights from the data.", "データからの洞察を共有したいと思います。", "advanced"),
        ("be based on", "These results are based on 500 responses.", "これらの結果は500件の回答に基づいています。", "advanced"),
        ("be based on", "Our analysis is based on the last quarter's data.", "分析は前四半期のデータに基づいています。", "advanced"),
        ("be based on", "The recommendations are based on customer feedback.", "提言は顧客のフィードバックに基づいています。", "advanced"),
        ("lead us to believe", "The data leads us to believe satisfaction is improving.", "データから満足度が向上していると考えられます。", "advanced"),
        ("lead us to believe", "These findings lead us to believe we need changes.", "これらの調査結果から変更が必要だと考えられます。", "advanced"),
        ("lead us to believe", "The trends lead us to believe growth will continue.", "トレンドから成長が続くと考えられます。", "advanced"),
    ],
    # === シナリオ20: プロジェクトの遅延を謝罪する ===
    20: [
        ("would like to apologize for", "I would like to apologize for the delay.", "遅延についてお詫び申し上げます。", "intermediate"),
        ("would like to apologize for", "I would like to apologize for any inconvenience.", "ご不便をおかけして申し訳ありません。", "intermediate"),
        ("would like to apologize for", "We would like to apologize for the confusion.", "混乱を招いたことをお詫び申し上げます。", "intermediate"),
        ("have been trying to catch up", "We have been trying to catch up on the schedule.", "スケジュールに追いつこうとしています。", "intermediate"),
        ("have been trying to catch up", "I have been trying to catch up with the workload.", "仕事量に追いつこうとしています。", "intermediate"),
        ("have been trying to catch up", "The team has been trying to catch up all week.", "チームは一週間ずっと追いつこうとしています。", "intermediate"),
        ("plan to prevent this from happening again", "We plan to prevent this from happening again.", "今後このようなことが起こらないようにする予定です。", "intermediate"),
        ("plan to prevent this from happening again", "I plan to prevent this from happening again by improving our process.", "プロセスを改善してこれが再発しないようにする予定です。", "intermediate"),
        ("plan to prevent this from happening again", "We have measures to prevent this from happening again.", "これが再発しないための対策があります。", "intermediate"),
    ],
    # === シナリオ21: 体調不良で休む ===
    21: [
        ("not feel well today", "I'm not feeling well today.", "今日は体調が悪いです。", "intermediate"),
        ("not feel well today", "I haven't been feeling well since yesterday.", "昨日から体調が悪いです。", "intermediate"),
        ("not feel well today", "I don't feel well enough to come in today.", "今日は出勤できるほど体調が良くありません。", "intermediate"),
        ("need to take the day off", "I need to take the day off to rest.", "休むために休暇を取る必要があります。", "intermediate"),
        ("need to take the day off", "I need to take the day off to see a doctor.", "医者に診てもらうために休暇を取る必要があります。", "intermediate"),
        ("need to take the day off", "I'm sorry, but I need to take the day off.", "申し訳ありませんが、休暇を取る必要があります。", "intermediate"),
        ("hand over my tasks", "I will hand over my tasks to my colleague.", "私の仕事を同僚に引き継ぎます。", "intermediate"),
        ("hand over my tasks", "Let me hand over my tasks before I leave.", "出る前に仕事を引き継がせてください。", "intermediate"),
        ("hand over my tasks", "I've already handed over my tasks for today.", "今日の仕事はすでに引き継ぎました。", "intermediate"),
    ],
    # === シナリオ22: 病院で症状を説明 ===
    22: [
        ("have been experiencing", "I have been experiencing headaches for a week.", "1週間頭痛が続いています。", "intermediate"),
        ("have been experiencing", "I have been experiencing dizziness.", "めまいがしています。", "intermediate"),
        ("have been experiencing", "I have been experiencing stomach pain.", "胃の痛みが続いています。", "intermediate"),
        ("started about ... ago", "It started about three days ago.", "3日ほど前に始まりました。", "intermediate"),
        ("started about ... ago", "The pain started about a week ago.", "痛みは1週間ほど前に始まりました。", "intermediate"),
        ("started about ... ago", "The symptoms started about two hours ago.", "症状は2時間ほど前に始まりました。", "intermediate"),
        ("be allergic to", "I'm allergic to penicillin.", "ペニシリンにアレルギーがあります。", "intermediate"),
        ("be allergic to", "I'm not allergic to anything that I know of.", "私が知る限り、何にもアレルギーはありません。", "intermediate"),
        ("be allergic to", "I might be allergic to this medication.", "この薬にアレルギーがあるかもしれません。", "intermediate"),
    ],
    # === シナリオ23: 薬局で薬を購入 ===
    23: [
        ("be looking for something for", "I'm looking for something for a cold.", "風邪に効くものを探しています。", "beginner"),
        ("be looking for something for", "I'm looking for something for allergies.", "アレルギーに効くものを探しています。", "beginner"),
        ("be looking for something for", "I'm looking for something for a headache.", "頭痛に効くものを探しています。", "beginner"),
        ("how often should I take", "How often should I take this medicine?", "この薬はどのくらいの頻度で飲めばいいですか？", "beginner"),
        ("how often should I take", "How often should I take these pills?", "この錠剤はどのくらいの頻度で飲めばいいですか？", "beginner"),
        ("how often should I take", "How often should I take it with food?", "食事と一緒にどのくらいの頻度で飲めばいいですか？", "beginner"),
        ("have any side effects", "Does this medicine have any side effects?", "この薬に副作用はありますか？", "beginner"),
        ("have any side effects", "I want to know if this will have any side effects.", "これに副作用があるか知りたいです。", "beginner"),
        ("have any side effects", "What kind of side effects does this have?", "これにはどんな副作用がありますか？", "beginner"),
    ],
    # === シナリオ24: 歯医者で予約・相談 ===
    24: [
        ("have a toothache", "I have a toothache in my back tooth.", "奥歯が痛いです。", "intermediate"),
        ("have a toothache", "I've had a toothache for several days.", "数日間歯が痛いです。", "intermediate"),
        ("have a toothache", "I have a toothache that won't go away.", "治らない歯の痛みがあります。", "intermediate"),
        ("would like to make an appointment", "I would like to make an appointment for next week.", "来週の予約を取りたいのですが。", "intermediate"),
        ("would like to make an appointment", "I would like to make an appointment as soon as possible.", "できるだけ早く予約を取りたいのですが。", "intermediate"),
        ("would like to make an appointment", "I would like to make an appointment for a checkup.", "検診の予約を取りたいのですが。", "intermediate"),
        ("how much will it cost", "How much will the treatment cost?", "治療費はいくらですか？", "intermediate"),
        ("how much will it cost", "How much will it cost without insurance?", "保険なしだといくらですか？", "intermediate"),
        ("how much will it cost", "Can you tell me how much it will cost?", "いくらかかるか教えていただけますか？", "intermediate"),
    ],
    # === シナリオ25: スーパーで店員に質問 ===
    25: [
        ("be looking for", "I'm looking for organic vegetables.", "オーガニック野菜を探しています。", "beginner"),
        ("be looking for", "I'm looking for gluten-free products.", "グルテンフリーの商品を探しています。", "beginner"),
        ("be looking for", "I'm looking for the dairy section.", "乳製品コーナーを探しています。", "beginner"),
        ("do you have any", "Do you have any fresh fish today?", "今日は新鮮な魚はありますか？", "beginner"),
        ("do you have any", "Do you have any of these in stock?", "これの在庫はありますか？", "beginner"),
        ("do you have any", "Do you have any special offers today?", "今日は特売品はありますか？", "beginner"),
        ("where can I find", "Where can I find the bread aisle?", "パン売り場はどこですか？", "beginner"),
        ("where can I find", "Where can I find cooking oil?", "料理油はどこにありますか？", "beginner"),
        ("where can I find", "Where can I find international foods?", "輸入食品はどこにありますか？", "beginner"),
    ],
    # === シナリオ26: 服屋で試着・相談 ===
    26: [
        ("would like to try on", "I would like to try on this jacket.", "このジャケットを試着したいのですが。", "beginner"),
        ("would like to try on", "I would like to try on these pants.", "このパンツを試着したいのですが。", "beginner"),
        ("would like to try on", "Can I try on this in a different size?", "別のサイズで試着できますか？", "beginner"),
        ("do you have this in", "Do you have this in a larger size?", "これのもっと大きいサイズはありますか？", "beginner"),
        ("do you have this in", "Do you have this in blue?", "これの青はありますか？", "beginner"),
        ("do you have this in", "Do you have this in a medium?", "これのMサイズはありますか？", "beginner"),
        ("what do you recommend", "What do you recommend for a formal occasion?", "フォーマルな場には何がおすすめですか？", "beginner"),
        ("what do you recommend", "What do you recommend to go with this?", "これに合わせるには何がおすすめですか？", "beginner"),
        ("what do you recommend", "What do you recommend for summer?", "夏には何がおすすめですか？", "beginner"),
    ],
    # === シナリオ27: 美容院で髪型をオーダー ===
    27: [
        ("would like to get", "I would like to get a trim.", "少し整えてもらいたいです。", "intermediate"),
        ("would like to get", "I would like to get layers.", "レイヤーを入れてもらいたいです。", "intermediate"),
        ("would like to get", "I would like to get highlights.", "ハイライトを入れてもらいたいです。", "intermediate"),
        ("want to keep the length", "I want to keep the length but add volume.", "長さは保ちつつボリュームを出したいです。", "intermediate"),
        ("want to keep the length", "I want to keep the length at the back.", "後ろの長さは保ちたいです。", "intermediate"),
        ("want to keep the length", "I want to keep the length but thin it out.", "長さは保ちつつ量を減らしたいです。", "intermediate"),
        ("not too short", "Please don't cut it too short.", "短くしすぎないでください。", "intermediate"),
        ("not too short", "I want it shorter but not too short.", "短くしたいですが、短すぎないように。", "intermediate"),
        ("not too short", "Not too short on the sides, please.", "横は短くしすぎないでください。", "intermediate"),
    ],
    # === シナリオ28: 携帯ショップで契約相談 ===
    28: [
        ("be interested in switching to", "I'm interested in switching to a cheaper plan.", "もっと安いプランに変更したいです。", "advanced"),
        ("be interested in switching to", "I'm interested in switching to unlimited data.", "無制限データプランに変更したいです。", "advanced"),
        ("be interested in switching to", "I'm interested in switching to a family plan.", "ファミリープランに変更したいです。", "advanced"),
        ("what's included in", "What's included in this monthly plan?", "この月額プランには何が含まれていますか？", "advanced"),
        ("what's included in", "What's included in the basic package?", "基本パッケージには何が含まれていますか？", "advanced"),
        ("what's included in", "What's included in terms of international calls?", "国際電話については何が含まれていますか？", "advanced"),
        ("are there any hidden fees", "Are there any hidden fees I should know about?", "知っておくべき隠れた料金はありますか？", "advanced"),
        ("are there any hidden fees", "Are there any hidden fees for cancellation?", "解約に隠れた料金はありますか？", "advanced"),
        ("are there any hidden fees", "I want to make sure there are no hidden fees.", "隠れた料金がないか確認したいです。", "advanced"),
    ],
    # === シナリオ29: 家電量販店で相談 ===
    29: [
        ("be looking for a ... that", "I'm looking for a laptop that's lightweight.", "軽いノートパソコンを探しています。", "intermediate"),
        ("be looking for a ... that", "I'm looking for a TV that has good picture quality.", "画質の良いテレビを探しています。", "intermediate"),
        ("be looking for a ... that", "I'm looking for a camera that's good for beginners.", "初心者向けのカメラを探しています。", "intermediate"),
        ("what's the difference between", "What's the difference between these two models?", "この2つのモデルの違いは何ですか？", "intermediate"),
        ("what's the difference between", "What's the difference between LED and OLED?", "LEDとOLEDの違いは何ですか？", "intermediate"),
        ("what's the difference between", "What's the difference in terms of performance?", "性能の違いは何ですか？", "intermediate"),
        ("does it come with a warranty", "Does it come with a warranty?", "保証は付いていますか？", "intermediate"),
        ("does it come with a warranty", "Does it come with an extended warranty option?", "延長保証のオプションはありますか？", "intermediate"),
        ("does it come with a warranty", "How long does the warranty last?", "保証期間はどのくらいですか？", "intermediate"),
    ],
    # === シナリオ30: オンライン注文の問い合わせ ===
    30: [
        ("would like to check on", "I would like to check on my order status.", "注文状況を確認したいのですが。", "beginner"),
        ("would like to check on", "I would like to check on my delivery.", "配送状況を確認したいのですが。", "beginner"),
        ("would like to check on", "I would like to check on a refund.", "返金について確認したいのですが。", "beginner"),
        ("hasn't arrived yet", "My package hasn't arrived yet.", "荷物がまだ届いていません。", "beginner"),
        ("hasn't arrived yet", "The item I ordered hasn't arrived yet.", "注文した商品がまだ届いていません。", "beginner"),
        ("hasn't arrived yet", "It says delivered but it hasn't arrived yet.", "配達済みとなっていますがまだ届いていません。", "beginner"),
        ("would like to return", "I would like to return this item.", "この商品を返品したいのですが。", "beginner"),
        ("would like to return", "I would like to return this for a refund.", "返金のためにこれを返品したいのですが。", "beginner"),
        ("would like to return", "How do I return this product?", "この商品はどうやって返品すればいいですか？", "beginner"),
    ],
    # === シナリオ31: 不動産屋で部屋探し ===
    31: [
        ("be looking for a place", "I'm looking for a place near the station.", "駅の近くの物件を探しています。", "advanced"),
        ("be looking for a place", "I'm looking for a place with two bedrooms.", "2LDKの物件を探しています。", "advanced"),
        ("be looking for a place", "I'm looking for a place that allows pets.", "ペット可の物件を探しています。", "advanced"),
        ("within my budget", "Is there anything within my budget?", "予算内で何かありますか？", "advanced"),
        ("within my budget", "I need to stay within my budget of $1500.", "1500ドルの予算内に収めたいです。", "advanced"),
        ("within my budget", "This is a bit over my budget.", "これは予算を少しオーバーしています。", "advanced"),
        ("would like to schedule a viewing", "I would like to schedule a viewing.", "内見の予約をしたいのですが。", "advanced"),
        ("would like to schedule a viewing", "When can I schedule a viewing?", "いつ内見できますか？", "advanced"),
        ("would like to schedule a viewing", "I would like to schedule a viewing for this weekend.", "今週末の内見を予約したいのですが。", "advanced"),
    ],
    # === シナリオ32: 引っ越し業者に見積もり依頼 ===
    32: [
        ("would like to get a quote", "I would like to get a quote for moving.", "引っ越しの見積もりをお願いしたいのですが。", "intermediate"),
        ("would like to get a quote", "I would like to get a quote for next month.", "来月の見積もりをお願いしたいのですが。", "intermediate"),
        ("would like to get a quote", "Can I get a quote over the phone?", "電話で見積もりをもらえますか？", "intermediate"),
        ("be moving from ... to", "I'm moving from Tokyo to Osaka.", "東京から大阪に引っ越します。", "intermediate"),
        ("be moving from ... to", "We're moving from an apartment to a house.", "アパートから一戸建てに引っ越します。", "intermediate"),
        ("be moving from ... to", "I'm moving from the 3rd floor to the 1st floor.", "3階から1階に引っ越します。", "intermediate"),
        ("how much would it cost", "How much would it cost for a small move?", "小さな引っ越しだといくらですか？", "intermediate"),
        ("how much would it cost", "How much would it cost to move this weekend?", "今週末の引っ越しだといくらですか？", "intermediate"),
        ("how much would it cost", "How much would it cost including packing?", "梱包込みだといくらですか？", "intermediate"),
    ],
    # === シナリオ33: 修理業者を呼ぶ ===
    33: [
        ("have a problem with", "I have a problem with my air conditioner.", "エアコンに問題があります。", "intermediate"),
        ("have a problem with", "I have a problem with my washing machine.", "洗濯機に問題があります。", "intermediate"),
        ("have a problem with", "I have a problem with my water heater.", "給湯器に問題があります。", "intermediate"),
        ("stopped working", "My refrigerator stopped working.", "冷蔵庫が動かなくなりました。", "intermediate"),
        ("stopped working", "The heater stopped working suddenly.", "暖房が突然動かなくなりました。", "intermediate"),
        ("stopped working", "It stopped working this morning.", "今朝動かなくなりました。", "intermediate"),
        ("how soon can you come", "How soon can you come to fix it?", "いつ修理に来てもらえますか？", "intermediate"),
        ("how soon can you come", "How soon can you come? It's urgent.", "いつ来れますか？緊急です。", "intermediate"),
        ("how soon can you come", "Can you come today or tomorrow?", "今日か明日来てもらえますか？", "intermediate"),
    ],
    # === シナリオ34: 隣人に挨拶・自己紹介 ===
    34: [
        ("just moved in", "Hi, I just moved in next door.", "こんにちは、隣に引っ越してきました。", "beginner"),
        ("just moved in", "We just moved in last week.", "先週引っ越してきたばかりです。", "beginner"),
        ("just moved in", "I just moved in to apartment 302.", "302号室に引っ越してきました。", "beginner"),
        ("nice to meet you", "Nice to meet you. I'm your new neighbor.", "はじめまして。新しい隣人です。", "beginner"),
        ("nice to meet you", "It's nice to meet you finally.", "やっとお会いできて嬉しいです。", "beginner"),
        ("nice to meet you", "Nice to meet you. I hope we get along.", "はじめまして。よろしくお願いします。", "beginner"),
        ("is there anything I should know", "Is there anything I should know about the building?", "建物について知っておくべきことはありますか？", "beginner"),
        ("is there anything I should know", "Is there anything I should know about garbage day?", "ゴミの日について知っておくべきことはありますか？", "beginner"),
        ("is there anything I should know", "Is there anything I should know about parking?", "駐車場について知っておくべきことはありますか？", "beginner"),
    ],
    # === シナリオ35: 郵便局で荷物を送る ===
    35: [
        ("would like to send this to", "I would like to send this to the United States.", "これをアメリカに送りたいのですが。", "beginner"),
        ("would like to send this to", "I would like to send this package to my family.", "この荷物を家族に送りたいのですが。", "beginner"),
        ("would like to send this to", "I would like to send this by express mail.", "これを速達で送りたいのですが。", "beginner"),
        ("how long will it take", "How long will it take to arrive?", "届くまでどのくらいかかりますか？", "beginner"),
        ("how long will it take", "How long will it take by regular mail?", "普通郵便だとどのくらいかかりますか？", "beginner"),
        ("how long will it take", "How long will it take for international delivery?", "国際配送だとどのくらいかかりますか？", "beginner"),
        ("can I get tracking", "Can I get tracking for this package?", "この荷物の追跡はできますか？", "beginner"),
        ("can I get tracking", "Can I get tracking and insurance?", "追跡と保険を付けられますか？", "beginner"),
        ("can I get tracking", "How much extra for tracking?", "追跡を付けるといくら追加ですか？", "beginner"),
    ],
    # === シナリオ36: 銀行で口座開設 ===
    36: [
        ("would like to open an account", "I would like to open a savings account.", "普通預金口座を開設したいのですが。", "intermediate"),
        ("would like to open an account", "I would like to open a checking account.", "当座預金口座を開設したいのですが。", "intermediate"),
        ("would like to open an account", "I would like to open an account for my child.", "子供の口座を開設したいのですが。", "intermediate"),
        ("what documents do I need", "What documents do I need to bring?", "何の書類を持ってくればいいですか？", "intermediate"),
        ("what documents do I need", "What documents do I need for verification?", "本人確認に何の書類が必要ですか？", "intermediate"),
        ("what documents do I need", "Do I need any documents besides my ID?", "身分証明書の他に書類は必要ですか？", "intermediate"),
        ("are there any fees", "Are there any fees for this account?", "この口座に手数料はありますか？", "intermediate"),
        ("are there any fees", "Are there any monthly fees?", "月額手数料はありますか？", "intermediate"),
        ("are there any fees", "Are there any fees for international transfers?", "海外送金に手数料はありますか？", "intermediate"),
    ],
    # === シナリオ37: 図書館で本を探す ===
    37: [
        ("be looking for books about", "I'm looking for books about Japanese history.", "日本史の本を探しています。", "beginner"),
        ("be looking for books about", "I'm looking for books about cooking.", "料理の本を探しています。", "beginner"),
        ("be looking for books about", "I'm looking for books about business.", "ビジネスの本を探しています。", "beginner"),
        ("where can I find", "Where can I find the fiction section?", "小説のコーナーはどこですか？", "beginner"),
        ("where can I find", "Where can I find children's books?", "児童書はどこにありますか？", "beginner"),
        ("where can I find", "Where can I find magazines?", "雑誌はどこにありますか？", "beginner"),
        ("how long can I borrow", "How long can I borrow this book?", "この本はどのくらい借りられますか？", "beginner"),
        ("how long can I borrow", "How long can I borrow DVDs?", "DVDはどのくらい借りられますか？", "beginner"),
        ("how long can I borrow", "Can I extend the borrowing period?", "貸出期間を延長できますか？", "beginner"),
    ],
    # === シナリオ38: 友人を食事に誘う ===
    38: [
        ("would you like to grab", "Would you like to grab lunch tomorrow?", "明日ランチでもどう？", "beginner"),
        ("would you like to grab", "Would you like to grab coffee sometime?", "いつかコーヒーでもどう？", "beginner"),
        ("would you like to grab", "Would you like to grab dinner after work?", "仕事の後、夕食でもどう？", "beginner"),
        ("are you free on", "Are you free on Saturday evening?", "土曜の夜は空いてる？", "beginner"),
        ("are you free on", "Are you free on the weekend?", "週末は空いてる？", "beginner"),
        ("are you free on", "Are you free on Friday for dinner?", "金曜の夕食、空いてる？", "beginner"),
        ("how about we go to", "How about we go to that new restaurant?", "あの新しいレストランに行かない？", "beginner"),
        ("how about we go to", "How about we go to the Italian place?", "イタリアンのお店に行かない？", "beginner"),
        ("how about we go to", "How about we go to somewhere quiet?", "静かなところに行かない？", "beginner"),
    ],
    # === シナリオ39: パーティーで初対面の人と会話 ===
    39: [
        ("how do you know", "How do you know the host?", "主催者とはどういうお知り合いですか？", "intermediate"),
        ("how do you know", "How do you know everyone here?", "ここにいる皆さんとはどういうお知り合いですか？", "intermediate"),
        ("how do you know", "How do you know each other?", "お二人はどういうお知り合いですか？", "intermediate"),
        ("what do you do", "What do you do for a living?", "お仕事は何をされていますか？", "intermediate"),
        ("what do you do", "What do you do in your free time?", "暇な時は何をしていますか？", "intermediate"),
        ("what do you do", "So, what do you do?", "それで、お仕事は？", "intermediate"),
        ("would love to keep in touch", "I would love to keep in touch with you.", "ぜひ連絡を取り合いたいです。", "intermediate"),
        ("would love to keep in touch", "Let's keep in touch!", "連絡を取り合いましょう！", "intermediate"),
        ("would love to keep in touch", "I would love to keep in touch. Here's my card.", "ぜひ連絡を取り合いたいです。名刺をどうぞ。", "intermediate"),
    ],
    # === シナリオ40: 習い事の体験申し込み ===
    40: [
        ("be interested in trying", "I'm interested in trying your yoga class.", "ヨガクラスを体験してみたいです。", "beginner"),
        ("be interested in trying", "I'm interested in trying the cooking course.", "料理コースを体験してみたいです。", "beginner"),
        ("be interested in trying", "I'm interested in trying a lesson.", "レッスンを体験してみたいです。", "beginner"),
        ("do you offer trial lessons", "Do you offer trial lessons?", "体験レッスンはありますか？", "beginner"),
        ("do you offer trial lessons", "Do you offer free trial lessons?", "無料の体験レッスンはありますか？", "beginner"),
        ("do you offer trial lessons", "How much are the trial lessons?", "体験レッスンはいくらですか？", "beginner"),
        ("what do I need to bring", "What do I need to bring for the class?", "クラスには何を持っていけばいいですか？", "beginner"),
        ("what do I need to bring", "What do I need to bring for the trial?", "体験には何を持っていけばいいですか？", "beginner"),
        ("what do I need to bring", "Do I need to bring my own equipment?", "自分の道具を持っていく必要がありますか？", "beginner"),
    ],
    # === シナリオ41: ジムに入会する ===
    41: [
        ("be looking to join", "I'm looking to join a gym.", "ジムに入会したいです。", "intermediate"),
        ("be looking to join", "I'm looking to join a fitness class.", "フィットネスクラスに入会したいです。", "intermediate"),
        ("be looking to join", "I'm looking to join as a family.", "家族で入会したいです。", "intermediate"),
        ("what's included in the membership", "What's included in the membership?", "会員特典には何が含まれていますか？", "intermediate"),
        ("what's included in the membership", "What's included in the basic membership?", "基本会員には何が含まれていますか？", "intermediate"),
        ("what's included in the membership", "Is the pool included in the membership?", "プールは会員に含まれていますか？", "intermediate"),
        ("are there any contracts", "Are there any long-term contracts?", "長期契約はありますか？", "intermediate"),
        ("are there any contracts", "Are there any cancellation fees?", "解約料はありますか？", "intermediate"),
        ("are there any contracts", "Can I cancel anytime without a contract?", "契約なしでいつでも解約できますか？", "intermediate"),
    ],
    # === シナリオ42: 機内でCAにリクエスト ===
    42: [
        ("could I have", "Could I have a blanket, please?", "ブランケットをいただけますか？", "beginner"),
        ("could I have", "Could I have some water?", "お水をいただけますか？", "beginner"),
        ("could I have", "Could I have another pillow?", "もう一つ枕をいただけますか？", "beginner"),
        ("would it be possible to", "Would it be possible to change my seat?", "席を変えていただくことは可能ですか？", "beginner"),
        ("would it be possible to", "Would it be possible to get a vegetarian meal?", "ベジタリアンミールをいただくことは可能ですか？", "beginner"),
        ("would it be possible to", "Would it be possible to recline my seat?", "席を倒すことは可能ですか？", "beginner"),
        ("is there any way to", "Is there any way to get headphones?", "ヘッドフォンをもらう方法はありますか？", "beginner"),
        ("is there any way to", "Is there any way to charge my phone?", "電話を充電する方法はありますか？", "beginner"),
        ("is there any way to", "Is there any way to get more legroom?", "足元のスペースを広げる方法はありますか？", "beginner"),
    ],
    # === シナリオ43: 乗り継ぎ便を確認 ===
    43: [
        ("have a connecting flight to", "I have a connecting flight to London.", "ロンドンへの乗り継ぎ便があります。", "intermediate"),
        ("have a connecting flight to", "I have a connecting flight in two hours.", "2時間後に乗り継ぎ便があります。", "intermediate"),
        ("have a connecting flight to", "My connecting flight leaves at 3 PM.", "乗り継ぎ便は午後3時発です。", "intermediate"),
        ("will I make my connection", "Will I make my connection if we're delayed?", "遅延した場合、乗り継ぎに間に合いますか？", "intermediate"),
        ("will I make my connection", "Will I make my connection with only 45 minutes?", "45分しかないですが、乗り継ぎに間に合いますか？", "intermediate"),
        ("will I make my connection", "I'm worried I won't make my connection.", "乗り継ぎに間に合わないか心配です。", "intermediate"),
        ("do I need to pick up my luggage", "Do I need to pick up my luggage?", "荷物を受け取る必要がありますか？", "intermediate"),
        ("do I need to pick up my luggage", "Do I need to pick up my luggage and recheck it?", "荷物を受け取って再度預ける必要がありますか？", "intermediate"),
        ("do I need to pick up my luggage", "Will my luggage transfer automatically?", "荷物は自動的に移されますか？", "intermediate"),
    ],
    # === シナリオ44: 荷物が届かない！ ===
    44: [
        ("my luggage didn't arrive", "My luggage didn't arrive on the carousel.", "私の荷物がターンテーブルに届きませんでした。", "advanced"),
        ("my luggage didn't arrive", "My luggage didn't arrive with the flight.", "私の荷物がフライトと一緒に届きませんでした。", "advanced"),
        ("my luggage didn't arrive", "I've been waiting but my luggage didn't arrive.", "待っていましたが、荷物が届きませんでした。", "advanced"),
        ("it's a ... colored suitcase", "It's a black suitcase with wheels.", "車輪付きの黒いスーツケースです。", "advanced"),
        ("it's a ... colored suitcase", "It's a blue hard-shell suitcase.", "青いハードシェルのスーツケースです。", "advanced"),
        ("it's a ... colored suitcase", "It's a red suitcase with a name tag.", "名札付きの赤いスーツケースです。", "advanced"),
        ("what compensation can I get", "What compensation can I get for this?", "これに対してどんな補償がありますか？", "advanced"),
        ("what compensation can I get", "What compensation can I get for the delay?", "遅延に対してどんな補償がありますか？", "advanced"),
        ("what compensation can I get", "Can I get compensation for my expenses?", "出費に対して補償を受けられますか？", "advanced"),
    ],
    # === シナリオ45: 空港でフライト変更 ===
    45: [
        ("need to change my flight", "I need to change my flight to tomorrow.", "フライトを明日に変更する必要があります。", "advanced"),
        ("need to change my flight", "I need to change my flight due to an emergency.", "緊急事態のためフライトを変更する必要があります。", "advanced"),
        ("need to change my flight", "I need to change my flight to an earlier time.", "フライトをもっと早い時間に変更する必要があります。", "advanced"),
        ("are there any available flights", "Are there any available flights today?", "今日利用可能なフライトはありますか？", "advanced"),
        ("are there any available flights", "Are there any available flights to New York?", "ニューヨーク行きの利用可能なフライトはありますか？", "advanced"),
        ("are there any available flights", "Are there any available direct flights?", "利用可能な直行便はありますか？", "advanced"),
        ("will there be any additional charges", "Will there be any additional charges?", "追加料金はありますか？", "advanced"),
        ("will there be any additional charges", "Will there be any additional charges for the change?", "変更に追加料金はありますか？", "advanced"),
        ("will there be any additional charges", "How much will the additional charges be?", "追加料金はいくらですか？", "advanced"),
    ],
    # === シナリオ46: レンタカーを借りる ===
    46: [
        ("would like to rent a", "I would like to rent a compact car.", "コンパクトカーを借りたいです。", "intermediate"),
        ("would like to rent a", "I would like to rent an SUV for the week.", "1週間SUVを借りたいです。", "intermediate"),
        ("would like to rent a", "I would like to rent an automatic car.", "オートマ車を借りたいです。", "intermediate"),
        ("what insurance options do you have", "What insurance options do you have?", "どんな保険オプションがありますか？", "intermediate"),
        ("what insurance options do you have", "What insurance options do you recommend?", "どの保険オプションがおすすめですか？", "intermediate"),
        ("what insurance options do you have", "Do I need additional insurance?", "追加の保険は必要ですか？", "intermediate"),
        ("where do I return the car", "Where do I return the car?", "車はどこで返却しますか？", "intermediate"),
        ("where do I return the car", "Can I return the car at a different location?", "別の場所で車を返却できますか？", "intermediate"),
        ("where do I return the car", "What time do I need to return the car?", "何時に車を返却する必要がありますか？", "intermediate"),
    ],
    # === シナリオ47: 電車・バスのチケット購入 ===
    47: [
        ("would like a ticket to", "I would like a ticket to Manchester.", "マンチェスター行きのチケットをお願いします。", "beginner"),
        ("would like a ticket to", "I would like two tickets to the city center.", "市内中心部へのチケットを2枚お願いします。", "beginner"),
        ("would like a ticket to", "I would like a ticket to the airport.", "空港行きのチケットをお願いします。", "beginner"),
        ("one way or round trip", "Is this ticket one way or round trip?", "このチケットは片道ですか往復ですか？", "beginner"),
        ("one way or round trip", "I'd like a round trip ticket.", "往復チケットをお願いします。", "beginner"),
        ("one way or round trip", "One way ticket, please.", "片道チケットをお願いします。", "beginner"),
        ("which platform does it leave from", "Which platform does it leave from?", "どのホームから出発しますか？", "beginner"),
        ("which platform does it leave from", "Which platform does the 10 AM train leave from?", "10時の電車はどのホームから出発しますか？", "beginner"),
        ("which platform does it leave from", "Can you tell me which platform?", "どのホームか教えていただけますか？", "beginner"),
    ],
    # === シナリオ48: ホテルの部屋に問題発生 ===
    48: [
        ("there's a problem with", "There's a problem with the air conditioning.", "エアコンに問題があります。", "intermediate"),
        ("there's a problem with", "There's a problem with the TV.", "テレビに問題があります。", "intermediate"),
        ("there's a problem with", "There's a problem with the shower.", "シャワーに問題があります。", "intermediate"),
        ("would it be possible to change rooms", "Would it be possible to change rooms?", "部屋を変更していただくことは可能ですか？", "intermediate"),
        ("would it be possible to change rooms", "Would it be possible to change to a quieter room?", "もっと静かな部屋に変更していただくことは可能ですか？", "intermediate"),
        ("would it be possible to change rooms", "Would it be possible to change to a higher floor?", "上の階に変更していただくことは可能ですか？", "intermediate"),
        ("can I get a discount", "Can I get a discount for the inconvenience?", "ご不便をおかけしたことで割引をいただけますか？", "intermediate"),
        ("can I get a discount", "Can I get a discount for tonight?", "今夜の分は割引をいただけますか？", "intermediate"),
        ("can I get a discount", "Is there any compensation I can get?", "何か補償をいただけますか？", "intermediate"),
    ],
    # === シナリオ49: ルームサービスを注文 ===
    49: [
        ("would like to order", "I would like to order from room service.", "ルームサービスで注文したいのですが。", "beginner"),
        ("would like to order", "I would like to order breakfast.", "朝食を注文したいのですが。", "beginner"),
        ("would like to order", "I would like to order the club sandwich.", "クラブサンドイッチを注文したいのですが。", "beginner"),
        ("could you leave out the", "Could you leave out the onions?", "玉ねぎを抜いてもらえますか？", "beginner"),
        ("could you leave out the", "Could you leave out the cheese?", "チーズを抜いてもらえますか？", "beginner"),
        ("could you leave out the", "Could you leave out the spicy sauce?", "辛いソースを抜いてもらえますか？", "beginner"),
        ("how long will it take", "How long will it take to deliver?", "届くまでどのくらいかかりますか？", "beginner"),
        ("how long will it take", "How long will it take for the order?", "注文が届くまでどのくらいかかりますか？", "beginner"),
        ("how long will it take", "Can you give me an estimate of how long it will take?", "どのくらいかかるか目安を教えていただけますか？", "beginner"),
    ],
    # === シナリオ50: レイトチェックアウトを交渉 ===
    50: [
        ("would it be possible to check out later", "Would it be possible to check out at 2 PM?", "午後2時にチェックアウトすることは可能ですか？", "intermediate"),
        ("would it be possible to check out later", "Would it be possible to check out a bit later?", "もう少し遅くチェックアウトすることは可能ですか？", "intermediate"),
        ("would it be possible to check out later", "Would it be possible to extend my checkout time?", "チェックアウト時間を延長することは可能ですか？", "intermediate"),
        ("is there an extra charge", "Is there an extra charge for late checkout?", "レイトチェックアウトには追加料金がありますか？", "intermediate"),
        ("is there an extra charge", "Is there an extra charge for extending by two hours?", "2時間延長すると追加料金がありますか？", "intermediate"),
        ("is there an extra charge", "How much is the extra charge?", "追加料金はいくらですか？", "intermediate"),
        ("could you hold my luggage", "Could you hold my luggage until the evening?", "夕方まで荷物を預かっていただけますか？", "intermediate"),
        ("could you hold my luggage", "Could you hold my luggage after checkout?", "チェックアウト後に荷物を預かっていただけますか？", "intermediate"),
        ("could you hold my luggage", "Is there a place to hold my luggage?", "荷物を預けられる場所はありますか？", "intermediate"),
    ],
    # === シナリオ51: Airbnbホストとやりとり ===
    51: [
        ("how do I get into", "How do I get into the apartment?", "アパートにはどうやって入ればいいですか？", "intermediate"),
        ("how do I get into", "How do I get into the building?", "建物にはどうやって入ればいいですか？", "intermediate"),
        ("how do I get into", "How do I get into the lockbox?", "鍵ボックスはどうやって開ければいいですか？", "intermediate"),
        ("is there ... available", "Is there WiFi available?", "WiFiはありますか？", "intermediate"),
        ("is there ... available", "Is there parking available?", "駐車場はありますか？", "intermediate"),
        ("is there ... available", "Is there a washing machine available?", "洗濯機はありますか？", "intermediate"),
        ("how can I reach you if", "How can I reach you if there's a problem?", "問題があった場合、どうやって連絡すればいいですか？", "intermediate"),
        ("how can I reach you if", "How can I reach you if I need help?", "助けが必要な場合、どうやって連絡すればいいですか？", "intermediate"),
        ("how can I reach you if", "What's the best way to reach you?", "連絡を取る最良の方法は何ですか？", "intermediate"),
    ],
    # === シナリオ52: 観光案内所で情報収集 ===
    52: [
        ("what do you recommend", "What do you recommend for first-time visitors?", "初めて訪れる人には何がおすすめですか？", "beginner"),
        ("what do you recommend", "What do you recommend seeing in one day?", "1日で見るには何がおすすめですか？", "beginner"),
        ("what do you recommend", "What do you recommend for families?", "家族連れには何がおすすめですか？", "beginner"),
        ("how do I get to", "How do I get to the main square?", "メイン広場にはどうやって行けますか？", "beginner"),
        ("how do I get to", "How do I get to the museum from here?", "ここから博物館にはどうやって行けますか？", "beginner"),
        ("how do I get to", "How do I get to the beach?", "ビーチにはどうやって行けますか？", "beginner"),
        ("do you have a map", "Do you have a map of the area?", "この地域の地図はありますか？", "beginner"),
        ("do you have a map", "Do you have a map in English?", "英語の地図はありますか？", "beginner"),
        ("do you have a map", "Do you have a free map I can take?", "持っていける無料の地図はありますか？", "beginner"),
    ],
    # === シナリオ53: 現地ツアーに申し込む ===
    53: [
        ("what does the tour include", "What does the tour include?", "ツアーには何が含まれていますか？", "intermediate"),
        ("what does the tour include", "What does the tour include for lunch?", "ツアーの昼食には何が含まれていますか？", "intermediate"),
        ("what does the tour include", "Does the tour include transportation?", "ツアーには交通費が含まれていますか？", "intermediate"),
        ("where do we meet", "Where do we meet for the tour?", "ツアーの集合場所はどこですか？", "intermediate"),
        ("where do we meet", "Where do we meet in the morning?", "朝の集合場所はどこですか？", "intermediate"),
        ("where do we meet", "What time and where do we meet?", "何時にどこで集合ですか？", "intermediate"),
        ("what's your cancellation policy", "What's your cancellation policy?", "キャンセルポリシーは何ですか？", "intermediate"),
        ("what's your cancellation policy", "What's your cancellation policy for bad weather?", "悪天候の場合のキャンセルポリシーは何ですか？", "intermediate"),
        ("what's your cancellation policy", "Can I get a full refund if I cancel?", "キャンセルした場合、全額返金されますか？", "intermediate"),
    ],
    # === シナリオ54: 美術館・博物館で質問 ===
    54: [
        ("how much is admission", "How much is admission for adults?", "大人の入場料はいくらですか？", "beginner"),
        ("how much is admission", "How much is admission for students?", "学生の入場料はいくらですか？", "beginner"),
        ("how much is admission", "Is admission free on certain days?", "特定の日は入場無料ですか？", "beginner"),
        ("do you have audio guides", "Do you have audio guides available?", "音声ガイドはありますか？", "beginner"),
        ("do you have audio guides", "Do you have audio guides in Japanese?", "日本語の音声ガイドはありますか？", "beginner"),
        ("do you have audio guides", "How much are the audio guides?", "音声ガイドはいくらですか？", "beginner"),
        ("where can I find", "Where can I find the impressionist paintings?", "印象派の絵画はどこにありますか？", "beginner"),
        ("where can I find", "Where can I find the gift shop?", "ギフトショップはどこですか？", "beginner"),
        ("where can I find", "Where can I find the special exhibition?", "特別展示はどこですか？", "beginner"),
    ],
    # === シナリオ55: 写真を撮ってもらう ===
    55: [
        ("would you mind taking", "Would you mind taking a photo of us?", "写真を撮っていただけますか？", "beginner"),
        ("would you mind taking", "Would you mind taking one more?", "もう一枚撮っていただけますか？", "beginner"),
        ("would you mind taking", "Would you mind taking a few photos?", "何枚か撮っていただけますか？", "beginner"),
        ("could you get ... in the background", "Could you get the tower in the background?", "背景にタワーを入れてもらえますか？", "beginner"),
        ("could you get ... in the background", "Could you get the sunset in the background?", "背景に夕日を入れてもらえますか？", "beginner"),
        ("could you get ... in the background", "Could you get the whole building in the frame?", "建物全体を入れてもらえますか？", "beginner"),
        ("thank you so much", "Thank you so much for your help!", "手伝っていただきありがとうございました！", "beginner"),
        ("thank you so much", "Thank you so much! That's perfect!", "ありがとうございます！完璧です！", "beginner"),
        ("thank you so much", "Thank you so much! Have a nice day!", "ありがとうございます！良い一日を！", "beginner"),
    ],
    # === シナリオ56: 現地の人におすすめを聞く ===
    56: [
        ("do you know any good", "Do you know any good restaurants around here?", "この辺りで良いレストランを知っていますか？", "intermediate"),
        ("do you know any good", "Do you know any good cafes nearby?", "近くに良いカフェを知っていますか？", "intermediate"),
        ("do you know any good", "Do you know any good places to visit?", "訪れる良い場所を知っていますか？", "intermediate"),
        ("what would you recommend for", "What would you recommend for dinner?", "夕食には何がおすすめですか？", "intermediate"),
        ("what would you recommend for", "What would you recommend for local food?", "地元の料理では何がおすすめですか？", "intermediate"),
        ("what would you recommend for", "What would you recommend for a quick meal?", "軽食には何がおすすめですか？", "intermediate"),
        ("how do I get there", "How do I get there from here?", "ここからどうやって行けますか？", "intermediate"),
        ("how do I get there", "How do I get there by public transport?", "公共交通機関でどうやって行けますか？", "intermediate"),
        ("how do I get there", "Is it far? How do I get there?", "遠いですか？どうやって行けますか？", "intermediate"),
    ],
    # === シナリオ57: 道に迷って助けを求める ===
    57: [
        ("trying to get to", "I'm trying to get to the train station.", "駅に行こうとしています。", "beginner"),
        ("trying to get to", "I'm trying to get to this address.", "この住所に行こうとしています。", "beginner"),
        ("trying to get to", "I'm trying to get to the city center.", "市内中心部に行こうとしています。", "beginner"),
        ("could you point me in the direction", "Could you point me in the direction of the park?", "公園の方向を教えていただけますか？", "beginner"),
        ("could you point me in the direction", "Could you point me in the right direction?", "正しい方向を教えていただけますか？", "beginner"),
        ("could you point me in the direction", "Could you point me in the direction of the hotel?", "ホテルの方向を教えていただけますか？", "beginner"),
        ("is it far from here", "Is it far from here?", "ここから遠いですか？", "beginner"),
        ("is it far from here", "Is it walking distance from here?", "ここから歩いて行ける距離ですか？", "beginner"),
        ("is it far from here", "How far is it from here?", "ここからどのくらい遠いですか？", "beginner"),
    ],
    # === シナリオ58: 体調不良で現地の病院へ ===
    58: [
        ("have been feeling ... since", "I have been feeling dizzy since this morning.", "今朝からめまいがしています。", "advanced"),
        ("have been feeling ... since", "I have been feeling nauseous since yesterday.", "昨日から吐き気がしています。", "advanced"),
        ("have been feeling ... since", "I have been feeling weak since last night.", "昨夜から体がだるいです。", "advanced"),
        ("have travel insurance", "I have travel insurance from my country.", "母国の旅行保険に入っています。", "advanced"),
        ("have travel insurance", "I have travel insurance. Here's the document.", "旅行保険に入っています。書類はこちらです。", "advanced"),
        ("have travel insurance", "Do you accept this travel insurance?", "この旅行保険は使えますか？", "advanced"),
        ("can I get a medical certificate", "Can I get a medical certificate?", "診断書をいただけますか？", "advanced"),
        ("can I get a medical certificate", "Can I get a medical certificate for my insurance?", "保険用の診断書をいただけますか？", "advanced"),
        ("can I get a medical certificate", "I need a medical certificate for work.", "仕事のために診断書が必要です。", "advanced"),
    ],
    # === シナリオ59: パスポート紛失の対応 ===
    59: [
        ("lost my passport", "I've lost my passport.", "パスポートをなくしました。", "advanced"),
        ("lost my passport", "I lost my passport yesterday.", "昨日パスポートをなくしました。", "advanced"),
        ("lost my passport", "I think I lost my passport at the hotel.", "ホテルでパスポートをなくしたと思います。", "advanced"),
        ("what do I need to do to get a replacement", "What do I need to do to get a replacement?", "再発行には何が必要ですか？", "advanced"),
        ("what do I need to do to get a replacement", "What do I need to do to get an emergency passport?", "緊急パスポートを取得するには何が必要ですか？", "advanced"),
        ("what do I need to do to get a replacement", "What documents do I need for a replacement?", "再発行にはどんな書類が必要ですか？", "advanced"),
        ("how long will it take", "How long will it take to get a new passport?", "新しいパスポートの取得にはどのくらいかかりますか？", "advanced"),
        ("how long will it take", "How long will it take for an emergency document?", "緊急書類の発行にはどのくらいかかりますか？", "advanced"),
        ("how long will it take", "I have a flight tomorrow. How long will it take?", "明日フライトがあります。どのくらいかかりますか？", "advanced"),
    ],
    # === シナリオ60: 両替所で両替 ===
    60: [
        ("would like to exchange", "I would like to exchange US dollars to yen.", "米ドルを円に両替したいのですが。", "beginner"),
        ("would like to exchange", "I would like to exchange 500 euros.", "500ユーロを両替したいのですが。", "beginner"),
        ("would like to exchange", "I would like to exchange these bills.", "これらの紙幣を両替したいのですが。", "beginner"),
        ("what's the exchange rate", "What's the exchange rate today?", "今日の為替レートはいくらですか？", "beginner"),
        ("what's the exchange rate", "What's the exchange rate for dollars?", "ドルの為替レートはいくらですか？", "beginner"),
        ("what's the exchange rate", "Is this a good exchange rate?", "これは良いレートですか？", "beginner"),
        ("could I have it in smaller bills", "Could I have it in smaller bills?", "小さい紙幣でいただけますか？", "beginner"),
        ("could I have it in smaller bills", "Could I have some in coins?", "いくらか硬貨でいただけますか？", "beginner"),
        ("could I have it in smaller bills", "Could I have a mix of large and small bills?", "大きい紙幣と小さい紙幣を混ぜていただけますか？", "beginner"),
    ],
    # === シナリオ61: お土産屋で買い物 ===
    61: [
        ("what's popular as a souvenir", "What's popular as a souvenir from here?", "ここからのお土産で人気なのは何ですか？", "beginner"),
        ("what's popular as a souvenir", "What's popular as a souvenir for kids?", "子供へのお土産で人気なのは何ですか？", "beginner"),
        ("what's popular as a souvenir", "What's popular as a gift for coworkers?", "同僚へのギフトで人気なのは何ですか？", "beginner"),
        ("is this made locally", "Is this made locally?", "これは地元で作られていますか？", "beginner"),
        ("is this made locally", "Is this handmade locally?", "これは地元で手作りされていますか？", "beginner"),
        ("is this made locally", "Are these products made locally?", "これらの商品は地元で作られていますか？", "beginner"),
        ("could you wrap it as a gift", "Could you wrap it as a gift?", "ギフト包装していただけますか？", "beginner"),
        ("could you wrap it as a gift", "Could you wrap these separately?", "これらを別々に包装していただけますか？", "beginner"),
        ("could you wrap it as a gift", "Could you add a ribbon?", "リボンを付けていただけますか？", "beginner"),
    ],
}


def get_shadowing_sentences_for_scenario(scenario_id: int) -> List[Dict[str, Any]]:
    """指定シナリオIDのシャドーイング文を取得"""
    data = SHADOWING_SEED_DATA.get(scenario_id, [])
    result = []
    for idx, (key_phrase, sentence_en, sentence_ja, difficulty) in enumerate(data, start=1):
        result.append({
            "scenario_id": scenario_id,
            "key_phrase": key_phrase,
            "sentence_en": sentence_en,
            "sentence_ja": sentence_ja,
            "order_index": idx,
            "difficulty": difficulty,
        })
    return result


def get_all_shadowing_sentences() -> List[Dict[str, Any]]:
    """全シナリオのシャドーイング文を取得"""
    all_sentences = []
    for scenario_id in SHADOWING_SEED_DATA.keys():
        all_sentences.extend(get_shadowing_sentences_for_scenario(scenario_id))
    return all_sentences
