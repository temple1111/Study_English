
import json

def main():
    print("英単語学習CLIアプリへようこそ！")
    print("まずはあなたのことを教えてください。")

    user_profile = {}

    user_profile["name"] = input("お名前を教えてください: ")
    user_profile["level"] = input("現在の英語レベルを教えてください（例: 初級、中級、上級）: ")
    user_profile["goal"] = input("学習目標を教えてください（例: TOEIC 800点、日常会話、ビジネス英語）: ")

    print(f"\n{user_profile['name']}さん、こんにちは！")
    print(f"あなたの英語レベルは {user_profile['level']}、目標は {user_profile['goal']} ですね。")
    print("これから一緒に頑張りましょう！")

    learning_mode(user_profile) # Call the learning mode

if __name__ == "__main__":
    main()

def learning_mode(user_profile):
    words = [
        {"word": "ubiquitous", "meaning": "どこにでもある、偏在する"},
        {"word": "ephemeral", "meaning": "つかの間の、はかない"},
        {"word": "benevolent", "meaning": "慈悲深い、親切な"},
        {"word": "cacophony", "meaning": "不協和音、耳障りな音"},
        {"word": "dichotomy", "meaning": "二分、両極端"},
    ]
    correct_answers = 0
    total_questions = len(words)

    print("\n--- 学習モード開始 ---")
    print("単語の意味を答えてください。")

    for i, item in enumerate(words):
        print(f"\nQ{i+1}: {item['word']}")
        user_answer = input("意味: ")
        if user_answer == item['meaning']:
            print("正解！")
            correct_answers += 1
        else:
            print(f"不正解。正解は「{item['meaning']}」でした。")
        # ここにAIによる解説や類義語の提供ロジックを追加予定

    print("\n--- 学習モード終了 ---")
    accuracy_percentage = (correct_answers / total_questions) * 100
    print(f"結果: {total_questions}問中 {correct_answers}問正解 ({accuracy_percentage:.2f}%)") 

    if accuracy_percentage >= 80: # 例: 80%以上で記録を提案
        print("\n素晴らしい！目標達成です！")
        record_choice = input("この学習成果をSymbolブロックチェーンに記録しますか？ (y/n): ").lower()
        if record_choice == 'y':
            # 仮のユーザーIDと学習内容
            user_id = user_profile["name"] # 仮に名前をIDとする
            learning_content = f"英単語学習（{user_profile['level']}レベル）"
            record_achievement_on_blockchain(user_id, learning_content, accuracy_percentage)
        else:
            print("記録をスキップしました。")


def record_achievement_on_blockchain(user_id, learning_content, accuracy_rate):
    """
    学習成果をSymbolブロックチェーンに記録する関数（仮実装）
    """
    print("\n--- ブロックチェーン記録機能 ---")
    print(f"ユーザーID: {user_id}")
    print(f"学習内容: {learning_content}")
    print(f"正解率: {accuracy_rate:.2f}%")
    print("Symbolブロックチェーンに記録を試みます...")

    # ここにSymbol SDKを使った実際のトランザクション発行ロジックを実装
    # 例:
    # facade = NemFacade(Network.TESTNET)
    # private_key = PrivateKey.random() # テスト用、実際はユーザーの秘密鍵を使用
    # signer = facade.create_signer(private_key)
    # 
    # message_payload = json.dumps({
    #     "userId": user_id,
    #     "date": datetime.now().isoformat(),
    #     "content": learning_content,
    #     "accuracy": accuracy_rate
    # })
    # 
    # transaction = facade.create_transfer_transaction(
    #     signer.public_key,
    #     facade.network.public_key, # Recipient (e.g., a dedicated achievement account)
    #     1, # Amount (e.g., 1 unit of native token, or 0 if only message)
    #     Message(message_payload.encode('utf8'))
    # )
    # 
    # signed_transaction = signer.sign(transaction)
    # 
    # # Announce the transaction (requires a node URL)
    # # print(f"Transaction hash: {signed_transaction.hash}")
    # # print(f"Transaction payload: {signed_transaction.payload}")
    print("（実際にはSymbolブロックチェーンに記録されました）")
    print("記録が完了しました！")

from datetime import datetime
